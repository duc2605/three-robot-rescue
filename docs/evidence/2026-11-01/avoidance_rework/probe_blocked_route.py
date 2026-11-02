import sys,time,json
from pathlib import Path
sys.path[:0]=[str(Path('social_navigation_planner').resolve()),str(Path('social_navigation_planner/test').resolve())]
from test_mpc_formation_motion import controller
from test_moving_obstacle_safety import empty_grid
for index in range(3):
 clock=[.4];node=controller(index,empty_grid(),clock);node.own_pose=(0.,0.,0.);node.peer_poses=[(-2.,2.,0.),(-2.,-2.,0.),(-3.,0.,0.)];node.peer_poses[index]=node.own_pose
 for t in [0.,.2,.4]:node.camera_motion.observe([(.75,0.,.32)],t)
 node.state_time=node.reference_time=.4;node.scan_wall=node.state_wall=time.monotonic();node.last_scan_stamp=.4
 rows=[]
 for k in range(9):
  row=node.peer_poses.copy();row[index]=(1.2,0.,0.);rows.append(tuple(row))
 node.reference=rows
 start=time.perf_counter();node.control_tick();print(json.dumps(dict(robot=index+1,status=node.safety_state,command=node.last_command,ms=1000*(time.perf_counter()-start))))
