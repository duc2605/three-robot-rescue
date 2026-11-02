"""Summarize recorded poses/decisions/contacts without launching simulation."""
import collections,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parent

def rows(p):
    if not p.exists():return []
    data=[]
    with p.open() as stream:
        for line in stream:
            try:data.append(json.loads(line))
            except ValueError:pass
    return data

def analyze(folder):
    frames=[f for f in rows(folder/'world_frames.jsonl') if f.get('objects')]
    events=[r for r in rows(folder/'navigation.jsonl') if r.get('kind')=='decision']
    goals=rows(folder/'goals.jsonl');goal=goals[-1]['xy'] if goals else None
    contacts=collections.Counter();points={r:[] for r in ['robot1','robot2','robot3']}
    for f in frames:
        for c in f.get('contacts',[]):
            if 'ground_plane' not in [c['a'],c['b']]:contacts[' / '.join(sorted([c['a'],c['b']]))]+=1
        for o in f['objects']:
            if o['name'] in points:points[o['name']].append((f['t'],o['p'][:2]))
    result={'session':str(folder),'frame_count':len(frames),'sim_range':[frames[0]['t'],frames[-1]['t']],
            'goal':goal,'non_ground_contact_frame_counts':dict(contacts),'robots':{}}
    for robot,xy in points.items():
        decisions=[e for e in events if e['robot']==robot]
        escapes=[e['t'] for e in decisions if e['reason']=='checked_escape_command']
        after=[e for e in decisions if escapes and e['t']>escapes[-1] and e['reason']=='mpc_tracking_command']
        result['robots'][robot]={'root_distance_m':sum(math.dist(a[1],b[1]) for a,b in zip(xy,xy[1:])),
          'last_xy':xy[-1][1],'decision_counts':dict(collections.Counter(e['reason'] for e in decisions)),
          'last_escape_t':escapes[-1] if escapes else None,'first_tracking_after_last_escape_t':after[0]['t'] if after else None}
        if robot=='robot3' and goal:
            result['robots'][robot].update(min_goal_distance_m=min(math.dist(p,goal) for t,p in xy),last_goal_distance_m=math.dist(xy[-1][1],goal),
                first_within_15cm_t=next((t for t,p in xy if math.dist(p,goal)<.15),None),
                after_last_escape_min_goal_distance_m=min((math.dist(p,goal) for t,p in xy if escapes and t>escapes[-1]),default=None))
    return result

if __name__=='__main__':
    result={'baseline':analyze(Path('recordings/lidar_vung_01')),'one_validation':analyze(Path('recordings/nk076_resume_goal_once')),
            'limits':'One headless run, not repeated benchmark, conditions differ from user GUI run; source escape policy unchanged. Counts are samples, not independent attempts.'}
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
