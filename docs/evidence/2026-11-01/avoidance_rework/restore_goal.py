import json,time,re
from pathlib import Path
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped,PoseArray
rclpy.init(args=['--ros-args','-p','use_sim_time:=true']);n=Node('restore_last_selected_goal');new=[None];ready=[False]
n.create_subscription(PoseStamped,'/goal_pose',lambda m:new.__setitem__(0,[m.pose.position.x,m.pose.position.y]),10)
n.create_subscription(PoseArray,'/formation/robot_states',lambda m:ready.__setitem__(0,len(m.poses)==3),10)
pub=n.create_publisher(PoseStamped,'/goal_pose',10)
start=time.monotonic()
while time.monotonic()-start<25:
 rclpy.spin_once(n,timeout_sec=.05)
 if ready[0] and pub.get_subscription_count()>0 and time.monotonic()-start>2:break
log=Path('log/manual_lidar_only.log').read_text(errors='replace')
result={'published':False,'reason':None}
if new[0] or 'Setting goal pose:' in log:result.update(reason='New user goal takes priority',goal=new[0])
elif ready[0] and pub.get_subscription_count():
 goals=[json.loads(Path('docs/evidence/2026-11-01/avoidance_rework/final_saved_goal.json').read_text())['values']]
 if goals:
  values=[float(v) for v in goals[-1]];m=PoseStamped();m.header.frame_id='map';m.header.stamp=n.get_clock().now().to_msg();m.pose.position.x,m.pose.position.y=values[:2];m.pose.orientation.x,m.pose.orientation.y,m.pose.orientation.z,m.pose.orientation.w=values[2:];pub.publish(m);result.update(published=True,goal=values[:2],reason='Restore last RViz selection from previous session log; rounded log precision')
  end=time.monotonic()+.5
  while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.05)
 else:result['reason']='No previous RViz goal in saved log; nothing published'
else:result['reason']='No ready robot state or goal subscriber; nothing published'
Path('docs/evidence/2026-11-01/avoidance_rework/goal_restore.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));n.destroy_node();rclpy.shutdown()
