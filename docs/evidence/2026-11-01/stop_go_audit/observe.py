import rclpy,time,json,collections
from pathlib import Path
from std_msgs.msg import String
from geometry_msgs.msg import Twist,PoseArray
from rosgraph_msgs.msg import Clock
from rclpy.qos import qos_profile_sensor_data
rclpy.init();node=rclpy.create_node('read_only_map_fix_check');subs=[];counts=collections.Counter();latest={};first=None
changes=[]
def update(key,value):
 global first
 counts[key]+=1
 if key=='poses' and first is None:first=value
 if key.endswith('/safety') and latest.get(key)!=value:changes.append((key,value))
 latest[key]=value
for i in range(1,4):
 name=f'robot{i}'
 def cmd(msg,name=name):
  value=[msg.linear.x,msg.linear.y,msg.angular.z];update(name+'/cmd',value)
  if any(abs(v)>.001 for v in value):counts[name+'/nonzero']+=1
 subs.append(node.create_subscription(Twist,f'/{name}/cmd_vel',cmd,10))
 subs.append(node.create_subscription(String,f'/{name}/safety_status',lambda m,name=name:update(name+'/safety',m.data),10))
subs.append(node.create_subscription(Clock,'/navigation/clock',lambda m:update('clock',m.clock.sec+m.clock.nanosec/1e9),qos_profile_sensor_data))
subs.append(node.create_subscription(PoseArray,'/formation/robot_states',lambda m:update('poses',[(p.position.x,p.position.y) for p in m.poses]),1))
start=time.monotonic()
while time.monotonic()-start<10:rclpy.spin_once(node,timeout_sec=.1)
result={'counts':dict(counts),'first_poses':first,'latest':latest,'status_changes':changes}
Path('docs/evidence/2026-11-01/stop_go_audit/runtime.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'latest':result['latest'],'status_categories':{r:dict(collections.Counter(v.split(';')[0] for k,v in changes if k==r+'/safety')) for r in ['robot1','robot2','robot3']}}))
node.destroy_node();rclpy.shutdown()
