import json,time,collections,math
from pathlib import Path
import rclpy
from geometry_msgs.msg import PoseArray,Twist
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
from rclpy.qos import qos_profile_sensor_data
rclpy.init();n=rclpy.create_node('read_only_handoff_audit');subs=[];counts=collections.Counter();latest={};first=None;last=None;travel=[0.,0.,0.];events=[]
def update(k,v):
 global first,last
 counts[k]+=1
 if k.endswith('cmd') and any(abs(x)>.001 for x in v):counts[k+'/nonzero']+=1
 if k.endswith('safety') and latest.get(k)!=v:events.append({'wall':time.monotonic(),'sim':latest.get('clock'),'key':k,'value':v})
 if k=='poses':
  if first is None:first=v
  if last:
   for i,(a,b) in enumerate(zip(last,v)):
    d=math.dist(a,b)
    if d>.002:travel[i]+=d
  last=v
 latest[k]=v
for i in range(1,4):
 r=f'robot{i}'
 subs.append(n.create_subscription(Twist,f'/{r}/cmd_vel',lambda m,r=r:update(r+'/cmd',[m.linear.x,m.linear.y,m.angular.z]),10))
 subs.append(n.create_subscription(String,f'/{r}/safety_status',lambda m,r=r:update(r+'/safety',m.data),10))
subs.append(n.create_subscription(PoseArray,'/formation/reference',lambda m:update('reference_length',len(m.poses)),1))
subs.append(n.create_subscription(PoseArray,'/formation/robot_states',lambda m:update('poses',[(p.position.x,p.position.y) for p in m.poses]),1))
subs.append(n.create_subscription(Clock,'/navigation/clock',lambda m:update('clock',m.clock.sec+m.clock.nanosec/1e9),qos_profile_sensor_data))
start=time.monotonic()
while time.monotonic()-start<20:rclpy.spin_once(n,timeout_sec=.1)
result={'duration_wall_s':time.monotonic()-start,'counts':dict(counts),'first_poses':first,'travel_sampled_m':travel,'latest':latest,'status_changes':events,'limits':'Live unpaired sample, not controlled A/B or contact-free proof.'}
Path('docs/evidence/2026-11-01/stable_handoff/runtime.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'counts':dict(counts),'travel_sampled_m':travel,'latest':latest}))
n.destroy_node();rclpy.shutdown()
