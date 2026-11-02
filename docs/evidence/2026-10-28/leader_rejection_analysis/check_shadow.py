import sys,time,json,math,inspect,textwrap,types,collections,ast
from pathlib import Path
sys.path[:0]=['social_navigation_planner','social_navigation_planner/test']
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy,qos_profile_sensor_data
from geometry_msgs.msg import PoseArray
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from rosgraph_msgs.msg import Clock
import social_navigation_planner.dstar_mpc_controller as module
from social_navigation_planner.grid_clearance import GridClearance
from test_mpc_formation_motion import controller
clock=[0.];empty=GridClearance(1,1,1.,(0.,0.,0.),[False],.15)
nodes=[controller(i,empty,clock) for i in range(3)]
for node in nodes:node.robot_name=f'robot{node.robot_index+1}';node.own_pose=None;node.peer_poses=[None]*3;node.physical_grid=None;node.occupied_threshold=50;node.unknown_is_obstacle=True
current_risk=module.collision_risk
# The current process predates the stationary-close extension. Geometry
# rollout is unchanged; use its moving-only trigger for this shadow replay.
namespace=dict(module.__dict__)
namespace['collision_risk']=lambda o,*args:current_risk(o,*args) if math.hypot(*o.velocity)>=.05 else None
counts={};examples=[]
def reject(node,data):
 a=(data['x'],data['y']);b=data['after'];start,end=data['start'],data['end'];reasons=[]
 physical=node.physical_grid.segment_clearance(a,b,node.inflation_radius)
 laser=min((module.swept_separation(a,b,p,p) for p in data['laser']),default=math.inf)
 peers=all(module.peer_motion_free(a,b,node.peer_at(i,start,clock[0]),node.peer_at(i,end,clock[0]),preferred=.42) for i in data['peers'])
 if physical<node.inflation_radius-1e-9:reasons.append('physical_map')
 if laser<node.robot_radius+.03:reasons.append('raw_lidar')
 if any(g<.03 for g in data['gaps']):reasons.append('tracked_obstacle')
 if not peers:reasons.append('peer')
 counts.update({r:counts.get(r,0)+1 for r in reasons})
 if len(examples)<2:
  examples.append({'step':data['k'],'reasons':reasons,'physical_clearance':physical,'raw_lidar_distance':laser,'track_gaps':data['gaps'],'before':a,'after':b})
namespace['record_reject']=reject
source=textwrap.dedent(inspect.getsource(module.DistributedRobotMPC.yield_to_moving_obstacles))
source=source.replace('                        break','                        record_reject(self, locals())\n                        break')
class GuardInstrument(ast.NodeTransformer):
 def visit_Break(self,node):
  return [ast.parse('record_reject(self, locals())').body[0],node]
exec(compile(ast.fix_missing_locations(GuardInstrument().visit(ast.parse(source))),'<shadow_guard>','exec'),namespace)
for node in nodes:node.yield_to_moving_obstacles=types.MethodType(namespace['yield_to_moving_obstacles'],node)
def normal_reject(reason,node,data):
 counts[reason]=counts.get(reason,0)+1
 if len(examples)<2:
  examples.append({'step':data.get('step'),'reason':reason,'before':data.get('before'),'after':data.get('after'),'minimum_clearance':data.get('minimum_clearance'),'track_gaps':[o.clearance(data['before'],data['after'],clock[0]+(data['step']-1)*node.mpc_dt,clock[0]+data['step']*node.mpc_dt,node.robot_radius) for o in data.get('moving',[])]})
namespace['normal_reject']=normal_reject
class Instrument(ast.NodeTransformer):
 def visit_If(self,node):
  self.generic_visit(node)
  if not node.body or not isinstance(node.body[-1],ast.Continue):return node
  expr=ast.unparse(node.test);reason=None
  if 'self.segment_free' in expr:reason='normal_planning_map'
  elif 'swept_separation' in expr:reason='normal_raw_lidar'
  elif 'o.clearance' in expr:reason='normal_tracked_obstacle'
  elif 'peer_motion_free' in expr:reason='normal_peer'
  if reason:
   call=ast.parse('normal_reject('+repr(reason)+', self, locals())').body[0]
   node.body.insert(-1,call)
  return node
code=Instrument().visit(ast.parse(textwrap.dedent(inspect.getsource(module.DistributedRobotMPC.control_tick))))
exec(compile(ast.fix_missing_locations(code),'<shadow_mpc>','exec'),namespace)
for node in nodes:node.control_tick=types.MethodType(namespace['control_tick'],node)

rclpy.init();reader=Node('read_only_guard_rejection_shadow');subs=[];events=[]
def stamp(m):return m.header.stamp.sec+m.header.stamp.nanosec/1e9
def team(m):
 if len(m.poses)==3:
  poses=[(p.position.x,p.position.y,module.quaternion_yaw(p.orientation)) for p in m.poses]
  for node in nodes:node.own_pose=poses[node.robot_index];node.peer_poses=poses.copy();node.state_time=stamp(m);node.state_wall=time.monotonic()
def physical(m):
 for node in nodes:node.physical_map_callback(m)
def scan(m,i):
 for node in nodes:
  if node.own_pose is None:continue
  if node.robot_index==i:node.scan_callback(m)
  else:node.peer_scan_callback(m,i)
def people(m):
 for node in nodes:node.people_callback(m)
q=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
subs.append(reader.create_subscription(OccupancyGrid,'/map',physical,q))
def planning(m):
 for node in nodes:node.map_callback(m)
def reference(m):
 for node in nodes:node.reference_callback(m)
subs.append(reader.create_subscription(OccupancyGrid,'/social_navigation/map',planning,q))
subs.append(reader.create_subscription(PoseArray,'/formation/reference',reference,1))
for index in range(3):
 def prediction(m,i=index):
  for node in nodes:
   if node.robot_index!=i:node.prediction_callback(m,i)
 subs.append(reader.create_subscription(PoseArray,f'/robot{index+1}/mpc_prediction',prediction,1))
subs.append(reader.create_subscription(Clock,'/clock',lambda m:clock.__setitem__(0,m.clock.sec+m.clock.nanosec/1e9),qos_profile_sensor_data))
subs.append(reader.create_subscription(PoseArray,'/formation/robot_states',team,10))
subs.append(reader.create_subscription(PoseArray,'/leader/people/poses',people,1))
for i in range(3):subs.append(reader.create_subscription(LaserScan,f'/robot{i+1}/scan',lambda m,i=i:scan(m,i),qos_profile_sensor_data))
start=time.monotonic();last=0
while time.monotonic()-start<14:
 rclpy.spin_once(reader,timeout_sec=.05)
 elapsed=time.monotonic()-start
 if elapsed-last<1 or elapsed<4:continue
 last=elapsed
 for node in nodes:
  if node.own_pose is None or node.physical_grid is None:continue
  moving=node.camera_motion.recent(clock[0])+[o for t in node.team_lidar_motion for o in t.recent(clock[0])]
  counts={};examples=[]
  node.control_tick()
  events.append({'robot':node.robot_name,'sim':clock[0],'wall':elapsed,'pose':node.own_pose,'status':node.safety_state,'command':node.last_command,'rejections':dict(counts),'examples':examples,'scan_age':clock[0]-node.last_scan_stamp,'scan_wall_age':time.monotonic()-node.scan_wall,'tracks':[{'position':o.position,'velocity':o.velocity,'radius':o.radius,'stamp':o.stamp,'initial_gap':o.clearance(node.own_pose,node.own_pose,clock[0],clock[0],node.robot_radius)} for o in moving]})
result={'note':'Read-only shadow replay of measured topics; Capture publishers only. Moving-only trigger emulates old running version. Shadow histories/predictions can differ from internal process; this is not live rejection telemetry.','events':events}
Path('log/guard_rejection_shadow.json').write_text(json.dumps(result,indent=2)+'\n')
for name in ['robot1','robot2','robot3']:
 rr=[r for r in events if r['robot']==name];counter=collections.Counter()
 for r in rr:counter.update(r['rejections'])
 print(json.dumps({'robot':name,'samples':len(rr),'status_counts':dict(collections.Counter(r['status'] for r in rr)),'rejections':dict(counter),'last':rr[-1] if rr else None}))
reader.destroy_node();rclpy.shutdown()
