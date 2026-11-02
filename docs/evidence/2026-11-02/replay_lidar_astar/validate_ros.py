"""Controlled ROS publishers; no Gazebo and no navigation command is issued."""
import json,math,os,time,sys
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;FOLDER=OUT/'dense_fixture'
FOLDER.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'social_navigation_sim/scripts')]
from replay_sensor_recorder import ReplaySensorRecorder
from view_replay import export
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile,DurabilityPolicy
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Path as RosPath
from geometry_msgs.msg import PoseStamped,TransformStamped
from tf2_msgs.msg import TFMessage
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC
os.environ['SOCIAL_REPLAY_DIRECTORY']=str(FOLDER)
os.environ.pop('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY',None)
rclpy.init(args=['--ros-args','-p','directory:='+str(FOLDER),'-p','use_sim_time:=true','-p','robot_name:=robot1'])
recorder=ReplaySensorRecorder();publisher=rclpy.create_node('fixture_sensor_inputs');controller=DistributedRobotMPC()
executor=SingleThreadedExecutor();executor.add_node(recorder);executor.add_node(publisher)
clock=publisher.create_publisher(Clock,'/clock',10)
scanpub=publisher.create_publisher(LaserScan,'/robot1/scan',10)
pathpub=publisher.create_publisher(RosPath,'/robot1/escape_path',10)
extra_scans={n:publisher.create_publisher(LaserScan,f'/{n}/scan',10) for n in ['robot2','robot3']}
extra_paths={n:publisher.create_publisher(RosPath,f'/{n}/escape_path',10) for n in ['robot2','robot3']}
tfpub=publisher.create_publisher(TFMessage,'/tf_static',QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
def spin(seconds=.15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:executor.spin_once(timeout_sec=.01)
def set_clock(t):
 msg=Clock();msg.clock.sec=int(t);msg.clock.nanosec=round((t-int(t))*1e9);clock.publish(msg);spin()
def scan(t,angle,distance):
 msg=LaserScan();msg.header.frame_id='robot1/lidar_link_1';msg.header.stamp.sec=int(t);msg.header.stamp.nanosec=round((t-int(t))*1e9)
 msg.range_min=.08;msg.range_max=2.;msg.angle_min=angle;msg.angle_increment=2*math.pi/239
 msg.ranges=[distance]+[math.inf]*239;scanpub.publish(msg);spin()
def path(t,points):
 msg=RosPath();msg.header.frame_id='map';msg.header.stamp.sec=int(t);msg.header.stamp.nanosec=round((t-int(t))*1e9)
 for x,y in points:
  p=PoseStamped();p.pose.position.x=x;p.pose.position.y=y;msg.poses.append(p)
 pathpub.publish(msg);spin()
try:
 spin(.4)
 tr=TransformStamped();tr.header.frame_id='robot1/base_footprint';tr.child_frame_id='robot1/robot1/lidar_link_1';tr.transform.translation.z=.1;tr.transform.rotation.w=1.
 tfpub.publish(TFMessage(transforms=[tr]));spin()
 for k in range(10):
  t=k*.1;set_clock(t);scan(t,0.,2. if k==0 else .5)
 set_clock(1.1);scan(1.,-math.pi/2,1.);path(1.,[(0.,0.),(0.,.72)])
 for name,pub in extra_scans.items():
  msg=LaserScan();msg.header.frame_id=name+'/base_footprint';msg.header.stamp.sec=1
  msg.range_min=.08;msg.range_max=2.;msg.angle_min=-math.pi;msg.angle_increment=2*math.pi/239;msg.ranges=[.7]+[math.inf]*239
  pub.publish(msg)
  msg2=RosPath();msg2.header.frame_id='map';msg2.header.stamp.sec=1
  y=-1.5 if name=='robot2' else 1.5
  for x,py in [(-2.5,y),(-1.9,y+.5)]:
   q=PoseStamped();q.pose.position.x=x;q.pose.position.y=py;msg2.poses.append(q)
  extra_paths[name].publish(msg2)
 spin()
 controller.selected_escape_goal=(.72,0.);controller.selected_escape_stops=True;controller.selected_escape_terminal_safe=True
 controller.replay_escape_decision(1.,'controlled_fixture',True);spin(.3)
 set_clock(1.4);path(1.4,[]);controller.replay_escape_decision(1.4,'controlled_stop');spin()
 set_clock(.1);scan(.1,0.,2.)
finally:
 recorder.writer.close();executor.shutdown();recorder.destroy_node();publisher.destroy_node();controller.destroy_node()
 if rclpy.ok():rclpy.shutdown()
rows=[json.loads(l) for l in (FOLDER/'navigation.jsonl').read_text().splitlines()]
assert any(r['kind']=='scan' and r['extrinsic']['tf_frame']=='robot1/robot1/lidar_link_1' for r in rows)
assert any(r['kind']=='scan' and r['epoch']==1 for r in rows)
assert {r['robot'] for r in rows if r['kind']=='scan'}=={'robot1','robot2','robot3'}
assert {r['robot'] for r in rows if r['kind']=='astar' and r['goal']}=={'robot1','robot2','robot3'}
assert any(r['kind']=='astar' and r['goal']==[0.,.72] for r in rows)
assert any(r['kind']=='decision' and r['goal']==[.72,0.] for r in rows)
assert any(r['kind']=='astar' and r['goal'] is None for r in rows)
scene={'world':'KIỂM THỬ TỔNG HỢP — KHÔNG PHẢI GAZEBO','bounds':[-5.,-4.,4.,4.],'objects':{},'source':'Synthetic viewer fixture with real ROS telemetry transport'}
for name in ['robot1','robot2','robot3']:scene['objects'][name]={'kind':'robot','radius':.15,'z':[0.,.2],'shapes':[]}
scene['objects']['nguoi_A']={'kind':'human','shapes':[{'collision':True,'polygon':[[-.2,-.2],[.2,-.2],[.2,.2],[-.2,.2]],'z':[0.,1.8]}]}
scene['objects']['wall']={'kind':'object','shapes':[{'collision':True,'polygon':[[-.05,-.5],[.05,-.5],[.05,.5],[-.05,.5]],'z':[0.,2.]}]}
frames=[]
for epoch,t in [(0,round(k*.05,3)) for k in range(41)]+[(1,.1)]:
 frames.append({'t':t,'epoch':epoch,'paused':False,'objects':[
 {'name':'robot1','p':[0.,0.,0.,0.,0.,min(math.pi/2,max(0.,(t-.5)*math.pi)) if epoch==0 else 0.]},
 {'name':'robot2','p':[-2.5,-1.5,0.,0.,0.,0.]},{'name':'robot3','p':[-2.5,1.5,0.,0.,0.,0.]},
 {'name':'nguoi_A','p':[max(1.2,2.6-2.8*t) if epoch==0 else 2.6,0.,0.,0.,0.,0.]},
 {'name':'wall','p':[.5,0.,-50. if t>=1. else 0.,0.,0.,0.]}]})
(FOLDER/'scene.json').write_text(json.dumps(scene,ensure_ascii=False))
(FOLDER/'world_frames.jsonl').write_text(''.join(json.dumps(f)+'\n' for f in frames))
(FOLDER/'session.json').write_text(json.dumps({'state':'controlled_ROS_fixture — synthetic poses'}))
export(FOLDER,OUT/'replay.html')
(OUT/'ros_validation.json').write_text(json.dumps({'domain':os.environ.get('ROS_DOMAIN_ID'),'events':len(rows),'epoch_reset':True,'all_three_robots':True,'real_static_tf_alias':True,'distinct_astar_mpc':True,'no_gazebo':True,'no_command_publisher_spun':True},indent=2)+'\n')
print('PASS controlled ROS scan/path/decision, static TF alias, reset, clear; synthetic poses only')
