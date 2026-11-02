"""No spinning/commands: inspect constructed controller sensor subscriptions."""
import json,os
from pathlib import Path
import rclpy
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC
os.environ.pop('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY',None)
results=[]
for name in ['robot1','robot2','robot3']:
 rclpy.init(args=['--ros-args','-p','robot_name:='+name])
 node=DistributedRobotMPC()
 try:
  topics=[s.topic_name for s in node.subscriptions]
  assert '/leader/people/poses' not in topics
  assert all('/'+n+'/scan' in topics for n in ['robot1','robot2','robot3'])
  assert node.lidar_obstacle_range==2. and not node.avoidance_use_camera
  assert node.lidar_motion.padding==.02
  results.append({'robot':name,'camera_subscription':False,'lidar_range':node.lidar_obstacle_range,'all_three_scan_subscriptions':True})
 finally:node.destroy_node();rclpy.shutdown()
Path(__file__).with_name('defaults.json').write_text(json.dumps(results,indent=2)+'\n')
print(results)
