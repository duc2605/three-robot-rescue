"""Preserve negative iterations and final test without publishing ROS data."""
import gzip
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('old_inspector',ROOT/'docs/evidence/2026-11-02/lidar_2m_avoidance/analyze_runs.py')
inspector=importlib.util.module_from_spec(spec);spec.loader.exec_module(inspector)
trials=[]
for i in [1,2,3,4,5,6]:
    source=ROOT/f'recordings/nk073_validation_{i:02d}'
    if not (source/'world_frames.jsonl').exists():continue
    result,frames=inspector.inspect(source)
    result['phase']={1:'Fusion, flow commitment, braking prediction; cruise-only rollout still rejected refuges.',
                     2:'Both cruise/refuge rollout; remaining map-supported phantom motion constraints.',
                     3:'Map-supported motion gate; raw rays retained; paused-object approach still failed.',
                     4:'Recent-turn/pause reserve; escape budget still interrupted follower acceleration.',
                     5:'Warm direction; refuge still moved with robot; contacts and physics slowdown.',
                     6:'Final: fixed world refuge revalidated until risk passes.'}[i]
    result['early_stopped_for_observed_failure']=i in [1,2,3,4,5]
    if (source/'diagnostics_config.json').exists():
        cfg=json.loads((source/'diagnostics_config.json').read_text())
        result['runtime_sources']=cfg['sources']
        result['source_matches_current']={name:hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()==entry['sha256']
                                          for name,entry in cfg['sources'].items()}
    trials.append(result)
    durable=OUT/f'trial{i:02d}_replay';durable.mkdir(exist_ok=True)
    for name in ['scene.json','goals.jsonl','diagnostics_config.json']:
        if (source/name).exists():shutil.copy2(source/name,durable/name)
    with (source/'world_frames.jsonl').open('rb') as inp,gzip.open(durable/'world_frames.jsonl.gz','wb') as output:
        shutil.copyfileobj(inp,output)
    # Retain raw diagnostics around important encounters, not only aggregates.
    for path in source.glob('stop_robot*.jsonl'):
        with gzip.open(durable/(path.name+'.gz'),'wt') as output:
            for row in inspector.read_lines(path):
                if any(a<=row.get('t',-1)<=b for a,b in [(28,34),(73,97),(136,149),(189,204),(240,251)]):
                    output.write(json.dumps(row)+'\n')
final=trials[-1]
payload={'trials':trials,'final':final,
         'conditions':{'goal':[1.0355337858200073,-1.9790207147598267],'goal_after_sim':8.69,
                       'camera':False,'range_m':2.,'gui':False,'rviz':False,
                       'final_domain':60,'final_partition':'nk073_validation_06',
                       'ROS_LOCALHOST_ONLY':'0','RMW_FASTRTPS_PUBLICATION_MODE':'ASYNCHRONOUS'},
         'limits':['Single final trial, not a repeated controlled benchmark.',
                   'Raw pose/contact indicates observed physics, not guaranteed perception accuracy.',
                   'Braking reserve is not a calibration of wheel or actuator physics.',
                   'Earlier changed source hashes are expected; per-trial source config and checkpoints preserved.']}
(OUT/'validation_summary.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
_,frames=inspector.inspect(ROOT/final['folder'])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,7))
for name,color in [('robot1','#d84343'),('robot2','#2675c6'),('robot3','#079965'),('patrol_person','#8a53b4'),('tv_viewer_a_walking','#e69a22'),('tv_viewer_a_returning','#a4832c')]:
    chain=[];label=name
    for f in frames:
        obj=next((o for o in f['objects'] if o['name']==name),None)
        if obj is None or obj['p'][2]<-5:
            if chain:ax.plot(*zip(*chain),color=color,label=label,lw=1.3);label=None;chain=[]
        else:chain.append(obj['p'][:2])
    if chain:ax.plot(*zip(*chain),color=color,label=label,lw=1.3)
for group in final['contact_pairs']:
    for event in group['episodes']:
        f=min(frames,key=lambda f:abs(f['t']-event['first_t']))
        obj=next((o for o in f['objects'] if o['name'] in group['pair'] and o['name'].startswith('robot')),None)
        if obj:ax.scatter(*obj['p'][:2],c='red',marker='x',s=70)
ax.scatter(*payload['conditions']['goal'],c='#b71db9',marker='*',s=180,label='Selected goal')
ax.set(title=f"NK-073 final trial: {final['time'][0]:.3f}–{final['time'][1]:.3f} sim s\n{len(final['contact_pairs'])} observed non-ground contact pairs",xlabel='World X (m)',ylabel='World Y (m)')
ax.set_aspect('equal',adjustable='datalim');ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(OUT/'final_trajectories.png',dpi=150);plt.close(fig)
print(json.dumps({'final_time':final['time'],'contacts':final['contact_pairs'],'robots':final['robots']},ensure_ascii=False))
