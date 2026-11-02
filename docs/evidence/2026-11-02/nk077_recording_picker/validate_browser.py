"""Firefox verifies live/offline overlays using synthetic poses + ROS fixtures."""
import base64,json,os,shutil,socket,subprocess,tempfile,time,urllib.request
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
profile=Path(tempfile.mkdtemp(prefix='nk074_browser_',dir='/home/duc/snap/firefox/common'))
(profile/'user.js').write_text('user_pref("marionette.port", 2834);\n')
env=os.environ.copy();env.update(MOZ_DISABLE_CONTENT_SANDBOX='1',LIBGL_ALWAYS_SOFTWARE='1')
proc=subprocess.Popen(['firefox','--headless','--no-remote','--marionette','--profile',str(profile),'about:blank'],env=env,stdout=(OUT/'browser.log').open('w'),stderr=subprocess.STDOUT)
server=None
try:
 for _ in range(150):
  try:sock=socket.create_connection(('127.0.0.1',2834),timeout=1);break
  except OSError:time.sleep(.1)
 else:raise RuntimeError('No Firefox control port')
 sock.settimeout(30)
 def recv():
  prefix=b''
  while not prefix.endswith(b':'):prefix+=sock.recv(1)
  remaining=int(prefix[:-1]);data=b''
  while len(data)<remaining:data+=sock.recv(remaining-len(data))
  return json.loads(data)
 recv();sequence=0
 def send(name,params):
  global sequence
  sequence+=1;data=json.dumps([0,sequence,name,params]).encode();sock.sendall(str(len(data)).encode()+b':'+data)
  response=recv();assert response[2] is None,response
  return response[3].get('value',response[3]) if isinstance(response[3],dict) else response[3]
 def js(code):return send('WebDriver:ExecuteScript',{'script':'return window.eval('+json.dumps('(function(){'+code+'})()')+');','args':[]})
 send('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{}}})
 send('WebDriver:SetWindowRect',{'x':0,'y':0,'width':1700,'height':1150})
 # HTTP fixture has two recordings with distinct scene/frames/goals/scans.
 import threading
 from http.server import ThreadingHTTPServer
 import sys
 sys.path.insert(0,str(ROOT/'scripts'))
 import view_replay
 fixture=Path(tempfile.mkdtemp(prefix='nk077_recordings_'))
 view_replay.ROOT=fixture
 for name,t in [('current',1.),('cũ có dấu',2.)]:
  folder=fixture/'recordings'/name;folder.mkdir(parents=True)
  (folder/'scene.json').write_text(json.dumps({'world':name,'objects':{},'bounds':[-3,-3,3,3]}))
  (folder/'world_frames.jsonl').write_text(json.dumps({'t':t,'epoch':0,'objects':[]})+'\n')
  (folder/'goals.jsonl').write_text(json.dumps({'t':t,'epoch':0,'xy':[t,0]})+'\n')
 http=ThreadingHTTPServer(('127.0.0.1',0),view_replay.make_handler(fixture/'recordings'/'current'))
 thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
 url=f'http://127.0.0.1:{http.server_port}/'
 def waitfor(expression):
  for _ in range(120):
   if js('return '+expression+';'):return
   time.sleep(.1)
  raise AssertionError(expression)
 send('WebDriver:Navigate',{'url':url})
 waitfor("scene?.world==='current' && frames.length===1 && document.getElementById('recordingList').options.length===2")
 js("document.getElementById('recordingList').value='saved:cũ có dấu';document.getElementById('openRecording').click();")
 waitfor("scene?.world==='cũ có dấu' && frames.length===1 && frames[0].t===2 && goals[0]?.xy[0]===2")
 assert 'recording=' in js('return location.search;')
 # Folder loading on HTTP stops future polling, even after the timer ticks.
 js(r"""window.folderLoad=loadFiles([
 new File([JSON.stringify({world:'folder',objects:{},bounds:[-3,-3,3,3]})],'scene.json'),
 new File([JSON.stringify({t:7,epoch:0,objects:[]})+'\n'+ '{\"t\":'],'world_frames.jsonl')
 ]);""")
 waitfor("offline && scene?.world==='folder' && frames.length===1 && frames[0].t===7")
 time.sleep(1.3)
 assert js("return scene.world==='folder' && frames[0].t===7 && !document.getElementById('live').checked;")
 (OUT/'picker.png').write_bytes(base64.b64decode(send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})))
 # Standalone export still supports manually selecting another local folder.
 standalone=OUT/'offline.html'
 standalone.write_text(view_replay.TEMPLATE.read_text().replace('__REPLAY_DATA__',json.dumps({'scene':{'world':'embedded','objects':{},'bounds':[-3,-3,3,3]},'frames':[{'t':9,'epoch':0,'objects':[]}]})))
 send('WebDriver:Navigate',{'url':standalone.as_uri()})
 waitfor("scene?.world==='embedded'")
 assert js("return document.getElementById('recordingList').disabled && !document.getElementById('openFolder').disabled;")
 result={'http_switch_unicode':True,'scene_frames_goals_match_selected':True,'folder_import':True,'partial_tail_ignored':True,'http_poll_does_not_replace_local_folder':True,'standalone_folder_available':True,'gazebo_started':False}
 (OUT/'browser_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS browser recording switch, folder import, no mixed poll, standalone')
 http.shutdown();http.server_close();thread.join()
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
finally:
 if server is not None:server.terminate();server.wait(timeout=5)
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
