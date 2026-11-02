import math,time,json
from pathlib import Path
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy,qos_profile_sensor_data
from geometry_msgs.msg import PoseArray,Pose,Twist
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from rosgraph_msgs.msg import Clock
from std_msgs.msg import String
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC
rclpy.init(args=['--ros-args','-p','use_sim_time:=true','-p','robot_name:=robot3'])
c=DistributedRobotMPC();p=Node('isolated_uncertainty_inputs');e=SingleThreadedExecutor();e.add_node(c);e.add_node(p)
commands=[];statuses=[]
subs=[p.create_subscription(Twist,'/robot3/cmd_vel',lambda m:commands.append([m.linear.x,m.linear.y,m.angular.z]),10),p.create_subscription(String,'/robot3/safety_status',lambda m:statuses.append(m.data),10)]
q=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
mp=p.create_publisher(OccupancyGrid,'/map',q);cp=p.create_publisher(Clock,'/clock',10)
tp=p.create_publisher(PoseArray,'/formation/robot_states',10);pp=p.create_publisher(PoseArray,'/leader/people/poses',10);sp=p.create_publisher(LaserScan,'/robot3/scan',qos_profile_sensor_data)
def spin(seconds):
 end=time.monotonic()+seconds
 while time.monotonic()<end:e.spin_once(timeout_sec=.01)
def header(m,t):m.header.frame_id='map';m.header.stamp.sec=int(t);m.header.stamp.nanosec=round((t-int(t))*1e9)
spin(.3)
m=OccupancyGrid();m.header.frame_id='map';m.info.width=m.info.height=100;m.info.resolution=.1;m.info.origin.position.x=m.info.origin.position.y=-5.;m.info.origin.orientation.w=1.;m.data=[0]*10000;mp.publish(m);spin(.2)
for t in [0.,.2,.4]:
 cl=Clock();cl.clock.sec=int(t);cl.clock.nanosec=round((t-int(t))*1e9);cp.publish(cl);spin(.04)
 team=PoseArray();header(team,t)
 for x,y in [(-2.,2.),(-2.,-2.),(0.,0.)]:
  pose=Pose();pose.position.x=x;pose.position.y=y;pose.orientation.w=1.;team.poses.append(pose)
 person=PoseArray();header(person,t);pose=Pose();pose.position.x=.56;pose.orientation.w=1.;person.poses=[pose]
 scan=LaserScan();header(scan,t);scan.header.frame_id='robot3/base_link';scan.range_min=.08;scan.range_max=10.;scan.angle_min=-math.pi;scan.angle_increment=2*math.pi/239;scan.ranges=[math.inf]*240
 # A sparse visible body surface 0.56 m away, spanning +/-0.32 m.
 for i in range(240):
  angle=scan.angle_min+i*scan.angle_increment
  if abs(angle)<math.atan2(.32,.56):scan.ranges[i]=.56/math.cos(angle)
 tp.publish(team);pp.publish(person);sp.publish(scan);spin(.1)
c.control_tick();spin(.05)
assert any(math.hypot(*cmd[:2])>.001 for cmd in commands),statuses
assert any('uncertainty_recovery=True' in s for s in statuses),statuses
tracks=c.camera_motion.recent(.4)+c.lidar_motion.recent(.4)
result={'domain':94,'nonzero_escape_command':next(cmd for cmd in reversed(commands) if math.hypot(*cmd[:2])>.001),'status':statuses[-1],'initial_buffer_gaps':[o.clearance(c.own_pose,c.own_pose,.4,.4,.15) for o in tracks],'initial_body_gaps':[o.body_clearance(c.own_pose,c.own_pose,.4,.4,.15) for o in tracks],'input':'Synthetic stamped RGB-D poses, full scan and physical map; no Gazebo, no ground-truth perception'}
c.scan_wall=time.monotonic()-3;c.watchdog();spin(.04)
assert commands[-1]==[0.,0.,0.];result['stale_scan_stopped']=True
Path('docs/evidence/2026-10-28/leader_uncertainty_recovery/ros_smoke.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
e.remove_node(c);e.remove_node(p);c.destroy_node();p.destroy_node();rclpy.shutdown()
