"""Offline correlation only: GT evaluates tracks, never feeds navigation."""
import gzip,json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
SRC=OUT.parent/'nk078_social_camera_120s'
with gzip.open(SRC/'world_frames.jsonl.gz','rt') as f:frames=[json.loads(l) for l in f]
with gzip.open(SRC/'contact_diagnostics.jsonl.gz','rt') as f:records=[json.loads(l) for l in f]
def pose(t,name):
    frame=min(frames,key=lambda r:abs(r['t']-t))
    return frame['t'],next(o['p'] for o in frame['objects'] if o['name']==name)
def velocity(t):
    ta,a=pose(t-.05,'patrol_person');tb,b=pose(t+.05,'patrol_person')
    return [(b[i]-a[i])/(tb-ta) for i in [0,1]]
def sample(robot,t):
    r=min([r for r in records if r.get('robot')==robot],key=lambda r:abs(r['t']-t))
    # Spatial correspondence for this audit, not a person identity from LiDAR.
    track=min(r['selected_lidar_tracks'],key=lambda o:math.dist(o['position'],pose(o['stamp'],'patrol_person')[1][:2]))
    yaw=r['pose'][2];vx,vy,_=r['command']
    return dict(robot=robot,t=r['t'],reason=r['reason'],pose=r['pose'],command_body=r['command'],
        command_world=[vx*math.cos(yaw)-vy*math.sin(yaw),vx*math.sin(yaw)+vy*math.cos(yaw)],
        last_selected_goal=r.get('selected_escape_goal'),selected_goal_is_new=r['reason']=='checked_escape_command',
        nearby_track=track,ground_truth_patrol_velocity_at_track_stamp=velocity(track['stamp']),
        scan_age_sim=r['scan_age_sim'],state_age_sim=r['state_age_sim'],
        compute_ms=r['compute_elapsed_wall_ms'],rejected_checks=r['rejected_checks'])
checkpoints=[sample(robot,t) for robot,t in [('robot3',83.),('robot3',83.1),('robot3',83.5),('robot3',84.1),('robot2',84.),('robot2',85.1),('robot2',85.6)]]
a=pose(83.201,'robot3');b=pose(84.151,'robot3')
result={'source_session':'recordings/nk078_social_camera_120s_once',
 'checkpoints':checkpoints,'leader_root_displacement_during_zero_command':{'start_t':a[0],'end_t':b[0],'start':a[1][:2],'end':b[1][:2],'distance_m':math.dist(a[1][:2],b[1][:2])},
 'ground_truth_use':'offline evaluation only; no semantic identity from LiDAR implied',
 'source_hashes':{str(p.relative_to(Path.cwd())):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path.cwd()/'social_navigation_planner/social_navigation_planner/moving_obstacles.py',Path.cwd()/'social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py']},
 'limits':['No new simulation or intervention','No proof an admissible physical escape existed after83.3s','No actuator/wheel diagnosis from root drift alone','No matched120s cameraoff baseline; do not attribute causality to camera enable alone']}
(OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
for c in checkpoints:print(c['robot'],c['t'],c['reason'],'track v',c['nearby_track']['velocity'],'GT v',c['ground_truth_patrol_velocity_at_track_stamp'])
print('zero-command root displacement',result['leader_root_displacement_during_zero_command']['distance_m'])
