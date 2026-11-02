import json,math,re,collections,datetime,statistics
from pathlib import Path
p=Path(Path('log/audit_10min_latest.txt').read_text().strip());base=json.loads((p/'summary.json').read_text());rows=[json.loads(s) for s in (p/'snapshots.jsonl').read_text().splitlines()];events=[json.loads(s) for s in (p/'events.jsonl').read_text().splitlines()]
def quantile(v,q):
 v=sorted(v);return v[round((len(v)-1)*q)] if v else None
ages={}
for k in ['robot1/scan','robot2/scan','robot3/scan','rgb','team','reference']:
 vals=[r['age'][k]['receipt_age'] for r in rows if k in r['age']];caps=[r['age'][k]['capture_age'] for r in rows if k in r['age'] and r['age'][k]['capture_age'] is not None]
 ages[k]={'receipt_p50':quantile(vals,.5),'receipt_p95':quantile(vals,.95),'receipt_max':max(vals,default=None),'capture_p95':quantile(caps,.95),'capture_max':max(caps,default=None),'capture_over_0_3_sample_count':sum(x>.3 for x in caps),'sample_count':len(vals)}
intervals=[];active=None;previous=None
for r in rows:
 team=r['latest'].get('team')
 if not team or len(team)!=3:continue
 if previous:
  unchanged=math.dist(team[2][:2],previous['latest']['team'][2][:2])<=.002
  if unchanged and active is None:active=previous
  if not unchanged and active is not None:
   intervals.append({'start':active['elapsed'],'end':previous['elapsed'],'duration':previous['elapsed']-active['elapsed'],'xy':active['latest']['team'][2][:2]});active=None
 previous=r
if active:intervals.append({'start':active['elapsed'],'end':previous['elapsed'],'duration':previous['elapsed']-active['elapsed'],'xy':active['latest']['team'][2][:2]})
intervals.sort(key=lambda d:d['duration'],reverse=True)
goal_distances=[math.dist(r['latest']['team'][2][:2],r['goal']) for r in rows if r['goal'] and len(r['latest'].get('team',[]))==3]
begin=datetime.datetime.fromisoformat(base['started_vietnam']).timestamp();end=datetime.datetime.fromisoformat(base['ended_vietnam']).timestamp()
source=Path('log/manual_dynamic.log').read_text(errors='replace').splitlines();filtered=[]
for line in source:
 m=re.search(r'\[([0-9]{10}\.[0-9]+)\]',line)
 if m and begin<=float(m[1])<=end:filtered.append(line)
(p/'runtime_log_during_audit.log').write_text('\n'.join(filtered)+'\n')
logcounts={k:sum(text in line for line in filtered) for k,text in {'yield_ready':'Follower yield ready:','passed_followers':'Leader passed followers;','no_route':'no route for the leader','no_fresh_rgb':'No fresh leader RGB images','errors':'[ERROR]'}.items()}
refrows=[r for r in rows if 'reference' in r['latest']];empty=sum(r['latest']['reference']['length']==0 for r in refrows)
leader_events=[e for e in events if e['kind']=='robot3/safety_change'];recoveries=[e for e in leader_events if 'uncertainty_recovery=True' in str(e['value'])];yielding=[e for e in leader_events if 'yielding with checked local escape' in str(e['value'])]
social_tv=[int(m[1]) for r in rows if (m:=re.search(r'\btv_regions=(\d+)',r['latest'].get('social','')))];cached=[int(m[1]) for r in rows if (m:=re.search(r'\bremembered_viewing_regions=(\d+)',r['latest'].get('social','')))]
result={'duration_wall':base['duration_wall_seconds'],'started_vietnam':base['started_vietnam'],'ended_vietnam':base['ended_vietnam'],'sim_elapsed':base['sim_elapsed'],'rtf_overall_from_clock':base['sim_elapsed']/base['duration_wall_seconds'],'goal_changes':base['goal_changes'],'last_goal':base['goal'],'leader_goal_distance_last':base['leader_goal_distance'],'leader_goal_distance_min_sampled':min(goal_distances,default=None),'sampled_path_lengths':base['path_length_sampled'],'commands':base['command_counts'],'leader_yield_status_transitions':len(yielding),'leader_uncertainty_recovery_transitions':len(recoveries),'recovery_examples':recoveries[:3],'longest_leader_xy_stationary_intervals':intervals[:5],'reference_empty_samples':empty,'reference_observed_samples':len(refrows),'sensor_age':ages,'log_counts_during_window':logcounts,'tv_regions_minmax':[min(social_tv),max(social_tv)] if social_tv else None,'remembered_viewing_regions_minmax':[min(cached),max(cached)] if cached else None,'limitations':base['limitations']+['Nonzero command or near-goal pose is not proof of avoidance success','Stationary intervals use 2mm per-snapshot threshold and do not exclude yaw changes','No measured contact sensor; user reported leader had not avoided; do not classify this run collision-free','TV region already absent at monitor start; cannot attribute previous disappearance solely from this window']}
(p/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
try:
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 ts=[r['elapsed']/60 for r in rows];fig,ax=plt.subplots(3,1,figsize=(10,8),sharex=True)
 clocks=[r['sim'] for r in rows];rtf=[None]+[(b-a)/(rows[i]['elapsed']-rows[i-1]['elapsed']) if a is not None and b is not None else math.nan for i,(a,b) in enumerate(zip(clocks,clocks[1:]),1)]
 ax[0].plot(ts,rtf);ax[0].set_ylabel('RTF');ax[0].set_title('Read-only audit: 10 minutes, 2026-11-01')
 distances=[math.dist(r['latest']['team'][2][:2],r['goal']) if r['goal'] and len(r['latest'].get('team',[]))==3 else math.nan for r in rows];ax[1].plot(ts,distances);ax[1].set_ylabel('Leader to goal (m)')
 for k,label in [('robot3/scan','Leader LiDAR'),('rgb','RGB'),('team','Robot poses')]:ax[2].plot(ts,[r['age'].get(k,{}).get('receipt_age',math.nan) for r in rows],label=label)
 ax[2].axhline(2.,color='r',ls='--',lw=.8,label='2 s reference line');ax[2].set_ylabel('Receipt age (wall s)');ax[2].set_xlabel('Wall minutes');ax[2].legend()
 for a in ax:a.grid(True,alpha=.3)
 fig.tight_layout();fig.savefig(p/'runtime_plot.png',dpi=150);plt.close(fig)
except ImportError:pass
