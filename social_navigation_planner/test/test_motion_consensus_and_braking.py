"""Measured NK-072 regressions; replay inputs, not a fresh Gazebo result."""
import json
import math
from pathlib import Path

import pytest
from social_navigation_planner.moving_obstacles import MovingObstacle, select_lidar_tracks
from social_navigation_planner.local_escape import plan_escape
from social_navigation_planner.scan_pose_history import ScanPoseHistory
from social_navigation_planner.robot_motion import braking_pose
from test_mpc_formation_motion import controller
from test_moving_obstacle_safety import empty_grid


def test_recorded_robot2_wrong_local_direction_is_corrected_by_two_views():
    path=Path(__file__).resolve().parents[2]/'docs/evidence/2026-11-02/lidar_2m_01_audit/checkpoints.json'
    row=next(r for r in json.loads(path.read_text()) if r['robot']=='robot2' and abs(r['t']-30.)<.01)
    local=[];remote=[];sources=[]
    for o in row['tracks']:
        obj=MovingObstacle(tuple(o['position']),tuple(o['velocity']),o['radius'],o['stamp'])
        if o['source']=='lidar_2':local.append(obj)
        else:remote.append(obj);sources.append(o['source'])
    before=min(local,key=lambda o:math.dist(o.position,(1.6,-2.17)))
    assert before.velocity[1]<-.4
    fused=select_lidar_tracks(local,remote,row['t'],sources)
    after=min(fused,key=lambda o:math.dist(o.position,(1.6,-2.17)))
    assert .25<after.velocity[1]<.4


def test_duplicates_from_one_observer_are_not_two_votes():
    local=MovingObstacle((1.,0.),(0.,-.4),.4,1.)
    remote=[MovingObstacle((1.01,0.),(0.,.35),.4,1.),MovingObstacle((1.02,0.),(0.,.34),.4,1.)]
    assert select_lidar_tracks([local],remote,1.,[0,0])[0].velocity==local.velocity
    assert select_lidar_tracks([local],remote,1.,[0,2])[0].velocity[1]>.3


def test_stale_votes_cannot_override_current_measurement():
    local=MovingObstacle((1.,0.),(0.,-.4),.4,1.)
    remote=[MovingObstacle((1.,0.),(0.,.35),.4,.5)]*2
    assert select_lidar_tracks([local],remote,1.,[0,2])[0].velocity==local.velocity


def test_connector_ranks_all_checked_goals_instead_of_first_feasible():
    plan=plan_escape((0.,0.,0.),0.,.28,lambda *args:True,lambda *args:True,
                     goal_score=lambda p:p[1])
    assert plan is not None and plan.side=='right' and plan.goal[1]<-.5


def test_escape_points_can_follow_flow_normals_at_arbitrary_robot_heading():
    plan=plan_escape((0.,0.,.8),0.,.28,lambda *args:True,lambda *args:True,
                     escape_angles=[('left',math.pi/2),('right',-math.pi/2)],
                     goal_score=lambda p:-p[1])
    assert abs(plan.goal[0])<.01 and plan.goal[1]>.5


def test_pose_velocity_is_world_frame_bounded_and_expires():
    history=ScanPoseHistory()
    for t in [0.,.1,.2]:history.add(0,t,(.45*t,0.,math.pi/2))
    assert history.velocity(0,.2)==pytest.approx((.45,0.,0.))
    assert history.velocity(0,1.)==(0.,0.,0.)
    history.clear();history.add(0,0.,(0.,0.,0.));history.add(0,.1,(10.,0.,0.))
    assert history.velocity(0,.1)==(0.,0.,0.)


def moving_node(index=2):
    node=controller(index,empty_grid(),[.2]);node.state_time=.2
    node.peer_poses=[(.6,0.,0.),(-3.,3.,0.),(0.,0.,0.)]
    node.own_pose=node.peer_poses[index];node.scan_pose_history=ScanPoseHistory()
    for t in [0.,.1,.2]:
        node.scan_pose_history.add(0,t,(.69-.45*t,0.,0.))
        node.scan_pose_history.add(2,t,(.45*t,0.,0.))
    return node


def test_peer_coasting_is_checked_even_when_advertised_path_is_stationary():
    node=moving_node()
    node.peer_predictions[0]=[(.6,0.,0.)]*9;node.peer_prediction_times[0]=.2
    assert not node.peer_sweep_safe((0.,0.),(0.,0.),0,.2,1.2,.2)


def test_stop_broadcasts_braking_motion_without_issuing_motion_command():
    node=moving_node();node.own_pose=node.peer_poses[2]=(.09,0.,0.)
    node.publish_stop('fixture_brake')
    trajectory=node.poses_from(node.prediction_pub.messages[-1])
    assert node.last_command==(0.,0.,0.)
    assert trajectory[-1][0]>trajectory[0][0]+.2
    assert trajectory[-1][0]<.6


def test_braking_prediction_has_finite_stopping_distance():
    p=braking_pose((0.,0.,0.),(.45,0.,0.),10.)
    assert p==pytest.approx(braking_pose((0.,0.,0.),(.45,0.,0.),20.))
    assert p[0]==pytest.approx(.45*.3+.45**2/(2*.4))


def test_recorded_refuge_near_static_object_is_not_driven_through():
    import time
    path=Path(__file__).resolve().parents[2]/'docs/evidence/2026-11-02/nk073_motion_escape/trial01_blocked_refuge.json'
    row=json.loads(path.read_text());node=controller(0,empty_grid(),[row['t']])
    node.own_pose=tuple(row['pose']);node.peer_poses=[tuple(p) for p in row['peers']]
    node.state_time=node.last_scan_stamp=row['t']
    node.state_wall=node.scan_wall=time.monotonic()
    obstacles=[MovingObstacle(tuple(o['position']),tuple(o['velocity']),o['radius'],o['stamp'])
               for o in row['selected_lidar_tracks']]
    assert node.yield_to_moving_obstacles(row['t'],obstacles)
    assert node.guard_active,node.safety_state
    path=node.escape_full_trajectory
    # Exit transversely before stopping in the gap, not into the static disk.
    assert path[-1][0]<node.own_pose[0]-.3
    assert all(o.clearance(a,b,row['t']+k*node.mpc_dt,row['t']+(k+1)*node.mpc_dt,node.robot_radius)>=.03-1e-8
               for o in obstacles for k,(a,b) in enumerate(zip(path,path[1:])))


def test_map_supported_cluster_does_not_gain_phantom_motion_but_raw_rays_remain():
    from social_navigation_planner.grid_clearance import GridClearance
    from test_lidar_2m_avoidance import circle_scan
    grid=empty_grid();blocked=list(grid.occupied)
    # Small mapped fixture explains the centre, while some visible rays lie
    # outside its occupied cells, as in the measured standing-object case.
    for y in range(grid.height):
        for x in range(grid.width):
            wx=-6.+(x+.5)*.05;wy=-6.+(y+.5)*.05
            if math.hypot(wx-1.,wy)<.08:blocked[y*grid.width+x]=True
    grid=GridClearance(grid.width,grid.height,.05,(-6.,-6.,0.),blocked,.15)
    clock=[.4];node=controller(2,grid,clock)
    node.own_pose=(0.,0.,0.);node.peer_poses=[(-3.,3.,0.),(-3.,-3.,0.),node.own_pose]
    node.state_time=.4;node.last_scan_stamp=-math.inf
    node.scan_callback(circle_scan(node.own_pose,(1.,0.),.4))
    assert node.scan_points,'map cluster filtering must not erase local raw obstacle rays'
    assert node.lidar_motion.recent(.4)==[]
    assert node.stationary_scan_points(.4,[])


def test_coherent_recent_turn_does_not_wait_for_the_long_window():
    from social_navigation_planner.moving_obstacles import MotionTracks
    tracks=MotionTracks()
    for k in range(7):tracks.observe([(1.,0.,.32)],k*.1)
    tracks.observe([(.96,0.,.32)],.7);tracks.observe([(.92,0.,.32)],.8)
    assert tracks.recent(.8)[0].velocity[0]<-.3


def test_recently_moving_object_has_bounded_pause_reserve_and_then_expires():
    from social_navigation_planner.moving_obstacles import MotionTracks
    tracks=MotionTracks(padding=.02,pause_reserve=True)
    for k in range(5):tracks.observe([(.35*k*.1,0.,.32)],k*.1)
    for k in range(5,16):tracks.observe([(.14,0.,.32)],k*.1)
    assert tracks.recent(1.5)[0].radius>.54
    for k in range(16,41):tracks.observe([(.14,0.,.32)],k*.1)
    assert tracks.recent(4.)[0].radius==pytest.approx(.34)


def test_committed_escape_is_revalidated_before_budget_starves_its_direction(monkeypatch):
    from types import SimpleNamespace
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader();node.peer_poses=[(0.,.7,0.),(-.7,.7,0.),node.own_pose]
    node.escape_heading=-math.pi/2;node.escape_flow_angle=math.pi
    node.escape_commit_until=clock[0]+1.25;node.escape_plan_time=clock[0]
    objects=[MovingObstacle((1.3,0.),(-.4,0.),.32,clock[0])]
    budget=[100.]
    def perf():budget[0]+=.001;return budget[0]
    monkeypatch.setattr('social_navigation_planner.dstar_mpc_controller.time.perf_counter',perf)
    assert node.yield_to_moving_obstacles(clock[0],objects)
    assert node.guard_active
    assert node.last_command[1]<-.01
    # A newly blocked map must invalidate the warm direction; never replay it.
    node.physical_grid=SimpleNamespace(segment_clearance=lambda *args:0.)
    assert node.yield_to_moving_obstacles(clock[0],objects)
    assert node.last_command==(0.,0.,0.)


def test_refuge_remains_in_world_coordinates_as_robot_approaches():
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader()
    obstacles=[MovingObstacle((1.2,0.),(-.35,0.),.32,clock[0])]
    node.yield_to_moving_obstacles(clock[0],obstacles)
    assert node.guard_active
    goal=node.refuge_goal
    node.own_pose=(node.own_pose[0]+.08*math.cos(node.escape_heading),
                   node.own_pose[1]+.08*math.sin(node.escape_heading),0.)
    node.peer_poses[node.robot_index]=node.own_pose
    node.yield_to_moving_obstacles(clock[0],obstacles)
    assert node.guard_active
    assert node.refuge_goal==pytest.approx(goal)
    assert node.selected_escape_stops


def test_safe_refuge_waits_for_approaching_flow_then_releases_without_changing_reference():
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader();node.refuge_goal=(0.,0.);node.refuge_expires=clock[0]+3.
    reference=node.reference.copy();node.moving_pause_until=-math.inf
    incoming=MovingObstacle((1.2,1.),(0.,-.4),.32,clock[0])
    assert node.yield_to_moving_obstacles(clock[0],[incoming])
    assert node.last_command==(0.,0.,0.)
    assert 'waiting' in node.safety_state
    away=MovingObstacle((1.2,1.),(0.,.4),.32,clock[0])
    assert not node.yield_to_moving_obstacles(clock[0],[away])
    assert node.reference==reference


def test_buffer_recovery_cannot_cut_inside_physical_body_floor():
    from social_navigation_planner.moving_obstacles import escape_motion_free
    o=MovingObstacle((.6,0.),(-.35,0.),.45,0.)
    # This improves on holding but still passes too close to the body.
    assert not escape_motion_free(o,(0.,0.),(0.,.04),0.,.4,.15)
    assert escape_motion_free(o,(0.,0.),(-.1,.1),0.,.4,.15)
