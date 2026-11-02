"""Bounded isolated ROS/Gazebo run; preserve source and runtime record separately."""
import json,os,signal,subprocess,time
from pathlib import Path
import rclpy
from geometry_msgs.msg import PoseArray,PoseStamped,Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
from nav_msgs.msg import OccupancyGrid
from visualization_msgs.msg import MarkerArray
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile,DurabilityPolicy
from rcl_interfaces.srv import GetParameters
from rosidl_runtime_py.convert import message_to_ordereddict
import cv2
from cv_bridge import CvBridge
out=Path(__file__).resolve().parent
runtime=Path.cwd()/'recordings/nk078_social_camera_120s_once'
assert not runtime.exists(),'Choose a new runtime directory'
log=Path('/tmp/nk078_live.log').open('w')
proc=subprocess.Popen(['bash','scripts/run_dynamic.sh','--diagnose-stop',str(runtime),
                       'rviz:=false','gazebo_gui:=false','gazebo_rendering:=intel',
                       'leader_camera:=true','person_detection:=true','head_pose_enabled:=true',
                       'body_pose_enabled:=true','social_avoidance:=true',
                       'social_observation:=true','social_auto_observe:=true'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
rclpy.init();node=rclpy.create_node('isolated_avoidance_validation')
latest={};scans={};statuses={};commands={};samples=[];sent=False;last_sample=0.;last_progress=0.;sim_clock=[0.];params={};parameter_futures=[]
def state(msg):
 latest['t']=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
 latest['poses']=[[p.position.x,p.position.y] for p in msg.poses]
node.create_subscription(PoseArray,'/formation/robot_states',state,10)
for name in ['robot1','robot2','robot3']:
 node.create_subscription(LaserScan,f'/{name}/scan',lambda msg,n=name:scans.update({n:{'range_max':msg.range_max,'rays':len(msg.ranges)}}),rclpy.qos.qos_profile_sensor_data)
 node.create_subscription(String,f'/{name}/safety_status',lambda msg,n=name:statuses.update({n:msg.data}),10)
 node.create_subscription(Twist,f'/{name}/cmd_vel',lambda msg,n=name:commands.update({n:[msg.linear.x,msg.linear.y,msg.angular.z]}),10)
events=(out/'social_events.jsonl').open('x')
message_counts={};image_times=[];last_image=[-20.];bridge=CvBridge()
def event(topic,data):
 message_counts[topic]=message_counts.get(topic,0)+1
 events.write(json.dumps(dict(t=sim_clock[0],topic=topic,data=data),allow_nan=False)+'\n')
 if message_counts[topic]%10==0:events.flush()
node.create_subscription(Clock,'/clock',lambda m:sim_clock.__setitem__(0,m.clock.sec+m.clock.nanosec*1e-9),rclpy.qos.qos_profile_sensor_data)
for topic in ['/leader/people/status','/leader/people/activity','/leader/people/body_observations',
 '/leader/people/tv_screens','/social_navigation/status','/social_navigation/attention_debug',
 '/social_navigation/observation_status','/social_navigation/search_status']:
 node.create_subscription(String,topic,lambda m,t=topic:event(t,m.data),10)
for topic in ['/leader/people/poses','/leader/people/head_poses','/leader/people/social_body_poses','/leader/people/attention_targets']:
 node.create_subscription(PoseArray,topic,lambda m,t=topic:event(t,message_to_ordereddict(m)),10)
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
node.create_subscription(OccupancyGrid,'/social_navigation/keepout',lambda m:event('/social_navigation/keepout',dict(stamp=message_to_ordereddict(m.header.stamp),width=m.info.width,height=m.info.height,nonzero=sum(v>0 for v in m.data),max=max(m.data,default=0))),qos)
node.create_subscription(MarkerArray,'/social_navigation/markers',lambda m:event('/social_navigation/markers',message_to_ordereddict(m)),qos)
def image(m):
 if sim_clock[0]-last_image[0]<20. or len(image_times)>=6:return
 try:
  name=f'detection_{sim_clock[0]:07.3f}.jpg'
  cv2.imwrite(str(out/name),bridge.imgmsg_to_cv2(m,'bgr8'))
  image_times.append(dict(t=sim_clock[0],file=name,capture_stamp=message_to_ordereddict(m.header.stamp)))
  last_image[0]=sim_clock[0]
 except Exception as e:event('image_save_error',str(e))
node.create_subscription(Image,'/leader/people/image',image,rclpy.qos.qos_profile_sensor_data)
for name,keys in [('three_robot_dstar_mpc',['social_observation_enabled']),
 ('robot3_distributed_mpc',['planning_map_topic','avoidance_use_camera']),
 ('social_navigation',['require_activity_window','auto_observe']),
 ('leader_person_detector',['body_pose_enabled','head_pose_enabled'])]:
 client=node.create_client(GetParameters,'/'+name+'/get_parameters')
 parameter_futures.append([name,keys,client,None])
goal=node.create_publisher(PoseStamped,'/goal_pose',10)
started=time.monotonic()
try:
 while proc.poll() is None and time.monotonic()-started<1200:
  rclpy.spin_once(node,timeout_sec=.05)
  wall=time.monotonic()
  for item in parameter_futures:
   name,keys,client,future=item
   if future is None and client.service_is_ready():
    item[3]=client.call_async(GetParameters.Request(names=keys))
   elif future is not None and future.done() and name not in params:
    try:params[name]=dict(zip(keys,[message_to_ordereddict(v) for v in future.result().values]))
    except Exception as e:params[name]={'error':str(e)}
  if not sent and len(scans)==3 and len(latest.get('poses',[]))==3 and latest.get('t',0)>=3.031:
   msg=PoseStamped();msg.header.frame_id='map';msg.pose.position.x=1.0815577507019043;msg.pose.position.y=-2.0020322799682617;msg.pose.orientation.w=1.
   goal.publish(msg);sent=True;latest['goal_sent_sim']=latest['t']
  if wall-last_sample>=1.:
   samples.append(dict(wall=wall-started,**latest,status=dict(statuses),commands=dict(commands)))
   last_sample=wall
  if wall-last_progress>=15.:print('progress',sim_clock[0], 'wall',round(wall-started),flush=True);last_progress=wall
  if sim_clock[0]>=120.:break
  if not sent and wall-started>120:break
except KeyboardInterrupt:
 pass
finally:
 # Persist observer state before signalling the owned launch tree. A parent
 # supervisor can terminate the harness during cleanup, after the run ended.
 (out/'pre_cleanup.json').write_text(json.dumps(dict(
     last_sim=sim_clock[0],completed_120_sim=sim_clock[0]>=120.,parameters=params,
     goal_sent=sent,wall_seconds=time.monotonic()-started,social_topic_counts=message_counts,
     detection_images=image_times),indent=2)+'\n')
 (out/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
 events.flush()
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
 log.close();events.close()
summary={'goal_sent':sent,'goal':[1.0815577507019043,-2.0020322799682617],'last_sim':sim_clock[0],'target_sim':120.,'completed_120_sim':sim_clock[0]>=120.,
         'parameters':params,'social_topic_counts':message_counts,'detection_images':image_times,
         'wall_seconds':time.monotonic()-started,'scans':scans,'last_status':statuses,
         'launch_exit':proc.poll(),'ros_domain':os.environ.get('ROS_DOMAIN_ID'),
         'profile':{'camera':True,'person_detection':True,'body_pose':True,'social_avoidance':True,'social_observation':True,'social_auto_observe':True,'rviz':False,'gazebo_gui':False},
         'scope':'One isolated full-stack run; not repeated benchmark or proof of general avoidance.'}
(out/'live.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
print(summary)
