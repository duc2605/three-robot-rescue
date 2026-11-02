"""Regressions for a scripted pedestrian walking into a stopped leader.

Uses measured-observation inputs and production MPC with kinematic feedback;
no Gazebo, network publishers, authored human timeline, or real robot commands.
"""
import math
import time

import pytest

from social_navigation_planner.moving_obstacles import MotionTracks, scan_clusters
from social_navigation_planner.grid_clearance import GridClearance
from social_navigation_planner.adaptive_structure import swept_separation

pytest.importorskip('rclpy')
from geometry_msgs.msg import PoseArray
from sensor_msgs.msg import LaserScan
from test_mpc_formation_motion import controller


def empty_grid():
    return GridClearance(240, 240, .05, (-6., -6., 0.), [False]*(240*240), .15)


def measured_person(node, now, xy):
    node.camera_motion.observe([(*xy,.32)],now)
    node.state_time = now
    node.state_wall = node.scan_wall = time.monotonic()
    node.last_scan_time = now
    node.last_scan_stamp = now


def stopped_leader():
    clock = [.4]
    node = controller(2,empty_grid(),clock)
    node.own_pose = (0.,0.,0.)
    node.peer_poses = [(-2.,2.,0.),(-2.,-2.,0.),node.own_pose]
    for t in [0.,.2,.4]:measured_person(node,t,(1.3-.35*t,0.))
    return node,clock


def test_three_captures_estimate_motion_but_duplicate_stamps_do_not():
    tracks = MotionTracks()
    tracks.observe([(1.,0.,.32)],0.)
    tracks.observe([(.93,0.,.32)],.2)
    assert tracks.recent(.2)[0].velocity == (0.,0.)
    tracks.observe([(.86,0.,.32)],.4)
    assert tracks.recent(.4)[0].velocity == pytest.approx((-.35,0.))
    tracks.observe([(10.,10.,.32)],.4)
    tracks.observe([(10.,10.,.32)],.3)
    assert len(tracks.recent(.4)) == 1
    assert tracks.recent(.4)[0].position == (.86,0.)


def test_tracks_expire_and_do_not_extrapolate_forever():
    tracks = MotionTracks()
    for t in [0.,.2,.4]:tracks.observe([(.35*t,0.,.32)],t)
    obstacle = tracks.recent(.4)[0]
    assert obstacle.at(1.) == pytest.approx((.35,0.))
    assert tracks.recent(1.21) == []


def test_noise_teleport_and_nonfinite_points_do_not_create_fast_motion():
    tracks = MotionTracks()
    for t,x in [(0.,0.),(.2,.005),(.4,-.005)]:tracks.observe([(x,0.,.32)],t)
    assert tracks.recent(.4)[0].velocity == (0.,0.)
    tracks.observe([(3.,0.,.32),(float('nan'),0.,.32)],.5)
    assert all(o.velocity == (0.,0.) for o in tracks.recent(.5))


def test_association_does_not_merge_two_people_when_order_reverses():
    tracks = MotionTracks()
    for i in range(4):
        t=i*.2;points=[(.35*t,0.,.32),(.8-.35*t,1.,.32)]
        tracks.observe(points if i%2 else points[::-1],t)
    people=sorted(tracks.recent(.6),key=lambda o:o.position[1])
    assert len(people)==2
    assert people[0].velocity[0] == pytest.approx(.35)
    assert people[1].velocity[0] == pytest.approx(-.35)


def test_lidar_clusters_keep_sparse_person_surface_but_reject_wide_wall():
    points=[(.9,-.05),(.9,0.),(.9,.05),(2.,0.),(3.,0.),(3.,.15),(3.,.3),
            (3.,.45),(3.,.6),(3.,.75),(3.,.9),(3.,1.05)]
    groups=scan_clusters(points)
    assert len(groups)==2
    assert groups[0][:2] == pytest.approx((.9,0.))
    assert groups[1][:2] == pytest.approx((2.,0.))


def test_stopped_leader_avoids_incoming_person_without_a_global_reference():
    node,clock=stopped_leader()
    node.reference=[]
    moved=False;minimum=math.inf
    for k in range(80):
        now=.4+k*.1;clock[0]=now
        person=(1.3-.35*now,0.)
        measured_person(node,now,person)
        before=node.own_pose
        node.peer_poses[2]=before
        node.control_tick()
        vx,vy,spin=node.last_command
        mid=before[2]+spin*.05
        after=(before[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),
               before[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),before[2]+.1*spin)
        next_person=(person[0]-.035,0.)
        separation=swept_separation(before,after,person,next_person)
        minimum=min(minimum,separation)
        assert separation > .47, (now,separation,node.safety_state)
        assert node.physical_grid.segment_free(before,after)
        assert all(math.dist(after[:2],p[:2])>.32 for p in node.peer_poses[:2])
        moved |= math.dist(before[:2],after[:2])>.001
        node.own_pose=after
    assert moved
    assert minimum>.47


def test_empty_reference_does_not_cancel_fresh_verified_yield():
    node,clock=stopped_leader();node.control_tick()
    assert node.guard_active and math.hypot(*node.last_command[:2])>0
    before=node.last_command
    msg=PoseArray();msg.header.frame_id='map'
    node.reference_callback(msg)
    assert node.last_command==before
    node.watchdog()
    assert node.last_command==before


@pytest.mark.parametrize('missing', ['scan','state','map','disabled','coverage'])
def test_guard_never_moves_with_stale_data_or_disabled_motion(missing):
    node,clock=stopped_leader()
    if missing=='scan':node.scan_wall=time.monotonic()-3
    if missing=='state':node.state_wall=time.monotonic()-3
    if missing=='map':node.physical_grid=None
    if missing=='disabled':node.motion_enabled=False
    if missing=='coverage':node.scan_coverage_ok=False
    node.control_tick()
    assert node.last_command==(0.,0.,0.)


def test_no_safe_escape_preserves_wall_constraints():
    node,clock=stopped_leader()
    node.physical_grid=GridClearance(40,40,.05,(-1.,-1.,0.),[True]*1600,.15)
    node.control_tick()
    assert node.last_command==(0.,0.,0.)
    assert 'no verified safe escape' in node.safety_state


def test_camera_data_requires_map_frame_and_recent_stamp():
    node,clock=stopped_leader();node.camera_motion.clear()
    for frame,stamp in [('camera',.4),('map',-1.),('map',2.)]:
        msg=PoseArray();msg.header.frame_id=frame
        msg.header.stamp.sec=int(stamp);msg.header.stamp.nanosec=int((stamp-int(stamp))*1e9)
        node.people_callback(msg)
    assert node.camera_motion.recent(.4)==[]


def test_clock_rewind_clears_forecasts_and_holds():
    node,clock=stopped_leader();node.last_control_time=2.
    node.control_tick()
    assert not node.camera_motion.recent(.4)
    assert node.last_command==(0.,0.,0.)


def test_watchdog_stops_yield_when_sensor_or_state_goes_stale():
    node,clock=stopped_leader();node.control_tick()
    assert node.guard_active
    node.scan_wall=time.monotonic()-3
    node.reference_wall=time.monotonic()  # A fresh plan must not mask a stale safety sensor.
    node.watchdog()
    assert node.last_command==(0.,0.,0.)


def test_lidar_motion_alone_can_trigger_checked_yield():
    node,clock=stopped_leader();node.camera_motion.clear()
    for t in [0.,.2,.4]:
        node.lidar_motion.observe(scan_clusters([(1.1-.35*t,y) for y in [-.04,0.,.04]]),t)
    node.control_tick()
    assert node.guard_active
    assert math.hypot(*node.last_command[:2])>0


def test_swept_check_catches_person_crossing_between_prediction_endpoints():
    tracks=MotionTracks()
    for t in [0.,.2,.4]:tracks.observe([(-.6+t,0.,.32)],t)
    obstacle=tracks.recent(.4)[0]
    # At both endpoints the obstacle is separated; halfway it meets the robot.
    assert obstacle.clearance((0.,-.7),(0.,.7),.4,.8,.15)<0


def test_empty_and_stationary_tracks_leave_missing_reference_stopped():
    node,clock=stopped_leader();node.camera_motion.clear()
    for t in [0.,.2,.4]:node.camera_motion.observe([(1.,0.,.32)],t)
    node.control_tick()
    assert not node.guard_active
    assert node.last_command==(0.,0.,0.)


def test_reference_tracking_also_checks_temporally_crossing_person():
    node,clock=stopped_leader()
    node.reference=[[(*p,) for p in node.peer_poses] for _ in range(node.mpc_horizon+1)]
    node.reference_time=.4
    node.control_tick()
    assert node.guard_active and math.hypot(*node.last_command[:2])>0


def test_social_keepout_does_not_hide_moving_lidar_return():
    node,clock=stopped_leader();node.camera_motion.clear()
    # The physical map is clear, but the social map forecasts occupied space.
    node.hard_collision_grid=GridClearance(240,240,.05,(-6.,-6.,0.),[True]*(240*240),.15)
    node.last_scan_time=node.last_scan_stamp=-math.inf
    scan=LaserScan();scan.header.stamp.nanosec=400000000
    scan.range_min=.05;scan.range_max=10.;scan.ranges=[1.];scan.angle_increment=.1
    node.scan_callback(scan)
    assert node.scan_points, 'Social keepout must not filter out the person from raw LiDAR tracking'
    assert not node.scan_coverage_ok, 'A one-ray scan cannot authorize emergency movement'


def test_peer_at_candidate_escape_side_is_not_collided_with():
    node,clock=stopped_leader()
    node.peer_poses[0]=(0.,.55,0.)
    node.control_tick()
    assert node.guard_active
    predicted=node.poses_from(node.prediction_pub.messages[-1])
    assert all(math.dist(p[:2],node.peer_poses[0][:2])>=.42 for p in predicted)


def test_replayed_scan_cannot_refresh_its_wall_time():
    node,clock=stopped_leader();node.last_scan_time=node.last_scan_stamp=-math.inf
    scan=LaserScan();scan.header.stamp.nanosec=400000000
    scan.range_min=.05;scan.range_max=10.;scan.angle_increment=2*math.pi/239
    scan.ranges=[math.inf]*240
    node.scan_callback(scan)
    first=node.scan_wall
    clock[0]=.6;node.state_time=.6
    node.scan_callback(scan)
    assert node.scan_wall==first
    assert node.last_scan_stamp==pytest.approx(.4)


def sparse_scan(observer, point, stamp):
    scan=LaserScan();scan.header.frame_id='map'
    scan.header.stamp.sec=int(stamp)
    scan.header.stamp.nanosec=round((stamp-int(stamp))*1e9)
    scan.range_min=.08;scan.range_max=10.
    scan.angle_min=-math.pi;scan.angle_increment=2*math.pi/239
    scan.ranges=[math.inf]*240
    angle=(math.atan2(point[1]-observer[1],point[0]-observer[0])-observer[2]+math.pi)%(2*math.pi)-math.pi
    beam=round((angle+math.pi)/scan.angle_increment)
    scan.ranges[beam]=math.dist(observer[:2],point)
    return scan


@pytest.mark.parametrize('index', [0,1])
def test_each_follower_yields_from_peer_sparse_scan_with_camera_occluded(index):
    node,clock=stopped_leader();node.camera_motion.clear()
    node.robot_index=index
    node.team_lidar_motion=[MotionTracks() for _ in range(3)]
    node.lidar_motion=node.team_lidar_motion[index]
    node.own_pose=(0.,0.,0.)
    node.peer_poses=[(-2.,2.,0.),(-2.,-2.,0.),(-.6,0.,0.)]
    node.peer_poses[index]=node.own_pose
    # One leg return, seen only by a different robot. It does not refresh
    # the local 360-degree clearance scan needed to authorize an escape.
    for t in [0.,.2,.4,.6]:
        clock[0]=node.state_time=t
        node.peer_scan_callback(sparse_scan(node.peer_poses[2],(1.3-.35*t,0.),t),2)
    node.state_wall=node.scan_wall=time.monotonic()
    node.last_scan_stamp=.6
    node.control_tick()
    assert node.guard_active, node.safety_state
    assert math.hypot(*node.last_command[:2])>0
    assert 'band=slow' in node.safety_state
    node.scan_wall=time.monotonic()-3
    node.control_tick()
    assert node.last_command==(0.,0.,0.), 'Peer sighting must not replace the local clearance scan'


def test_confirmed_moving_return_is_not_also_frozen_across_escape_rollout():
    node,clock=stopped_leader()
    moving=node.camera_motion.recent(.4)
    node.scan_points=[(*moving[0].position,1.),(0.,1.5,1.)]
    assert node.stationary_scan_points(.4,moving)==[(0.,1.5)]
    assert len(node.stationary_scan_points(.4,[]))==2


def test_odd_lidar_beam_is_retained_for_leg_tracking():
    node,clock=stopped_leader();node.camera_motion.clear()
    node.last_scan_time=node.last_scan_stamp=-math.inf
    scan=sparse_scan(node.own_pose,(1.,0.),.4)
    scan.ranges=[math.inf]*240;scan.ranges[121]=1.
    node.scan_callback(scan)
    assert len(node.scan_points)==1
    assert len(node.lidar_motion.recent(.4))==1
    assert node.lidar_motion.recent(.4)[0].velocity==(0.,0.)


def test_follower_escapes_before_logged_contact_geometry_with_nearby_teammates():
    # Relative geometry captured at sim 26.483 s. Start observations 2.483 s
    # earlier, before overlap. This is kinematic feedback, not Gazebo replay.
    poses=[(2.1862476905,-2.2141150693,-3.0599277976),
           (1.6761732659,-2.7598619302,-1.9778582797),
           (1.6602096178,-3.3345621152,-.7859522957)]
    clock=[0.];node=controller(1,empty_grid(),clock)
    node.own_pose=poses[1];node.peer_poses=poses.copy()
    minimum=math.inf;moved=False
    for k in range(65):
        now=k*.1;clock[0]=now
        person=(1.3926288352+.35*(now-2.483),-2.5)
        measured_person(node,now,person);node.peer_poses[1]=node.own_pose
        before=node.own_pose;node.control_tick()
        vx,vy,spin=node.last_command;mid=before[2]+spin*.05
        after=(before[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),
               before[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),before[2]+.1*spin)
        minimum=min(minimum,swept_separation(before,after,person,(person[0]+.035,person[1])))
        assert minimum>.47, (now,minimum,node.safety_state)
        assert all(math.dist(after[:2],poses[i][:2])>.32 for i in [0,2])
        moved |= math.dist(before[:2],after[:2])>.001
        node.own_pose=after
    assert moved
    print(f'Logged follower geometry, kinematic minimum centre separation: {minimum:.3f} m')
