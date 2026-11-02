"""Real ROS initialization/timers in isolated domain; no Gazebo or sensor input."""
from pathlib import Path
import json, os, time
import rclpy
from rclpy.executors import SingleThreadedExecutor
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC, ThreeRobotDStarMPC
out=Path(__file__).resolve().parent/'ros_smoke_final'
out.mkdir(exist_ok=True)
os.environ.pop('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY',None)
rclpy.init(args=['--ros-args','-p','robot_name:=robot3'])
node=DistributedRobotMPC()
assert node.stop_diagnostics is None
node.destroy_node()
os.environ['SOCIAL_STOP_DIAGNOSTICS_DIRECTORY']=str(out)
controller=DistributedRobotMPC()
coordinator=ThreeRobotDStarMPC()
executor=SingleThreadedExecutor()
executor.add_node(controller);executor.add_node(coordinator)
try:
 deadline=time.monotonic()+1.6
 while time.monotonic()<deadline:executor.spin_once(timeout_sec=.05)
finally:
 for node in [controller,coordinator]:
  node.stop_diagnostics.close();executor.remove_node(node);node.destroy_node()
 executor.shutdown();rclpy.shutdown()
files={p.name:[json.loads(l) for l in p.read_text().splitlines()] for p in out.glob('*.jsonl')}
assert 'stop_robot3.jsonl' in files and 'stop_coordinator.jsonl' in files,files.keys()
assert any(r.get('reason')=='motion_disabled_or_missing_map_pose_or_stale_state' for r in files['stop_robot3.jsonl'])
assert any(r.get('reason')=='coordinator_stale_robot_poses' for r in files['stop_coordinator.jsonl'])
result={'default_writer_disabled':True,'opt_in_real_ros_timers_write_controller_and_coordinator':True,'ros_domain':os.environ['ROS_DOMAIN_ID'],'gazebo_started':False,'sensor_data_supplied':False,'counts':{n:len(v) for n,v in files.items()}}
(out.parent/'ros_smoke.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
