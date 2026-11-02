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
 import threading,sys
 from http.server import ThreadingHTTPServer
 sys.path.insert(0,str(ROOT/'scripts'));import view_replay
 runtime=ROOT/'recordings/nk078_social_camera_120s_once'
 http=ThreadingHTTPServer(('127.0.0.1',0),view_replay.make_handler(runtime))
 thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
 def waitfor(expression):
  for _ in range(300):
   if js('return '+expression+';'):return
   time.sleep(.1)
  raise AssertionError(expression)
 def seek(t):
  js(f"document.getElementById('live').checked=false;index=frames.findIndex(f=>f.t>={t});render();")
 send('WebDriver:Navigate',{'url':f'http://127.0.0.1:{http.server_port}/'})
 waitfor("frames.at(-1)?.t>=120 && perception.some(p=>p.kind==='camera'&&p.t>100)")
 seek(1.)
 assert js("return document.getElementById('leaderCamera').hidden;")
 seek(14.5)
 waitfor("document.getElementById('leaderCamera').complete && document.getElementById('leaderCamera').naturalWidth>0")
 assert js("return document.getElementById('socialStatus').textContent.includes('viewing_tv');")
 assert js("return document.getElementById('cameraStatus').textContent.includes('RỜI RẠC') && document.getElementById('cameraStatus').textContent.includes('ẢNH CŨ');")
 assert js("return perceptionAt('camera',frames[index],'detection').t;")==3.556
 (OUT/'tv_overlay.png').write_bytes(base64.b64decode(send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})))
 seek(84.5)
 assert js("return perceptionAt('camera',frames[index],'detection').t;")==64.501
 seek(84.9)
 waitfor("document.getElementById('leaderCamera').complete && document.getElementById('leaderCamera').naturalWidth>0")
 assert js("return perceptionAt('camera',frames[index],'detection').t;")==84.704
 assert js("return replayPNGCanvas().width===canvas.width+400;")
 png=js("return replayPNGCanvas().toDataURL('image/png').split(',')[1];")
 (OUT/'contact_camera.png').write_bytes(base64.b64decode(png))
 assert js("return !document.getElementById('cameraStatus').textContent.includes('ẢNH CŨ');")
 # Clear, old social TTL, separate epochs and legacy without perception.
 checks=js(r"""
 const f=frames[index],initial=perception;
 indexPerception([{t:1,stamp:1,epoch:7,kind:'social',regions:[{label:'fixture',points:[[0,0],[1,0],[0,1]]}]},{t:2,stamp:2,epoch:7,kind:'social',regions:[]}],true);
 drawPerception({t:1.5,epoch:7},null);const active=document.getElementById('socialStatus').textContent.includes('fixture');
 drawPerception({t:2.1,epoch:7},null);const clear=document.getElementById('socialStatus').textContent.startsWith('0 vùng');
 drawPerception({t:5,epoch:7},null);const stale=document.getElementById('socialStatus').textContent.includes('đã ẩn');
 const epoch=perceptionAt('social',{t:3,epoch:8})===null;
 indexPerception(initial,true);document.getElementById('cameraSource').value='raw';render();const rawMissing=document.getElementById('leaderCamera').hidden;
 document.getElementById('cameraSource').value='auto';render();
 return {active,clear,stale,epoch,rawMissing};
 """)
 assert all(checks.values()),checks
 # Standalone export must retain the original camera data and overlays.
 view_replay.export(runtime,OUT/'replay.html')
 send('WebDriver:Navigate',{'url':(OUT/'replay.html').as_uri()+'?frame=290'})
 waitfor("perception.length>0 && scene!==null")
 seek(14.5)
 waitfor("document.getElementById('leaderCamera').complete && document.getElementById('leaderCamera').naturalWidth>0")
 assert js("return document.getElementById('socialStatus').textContent.includes('viewing_tv');")
 js("accept({scene:scene,frames:frames});")
 assert js("return document.getElementById('leaderCamera').hidden && !document.getElementById('socialStatus').textContent.includes('viewing_tv');")
 result=dict(checks,http_replay=True,sparse_images_original=True,no_future_camera=True,social_overlay=True,png_with_camera=True,standalone=True,legacy_clear=True,gazebo_started=False)
 (OUT/'browser_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS original NK078 camera/social overlay, no future frames, sparse/stale labels, clear/epoch, PNG, HTML, legacy')
 http.shutdown();http.server_close();thread.join()
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
 import gzip,shutil
 with (OUT/'replay.html').open('rb') as src,gzip.open(OUT/'replay.html.gz','wb') as dst:shutil.copyfileobj(src,dst)
 (OUT/'replay.html').unlink()
finally:
 if server is not None:server.terminate();server.wait(timeout=5)
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
