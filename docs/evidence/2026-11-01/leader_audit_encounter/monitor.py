import collections,datetime,json,math,re,time
from pathlib import Path
from zoneinfo import ZoneInfo
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import PoseArray,PoseStamped,Twist
from sensor_msgs.msg import Image,LaserScan
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
TZ=ZoneInfo('Asia/Ho_Chi_Minh');began=datetime.datetime.now(TZ)
out=Path('docs/evidence/2026-11-01/leader_audit_encounter');out.mkdir(parents=True,exist_ok=True)
Path('log/lidar_only_audit_latest.txt').write_text(str(out)+'\n')
rclpy.init();n=Node('read_only_ten_minute_audit');subs=[];start=time.monotonic();now=None
counts=collections.Counter();latest={};received={};stamps={};status_counts={r:collections.Counter() for r in ['robot1','robot2','robot3']};cmd_counts={r:collections.Counter() for r in status_counts}
clock_samples=collections.deque(maxlen=10000);first_sim=None;last_pose=None;travel=[0.,0.,0.];first_pose=None;max_goal_progress=None;goal=None;goal_changes=[];statuses={};last_progress=0.;last_snapshot=-1.;last_report=0.;log_counts=collections.Counter();summaries=[];matched_min=math.inf
snap_file=out.joinpath('snapshots.jsonl').open('w');event_file=out.joinpath('events.jsonl').open('w');excerpt=out.joinpath('ros_log_excerpt.log').open('w');log_path=Path('log/manual_lidar_only.log');log_offset=log_path.stat().st_size if log_path.exists() else 0

def event(kind,value):
 event_file.write(json.dumps({'elapsed':round(time.monotonic()-start,3),'sim':now,'kind':kind,'value':value},ensure_ascii=False)+'\n');event_file.flush()
def stamp(m):return m.header.stamp.sec+m.header.stamp.nanosec/1e9
def update(k,value,m=None):
 counts[k]+=1;latest[k]=value;received[k]=time.monotonic()
 if m is not None:stamps[k]=stamp(m)
def clock(m):
 global now,first_sim
 now=m.clock.sec+m.clock.nanosec/1e9
 if first_sim is None:first_sim=now
 update('clock',now);clock_samples.append((time.monotonic(),now))
def team(m):update('team',[[p.position.x,p.position.y,2*math.atan2(p.orientation.z,p.orientation.w)] for p in m.poses],m)
def people(m):update('people',[[p.position.x,p.position.y] for p in m.poses],m)
def command(m,r):
 v=[m.linear.x,m.linear.y,m.angular.z];update(r+'/cmd',v);cmd_counts[r]['total']+=1
 if math.hypot(*v[:2])>.001:cmd_counts[r]['linear_nonzero']+=1
 if abs(v[2])>.001:cmd_counts[r]['angular_nonzero']+=1
 if any(abs(x)>.001 for x in v):cmd_counts[r]['any_nonzero']+=1
def safety(m,r):
 update(r+'/safety',m.data);status_counts[r][m.data]+=1
 if statuses.get(r)!=m.data:event(r+'/safety_change',m.data);statuses[r]=m.data
def reference(m):
 rows=m.poses;v={'length':len(rows),'leader_end':([rows[-1].position.x,rows[-1].position.y] if rows else None)}
 update('reference',v,m)
def set_goal(xy,source):
 global goal
 if goal!=xy:
  goal=xy;g={'elapsed':round(time.monotonic()-start,3),'sim':now,'xy':xy,'source':source};goal_changes.append(g);event('goal',g)
def goal_cb(m):update('goal_msg',[m.pose.position.x,m.pose.position.y],m);set_goal(latest['goal_msg'],'ROS /goal_pose')
def subscribe(typ,t,fn,q=10):subs.append(n.create_subscription(typ,t,fn,q))
subscribe(Clock,'/clock',clock,qos_profile_sensor_data);subscribe(PoseArray,'/formation/robot_states',team)
subscribe(PoseArray,'/leader/people/poses',people);subscribe(PoseArray,'/formation/reference',reference,1);subscribe(PoseStamped,'/goal_pose',goal_cb)
for r in status_counts:
 subscribe(Twist,f'/{r}/cmd_vel',lambda m,r=r:command(m,r))
 subscribe(String,f'/{r}/safety_status',lambda m,r=r:safety(m,r))
 subscribe(LaserScan,f'/{r}/scan',lambda m,r=r:update(r+'/scan',{'min':min(m.ranges)},m),qos_profile_sensor_data)
subscribe(Image,'/leader/camera/image_raw',lambda m:update('rgb',{'width':m.width,'height':m.height},m),qos_profile_sensor_data)
subscribe(String,'/social_navigation/status',lambda m:update('social',m.data),1)
subscribe(String,'/social_navigation/observation_status',lambda m:update('observation',m.data),1)
initial_log=log_path.read_text(errors='replace') if log_path.exists() else ''
initial_goal=None
for line in initial_log.splitlines():
 mat=re.search(r'Setting goal pose:.*Position\(([-0-9.]+), ([-0-9.]+),',line)
 if mat:initial_goal=[float(mat[1]),float(mat[2])]
metadata=Path('docs/evidence/2026-11-01/lidar_only_trial/goal_reapply.json')
# No historical goal fallback in this audit.
if initial_goal:set_goal(initial_goal,'trial initial goal (user or unchanged reapplied goal)')

def report(elapsed,final=False):
 sim_elapsed=now-first_sim if now is not None and first_sim is not None else None
 recent=[x for x in clock_samples if time.monotonic()-x[0]<=30]
 rtf=(recent[-1][1]-recent[0][1])/(recent[-1][0]-recent[0][0]) if len(recent)>1 else None
 xy=latest.get('team');dist=math.dist(xy[2][:2],goal) if xy and len(xy)==3 and goal and len(goal)==2 else None
 s={'elapsed':round(elapsed,1),'sim':now,'sim_elapsed':sim_elapsed,'rtf_recent':rtf,'goal':goal,'leader_goal_distance':dist,'team':xy,'path_length_sampled':travel.copy(),'command_counts':{r:dict(c) for r,c in cmd_counts.items()},'safety_latest':{r:latest.get(r+'/safety') for r in status_counts},'counts':dict(counts),'log_warning_counts':dict(log_counts),'social':latest.get('social'),'observation':latest.get('observation')}
 out.joinpath('progress.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(s,ensure_ascii=False),flush=True);summaries.append(s)
 if final:
  s.update(started_vietnam=began.isoformat(),ended_vietnam=datetime.datetime.now(TZ).isoformat(),duration_wall_seconds=elapsed,first_team=first_pose,status_message_counts={r:dict(c) for r,c in status_counts.items()},goal_changes=goal_changes,min_capture_matched_camera_center_distance=None if matched_min==math.inf else matched_min,limitations=['Read-only ROS observations; no contact sensor or ground-truth collision verification','Path length is sampled XY movement with 2 mm noise threshold per 1s snapshot','Status message counts are not time percentages or independent hazard encounters','Data age and receipt age differ; camera-center distance only computed with <=0.2s capture stamp difference','No goal, command, parameter or restart action by monitor'])
  out.joinpath('summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'out_dir':str(out),'duration_requested':120,'started_vietnam':began.isoformat()}),flush=True)
while time.monotonic()-start<120:
 rclpy.spin_once(n,timeout_sec=.1);elapsed=time.monotonic()-start
 if elapsed-last_snapshot>=1:
  last_snapshot=elapsed;wall=time.monotonic();poses=latest.get('team')
  if poses and len(poses)==3:
   if first_pose is None:first_pose=[p.copy() for p in poses]
   if last_pose:
    for i in range(3):
     ds=math.dist(poses[i][:2],last_pose[i][:2])
     if ds>.002:travel[i]+=ds
   last_pose=[p.copy() for p in poses]
  if poses and len(poses)==3 and latest.get('people') and abs(stamps.get('team',-100)-stamps.get('people',-200))<=.2:
   matched_min=min(matched_min,min(math.dist(poses[2][:2],p) for p in latest['people']))
  ages={k:{'receipt_age':round(wall-t,3),'capture_age':round(now-stamps[k],3) if now is not None and k in stamps else None} for k,t in received.items()}
  snap={'elapsed':round(elapsed,3),'sim':now,'goal':goal,'latest':latest,'age':ages};snap_file.write(json.dumps(snap,ensure_ascii=False)+'\n');snap_file.flush()
  if log_path.exists():
   if log_path.stat().st_size<log_offset:log_offset=0
   with log_path.open(errors='replace') as f:f.seek(log_offset);chunk=f.read();log_offset=f.tell()
   for line in chunk.splitlines():
    if any(t in line for t in ['[WARN]','[ERROR]','Formation:','Setting goal pose:','observation ']):excerpt.write(f'[{elapsed:.3f}s] '+line+'\n')
    if 'no route for the leader' in line:log_counts['no_route']+=1
    if 'No fresh leader RGB' in line:log_counts['no_fresh_rgb']+=1
    if '[ERROR]' in line:log_counts['errors']+=1
    mat=re.search(r'Setting goal pose:.*Position\(([-0-9.]+), ([-0-9.]+),',line)
    if mat:set_goal([float(mat[1]),float(mat[2])],'RViz log')
   excerpt.flush()
 if elapsed-last_report>=30:report(elapsed);last_report=elapsed
report(time.monotonic()-start,True)
snap_file.close();event_file.close();excerpt.close();n.destroy_node();rclpy.shutdown()
