"""Switch every replay stream together without exposing arbitrary local paths."""
import json
from pathlib import Path
import sys
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen
from urllib.parse import urlencode

import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import view_replay


def recording(path,t):
    path.mkdir(parents=True)
    for name,data in [('scene.json',{'name':path.name}),('session.json',{'state':path.name}),('navigation_status.json',{'bytes':t})]:
        (path/name).write_text(json.dumps(data))
    for name,data in [('world_frames.jsonl',{'t':t,'objects':[]}),('goals.jsonl',{'t':t,'xy':[t,0]}),('navigation.jsonl',{'t':t,'kind':'scan'}),('perception.jsonl',{'t':t,'kind':'social','regions':[]})]:
        (path/name).write_text(json.dumps(data)+'\n')
    return path


def test_catalog_and_switch_isolated_streams_and_reject_unknown_path(tmp_path,monkeypatch):
    monkeypatch.setattr(view_replay,'ROOT',tmp_path)
    current=recording(tmp_path/'recordings'/'current',1)
    old=recording(tmp_path/'recordings'/'cũ có dấu',2)
    (tmp_path/'recordings'/'incomplete').mkdir()
    outside=recording(tmp_path/'private',3)
    (tmp_path/'recordings'/'outside_link').symlink_to(outside,target_is_directory=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),view_replay.make_handler(current))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def get(path):
        with urlopen(f'http://127.0.0.1:{server.server_port}'+path) as response:return json.load(response)
    query='?'+urlencode({'recording':'saved:'+old.name})
    try:
        catalog=get('/recordings')
        assert [r['id'] for r in catalog['recordings']]==['','saved:'+old.name]
        assert get('/scene')['name']=='current'
        assert get('/scene'+query)['name']==old.name
        assert get('/frames'+query)['frames'][0]['t']==2
        assert get('/navigation'+query)['navigation'][0]['t']==2
        assert get('/perception'+query)['perception'][0]['t']==2
        assert get('/session'+query)['state']==old.name
        assert get('/goals'+query)[0]['t']==2
        assert get('/navigation-status'+query)['bytes']==2
        assert get('/scene')['name']=='current'  # another tab unaffected
        recording(tmp_path/'recordings'/'new',4)
        assert any(r['id']=='saved:new' for r in get('/recordings')['recordings'])
        for key in ['../private','saved:../private','saved:outside_link','saved:missing']:
            with pytest.raises(HTTPError) as error:get('/scene?'+urlencode({'recording':key}))
            assert error.value.code==400
    finally:
        server.shutdown();server.server_close();thread.join()
