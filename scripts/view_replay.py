#!/usr/bin/env python3
"""Open live/offline top-down replay; browse recorded sessions on localhost."""
import argparse
import json
from pathlib import Path
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=Path(__file__).with_name('replay_viewer.html')


def complete_frames(path):
    if not path.exists():
        raise ValueError('No world_frames.jsonl. This older session did not record measured Gazebo poses; start a new session.')
    content=path.read_text()
    lines=content.rpartition('\n')[0].splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def complete_goals(folder):
    path=folder/'goals.jsonl'
    if not path.exists():return []
    text=path.read_text()
    return [json.loads(line) for line in text.rpartition('\n')[0].splitlines() if line.strip()]


def complete_navigation(folder):
    path=folder/'navigation.jsonl'
    if not path.exists():return []
    return [json.loads(line) for line in path.read_text().rpartition('\n')[0].splitlines() if line.strip()]


def complete_perception(folder):
    path=folder/'perception.jsonl'
    if not path.exists():return []
    return [json.loads(line) for line in path.read_text().rpartition('\n')[0].splitlines() if line.strip()]


def export(folder, target):
    scene=json.loads((folder/'scene.json').read_text())
    frames=complete_frames(folder/'world_frames.jsonl')
    if not frames:raise ValueError('No complete Gazebo frames recorded yet')
    session=json.loads((folder/'session.json').read_text()) if (folder/'session.json').exists() else {}
    data=json.dumps({'scene':scene,'frames':frames,'session':session,'goals':complete_goals(folder),'navigation':complete_navigation(folder),'perception':complete_perception(folder),'perception_status':json.loads((folder/'perception_status.json').read_text()) if (folder/'perception_status.json').exists() else {},'navigation_status':json.loads((folder/'navigation_status.json').read_text()) if (folder/'navigation_status.json').exists() else {}},ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
    target.write_text(TEMPLATE.read_text().replace('__REPLAY_DATA__',data))
    print(f'Saved standalone replay: {target} ({len(frames)} frames)')


def available_recordings(folder):
    """Only expose replay directories, never arbitrary request paths."""
    result={'':folder.resolve()}
    root=(ROOT/'recordings').resolve()
    if root.is_dir():
        candidates=[]
        for path in root.iterdir():
            try:
                resolved=path.resolve()
                if (resolved.is_relative_to(root) and resolved.is_dir()
                        and (resolved/'scene.json').is_file()
                        and (resolved/'world_frames.jsonl').is_file()):
                    candidates.append((path.stat().st_mtime,path.name,resolved))
            except OSError:continue
        for _,name,path in sorted(candidates,reverse=True):
            if path!=folder.resolve():result['saved:'+name]=path
    return result


def make_handler(folder):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,value,kind='application/json'):
            content=value.encode() if isinstance(value,str) else json.dumps(value,allow_nan=False).encode()
            self.send_response(200);self.send_header('Content-Type',kind+'; charset=utf-8')
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
        def do_GET(self):
            request=urlparse(self.path)
            try:
                query=parse_qs(request.query)
                choices=available_recordings(folder)
                selected=query.get('recording',[''])[0]
                if selected not in choices:raise ValueError('Recording not found; refresh the recording list')
                current=choices[selected]
                if request.path=='/recordings':
                    self.send({'selected':selected,'recordings':[
                        {'id':key,'name':path.name+(' (mở ban đầu)' if key=='' else '')}
                        for key,path in choices.items()]})
                elif request.path=='/':self.send(TEMPLATE.read_text().replace('__REPLAY_DATA__','null'),'text/html')
                elif request.path=='/scene':self.send(json.loads((current/'scene.json').read_text()))
                elif request.path=='/session':self.send(json.loads((current/'session.json').read_text()) if (current/'session.json').exists() else {'state':'unknown'})
                elif request.path=='/goals':self.send(complete_goals(current))
                elif request.path=='/perception-status':self.send(json.loads((current/'perception_status.json').read_text()) if (current/'perception_status.json').exists() else {})
                elif request.path=='/navigation-status':self.send(json.loads((current/'navigation_status.json').read_text()) if (current/'navigation_status.json').exists() else {})
                elif request.path in ('/frames','/navigation','/perception'):
                    field=request.path.lstrip('/')
                    offset=max(0,int(parse_qs(request.query).get('offset',['0'])[0]));path=current/('world_frames.jsonl' if field=='frames' else field+'.jsonl')
                    if not path.exists():self.send({'offset':0,field:[]});return
                    reset=offset>path.stat().st_size
                    if reset:offset=0
                    with path.open('rb') as stream:
                        stream.seek(offset);chunk=stream.read(2*1024*1024)
                    end=chunk.rfind(b'\n')+1
                    frames=[json.loads(line) for line in chunk[:end].splitlines() if line.strip()]
                    self.send({'offset':offset+end,field:frames,'reset':reset})
                else:self.send_error(404)
            except (BrokenPipeError,ConnectionResetError):pass
            except (OSError,ValueError,KeyError) as error:self.send_error(400,str(error))
    return Handler


def serve(folder,port,open_browser):
    server=ThreadingHTTPServer(('127.0.0.1',port),make_handler(folder))
    url=f'http://127.0.0.1:{server.server_port}'
    print(f'Replay: {url}\nInitial recording: {folder}; use the recording picker to switch\nCtrl+C closes viewer only.',flush=True)
    if open_browser:threading.Timer(.4,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',type=Path,required=True)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--export',type=Path,help='Write a standalone HTML instead of running server')
    args=parser.parse_args();folder=args.session.resolve()
    if not (folder/'scene.json').exists():parser.error('This session has no scene.json; run a new simulation with replay recording.')
    try:
        if args.export:export(folder,args.export.resolve())
        else:serve(folder,args.port,not args.no_browser)
    except (ValueError,OSError) as error:parser.exit(1,str(error)+'\n')
