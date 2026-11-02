"""Verify wrapper activation with only final ROS executable stubbed."""
from pathlib import Path
import json, os, subprocess, tempfile
root=Path.cwd()
with tempfile.TemporaryDirectory(prefix='stop_diagnostic_launcher_') as temporary:
    folder=Path(temporary);stub=folder/'ros2';output=folder/'launch.json'
    stub.write_text('#!/usr/bin/python3\nimport os,json,sys\nopen(os.environ["VERIFY_LAUNCH_FILE"],"w").write(json.dumps({"args":sys.argv[1:],"pose":os.environ.get("SOCIAL_REPLAY_DIRECTORY"),"diagnostic":os.environ.get("SOCIAL_STOP_DIAGNOSTICS_DIRECTORY")}))\n');stub.chmod(0o755)
    script=(root/'scripts/run_dynamic.sh').read_text().replace('exec ros2 launch','exec "'+str(stub)+'" launch')
    script=script.replace('project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"','project_dir="'+str(root)+'"')
    env=os.environ.copy();env.update(VERIFY_LAUNCH_FILE=str(output),SOCIAL_REPLAY_DIRECTORY='/tmp/stale',SOCIAL_STOP_DIAGNOSTICS_DIRECTORY='/tmp/stale')
    def launch(*args):
        result=subprocess.run(['bash','-c',script,'run_dynamic.sh',*args],env=env,capture_output=True,text=True)
        return result,json.loads(output.read_text()) if output.exists() else None
    result,normal=launch('leader_robot:=robot2');assert result.returncode==0,result.stderr
    assert normal['pose'] is None and normal['diagnostic'] is None
    assert 'leader_robot:=robot2' in normal['args']
    result,replay=launch('--record-replay',str(folder/'replay'));assert result.returncode==0,result.stderr
    assert replay['pose'] and replay['diagnostic'] is None
    result,diagnose=launch('--diagnose-stop',str(folder/'diagnose'),'leader_robot:=robot1');assert result.returncode==0,result.stderr
    assert diagnose['pose']==diagnose['diagnostic']==str(folder/'diagnose')
    assert json.loads((folder/'diagnose/scene.json').read_text())['leader']=='robot1'
    result,_=launch('--diagnose-stop',str(folder/'diagnose'));assert result.returncode!=0
    result,_=launch('--diagnose-stop');assert result.returncode==2
assert not (root/'log/sessions').exists()
result={'default_unsets_inherited_flags':True,'replay_only_does_not_enable_diagnostics':True,
        'diagnose_enables_pose_and_controller_files':True,'launch_args_forwarded':True,
        'existing_directory_refused':True,'missing_directory_argument_refused':True,'gazebo_started':False}
Path(__file__).with_name('launcher_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
