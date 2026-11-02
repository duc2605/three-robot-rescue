import socket,json,time,subprocess,os,base64
from pathlib import Path
out=Path('/home/duc/three-robot-rescue/docs/evidence/2026-11-02/goal_markers')
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
 send('WebDriver:Navigate',{'url':(out/'replay.html').as_uri()+'?frame=40'})
 def js(code):return send('WebDriver:ExecuteScript',{'script':code,'args':[]})
 for _ in range(100):
  if js("return document.getElementById('alerts').textContent.length>0;"): break
  time.sleep(.1)
 result=js("return {before:goalAt({t:.1,epoch:0})||null,first:goalAt({t:1,epoch:0}),second:goalAt({t:2,epoch:0}),otherEpoch:goalAt({t:2,epoch:1})||null,label:document.getElementById('goal').textContent};")
 assert result['before'] is None and result['otherEpoch'] is None,result
 assert result['first']['sequence']==1 and result['second']['sequence']==2,result
 assert 'GOAL #2' in result['label'],result
 js("document.getElementById('seek').value=0;document.getElementById('seek').dispatchEvent(new Event('input'));")
 assert 'Chưa có goal' in js("return document.getElementById('goal').textContent;")
 js("document.getElementById('seek').value=40;document.getElementById('seek').dispatchEvent(new Event('input'));")
 picture=send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})
 (out/'viewer.png').write_bytes(base64.b64decode(picture))
 (out/'browser_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS: selected goal timing, replacement, no future goal, epoch isolation, screenshot')
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
finally:
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
