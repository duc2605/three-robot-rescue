"""Speed-aware escape goals and camera-sweep preemption regressions."""
import math
import time

import pytest

from social_navigation_planner.local_escape import plan_escape
from social_navigation_planner.moving_obstacles import MovingObstacle, MotionTracks, collision_risk
from social_navigation_planner.grid_clearance import segment_box_distance_squared
from social_navigation_planner.social_observation import ObservationSweep
from social_navigation_planner.adaptive_structure import swept_separation

pytest.importorskip('rclpy')
from std_msgs.msg import String
from test_mpc_formation_motion import coordinator, Capture
from test_moving_obstacle_safety import stopped_leader, measured_person, empty_grid


def test_speed_and_ttc_distinguish_slow_fast_and_moving_away():
    slow=collision_risk(MovingObstacle((.8,0.),(-.2,0.),.32,0.),(0.,0.),0.,.15)
    fast=collision_risk(MovingObstacle((1.2,0.),(-.8,0.),.32,0.),(0.,0.),0.,.15)
    assert slow['band']=='slow' and slow['horizon']==3.
    assert fast['band']=='fast' and fast['horizon']==3.
    assert fast['ttc']<slow['ttc']
    assert collision_risk(MovingObstacle((1.2,0.),(.8,0.),.32,0.),(0.,0.),0.,.15) is None


def test_slow_person_below_previous_threshold_is_measured():
    tracks=MotionTracks()
    for t in [0.,.2,.4]:tracks.observe([(.08*t,0.,.32)],t)
    assert tracks.recent(.4)[0].velocity==pytest.approx((.08,0.))


@pytest.mark.parametrize('side,allow',[
    ('left',lambda p:p[0]>=-.01 and p[1]>=-.01),
    ('right',lambda p:p[0]>=-.01 and p[1]<=.01),
    ('rear',lambda p:p[0]<=.01 and abs(p[1])<=.01),
])
def test_astar_chooses_an_available_rear_left_or_right_goal(side,allow):
    plan=plan_escape((0.,0.,0.),0.,.28,
                     lambda a,b,t,u:allow(a) and allow(b),lambda p,t,u:allow(p))
    assert plan is not None and plan.side==side
    assert .5<=math.dist((0.,0.),plan.goal)<=.8
    assert all(allow(p) for p in plan.points)


def test_astar_goes_around_a_wall_instead_of_connecting_straight_to_side_goal():
    box=(-.04,.16,.04,.24)
    def safe(a,b,t,u):
        return (min(a[0],b[0])>=-.01 and min(a[1],b[1])>=-.01
                and segment_box_distance_squared(a,b,box)>0)
    plan=plan_escape((0.,0.,0.),0.,.28,safe,lambda p,t,u:safe(p,p,t,u))
    assert plan is not None and plan.side=='left'
    assert any(p[0]>=.08 for p in plan.points)
    assert all(safe(a,b,0.,1.) for a,b in zip(plan.points,plan.points[1:]))


def test_astar_rejects_a_goal_where_person_will_arrive_during_hold():
    # A geometrically clear left goal becomes occupied at arrival time.
    plan=plan_escape((0.,0.,0.),0.,.28,lambda a,b,t,u:True,
                     lambda p,t,u:p[1]<.1)
    assert plan is not None and plan.side!='left'


def test_astar_search_has_a_bounded_failure_case():
    checks=[]
    plan=plan_escape((0.,0.,0.),0.,.28,
                     lambda a,b,t,u:checks.append((a,b)) or True,
                     lambda p,t,u:False,max_expansions=30)
    assert plan is None and len(checks)<=30*9


@pytest.mark.parametrize('speed,initial',[(.08,.95),(.35,1.3),(.8,2.6)])
def test_measured_slow_and_fast_pedestrians_do_not_hit_stopped_leader(speed,initial):
    node,clock=stopped_leader();node.camera_motion.clear();minimum=math.inf;moved=False
    for t in [0.,.2,.4]:measured_person(node,t,(initial-speed*t,0.))
    for k in range(85):
        now=.4+k*.1;clock[0]=now
        person=(initial-speed*now,0.);measured_person(node,now,person)
        before=node.own_pose;node.peer_poses[2]=before;node.control_tick()
        vx,vy,spin=node.last_command;mid=before[2]+.05*spin
        after=(before[0]+.1*(vx*math.cos(mid)-vy*math.sin(mid)),
               before[1]+.1*(vx*math.sin(mid)+vy*math.cos(mid)),before[2]+.1*spin)
        gap=swept_separation(before,after,person,(person[0]-.1*speed,0.))
        assert gap>.47,(now,speed,gap,node.safety_state)
        minimum=min(minimum,gap);moved |= math.dist(before[:2],after[:2])>.001
        assert node.physical_grid.segment_free(before,after)
        node.own_pose=after
    assert moved
    print(f'person_speed={speed:.2f}m/s; minimum_center_separation={minimum:.3f}m')


def test_camera_scan_is_cancelled_as_soon_as_mpc_reports_a_threat():
    node,clock=stopped_leader()
    now=clock[0]
    node.reference=ObservationSweep(tuple(node.peer_poses),2,0.,.4,.8,bearing=1.).rows(
        tuple(node.peer_poses),now,node.mpc_horizon,node.mpc_dt)
    node.reference_time=now
    node.control_tick()
    assert node.guard_active and math.hypot(*node.last_command[:2])>0
    main=coordinator(tuple(node.peer_poses),empty_grid())
    original_goal=main.goal_xy
    main.observation=object();main.observation_search_id=None
    main.observation_pub=Capture()
    main.moving_safety_callback(node.safety_pub.messages[-1],2)
    assert main.observation is None
    assert main.goal_xy==original_goal
    assert main.moving_safety_active()
    assert 'yielding' in main.observation_pub.messages[-1].data
    main.publish_reference(.1)
    assert len(main.reference_pub.messages[-1].poses)==3*(main.mpc_horizon+1)
    accepted,reason=main.start_observation()
    assert not accepted and 'priority' in reason
    main.moving_safety_callback(String(data='normal'),2)
    assert not main.moving_safety_active()
    assert main.replan_required


def test_old_safety_messages_do_not_lock_camera_observation_forever():
    node=coordinator(((0.,0.,0.),(-1.,1.,0.),(-1.,-1.,0.)),empty_grid())
    node.safety_holds={2:(99.,time.monotonic())}
    assert not node.moving_safety_active()
    node.safety_holds={2:(100.,time.monotonic()-3)}
    assert not node.moving_safety_active()


def test_mpc_publishes_only_a_local_temporary_goal():
    node,clock=stopped_leader();node.control_tick()
    assert node.guard_active
    assert node.escape_goal_pub.messages
    goal=node.escape_goal_pub.messages[-1].pose.position
    assert math.hypot(goal.x,goal.y)<=.8
    assert node.escape_path_pub.messages[-1].poses


def test_temporary_goal_leaves_pedestrian_approach_line_instead_of_only_retreating():
    node,clock=stopped_leader();node.control_tick()
    assert node.escape_plan is not None
    assert node.escape_plan.side in ('left','right')
    assert abs(node.escape_plan.goal[1])>=.64
