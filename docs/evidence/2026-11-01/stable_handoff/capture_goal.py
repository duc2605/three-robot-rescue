import json,re,time
from pathlib import Path
import rclpy
from nav_msgs.msg import Path as ROSPath
from geometry_msgs.msg import PoseStamped
text=Path('log/manual_lidar_only.log').read_text(errors='replace')
rows=re.findall(r'Setting goal pose:.*Position\(([-0-9.]+), ([-0-9.]+),',text)
assert rows
expected=tuple(map(float,rows[-1]));selected=None
rclpy.init();node=rclpy.create_node('preserve_selected_goal')
def goal(msg):
 global selected
 if msg.header.frame_id in ('map',''):
  selected={'xy':[msg.pose.position.x,msg.pose.position.y],'source':'user /goal_pose'}
def path(msg):
 global selected
 if msg.poses and selected is None:
  p=msg.poses[-1].pose.position
  if abs(p.x-expected[0])<.0001 and abs(p.y-expected[1])<.0001:
   selected={'xy':[p.x,p.y],'source':'exact last global-path endpoint matching selected goal log'}
a=node.create_subscription(ROSPath,'/dstar_lite/path',path,10)
b=node.create_subscription(PoseStamped,'/goal_pose',goal,10)
start=time.monotonic()
while time.monotonic()-start<10 and selected is None:rclpy.spin_once(node,timeout_sec=.1)
if selected is None:selected={'xy':expected,'source':'RViz goal log rounded coordinates; no fresh path received'}
Path('docs/evidence/2026-11-01/stable_handoff/retained_goal.json').write_text(json.dumps(selected,indent=2)+'\n')
print(json.dumps(selected))
node.destroy_node();rclpy.shutdown()
