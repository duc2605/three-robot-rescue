from pathlib import Path
import os,subprocess,signal,time,json
import rclpy
from visualization_msgs.msg import MarkerArray
root=Path.cwd();folder=root/'docs/evidence/2026-11-01/collision_audit';env=os.environ.copy();env['IGN_PARTITION']='contact_wire_'+str(os.getpid());env['IGN_GAZEBO_SYSTEM_PLUGIN_PATH']=str(root/'install/social_navigation_sim/lib')+':'+env.get('IGN_GAZEBO_SYSTEM_PLUGIN_PATH','')
# Set the same transport partition in this process and every child.
os.environ['IGN_PARTITION']=env['IGN_PARTITION'];processes=[];logfiles=[]
def start(args,label):
 log=(folder/(label+'.log')).open('w');logfiles.append(log)
 p=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);processes.append(p);return p
bridge=start(['/opt/ros/humble/lib/ros_gz_bridge/parameter_bridge','/collision_audit/events@std_msgs/msg/String[ignition.msgs.StringMsg','/collision_audit/status@std_msgs/msg/String[ignition.msgs.StringMsg'],'wire_bridge')
recorder=start(['/usr/bin/python3',str(root/'social_navigation_sim/scripts/collision_monitor.py'),'--ros-args','-p','log_file:='+str(folder/'wire_events.jsonl')],'wire_recorder')
rclpy.init();node=rclpy.create_node('contact_wire_probe');markers=[]
node.create_subscription(MarkerArray,'/collision_audit/markers',lambda m:markers.append([x.type for x in m.markers]),10)
def spin(seconds):
 end=time.monotonic()+seconds
 while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.02)
try:
 spin(2)
 sim=start(['ign','gazebo','-s','-r','-v','3','--iterations','6500',str(folder/'robot3_contact.sdf')],'wire_physics')
 began=time.monotonic()
 while sim.poll() is None and time.monotonic()-began<15:rclpy.spin_once(node,timeout_sec=.02)
 spin(.5)
 data=[json.loads(v) for v in (folder/'wire_events.jsonl').read_text().splitlines()]
 contacts=[e for e in data if e.get('category')=='human_robot']
 result=dict(recorded_events=[e['event'] for e in contacts],marker_messages=len(markers),red_sphere_received=any(2 in row for row in markers),end_received=any(e['event']=='contact_end' for e in contacts))
 result['passed']=bool(contacts and result['red_sphere_received'] and result['end_received'])
 (folder/'wire_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:
 node.destroy_node();rclpy.shutdown()
 for p in processes:
  if p.poll() is None:
   try:os.killpg(p.pid,signal.SIGINT)
   except ProcessLookupError:pass
 for p in processes:
  try:p.wait(timeout=4)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=3)
 for f in logfiles:f.close()
if not result['passed']:raise SystemExit('Contact ROS wire validation failed')
