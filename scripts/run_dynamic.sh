#!/usr/bin/env bash
# Shared runner: every invocation records into a fresh directory unless one is supplied.
set -eo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
if [[ ! -f install/setup.bash ]]; then
  echo 'Build the two packages first; see README.md.' >&2
  exit 1
fi
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-31}"
export QT_QPA_PLATFORM=xcb
# Each invocation selects its own recording; never inherit a previous session.
unset SOCIAL_REPLAY_DIRECTORY SOCIAL_STOP_DIAGNOSTICS_DIRECTORY
profile="dynamic"
launch_file="social_dynamic.launch.py"
default_scene="dynamic"
if [[ "${1:-}" == "--profile" ]]; then
  profile="${2:-}"
  case "$profile" in
    dynamic) ;;
    static) launch_file="social_static.launch.py"; default_scene="static" ;;
    paper1) launch_file="paper1_gwo_woa.launch.py"; default_scene="static" ;;
    paper2) launch_file="paper2_apf_mpc.launch.py"; default_scene="static" ;;
    *) echo 'Profile must be dynamic, static, paper1 or paper2' >&2; exit 2 ;;
  esac
  shift 2
fi
comparison_method=""
if [[ "${1:-}" == "--comparison" ]]; then
  comparison_method="${2:-}"
  if [[ ! "$comparison_method" =~ ^(0[1-9]|10)$ ]]; then
    echo 'Comparison method must be 01..10' >&2
    exit 2
  fi
  if [[ "$profile" != "dynamic" ]]; then
    echo 'Do not combine --profile with --comparison' >&2
    exit 2
  fi
  profile="compare$comparison_method"
  shift 2
fi
if [[ -n "$comparison_method" ]]; then
  for argument in "$@"; do
    case "$argument" in
      method:=*|navigation_backend:=*)
        echo 'Choose the comparison method with --comparison only; conflicting override refused.' >&2
        exit 2 ;;
    esac
  done
fi
# Default path is unique, visible to the user, and never overwrites old data.
if [[ "${1:-}" != "--record-replay" && "${1:-}" != "--diagnose-stop" ]]; then
  set -- --diagnose-stop "recordings/${profile}_$(date +%Y%m%d_%H%M%S_%N)_$$" "$@"
fi
diagnose_stop=false
if [[ "${1:-}" == "--record-replay" || "${1:-}" == "--diagnose-stop" ]]; then
  [[ "$1" == "--diagnose-stop" ]] && diagnose_stop=true
  if [[ -z "${2:-}" ]]; then
    echo 'Usage: run_dynamic.sh [--record-replay|--diagnose-stop] NEW_DIRECTORY [launch arguments]' >&2
    exit 2
  fi
  replay_directory="$2"
  shift 2
  /usr/bin/python3 - "$replay_directory" "$comparison_method" "$profile" "$default_scene" "$@" <<'PYTHON'
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / 'scripts'))
from replay_data import make_scene
folder = Path(sys.argv[1]).resolve()
args = sys.argv[5:]
world = next((a.split(':=',1)[1] for a in reversed(args) if a.startswith('social_scene:=')), sys.argv[4])
if world not in ('static', 'dynamic'):
    raise SystemExit('social_scene must be static or dynamic')
if sys.argv[3] in ('dynamic', 'static') and world != sys.argv[4]:
    raise SystemExit('Select the baseline scene with the dynamic/static runner profile')
scene = make_scene(Path.cwd(), 'social_static' if world == 'static' else 'social_dynamic')
scene['run_profile'] = sys.argv[3]
scene['navigation_backend'] = sys.argv[3] if sys.argv[3] in ('paper1', 'paper2') else 'baseline'
if sys.argv[2]:
    scene['comparison_method'] = int(sys.argv[2])
    scene['navigation_backend'] = 'compare' + sys.argv[2]
scene['sensor_replay'] = {'version':1,'stream':'navigation.jsonl','source':'ROS scans and planner outputs; replay/evaluation only'}
scene['perception_replay'] = {'stream':'perception.jsonl','camera':'raw and detection JPEG, max2Hz per source; manual recording only','social':'published social marker snapshots'}
scene['leader'] = next((arg.split(':=', 1)[1] for arg in reversed(args) if arg.startswith('leader_robot:=')), 'robot3')
# Refuse to overwrite any existing recording.
folder.mkdir(parents=True, exist_ok=False)
(folder / 'scene.json').write_text(json.dumps(scene, ensure_ascii=False, indent=2) + '\n')
PYTHON
  export SOCIAL_REPLAY_DIRECTORY="$(realpath "$replay_directory")"
  echo "Pose replay recording: $SOCIAL_REPLAY_DIRECTORY"
  printf 'Open this recording in another terminal: python3 scripts/view_replay.py --session %q\n' "$SOCIAL_REPLAY_DIRECTORY"
  if [[ "$diagnose_stop" == true ]]; then
    export SOCIAL_STOP_DIAGNOSTICS_DIRECTORY="$SOCIAL_REPLAY_DIRECTORY"
    /usr/bin/python3 - "$SOCIAL_STOP_DIAGNOSTICS_DIRECTORY" "$comparison_method" "$profile" <<'PYTHON'
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sources = {}
names = ['dstar_mpc_controller', 'stop_diagnostics', 'moving_obstacles', 'local_escape', 'scan_pose_history', 'robot_motion']
if sys.argv[2]:
    from social_navigation_planner.comparison_methods.registry import METHODS
    info = METHODS[int(sys.argv[2])]
    names += ['comparison_controller', 'comparison_methods.common', 'comparison_methods.registry']
    names += ['comparison_methods.' + info['module'] + '.' + part
              for part in ['pipeline', 'formation', 'trajectory', 'control']]
if sys.argv[3] == 'paper1':
    names += ['paper1_gwo_woa_node', 'paper1_gwo_woa_core']
elif sys.argv[3] == 'paper2':
    names += ['paper2_apf_mpc_node', 'paper2_apf_mpc_core']
for name in names:
    spec = importlib.util.find_spec('social_navigation_planner.' + name)
    if spec is None or spec.origin is None:
        raise SystemExit('Build social_navigation_planner before enabling diagnostics')
    source = Path(spec.origin).resolve()
    sources[name] = {'path': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
config = {'mode': 'manual_stop_diagnostics', 'sources': sources,
          'pre_wall_seconds': 3, 'post_recovery_wall_seconds': 5,
          'maximum_samples_per_wall_second': 10, 'maximum_bytes_per_stream': 20*1024*1024,
          'raw_camera_pixels_saved': False, 'full_lidar_ranges_saved': True,
          'stop_streams_full_lidar_ranges_saved': False,
          'raw_lidar_replay_stream': 'navigation.jsonl'}
config['run_profile'] = sys.argv[3]
config['navigation_backend'] = sys.argv[3] if sys.argv[3] in ('paper1', 'paper2') else 'baseline'
if sys.argv[2]:
    config['comparison_method'] = int(sys.argv[2])
    config['navigation_backend'] = 'compare' + sys.argv[2]
(Path(sys.argv[1]) / 'diagnostics_config.json').write_text(json.dumps(config, indent=2) + '\n')
PYTHON
    echo "Stop diagnosis enabled: $SOCIAL_STOP_DIAGNOSTICS_DIRECTORY/stop_*.jsonl"
  fi
fi
if [[ -n "$comparison_method" ]]; then
  exec ros2 launch social_navigation_sim comparison.launch.py \
    method:="$comparison_method" social_scene:=dynamic \
    rviz_rendering:=intel gazebo_rendering:=intel "$@"
fi
if [[ "$profile" == "dynamic" ]]; then
  exec ros2 launch social_navigation_sim "$launch_file" \
    rviz_rendering:=intel gazebo_rendering:=intel leader_camera:=false "$@"
fi
exec ros2 launch social_navigation_sim "$launch_file" \
  rviz_rendering:=intel gazebo_rendering:=intel "$@"
