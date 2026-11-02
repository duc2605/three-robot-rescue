"""Audit the saved opt-in session; no ROS/Gazebo or navigation changes."""
from pathlib import Path
import sys,json,hashlib,math,tarfile
sys.path.insert(0,str(Path.cwd()/'scripts'))
sys.path.insert(0,str(Path.cwd()/'social_navigation_planner'))
from analyze_stop_diagnostics import analyze,rows
from social_navigation_planner.moving_obstacles import MovingObstacle
root=Path.cwd();folder=root/'recordings/chan_doan_01';out=Path(__file__).resolve().parent
summary=analyze(folder)
config=json.loads((folder/'diagnostics_config.json').read_text())
frames=list(rows(folder/'world_frames.jsonl'))
summary['world_range']=[frames[0]['t'],frames[-1]['t']]
summary['world_frames']=len(frames)
summary['input_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.json*')}
selected={};snapshot={}
for robot,times in [('robot2',[74.221,75.3,78.9]),('robot3',[76.7,79,80,81.9,83.3])]:
 stream=[r for r in rows(folder/f'stop_{robot}.jsonl') if r.get('kind')]
 selected[robot]=[]
 for target in times:
  row=min((r for r in stream if r['reason']!='watchdog_wall_freshness'),key=lambda r:abs(r['t']-target))
  selected[robot].append(row)
  snapshot[f'{robot}_{target}']={k:row.get(k) for k in ['t','reason','pose','command','scan_age_sim','scan_age_wall','state_age_sim','state_age_wall','reference_age_sim','reference_age_wall','reference_rows','rejected_checks','rejected_checks_tick_t','compute_elapsed_wall_ms','guard_active']}
  snapshot[f'{robot}_{target}']['moving_risks']=sum(o.get('risk') is not None for o in row['tracks'])
  snapshot[f'{robot}_{target}']['camera_candidate_count']=row['sensors'].get('camera_candidates',{}).get('count')
 summary['streams'][f'stop_{robot}.jsonl']['last_t']=stream[-1]['t']
 summary['streams'][f'stop_{robot}.jsonl']['bytes']=(folder/f'stop_{robot}.jsonl').stat().st_size
r=selected['robot2'][-1]
obs=[MovingObstacle(tuple(o['position']),tuple(o['velocity']),o['radius'],o['stamp']) for o in r['tracks']]
initial=min(math.dist(o.at(r['t']),r['pose'][:2])-o.radius-r['limits']['robot_radius'] for o in obs)
checks=[]
for direction in range(16):
 angle=direction*math.pi/8
 end=(r['pose'][0]+.2*math.cos(angle),r['pose'][1]+.2*math.sin(angle))
 checks.append(min(o.clearance(r['pose'][:2],end,r['t'],r['t']+.15,r['limits']['robot_radius']) for o in obs))
assert initial<.03 and all(g<.03 for g in checks)
summary['numerical_start_overlap_check']={'robot':'robot2','t':r['t'],'minimum_start_track_surface_gap':initial,'required_margin':.03,'sixteen_direction_swept_gaps':checks,'interpretation':'Min swept separation includes the starting point; any path from this already-overlapping buffered start fails the strict .03 margin. This is track buffer overlap, not a new physical contact measurement.'}
stream=list(rows(folder/'stop_robot2.jsonl'))
i=next(i for i,r in enumerate(stream) if r.get('reason')=='checked_escape_command' and abs(r['t']-75.3)<.01)
following=stream[i:i+4]
summary['command_then_stop']={
    'first_command_t':following[0]['t'],'next_stop_t':following[1]['t'],
    'wall_seconds_between':following[1]['wall_monotonic']-following[0]['wall_monotonic'],
    'next_stop_reason':following[1]['reason'],
    'records':following}
summary['selected_snapshots']=snapshot
summary['limits'] += ['Tick t is sampled before computation; contact time matching is approximate when a tick takes seconds.','Compute wall time includes scheduling and diagnostic overhead; no controlled RTF or CPU benchmark.','All three robot files end near the configured 20 MiB cap; later contact diagnosis is incomplete.']
provenance={}
archive=root/'backups/20261102_002544_359477_mark_selected_goals_in_replay_source_only/source.tar.gz'
with tarfile.open(archive) as saved:
 for name,value in config['sources'].items():
  member='social_navigation_planner/social_navigation_planner/'+name+'.py'
  content=saved.extractfile(member).read()
  provenance[name]=hashlib.sha256(content).hexdigest()==value['sha256']
assert all(provenance.values())
summary['recorded_source_hash_matches_preserved_nk067_snapshot']=provenance
(out/'analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
with (out/'selected_diagnostics.jsonl').open('w') as f:
 for stream in selected.values():
  for row in stream:f.write(json.dumps(row,ensure_ascii=False)+'\n')
with (out/'contact_frames.jsonl').open('w') as f:
 for frame in frames:
  if any('ground_plane' not in (c['a'],c['b']) for c in frame.get('contacts',[])):
   f.write(json.dumps(frame,ensure_ascii=False)+'\n')
(out/'diagnostics_config.json').write_text(json.dumps(config,indent=2)+'\n')
print(json.dumps({'contacts':[(r['pair'],r['first_t'],r['last_t']) for r in summary['physics_contact_context']],'start_gap':initial,'recorded_source_verified':provenance,'world_range':summary['world_range']}))
