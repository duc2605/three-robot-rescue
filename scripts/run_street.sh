#!/usr/bin/env bash
# Outdoor-only runner: never substitutes static/dynamic world assets.
set -eo pipefail
street_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$street_root"
source /opt/ros/humble/setup.bash
if [[ ! -f install/setup.bash ]]; then
  echo 'Build social_navigation_sim and social_navigation_planner first.' >&2
  exit 1
fi
source install/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-31}"
export QT_QPA_PLATFORM=xcb
unset SOCIAL_REPLAY_DIRECTORY SOCIAL_STOP_DIAGNOSTICS_DIRECTORY
street_folder="recordings/street_$(date +%Y%m%d_%H%M%S_%N)_$$"
if [[ "${1:-}" == --diagnose-stop || "${1:-}" == --record-replay ]]; then
  street_folder="${2:?Provide a NEW recording directory}"
  shift 2
fi
/usr/bin/python3 - "$street_folder" "$@" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'scripts'))
from replay_data import make_scene
folder=Path(sys.argv[1]).resolve()
backend=next((a.split(':=',1)[1] for a in reversed(sys.argv[2:]) if a.startswith('navigation_backend:=')),'baseline')
if backend not in ['baseline',*[f'paper{i}' for i in range(1,9)]]:
    raise SystemExit('navigation_backend must be baseline or paper1..paper8')
paper=int(backend[5:]) if backend.startswith('paper') else None
if paper is not None and paper>=3:
    from social_navigation_planner.paper_models.catalog import require_runtime
    require_runtime(paper) # Check optional upstream before recording creation/launch.
scene=make_scene(Path.cwd(),'street_intersection')
# Decorations are visual context, not geometric obstacle/contact estimates.
import xml.etree.ElementTree as ET
models=ET.parse('social_navigation_sim/worlds/street_intersection.sdf').getroot().find('world')
for model in models.findall('model'):
    if not model.findall('link/collision'):
        scene['objects'][model.get('name')]['ignore_overlap']=True
scene.update(run_profile='street',navigation_backend=backend,leader='robot3',
             street_rule_mode='pedestrian',traffic_signal_source='authored scenario state',
             traffic_replay={'stream':'traffic.jsonl','source':'authored scenario state, NOT perception',
                             'pedestrian_green_axes':['east_west','north_south']},
             sensor_replay={'stream':'navigation.jsonl'},perception_replay={'stream':'perception.jsonl'})
sources={}
names=['dstar_mpc_controller','moving_obstacles','local_escape','scan_pose_history','robot_motion']
if paper in (1,2):
    names += [f'paper{paper}_'+('gwo_woa_node' if paper==1 else 'apf_mpc_node'),
              f'paper{paper}_'+('gwo_woa_core' if paper==1 else 'apf_mpc_core')]
elif paper is not None:
    names=['paper_experiment_node','paper_models.catalog','paper_models.kinematic',
           'paper_models.environment','grid_clearance','scan_pose_history']
    extra={5:'ho_mpc',6:'drivetrains',7:'robile',8:'deform'}.get(paper)
    if extra:names += ['paper_models.'+extra,'paper_models.upstream_sources']
for name in names:
    import importlib.util
    spec=importlib.util.find_spec('social_navigation_planner.'+name)
    if not spec or not spec.origin:raise SystemExit('Build planner before running')
    path=Path(spec.origin).resolve();sources[name]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
for relative in ['social_navigation_sim/scripts/street_navigation_rules.py',
                 'social_navigation_sim/scripts/street_rules.py',
                 'social_navigation_sim/src/street_traffic.cpp',
                 'social_navigation_sim/worlds/street_intersection.sdf']:
    path=Path(relative).resolve()
    sources[relative]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
folder.mkdir(parents=True,exist_ok=False)
(folder/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
(folder/'diagnostics_config.json').write_text(json.dumps({'run_profile':'street','navigation_backend':backend,'paper':paper,
    'controller_family':'baseline' if paper is None else 'paper_adaptation',
    'sources':sources,'launch_arguments':sys.argv[2:],'traffic_period_seconds':128,
    'street_rule_mode':'pedestrian','traffic_signal_source':'authored scenario state',
    'limitations':['Pedestrian road permissions use scenario signal state; visual traffic-light recognition and automatic vehicle mode remain future work.',
                   'Procedural people/animals and kinematic cars; no certified collision-free scenario.']},indent=2)+'\n')
PY
export SOCIAL_REPLAY_DIRECTORY="$(realpath "$street_folder")"
export SOCIAL_STOP_DIAGNOSTICS_DIRECTORY="$SOCIAL_REPLAY_DIRECTORY"
echo "Street recording: $SOCIAL_REPLAY_DIRECTORY"
printf 'Viewer: python3 scripts/view_replay.py --session %q\n' "$SOCIAL_REPLAY_DIRECTORY"
exec /usr/bin/python3 scripts/record_replay_media.py --session "$SOCIAL_REPLAY_DIRECTORY" -- \
  ros2 launch social_navigation_sim street_intersection.launch.py "$@"
