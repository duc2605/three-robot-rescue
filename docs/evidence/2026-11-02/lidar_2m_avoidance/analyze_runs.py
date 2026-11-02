"""Preserve measured outcomes of every trial, including failed intermediate versions."""
from pathlib import Path
import collections,gzip,hashlib,json,math,shutil
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent


def read_lines(path):
    with path.open('rb') as stream:
        for line in stream:
            if not line.endswith(b'\n'):break
            if line.strip():yield json.loads(line)


def inspect(folder):
    frames=list(read_lines(folder/'world_frames.jsonl'))
    hits=collections.defaultdict(list);robots={};previous={}
    for frame in frames:
        for contact in frame.get('contacts',[]):
            if 'ground_plane' not in (contact['a'],contact['b']):
                hits[tuple(sorted([contact['a'],contact['b']]))].append((frame['epoch'],contact))
        for obj in frame['objects']:
            name=obj['name']
            if name not in ['robot1','robot2','robot3']:continue
            entry=robots.setdefault(name,{'start':obj['p'][:2],'end':None,'sampled_xy_travel':0.})
            if name in previous and previous[name][0]==frame['epoch']:
                entry['sampled_xy_travel']+=math.dist(previous[name][1],obj['p'][:2])
            previous[name]=(frame['epoch'],obj['p'][:2]);entry['end']=obj['p'][:2]
    episodes=[]
    for pair,contacts in hits.items():
        combined=[]
        for epoch,c in sorted(contacts,key=lambda item:(item[0],item[1]['first_t'])):
            if combined and epoch==combined[-1]['epoch'] and c['first_t']-combined[-1]['last_t']<=.1:
                combined[-1]['last_t']=max(combined[-1]['last_t'],c['last_t'])
            else:combined.append({'epoch':epoch,'first_t':c['first_t'],'last_t':c['last_t']})
        episodes.append({'pair':list(pair),'episodes':combined})
    diagnostics={}
    for path in folder.glob('stop_robot*.jsonl'):
        counts=collections.Counter();maxspeed=0.;last=None;durations=[]
        for row in read_lines(path):
            if row.get('kind')!='controller':continue
            counts[row['reason']]+=1;last=row['t']
            maxspeed=max(maxspeed,math.hypot(*row['command'][:2]))
            if row.get('compute_elapsed_wall_ms') is not None:durations.append(row['compute_elapsed_wall_ms'])
        diagnostics[path.stem]={'last_t':last,'reasons':dict(counts),'max_saved_command_speed':maxspeed,
                                'max_saved_compute_elapsed_wall_ms':max(durations,default=None)}
    return {'folder':str(folder.relative_to(ROOT)),'frames':len(frames),
            'time':[frames[0]['t'],frames[-1]['t']], 'contact_pairs':episodes,
            'robots':robots,'diagnostics':diagnostics,
            'frame_sha256':hashlib.sha256((folder/'world_frames.jsonl').read_bytes()).hexdigest()},frames


if __name__=='__main__':
    trials=[]
    for i in range(1,11):
        folder=ROOT/f'recordings/lidar_2m_validation_{i:02d}'
        if not (folder/'world_frames.jsonl').exists():continue
        result,frames=inspect(folder)
        result['valid_avoidance_trial']=i not in [3,7]
        result['revision_note']={1:'Pilot exposed normal MPC deadline holds; GUI.',
            2:'Before local-priority fusion: TV walker contact robot1.',
            3:'Startup services failed; no scan/control validation.',
            4:'Before capture-time robot pose alignment: TV walker contact robot2.',
            5:'Before buffered scan retry: missing capture-pose packets and contacts.',
            6:'Before spatial components/motion persistence: remaining contacts.',
            7:'Startup services failed; not an avoidance success.',
            8:'Spatial persistence revision; speed variable shadowing still present.',
            9:'Bounded-speed revision; followers no contacts, leader patrol contact.',
            10:'Nearby approach and short pause guard after measured turn failure.'}[i]
        trials.append(result)
    final,frames=inspect(ROOT/'recordings/lidar_2m_validation_10')
    conditions={'ROS_DOMAIN_ID':54,'ROS_LOCALHOST_ONLY':'0','RMW_FASTRTPS_PUBLICATION_MODE':'ASYNCHRONOUS',
                'IGN_PARTITION':'lidar_2m_validation_10','gazebo_gui':False,'rviz':False,
                'camera':False,'goal':[1.0351457595825195,-2.035773515701294],
                'scope':'Single run, no repeated controlled benchmark; do not compare RTF across earlier trials.'}
    payload={'trials':trials,'final':final,'conditions':conditions,
             'limits':['Recorded engine contacts are not a universal safety guarantee.',
                       'Saved command speed samples are windowed diagnostics, not all commands.',
                       'Model root trajectories are not exact footprint clearance.',
                       'Earlier revisions and startup failures are retained, not relabelled as final success.']}
    (OUT/'validation_summary.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    durable=OUT/'final_replay';durable.mkdir(exist_ok=True)
    source=ROOT/'recordings/lidar_2m_validation_10'
    for name in ['scene.json','goals.jsonl','diagnostics_config.json']:
        if (source/name).exists():shutil.copyfile(source/name,durable/name)
    with (source/'world_frames.jsonl').open('rb') as inp,gzip.open(durable/'world_frames.jsonl.gz','wb') as output:
        shutil.copyfileobj(inp,output)
    with (OUT/'physics_contact_ledger.jsonl').open('w') as output:
        for frame in frames:
            row={k:frame.get(k) for k in ['t','epoch','physics_contact_source']}
            row['contacts']=[c for c in frame.get('contacts',[]) if 'ground_plane' not in (c['a'],c['b'])]
            output.write(json.dumps(row)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,7))
    for name,color in [('robot1','#d84343'),('robot2','#2675c6'),('robot3','#079965'),
                       ('tv_viewer_a_walking','#e69a22'),('patrol_person','#8a53b4'),('tv_viewer_a_returning','#a4832c')]:
        chain=[];label=name
        for frame in frames:
            obj=next((o for o in frame['objects'] if o['name']==name),None)
            if obj is None or obj['p'][2]<-5:
                if chain:ax.plot(*zip(*chain),color=color,lw=1.5,label=label);label=None;chain=[]
                continue
            chain.append(obj['p'][:2])
        if chain:ax.plot(*zip(*chain),color=color,lw=1.5,label=label)
    ax.scatter(*conditions['goal'],marker='*',s=180,c='#b71db9',label='Selected goal')
    for result in final['contact_pairs']:
        for episode in result['episodes']:
            frame=min(frames,key=lambda f:abs(f['t']-episode['first_t']))
            obj=next((o for o in frame['objects'] if o['name'] in result['pair'] and o['name'].startswith('robot')),None)
            if obj:ax.scatter(*obj['p'][:2],marker='x',s=90,c='red')
    ax.set(xlabel='World X (m)',ylabel='World Y (m)',
           title=f"Final recorded trial: {frames[0]['t']:.3f}-{frames[-1]['t']:.3f} sim s\n{len(final['contact_pairs'])} non-ground engine contact pairs")
    ax.set_aspect('equal',adjustable='datalim');ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(OUT/'final_trajectories.png',dpi=150);plt.close(fig)
    print(json.dumps({'final_time':final['time'],'final_contacts':final['contact_pairs'],
                      'final_robots':final['robots']},ensure_ascii=False))
