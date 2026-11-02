import json,math,collections,re
from pathlib import Path
base=Path('docs/evidence/2026-11-01')
for name in ['leader_audit_current','leader_audit_encounter']:
 folder=base/name;rows=[json.loads(s) for s in (folder/'snapshots.jsonl').read_text().splitlines()];result={}
 for robot in ['robot1','robot2','robot3']:
  counts=collections.Counter();examples=[];ages=[];still=longest=0.
  for a,b in zip(rows,rows[1:]):
   s=b['latest'].get(robot+'/safety','unknown');kind=s.split(':')[0];counts[kind]+=1
   if 'no feasible rollout' in s and len(examples)<3:examples.append(dict(elapsed=b['elapsed'],sim=b['sim'],status=s,reference=b['latest'].get('reference'),scan_age=b.get('age',{}).get(robot+'/scan')))
   age=b.get('age',{}).get(robot+'/scan',{}).get('capture_age');
   if age is not None:ages.append(age)
   i=int(robot[-1])-1;p=a['latest'].get('team',[]);q=b['latest'].get('team',[])
   if len(p)==len(q)==3 and math.dist(p[i][:2],q[i][:2])<.005:still+=b['elapsed']-a['elapsed'];longest=max(longest,still)
   else:still=0.
  result[robot]=dict(snapshot_status_counts=counts,blocked_examples=examples,longest_near_stationary_seconds=longest,scan_capture_age_max=max(ages) if ages else None,scan_age_over_point3=sum(v>.3 for v in ages))
 last=rows[-1];goal=last['goal'];team=last['latest'].get('team',[])
 result.update(snapshot_count=len(rows),duration_sampled=last['elapsed'],first_sim=rows[0]['sim'],last_sim=last['sim'],goal=goal,leader_goal_distance=math.dist(goal,team[2][:2]) if goal and len(team)==3 else None,empty_reference_snapshots=sum(r['latest'].get('reference',{}).get('length')==0 for r in rows))
 (folder/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
 print(name,json.dumps(result,ensure_ascii=False))
