"""Read recorded inputs around rightward body commands overlapping follower yield."""
from pathlib import Path
import json,math,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[4]
source=root/'log/sessions/20261101_192255_199210'
out=Path(__file__).resolve().parent
rows=[json.loads(line) for line in (source/'events.jsonl').read_text().splitlines()]
scans=[json.loads(line) for line in (source/'scans.jsonl').read_text().splitlines()]
def wall(row):return datetime.datetime.fromisoformat(row['wall_time_utc']).timestamp()
def last(kind,t):return [r for r in rows if r['kind']==kind and wall(r)<=t][-1]
def bounds(scan,lo,hi):
 points=[{'range_m':r,'body_angle_deg':math.degrees(scan['angle_min']+i*scan['angle_increment'])}
         for i,r in enumerate(scan['ranges']) if r is not None]
 hits=[p for p in points if lo<=p['body_angle_deg']<=hi]
 return {'finite_hits':len(hits),'nearest':min(hits,key=lambda p:p['range_m']) if hits else None}
times=['2026-11-01T12:26:08.400087+00:00','2026-11-01T12:27:23.470203+00:00','2026-11-01T12:29:29.533416+00:00']
results=[];chosen_events={};chosen_scans={}
fig,axes=plt.subplots(1,3,figsize=(15,6),layout='constrained')
for ax,when in zip(axes,times):
 cmd=next(r for r in rows if r['kind']=='/robot3/cmd_vel' and r['wall_time_utc']==when)
 t=wall(cmd);team=last('/formation/robot_states',t)
 scan=[r for r in scans if r['topic']=='/robot3/scan' and wall(r)<=t][-1]
 camera=last('/leader/people/poses',t)
 near_status=min([r for r in rows if r['kind']=='/robot3/safety_status'],key=lambda r:abs(wall(r)-t))
 x,y,yaw=team['value'][2];people=[]
 for p in camera['value']:
  dx,dy=p[0]-x,p[1]-y
  bx,by=math.cos(yaw)*dx+math.sin(yaw)*dy,-math.sin(yaw)*dx+math.cos(yaw)*dy
  people.append({'world_xy':p[:2],'body_xy':[bx,by],'range_m':math.hypot(bx,by),'angle_deg':math.degrees(math.atan2(by,bx))})
 direction=math.degrees(math.atan2(cmd['value'][1],cmd['value'][0]))
 followers={name:last(f'/{name}/safety_status',t) for name in ['robot1','robot2']}
 measured=[r for r in scan['ranges'] if r is not None]
 result={'wall_vietnam':datetime.datetime.fromisoformat(when).astimezone(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
         'sim_estimate':cmd['sim_estimate'],'command_body_vx_vy_omega':cmd['value'],'command_body_angle_deg':direction,
         'leader_world_pose':team['value'][2],'pose_capture_stamp':team['capture_stamp'],
         'scan_capture_stamp':scan['capture_stamp'],'scan_frame':scan['frame'],
         'scan_receipt_before_command_wall_s':t-wall(scan),'scan_capture_age_vs_pose_estimate_s':cmd['sim_estimate']-scan['capture_stamp'],
         'scan_rays':len(scan['ranges']),'finite_rays':len(measured),'range_min_m':min(measured),'range_max_m':max(measured),
         'sectors':{name:bounds(scan,lo,hi) for name,lo,hi in [('front',-45,45),('right',-135,-45),('left',45,135),('command_cone',direction-15,direction+15)]},
         'camera_people':people,'camera_capture_stamp':camera['capture_stamp'],
         'camera_receipt_before_command_wall_s':t-wall(camera),
         'leader_nearest_safety_status':near_status['value'],'status_wall_offset_from_command_s':wall(near_status)-t,
         'followers':{name:{'status':r['value'],'status_receipt_age_wall_s':t-wall(r)} for name,r in followers.items()}}
 results.append(result)
 for r in [cmd,team,camera,near_status,*followers.values()]:chosen_events[(r['kind'],r['wall_time_utc'])]=r
 chosen_scans[(scan['topic'],scan['wall_time_utc'])]=scan
 for r in rows:
  if abs(wall(r)-t)<=2:chosen_events[(r['kind'],r['wall_time_utc'])]=r
 points=[(i,r) for i,r in enumerate(scan['ranges']) if r is not None and r<=3.5]
 ax.scatter([-r*math.sin(scan['angle_min']+i*scan['angle_increment']) for i,r in points],
            [r*math.cos(scan['angle_min']+i*scan['angle_increment']) for i,r in points],s=10,c='gray',label='LiDAR return')
 visible=[p for p in people if p['range_m']<=3.5]
 ax.scatter([-p['body_xy'][1] for p in visible],[p['body_xy'][0] for p in visible],s=90,c='orange',marker='x',label='Camera person candidate')
 for p in visible:ax.annotate(f"{p['range_m']:.2f}m",(-p['body_xy'][1],p['body_xy'][0]),xytext=(5,5),textcoords='offset points')
 speed=math.hypot(*cmd['value'][:2]);vx,vy=cmd['value'][:2]
 ax.arrow(0,0,-vy/speed*.8,vx/speed*.8,width=.025,head_width=.15,color='red',length_includes_head=True,label='Command direction')
 ax.add_patch(plt.Circle((0,0),.15,fill=False,color='blue'))
 ax.axhline(0,c='lightgray',lw=.5);ax.axvline(0,c='lightgray',lw=.5)
 ax.set(xlim=(-3.5,3.5),ylim=(-3.5,3.5),aspect='equal',xlabel='Left (-) / Right (+), m',ylabel='Back (-) / Front (+), m',
        title=f"{result['wall_vietnam'][11:19]} | sim ~{cmd['sim_estimate']:.3f}s\nscan stamp {scan['capture_stamp']:.3f}s")
 ax.grid(alpha=.2)
axes[0].legend(loc='lower left',fontsize=8)
fig.suptitle('Robot-body frame: received LiDAR + camera; red = command, not executed trajectory\nMissing LiDAR returns do not prove free space. Camera candidates use latest preceding team pose.',fontsize=11)
fig.savefig(out/'body_frame_comparison.png',dpi=150)
limits=['Multiple matching episodes; user identified follower avoidance, not a unique timestamp.',
        'Recorded subscriber receipt/capture stamps are not proof of exact scan consumed by MPC.',
        'Camera points are measured person candidates, without saved identity or pixels; cannot identify which person user saw.',
        'No-return rays are not free-space evidence. LaserScan ranges are projected horizontal distances, height-filtered 0.025..0.40m.',
        'Right means negative body y, not necessarily right in Gazebo/RViz camera view.']
(out/'analysis.json').write_text(json.dumps({'source_session':str(source.relative_to(root)),'episodes':results,'limits':limits},ensure_ascii=False,indent=2)+'\n')
(out/'selected_events.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sorted(chosen_events.values(),key=wall)))
(out/'selected_scans.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in chosen_scans.values()))
print(json.dumps([{'time':r['wall_vietnam'],'sim':r['sim_estimate'],'right':r['sectors']['right'],'scan_age_sim':r['scan_capture_age_vs_pose_estimate_s'],'scan_age_wall':r['scan_receipt_before_command_wall_s'],'camera':r['camera_people'],'status':r['leader_nearest_safety_status']} for r in results],ensure_ascii=False))
