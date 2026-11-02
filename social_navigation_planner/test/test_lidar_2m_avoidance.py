"""2m raw ray observations + production control; kinematic, not Gazebo proof."""
import math
import time
import pytest
from sensor_msgs.msg import LaserScan
from social_navigation_planner.moving_obstacles import MovingObstacle, escape_motion_free
from social_navigation_planner.adaptive_structure import swept_separation
from test_mpc_formation_motion import controller
from test_moving_obstacle_safety import empty_grid


def circle_scan(observer,person,stamp):
    msg=LaserScan();msg.header.frame_id='base_link'
    msg.header.stamp.sec=int(stamp);msg.header.stamp.nanosec=round((stamp-int(stamp))*1e9)
    msg.angle_min=-math.pi;msg.angle_increment=2*math.pi/239
    msg.angle_max=math.pi;msg.range_min=.08;msg.range_max=2.
    msg.ranges=[]
    cx,cy=person[0]-observer[0],person[1]-observer[1]
    for i in range(240):
        a=observer[2]+msg.angle_min+i*msg.angle_increment
        projection=cx*math.cos(a)+cy*math.sin(a)
        disc=projection*projection-(cx*cx+cy*cy-.3*.3)
        distance=projection-math.sqrt(disc) if disc>=0 else math.inf
        msg.ranges.append(distance if .08<=distance<2. else math.inf)
    return msg


def lidar_node(index,clock,poses):
    node=controller(index,empty_grid(),clock)
    node.avoidance_use_camera=False
    for tracks in node.team_lidar_motion: tracks.padding=.02; tracks.persistence=.4; tracks.pause_reserve=True
    node.robot_name=f'robot{index+1}'
    node.own_pose=poses[index];node.peer_poses=poses.copy()
    node.last_scan_stamp=-math.inf
    return node


@pytest.mark.parametrize('index',[0,1,2])
@pytest.mark.parametrize('speed',[.15,.35,.8])
def test_each_robot_avoids_from_2m_rays_without_camera_or_reference(index,speed):
    clock=[0.];poses=[(-3.,3.,0.),(-3.,-3.,0.),(-3.,0.,0.)];poses[index]=(0.,0.,0.)
    node=lidar_node(index,clock,poses);minimum=math.inf;moved=False
    duration=1.9/speed+2.
    for k in range(math.ceil(duration/.1)):
        now=k*.1;clock[0]=now;person=(1.9-speed*now,0.)
        node.state_time=now;node.state_wall=time.monotonic();node.peer_poses[index]=node.own_pose
        node.scan_callback(circle_scan(node.own_pose,person,now))
        before=node.own_pose;node.control_tick()
        vx,vy,spin=node.last_command
        assert math.hypot(vx,vy)<=node.max_linear_speed+1e-9
        mid=before[2]+spin*.05
        after=(before[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),
               before[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),before[2]+.1*spin)
        separation=swept_separation(before,after,person,(person[0]-.1*speed,0.))
        minimum=min(minimum,separation)
        assert separation>.45,(index,speed,now,separation,node.safety_state)
        moved |= math.dist(before[:2],after[:2])>.001
        node.own_pose=after
    assert moved
    assert not node.camera_motion.recent(clock[0])


def test_recovery_leaves_overlapping_buffer_but_rejects_toward_or_crossing():
    o=MovingObstacle((.5,0.),(-.1,0.),.4,0.)
    assert o.clearance((0.,0.),(0.,.05),0.,.2,.15)<.03
    assert escape_motion_free(o,(0.,0.),(0.,.05),0.,.2,.15)
    assert not escape_motion_free(o,(0.,0.),(.05,0.),0.,.2,.15)
    assert not escape_motion_free(o,(0.,0.),(1.,0.),0.,.2,.15)
    assert not escape_motion_free(o,(0.,0.),(0.,0.),0.,.2,.15)


def test_two_meter_filter_ignores_returns_beyond_range():
    node=lidar_node(2,[.4],[(-3.,3.,0.),(-3.,-3.,0.),(0.,0.,0.)])
    node.state_time=.4
    scan=circle_scan(node.own_pose,(3.,0.),.4)
    scan.ranges=[2.01]*240;scan.range_max=10.
    node.scan_callback(scan)
    assert node.scan_points==[]


def test_lidar_only_mode_ignores_camera_motion_candidates():
    node=lidar_node(2,[.4],[(-3.,3.,0.),(-3.,-3.,0.),(0.,0.,0.)])
    for t in [0.,.2,.4]:node.camera_motion.observe([(1.3-.35*t,0.,.32)],t)
    node.state_time=.4;node.scan_wall=time.monotonic();node.last_scan_stamp=.4
    node.control_tick()
    assert node.last_command==(0.,0.,0.)
    assert not node.guard_active


def test_three_robot_team_yields_with_peer_separation():
    clock=[0.];poses=[(0.,.55,0.),(0.,-.55,0.),(.6,0.,0.)]
    nodes=[lidar_node(i,clock,poses) for i in range(3)]
    predictions=[None]*3; minimum=math.inf
    for k in range(85):
        now=k*.1;clock[0]=now;person=(2.2-.35*now,0.)
        after=[]
        for i,node in enumerate(nodes):
            node.own_pose=poses[i];node.peer_poses=poses.copy()
            node.state_time=now;node.state_wall=time.monotonic()
            node.peer_predictions=predictions.copy();node.peer_prediction_times=[now-.1]*3
            node.scan_callback(circle_scan(node.own_pose,person,now));node.control_tick()
            vx,vy,spin=node.last_command
            assert math.hypot(vx,vy)<=node.max_linear_speed+1e-9
            p=poses[i];mid=p[2]+.05*spin
            q=(p[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),p[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),p[2]+.1*spin)
            gap=swept_separation(p,q,person,(person[0]-.035,0.))
            minimum=min(minimum,gap)
            assert gap>.45,(i,now,gap,node.safety_state)
            after.append(q)
        for i in range(3):
            for j in range(i):
                assert swept_separation(poses[i],after[i],poses[j],after[j])>.32
        predictions=[n.poses_from(n.prediction_pub.messages[-1]) for n in nodes]
        poses=after
    assert minimum>.45


def test_slow_sim_clock_allows_fresh_sim_data_but_frozen_clock_stops(monkeypatch):
    import social_navigation_planner.dstar_mpc_controller as module
    node=lidar_node(2,[.11],[(-3.,3.,0.),(-3.,-3.,0.),(0.,0.,0.)])
    wall=[0.];monkeypatch.setattr(module.time,'monotonic',lambda:wall[0])
    node.sensor_wall_limit(0.)
    wall[0]=2.5;assert node.sensor_wall_limit(.1)>2.
    node.state_time=node.last_scan_stamp=.1
    node.state_wall=node.scan_wall=.2
    wall[0]=2.7
    assert node.escape_sensors_fresh(.11)
    wall[0]=6.
    assert not node.escape_sensors_fresh(.11)


def test_data_is_rechecked_after_escape_planning():
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader()
    original=node.physical_grid.segment_clearance
    def delayed(*args):
        clock[0]=.9
        return original(*args)
    node.physical_grid.segment_clearance=delayed
    node.control_tick()
    assert node.last_command==(0.,0.,0.)
    assert 'data expired' in node.safety_state


def test_astar_deadline_never_returns_partial_unchecked_path():
    from social_navigation_planner.local_escape import plan_escape
    calls=[]
    plan=plan_escape((0.,0.,0.),0.,.28,lambda *args:calls.append(args) or True,
                     lambda *args:True,deadline=time.perf_counter()-1.)
    assert plan is None and not calls


def test_local_track_wins_over_conflicting_remote_copy_but_not_occluded_objects():
    from social_navigation_planner.moving_obstacles import select_lidar_tracks
    local=MovingObstacle((1.,0.),(0.,0.),.34,1.)
    duplicate=MovingObstacle((1.15,0.),(-.7,0.),.34,1.)
    occluded=MovingObstacle((0.,1.2),(0.,-.3),.34,1.)
    assert select_lidar_tracks([local],[duplicate,occluded],1.)==[local,occluded]
    assert select_lidar_tracks([],[duplicate],1.)==[duplicate]


def test_circle_fit_uses_measured_centre_and_small_arcs_keep_conservative_radius():
    from social_navigation_planner.moving_obstacles import scan_clusters
    points=[(.3*math.cos(a),.3*math.sin(a)) for a in [2.7,2.9,math.pi,3.3,3.5]]
    observations=scan_clusters(points,(-1.,0.,0.))
    assert observations[0][:2]==pytest.approx((0.,0.),abs=1e-8)
    assert observations[0][2]>=.32
    small=[(.08*math.cos(a),.08*math.sin(a)) for a in [2.7,2.9,math.pi,3.3,3.5]]
    assert scan_clusters(small,(-1.,0.,0.))[0][2]>=.32


def test_spatial_components_join_interleaved_returns_of_same_object():
    from social_navigation_planner.moving_obstacles import scan_clusters
    points=[(1.,0.),(2.,1.),(1.1,.05),(2.1,1.05)]
    grouped=scan_clusters(points,(0.,0.,0.))
    assert len(grouped)==2


def test_short_motion_dropout_does_not_cancel_avoidance_but_expires():
    from social_navigation_planner.moving_obstacles import MotionTracks
    tracks=MotionTracks(padding=.02,persistence=.4)
    for t,x in [(0.,0.),(.1,.03),(.2,.06)]:tracks.observe([(x,0.,.32)],t)
    assert tracks.recent(.2)[0].velocity[0]==pytest.approx(.3)
    tracks.observe([(.01,0.,.32)],.3)
    assert tracks.recent(.3)[0].velocity[0]==pytest.approx(.3)
    tracks.observe([(.01,0.,.32)],.8)
    assert tracks.recent(.8)[0].velocity==(0.,0.)


def test_trigger_reserves_space_for_a_nearby_object_turning_toward_robot():
    from social_navigation_planner.moving_obstacles import collision_risk
    obstacle=MovingObstacle((.75,-1.),(0.,.4),.35,0.)
    assert collision_risk(obstacle,(0.,0.),0.,.15) is not None


def test_escape_rollout_never_uses_object_speed_as_robot_speed():
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader();node.control_tick()
    assert node.guard_active
    assert math.hypot(*node.last_command[:2])<=node.max_linear_speed+1e-9
    trajectory=node.poses_from(node.prediction_pub.messages[-1])
    assert all(math.dist(a[:2],b[:2])<=node.max_linear_speed*node.mpc_dt+1e-9
               for a,b in zip(trajectory,trajectory[1:]))


def test_near_approach_reserves_turn_space_without_triggering_on_departure():
    from social_navigation_planner.moving_obstacles import collision_risk
    toward=MovingObstacle((.9,-.4),(0.,.4),.35,0.)
    away=MovingObstacle((.9,-.4),(0.,-.4),.35,0.)
    assert collision_risk(toward,(0.,0.),0.,.15) is not None
    assert collision_risk(away,(0.,0.),0.,.15) is None


def test_short_pause_holds_goal_reference_then_releases():
    from test_moving_obstacle_safety import stopped_leader
    node,clock=stopped_leader();node.control_tick()
    assert node.guard_active
    reference=node.reference.copy()
    assert node.yield_to_moving_obstacles(clock[0]+.5,[])
    assert node.last_command==(0.,0.,0.)
    assert node.reference==reference
    assert not node.yield_to_moving_obstacles(clock[0]+1.3,[])
    assert node.reference==reference


@pytest.mark.parametrize('index',[0,1,2])
def test_corner_pause_then_turn_does_not_pull_robot_back_into_object(index):
    clock=[0.];poses=[(-3.,3.,0.),(-3.,-3.,0.),(-3.,0.,0.)]
    poses[index]=(0.,0.,0.);node=lidar_node(index,clock,poses)
    minimum=math.inf
    def person(t):
        if t<3.:return (.9,-1.6+.4*t)
        if t<3.7:return (.9,-.4)
        return (.9-.4*(t-3.7),-.4)
    for k in range(90):
        now=k*.1;clock[0]=now
        node.state_time=node.reference_time=now
        node.state_wall=node.reference_wall=time.monotonic()
        node.peer_poses[index]=node.own_pose
        rows=node.peer_poses.copy();rows[index]=(.4,0.,0.)
        node.reference=[rows for _ in range(node.mpc_horizon+1)]
        node.scan_callback(circle_scan(node.own_pose,person(now),now))
        before=node.own_pose;node.control_tick()
        vx,vy,w=node.last_command;mid=before[2]+.05*w
        after=(before[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),
               before[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),before[2]+.1*w)
        separation=swept_separation(before,after,person(now),person(now+.1))
        minimum=min(minimum,separation)
        assert separation>.45,(index,now,separation,node.safety_state)
        assert math.hypot(vx,vy)<=.28+1e-9
        node.own_pose=after
    assert minimum>.45
