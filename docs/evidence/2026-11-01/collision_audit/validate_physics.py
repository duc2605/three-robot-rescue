from pathlib import Path
import subprocess,os,signal,json,re,xml.etree.ElementTree as ET
root=Path.cwd();folder=root/'docs/evidence/2026-11-01/collision_audit';folder.mkdir(parents=True,exist_ok=True)
fixture=root/'social_navigation_sim/test/contact_fixtures/contact.sdf';results=[]
for robot,miss in [('robot1',False),('robot2',False),('robot3',False),('robot3',True)]:
 label=robot+('_near_miss' if miss else '_contact');tree=ET.parse(fixture);world=tree.getroot().find('world');world.find("model[@name='robot3']").set('name',robot);world.find("plugin[@name='rescue::CollisionAudit']/robot_model").text=robot
 if miss:
  world.find("model[@name='person_test']/pose").text='1 1 0 0 0 0'
  for pose in world.findall("plugin[@name='rescue::SocialScenarioMotion']/motion/key/pose"):
   values=pose.text.split();values[1]='1';pose.text=' '.join(values)
 case=folder/(label+'.sdf');tree.write(case)
 env=os.environ.copy();env['IGN_PARTITION']='contact_audit_'+label+'_'+str(os.getpid());env['IGN_GAZEBO_SYSTEM_PLUGIN_PATH']=str(root/'install/social_navigation_sim/lib')+':'+env.get('IGN_GAZEBO_SYSTEM_PLUGIN_PATH','')
 proc=subprocess.Popen(['ign','gazebo','-s','-r','-v','3','--iterations','6500',str(case)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,start_new_session=True)
 try:output=proc.communicate(timeout=16)[0]
 except subprocess.TimeoutExpired:
  os.killpg(proc.pid,signal.SIGINT);output=proc.communicate(timeout=5)[0]
 log=folder/(label+'.log');log.write_text(output);clean=re.sub(r'\x1b\[[0-9;]*m','',output);events=[]
 for line in clean.splitlines():
  if 'COLLISION_AUDIT ' in line:
   events.append(json.loads(line.split('COLLISION_AUDIT ',1)[1]))
 begins=[e for e in events if e['event']=='contact_begin' and e['category']=='human_robot'];ends=[e for e in events if e['event']=='contact_end' and e['category']=='human_robot']
 result=dict(case=label,returncode=proc.returncode,begins=len(begins),ends=len(ends),events=events,passed=(not begins if miss else bool(begins and ends)))
 results.append(result);(folder/'physics_validation.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='events'}),flush=True)
 if not result['passed']:raise SystemExit('Contact fixture failed: '+label)
