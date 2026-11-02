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
 send('WebDriver:Navigate',{'url':(OUT/'replay.html').as_uri()+'?frame=22'})
 for _ in range(100):
  if js("return !!document.getElementById('sensorStatus').textContent;"):break
  time.sleep(.1)
 result=js("""
 const sample=(t,e=0)=>frames.find(f=>Math.abs(f.t-t)<1e-7&&f.epoch===e);
 const blocked=telemetryAt('robot1','scan',sample(.5)),clear=telemetryAt('robot1','scan',sample(1.1));
 const key='0:robot1:scan',original=navigationIndex.get(key),sparse=[{...original[0]},{...clear}];
 navigationIndex.set(key,sparse);const gapEntry=rangeEntry(sparse[1],'nguoi_A');navigationIndex.set(key,original);
 const b=scanPeople(blocked,scanPoints(blocked),sample(.5)),c=scanPeople(clear,scanPoints(clear),sample(1.1));
 return {out:scanPeople(telemetryAt('robot1','scan',sample(0.)),scanPoints(telemetryAt('robot1','scan',sample(0.))),sample(0.)),
 blocked:b,clear:c,projection:scanPoints(clear).points[0],
 noFutureAstar:telemetryAt('robot1','astar',sample(1.))===null,
 astar:telemetryAt('robot1','astar',sample(1.1)).goal,mpc:telemetryAt('robot1','decision',sample(1.1)).goal,
 clearAstar:telemetryAt('robot1','astar',sample(1.4)).goal===null,
 clearMpc:telemetryAt('robot1','decision',sample(1.4)).goal===null,
 noOldEpoch:telemetryAt('robot1','astar',sample(.1,1))===null,
 missingTransform:scanPoints({...clear,extrinsic:null})===null,
 gapEntry,entry:rangeEntry(clear,'nguoi_A'),delayedScan:telemetryAt('robot1','scan',sample(1.)).stamp<1.,allThree:['robot1','robot2','robot3'].every(n=>telemetryAt(n,'scan',sample(1.1))!==null),
 label:document.getElementById('sensorStatus').textContent};
 """)
 assert result['out']['inRange']==[],result
 assert result['blocked']['inRange']==['nguoi_A'] and result['blocked']['nearReturns']==[],result
 assert result['clear']['nearReturns'][0]['name']=='nguoi_A',result
 assert abs(result['projection'][0]-1.)<1e-5 and abs(result['projection'][1])<1e-5,result
 assert result['entry']=={'from':.1,'to':.2},result
 assert result['gapEntry']=={'from':None,'to':1.} and result['delayedScan'],result
 assert result['astar']==[0.,.72] and result['mpc']==[.72,0.],result
 assert all(result[k] for k in ['noFutureAstar','clearAstar','clearMpc','noOldEpoch','missingTransform','allThree']),result
 picture=send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})
 (OUT/'all_robots.png').write_bytes(base64.b64decode(picture))
 js("document.getElementById('sensorRobot').value='robot1';document.getElementById('lidarRays').checked=true;render();")
 (OUT/'viewer.png').write_bytes(base64.b64decode(send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})))
 png=js("return document.getElementById('map').toDataURL('image/png').split(',')[1];")
 (OUT/'canvas_export.png').write_bytes(base64.b64decode(png))
 js("document.getElementById('seek').value=frames.findIndex(f=>f.epoch===0&&f.t===2.);document.getElementById('seek').dispatchEvent(new Event('input'));")
 assert 'DỮ LIỆU CŨ' in js("return document.getElementById('sensorStatus').textContent;"),result
 js("accept({scene:scene,frames:frames,goals:[]});")
 assert 'Cần ghi phiên mới' in js("return document.getElementById('sensorStatus').textContent;"),result
 # Serve a copy, preserving raw ROS fixture data as evidence.
 live=Path(tempfile.mkdtemp(prefix='nk074_http_'))
 for name in ['scene.json','world_frames.jsonl','navigation.jsonl','navigation_status.json']:
  shutil.copy2(OUT/'dense_fixture'/name,live/name)
 server=subprocess.Popen(['/usr/bin/python3','scripts/view_replay.py','--session',str(live),'--port','8774','--no-browser'],stdout=(OUT/'http.log').open('w'),stderr=subprocess.STDOUT)
 for _ in range(100):
  try:
   response=json.load(urllib.request.urlopen('http://127.0.0.1:8774/navigation?offset=0'));break
  except OSError:time.sleep(.05)
 assert len(response['navigation'])>5
 send('WebDriver:Navigate',{'url':'http://127.0.0.1:8774'})
 for _ in range(100):
  if js("return typeof navigation!=='undefined' && navigation.length>5;"):break
  time.sleep(.1)
 js("document.getElementById('live').checked=false;index=frames.findIndex(f=>f.epoch===0&&f.t===1.1);render();")
 assert 'MPC chọn' in js("return document.getElementById('sensorStatus').textContent;")
 offset=response['offset']
 with (live/'navigation.jsonl').open('a') as f:f.write('{"t":')
 partial=json.load(urllib.request.urlopen(f'http://127.0.0.1:8774/navigation?offset={offset}'))
 assert partial['offset']==offset and partial['navigation']==[]
 # Complete that row to prove incremental updates and epoch isolation.
 event={'t':.15,'stamp':.15,'epoch':1,'robot':'robot1','kind':'astar','goal':[.2,.2],'points':[[0.,0.],[.2,.2]]}
 with (live/'navigation.jsonl').open('a') as f:f.write(json.dumps(event)[len('{"t":'): ]+'\n')
 frame=json.loads((live/'world_frames.jsonl').read_text().splitlines()[-1]);frame['t']=.15
 with (live/'world_frames.jsonl').open('a') as f:f.write(json.dumps(frame)+'\n')
 for _ in range(100):
  if js("return frames.at(-1).t===.15;"):break
  time.sleep(.1)
 assert js("return telemetryAt('robot1','astar',frames.at(-1)).goal;")==[.2,.2]
 result.update(stale_hidden=True,legacy_missing_explicit=True,http_incremental=True,http_partial_line=True,png_export=True,fixture_only=True)
 (OUT/'browser_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS: range vs occluded returns, capture yaw, delayed receive, separate A*/MPC, clear/reset/stale/legacy, HTTP partial/incremental, PNG')
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
finally:
 if server is not None:server.terminate();server.wait(timeout=5)
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
