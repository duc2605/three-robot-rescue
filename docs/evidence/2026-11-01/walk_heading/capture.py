import subprocess,time,json
from pathlib import Path
folder=Path('docs/evidence/2026-11-01/walk_heading/rendered');folder.mkdir(exist_ok=True)
def call(service,requestType,responseType,request):
 return subprocess.run(['ign','service','-s',service,'--reqtype',requestType,'--reptype',responseType,'--timeout','5000','--req',request],capture_output=True,text=True,timeout=8)
time.sleep(8)
for label in ['first','second']:
 before=set(folder.glob('*.png'))
 result=call('/gui/screenshot','ignition.msgs.StringMsg','ignition.msgs.Boolean','data: "'+str(folder.resolve())+'"')
 time.sleep(.2)
 files=set(folder.glob('*.png'))-before
 for p in files:p.rename(folder/(label+'.png'))
 state=call('/world/social_dynamic/state','ignition.msgs.Empty','ignition.msgs.SerializedStepMap','')
 (folder/(label+'_state.pbtxt')).write_text(state.stdout)
 print(json.dumps(dict(label=label,screenshot=result.stdout.strip(),state_returncode=state.returncode)),flush=True)
 if label=='first':time.sleep(12)
