"""Bounded isolated ROS/Gazebo run; preserve source and runtime record separately."""
import json,os,signal,subprocess,time
from pathlib import Path
import rclpy
from geometry_msgs.msg import PoseArray,PoseStamped,Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
out=Path(__file__).resolve().parent
runtime=Path.cwd()/'recordings/nk076_resume_goal_once'
assert not runtime.exists(),'Choose a new runtime directory'
log=Path('/tmp/nk076_live.log').open('w')
proc=subprocess.Popen(['bash','scripts/run_dynamic.sh','--diagnose-stop',str(runtime),
                       'rviz:=false','gazebo_gui:=false','gazebo_rendering:=intel'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
rclpy.init();node=rclpy.create_node('isolated_avoidance_validation')
latest={};scans={};statuses={};commands={};samples=[];sent=False;last_sample=0.
def state(msg):
 latest['t']=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
 latest['poses']=[[p.position.x,p.position.y] for p in msg.poses]
node.create_subscription(PoseArray,'/formation/robot_states',state,10)
for name in ['robot1','robot2','robot3']:
 node.create_subscription(LaserScan,f'/{name}/scan',lambda msg,n=name:scans.update({n:{'range_max':msg.range_max,'rays':len(msg.ranges)}}),rclpy.qos.qos_profile_sensor_data)
 node.create_subscription(String,f'/{name}/safety_status',lambda msg,n=name:statuses.update({n:msg.data}),10)
 node.create_subscription(Twist,f'/{name}/cmd_vel',lambda msg,n=name:commands.update({n:[msg.linear.x,msg.linear.y,msg.angular.z]}),10)
goal=node.create_publisher(PoseStamped,'/goal_pose',10)
started=time.monotonic()
try:
 while proc.poll() is None and time.monotonic()-started<300:
  rclpy.spin_once(node,timeout_sec=.05)
  wall=time.monotonic()
  if not sent and len(scans)==3 and len(latest.get('poses',[]))==3 and latest.get('t',0)>=3.031:
   msg=PoseStamped();msg.header.frame_id='map';msg.pose.position.x=1.0815577507019043;msg.pose.position.y=-2.0020322799682617;msg.pose.orientation.w=1.
   goal.publish(msg);sent=True;latest['goal_sent_sim']=latest['t']
  if wall-last_sample>=1.:
   samples.append(dict(wall=wall-started,**latest,status=dict(statuses),commands=dict(commands)))
   last_sample=wall
  if len(samples)%15==0 and wall-last_sample<.05:print('progress',latest.get('t'),flush=True)
  if latest.get('t',0)>=165.2:break
  if not sent and wall-started>85:break
except KeyboardInterrupt:
 pass
finally:
 try:
  node.destroy_node()
  if rclpy.ok():rclpy.shutdown()
 except Exception:
  pass
 # Stop only this owned launch tree, checking process birth identifiers.
 parents={}
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    fields=(p/'stat').read_text().rsplit(')',1)[1].split();parents[int(p.name)]=(int(fields[1]),fields[19])
   except (OSError,IndexError):pass
 owned={proc.pid}
 # Gazebo's GUI/server launcher can fork out of the ROS launch tree.
 # Add only Gazebo processes carrying this test's exact partition/domain.
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   env=(p/'environ').read_bytes().split(b'\0');cmd=(p/'cmdline').read_bytes()
   if (('IGN_PARTITION='+os.environ['IGN_PARTITION']).encode() in env
       and ('ROS_DOMAIN_ID='+os.environ['ROS_DOMAIN_ID']).encode() in env
       and cmd.startswith(b'ign gazebo')):owned.add(int(p.name))
  except OSError:pass
 while True:
  found=owned|{pid for pid,(parent,_) in parents.items() if parent in owned}
  if found==owned:break
  owned=found
 def same(pid):
  try:
   fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
   return fields[0]!='Z' and fields[19]==parents[pid][1]
  except (OSError,KeyError,IndexError):return False
 for sig in [signal.SIGINT,signal.SIGTERM,signal.SIGKILL]:
  for pid in owned:
   if same(pid):
    try:os.kill(pid,sig)
    except ProcessLookupError:pass
  deadline=time.monotonic()+(8 if sig==signal.SIGINT else 3)
  while any(same(pid) for pid in owned) and time.monotonic()<deadline:time.sleep(.1)
 try:proc.wait(timeout=2)
 except subprocess.TimeoutExpired:pass
 log.close()
summary={'goal_sent':sent,'goal':[1.0815577507019043,-2.0020322799682617],'last_sim':latest.get('t'),
         'wall_seconds':time.monotonic()-started,'scans':scans,'last_status':statuses,
         'launch_exit':proc.poll(),'ros_domain':os.environ.get('ROS_DOMAIN_ID'),
         'scope':'One isolated full-stack run; not repeated benchmark or proof of general avoidance.'}
(out/'live.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
print(summary)
