import socket,json,time,subprocess,os,base64
from pathlib import Path
out=Path('/home/duc/three-robot-rescue/docs/evidence/2026-11-01/physical_contacts')
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
 data=js("return {alerts:document.getElementById('alerts').textContent,status:document.getElementById('status').textContent,physical:physicalNames};".replace(',physical:physicalNames',''))
 assert 'GAZEBO XÁC NHẬN CONTACT' in data['alerts'] and 'robot3' in data['alerts'] and 'person_contact' in data['alerts'],data
 assert 'không có số đo' in data['alerts'],data
 old=js("document.getElementById('seek').value=0;document.getElementById('seek').dispatchEvent(new Event('input'));return document.getElementById('alerts').textContent;")
 assert 'Không ghi nhận contact' in old,old
 legacy_frame=json.loads((out/'world_frames.jsonl').read_text().splitlines()[0])
 legacy_frame.pop('physics_contact_source');legacy_frame.pop('contacts')
 legacy_data={'scene':json.loads((out/'scene.json').read_text()),'frames':[legacy_frame]}
 legacy=js('accept('+json.dumps(legacy_data)+");return document.getElementById('alerts').textContent;")
 assert 'Bản ghi cũ' in legacy,legacy
 original={'scene':json.loads((out/'scene.json').read_text()),'frames':[json.loads(x) for x in (out/'world_frames.jsonl').read_text().splitlines()]}
 js('accept('+json.dumps(original)+');')
 picture=send('WebDriver:TakeScreenshot',{'id':None,'full':True,'scroll':False})
 (out/'viewer.png').write_bytes(base64.b64decode(picture))
 (out/'browser_validation.json').write_text(json.dumps({'contact_pair_display':True,'missing_depth_display':True,'no_contact_display':True,'legacy_unknown_display':True,'alerts':data['alerts']},ensure_ascii=False,indent=2)+'\n')
 print('PASS: physical contact UI, no-contact interval, legacy unknown, screenshot')
 send('Marionette:Quit',{'flags':['eForceQuit']});sock.close()
finally:
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
