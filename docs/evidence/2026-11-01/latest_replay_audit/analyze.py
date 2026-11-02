"""Offline measured pose/contact audit; run from project root."""
from pathlib import Path
import json, hashlib, math, collections, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path.cwd();source=ROOT/'recordings/thu_ne_01';out=Path(__file__).resolve().parent
raw=(source/'world_frames.jsonl').read_bytes();end=raw.rfind(b'\n')+1
frames=[json.loads(x) for x in raw[:end].splitlines() if x.strip()]
by=[{o['name']:o for o in f['objects']} for f in frames]
def nearest(t):return min(range(len(frames)),key=lambda i:abs(frames[i]['t']-t))
pairs=collections.defaultdict(list)
for f in frames:
 for c in f.get('contacts',[]):
  if 'ground_plane' not in (c['a'],c['b']):pairs[tuple(sorted([c['a'],c['b']]))].append((f['epoch'],c))
summary={'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes_read':end,'frames':len(frames),'sim_time':[frames[0]['t'],frames[-1]['t']],'epochs':sorted({f['epoch'] for f in frames}),'contacts':[],'windows':[],'limits':['No camera pixels, LiDAR scans, goal or cmd_vel recorded; cannot infer perception failure or command intent.','Measured displacement may include physics response; it is not a command.','Model root distance is not surface clearance.','Contact intervals merged across collision shapes with gaps <= 0.1 sim s; record count is not number of impacts.']}
for pair,hits in pairs.items():
 episodes=[]
 for epoch,c in sorted(hits,key=lambda h:(h[0],h[1]['first_t'],h[1]['last_t'])):
  if episodes and episodes[-1]['epoch']==epoch and c['first_t']-episodes[-1]['last_t']<=.1:
   episodes[-1]['last_t']=max(episodes[-1]['last_t'],c['last_t'])
  else:episodes.append({'epoch':epoch,'first_t':c['first_t'],'last_t':c['last_t']})
 summary['contacts'].append({'pair':pair,'collision_interval_records':len(hits),'episodes':episodes,'collision_pairs':sorted({(c['collision1'],c['collision2']) for _,c in hits})})
fig,axes=plt.subplots(1,2,figsize=(12,6))
selected=set()
for ax,(r,p,a,b) in zip(axes,[('robot3','tv_viewer_a_walking',28,33),('robot2','patrol_person',78,80.901)]):
 ids=[i for i,f in enumerate(frames) if a<=f['t']<=b and r in by[i] and p in by[i]]
 samples=[]
 for t in [a,a+1,a+2,b]:
  i=nearest(t);selected.add(i);rp=by[i][r]['p'];hp=by[i][p]['p'];j=nearest(frames[i]['t']-.5);dt=frames[i]['t']-frames[j]['t'];rv=[(rp[k]-by[j][r]['p'][k])/dt for k in range(2)];pv=[(hp[k]-by[j][p]['p'][k])/dt for k in range(2)];c,s=math.cos(rp[5]),math.sin(rp[5]);rel=[hp[k]-rp[k] for k in range(2)]
  samples.append({'t':frames[i]['t'],'robot_xy':rp[:2],'human_xy':hp[:2],'root_distance':math.hypot(*rel),'human_in_robot_body_xy':[c*rel[0]+s*rel[1],-s*rel[0]+c*rel[1]],'robot_measured_body_velocity':[c*rv[0]+s*rv[1],-s*rv[0]+c*rv[1]],'human_measured_world_velocity':pv})
 d,i=min((math.dist(by[i][r]['p'][:2],by[i][p]['p'][:2]),i) for i in ids)
 summary['windows'].append({'robot':r,'human':p,'time':[a,b],'root_min_distance':d,'root_min_time':frames[i]['t'],'robot_net_displacement':math.dist(by[ids[0]][r]['p'][:2],by[ids[-1]][r]['p'][:2]),'snapshots':samples})
 for name,color in [(r,'#009363'),(p,'#d67513')]:
  xy=[by[i][name]['p'][:2] for i in ids];ax.plot(*zip(*xy),color=color,label=name,linewidth=2)
  for t in [a,a+1,a+2,b]:
   i=nearest(t);x,y=by[i][name]['p'][:2];ax.scatter(x,y,c=color,s=25);ax.annotate(f'{frames[i]["t"]:.2f}s',(x,y),xytext=(8,5 if name==p else -15),textcoords='offset points',fontsize=8)
 # Measured human movement arrow and robot heading, deliberately distinct.
 i=ids[0];j=ids[-1];rp=by[i][r]['p'];hp=by[i][p]['p'];hq=by[j][p]['p']
 ax.arrow(rp[0],rp[1],.2*math.cos(rp[5]),.2*math.sin(rp[5]),head_width=.04,color='#167b9b',length_includes_head=True,label='Robot heading')
 ax.annotate('',xy=hq[:2],xytext=hp[:2],arrowprops={'arrowstyle':'->','color':'#d67513','lw':1.5})
 ax.set_title(f'{r}: {a:.2f}-{b:.3f} sim s\nMeasured roots; not commanded motion')
 ax.set_xlabel('World X (m)');ax.set_ylabel('World Y (m)');ax.set_aspect('equal',adjustable='datalim');ax.margins(.35);ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.suptitle('Actual Gazebo contact: leader vs TV walker; follower vs patrol')
fig.tight_layout();fig.savefig(out/'trajectories.png',dpi=160);plt.close(fig)
(out/'analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# Keep the actual contact and neighboring pose samples, not reconstructed routes.
for i,f in enumerate(frames):
 if any(c['a']!='ground_plane' and c['b']!='ground_plane' for c in f.get('contacts',[])):selected.add(i)
(out/'selected_frames.jsonl').write_text(''.join(json.dumps(frames[i],ensure_ascii=False)+'\n' for i in sorted(selected)))
shutil.copyfile(source/'scene.json',out/'scene.json')
print(json.dumps({'contacts':summary['contacts'],'windows':[{k:v for k,v in w.items() if k!='snapshots'} for w in summary['windows']]},ensure_ascii=False))
