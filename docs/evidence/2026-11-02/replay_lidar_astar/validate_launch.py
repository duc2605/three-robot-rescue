"""Run only the installed optional observer for two seconds, never Gazebo."""
import importlib.util,json,os
from pathlib import Path
from launch import LaunchDescription,LaunchService
from launch.actions import DeclareLaunchArgument,OpaqueFunction,TimerAction,EmitEvent
from launch.events import Shutdown
out=Path(__file__).resolve().parent;folder=out/'launch_smoke';folder.mkdir(exist_ok=False)
os.environ['SOCIAL_REPLAY_DIRECTORY']=str(folder)
spec=importlib.util.spec_from_file_location('sim_launch',Path.cwd()/'social_navigation_sim/launch/three_robot_sim.launch.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
service=LaunchService();service.include_launch_description(LaunchDescription([
 DeclareLaunchArgument('use_sim_time',default_value='true'),
 OpaqueFunction(function=module.launch_replay_sensor_recorder),
 TimerAction(period=2.,actions=[EmitEvent(event=Shutdown(reason='observer-only smoke complete'))])]))
code=service.run()
status=json.loads((folder/'navigation_status.json').read_text())
assert code==0 and status['writer_finished'] and status['error'] is None,(code,status)
assert (folder/'navigation.jsonl').read_text()==''
(out/'launch_validation.json').write_text(json.dumps({'exit':code,'status':status,'observer_only':True,'gazebo_started':False},indent=2)+'\n')
print('PASS installed optional observer startup/shutdown; no Gazebo or navigation launched')
