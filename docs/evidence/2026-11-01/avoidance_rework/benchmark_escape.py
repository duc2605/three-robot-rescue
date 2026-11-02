import importlib.util,sys,math,time,json,statistics
from pathlib import Path
sys.path.insert(0,str(Path('social_navigation_planner').resolve()))
from social_navigation_planner.local_escape import plan_escape
from social_navigation_planner.moving_obstacles import MovingObstacle
spec=importlib.util.spec_from_file_location('escape_before',str(Path(__file__).with_name('local_escape_before.py')));old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
obstacle=MovingObstacle((.9,0.),(-.35,0.),.32,0.)
result={}
for name,fn in [('before',old.plan_escape),('after',plan_escape)]:
 timings=[];edge_counts=[]
 for repeat in range(50):
  calls=[0]
  def edge(a,b,t,u):calls[0]+=1;return obstacle.clearance(a,b,t,u,.15)>=.03
  def hold(p,t,u):return obstacle.clearance(p,p,t,u,.15)>=.03
  began=time.perf_counter();plan=fn((0.,0.,0.),0.,.28,edge,hold);timings.append((time.perf_counter()-began)*1000);edge_counts.append(calls[0]);assert plan is not None
  assert all(edge(a,b,i*.3,(i+1)*.3) for i,(a,b) in enumerate(zip(plan.points,plan.points[1:])))
 result[name]=dict(repetitions=50,median_ms=statistics.median(timings),min_ms=min(timings),max_ms=max(timings),median_edge_checks=statistics.median(edge_counts),side=plan.side)
result['limit']='Same synthetic local escape input, sequential timing; not Gazebo RTF or full MPC benchmark.'
Path('docs/evidence/2026-11-01/avoidance_rework/escape_benchmark.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
