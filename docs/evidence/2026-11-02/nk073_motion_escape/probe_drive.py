import json,math,time
from pathlib import Path
import rclpy
from geometry_msgs.msg import PoseArray,Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
rclpy.init();node=rclpy.create_node('nk073_readonly_drive_probe')
cmd={};odom={};joints={};previous={};rows=[]
for name in ['robot1','robot2','robot3']:
 node.create_subscription(Twist,f'/{name}/cmd_vel',lambda m,n=name:cmd.update({n:[m.linear.x,m.linear.y,m.angular.z]}),10)
 node.create_subscription(Odometry,f'/{name}/odom',lambda m,n=name:odom.update({n:[m.twist.twist.linear.x,m.twist.twist.linear.y,m.twist.twist.angular.z]}),10)
 node.create_subscription(JointState,f'/{name}/joint_states',lambda m,n=name:joints.update({n:{k:v for k,v in zip(m.name,m.velocity) if 'omni_wheel_joint' in k}}),rclpy.qos.qos_profile_sensor_data)
def state(m):
 t=m.header.stamp.sec+m.header.stamp.nanosec*1e-9
 for i,p in enumerate(m.poses):
  n=f'robot{i+1}';q=p.orientation;yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z));pose=[p.position.x,p.position.y,yaw]
  old=previous.get(n)
  if old is not None and .03<t-old[0]<.3:
   dt=t-old[0];vx=(pose[0]-old[1][0])/dt;vy=(pose[1]-old[1][1])/dt
   body=[vx*math.cos(yaw)+vy*math.sin(yaw),-vx*math.sin(yaw)+vy*math.cos(yaw),math.atan2(math.sin(yaw-old[1][2]),math.cos(yaw-old[1][2]))/dt]
   rows.append(dict(t=t,robot=n,pose=pose,body_measured=body,command=cmd.get(n),odom=odom.get(n),wheel_velocities=joints.get(n)))
  previous[n]=(t,pose)
node.create_subscription(PoseArray,'/formation/robot_states',state,10)
start=time.monotonic()
while time.monotonic()-start<55:rclpy.spin_once(node,timeout_sec=.05)
node.destroy_node();rclpy.shutdown()
p=Path('docs/evidence/2026-11-02/nk073_motion_escape/drive_probe.json');p.write_text(json.dumps(rows,indent=2)+'\n');print(len(rows))
