"""Isolated coordinator callbacks; no executor, Gazebo, or real command output."""
import json,os,tempfile
from pathlib import Path
import rclpy
from social_navigation_planner.dstar_mpc_controller import ThreeRobotDStarMPC
class Capture:
 def publish(self,msg):self.message=msg
out=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temporary:
 os.environ['SOCIAL_REPLAY_DIRECTORY']=temporary
 os.environ.pop('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY',None)
 rclpy.init()
 node=ThreeRobotDStarMPC()
 try:
  node.set_goal(2.,1.)
  node.poses_ready=lambda:True
  node.robot_state=[(0.,0.,0.,True),(1.,0.,0.,True),(2.,0.,0.,True)]
  node.marker_pub=Capture()
  node.publish_markers()
  markers=[m for m in node.marker_pub.message.markers if m.ns=='selected_goal']
  assert len(markers)==1 and markers[0].pose.position.x==2. and markers[0].pose.position.y==1.
  row=json.loads((Path(temporary)/'goals.jsonl').read_text())
  assert row['xy']==[2.,1.]
  result={'rviz_goal_marker_at_selected_coordinates':True,'set_goal_records_history':True,'navigation_goal_unchanged':node.goal_xy==(2.,1.),'ros_domain':os.environ['ROS_DOMAIN_ID'],'gazebo_started':False}
  (out/'ros_marker_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
 finally:node.destroy_node();rclpy.shutdown()
