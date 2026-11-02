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
    import re
    result=analyze(Path('recordings/nk078_social_camera_120s_once'))
    events=rows(OUT/'social_events.jsonl')
    topics=collections.Counter(e['topic'] for e in events)
    detector=[e for e in events if e['topic']=='/leader/people/status']
    status=[e for e in events if e['topic']=='/social_navigation/status']
    maps=[e for e in events if e['topic']=='/social_navigation/keepout']
    result['camera_social']={'topic_counts':dict(topics),'first_detector_status':detector[0] if detector else None,
        'last_detector_status':detector[-1] if detector else None,'first_social_status':status[0] if status else None,
        'last_social_status':status[-1] if status else None,
        'max_keepout_cells':max((e['data']['nonzero'] for e in maps),default=0),
        'last_keepout_cells':maps[-1]['data']['nonzero'] if maps else None}
    for key in ['tv_regions','confirmed_regions','color_regions','person_tracks','tv_tracks','tv_raw_tracks']:
        numbers=[int(m.group(1)) for e in status if (m:=re.search(r'\b'+key+r'=(\d+)',e['data']))]
        result['camera_social']['max_'+key]=max(numbers,default=0)
    for key in ['people','located','heads','tv','bodies','lying_candidates','inference_ms']:
        numbers=[int(m.group(1)) for e in detector if (m:=re.search(r'\b'+key+r'=(\d+)',e['data']))]
        result['camera_social']['max_detector_'+key]=max(numbers,default=0)
    labels=collections.Counter()
    for e in events:
        if e['topic']=='/social_navigation/markers':
            for m in e['data'].get('markers',[]):
                if m.get('text'):labels[m['text']]+=1
    result['camera_social']['marker_labels']=dict(labels)
    pair_times={}
    for f in rows(Path('recordings/nk078_social_camera_120s_once/world_frames.jsonl')):
        for c in f.get('contacts',[]):
            if 'ground_plane' in [c['a'],c['b']]:continue
            key=' / '.join(sorted([c['a'],c['b']]))
            if key not in pair_times:pair_times[key]={'first_t':c['first_t'],'last_t':c['last_t']}
            pair_times[key]['last_t']=c['last_t']
    result['non_ground_contact_times']=pair_times
    # Report an actual departure and return, not a trivial near-goal tick.
    frames=rows(Path('recordings/nk078_social_camera_120s_once/world_frames.jsonl'))
    goal=result['goal'];distances=[]
    for frame in frames:
        robot=next((o for o in frame.get('objects',[]) if o['name']=='robot3'),None)
        if robot and goal:distances.append((frame['t'],math.dist(robot['p'][:2],goal)))
    arrival=next((t for t,d in distances if d<.15),None)
    departure=next((t for t,d in distances if arrival is not None and t>arrival and d>.5),None)
    returned=next((t for t,d in distances if departure is not None and t>departure and d<.15),None)
    result['leader_excursion']={'initial_arrival_t':arrival,'departure_beyond_50cm_t':departure,'return_within_15cm_t':returned}
    for kind in ['viewing_tv','facing_group','lying_person']:
        seen=[]
        for e in events:
            if e['topic']=='/social_navigation/markers' and any(m.get('text','').startswith(kind+'\n') for m in e['data'].get('markers',[])):seen.append(e['t'])
        result['camera_social'][kind+'_evidence']={'samples':len(seen),'first_t':seen[0] if seen else None,'last_t':seen[-1] if seen else None}
    result['scope']='One120s simulation with camera/social features enabled; no avoidance code changes, no repeated benchmark.'
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
