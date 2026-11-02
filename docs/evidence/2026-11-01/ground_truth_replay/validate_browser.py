import socket,json,time,subprocess,os,base64
from pathlib import Path
out=Path('/home/duc/three-robot-rescue/docs/evidence/2026-11-01/ground_truth_replay')
env=os.environ.copy();env.update(MOZ_DISABLE_CONTENT_SANDBOX='1',LIBGL_ALWAYS_SOFTWARE='1')
proc=subprocess.Popen(['firefox','--headless','--no-remote','--marionette','--profile','/home/duc/snap/firefox/common/replay_test_profile_20261101','about:blank'],env=env,stdout=(out/'browser_verified.log').open('w'),stderr=subprocess.STDOUT)
try:
 for _ in range(100):
  try:sock=socket.create_connection(('127.0.0.1',2829),timeout=1);break
  except OSError:time.sleep(.1)
 else:raise RuntimeError('No browser control port')
 sock.settimeout(20)
 def recv():
  prefix=b''
  while not prefix.endswith(b':'):prefix+=sock.recv(1)
  remaining=int(prefix[:-1]);data=b''
  while len(data)<remaining:data+=sock.recv(remaining-len(data))
  return json.loads(data)
 recv();sequence=0
 def send(name,params):
  nonlocal_dummy=None
  global sequence
  sequence+=1;data=json.dumps([0,sequence,name,params]).encode();sock.sendall(str(len(data)).encode()+b':'+data)
  response=recv();assert response[2] is None,response
  return response[3].get('value',response[3]) if isinstance(response[3],dict) else response[3]
 send('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{}}})
 send('WebDriver:SetWindowRect',{'x':0,'y':0,'width':1700,'height':1100})
 send('WebDriver:Navigate',{'url':(out/'fixture_run/replay.html').as_uri()+'?frame=40'})
 def js(code):return send('WebDriver:ExecuteScript',{'script':code,'args':[]})
 data=js('''return {right:direction({speed:.2,body:[0,-.2]}),left:direction({speed:.2,body:[0,.2]}),overlap:overlap({circle:[0,0,.15],z:[0,.2]},{polygon:[[-.1,-.1],[.1,-.1],[.1,.1],[-.1,.1]],z:[0,1]}),disjoint:overlap({circle:[0,0,.15],z:[0,.2]},{polygon:[[-.1,-.1],[.1,-.1],[.1,.1],[-.1,.1]],z:[.5,1]}),time:document.getElementById('time').textContent,robots:document.getElementById('robots').textContent};''')
 assert data['right']=='phải' and data['left']=='trái' and data['overlap'] and not data['disjoint']
 assert 'robot3 · leader: phải' in data['robots'],data
 after=js("document.getElementById('next').click();return document.getElementById('time').textContent;")
 assert after!=data['time']
 seek=js("let s=document.getElementById('seek');s.value=10;s.dispatchEvent(new Event('input'));return document.getElementById('time').textContent;")
 assert seek!=after
 js("document.getElementById('play').click();")
 time.sleep(.3)
 play=js("document.getElementById('play').click();return document.getElementById('time').textContent;")
 assert play!=seek
 js("let s=document.getElementById('seek');s.value=40;s.dispatchEvent(new Event('input'));document.getElementById('object').value='robot3';document.getElementById('object').dispatchEvent(new Event('change'));")
 image=send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})
 (out/'viewer.png').write_bytes(base64.b64decode(image))
 (out/'browser_validation.json').write_text(json.dumps({'geometry_overlap_and_height_checks':True,'right_left_body_labels':True,'measured_robot3_right_label':True,'step_seek_play':True,'before_step':data['time'],'after_step':after,'after_seek':seek,'after_play':play,'fixture_note':'Scripted simplified robot poses; not navigation validation.'},ensure_ascii=False,indent=2)+'\n')
 print('Browser checks passed: geometry, body direction, step/seek/play, screenshot')
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
finally:
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
