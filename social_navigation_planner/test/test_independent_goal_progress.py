"""Goal movement must not require successful follower assembly."""
import math
import pytest
from social_navigation_planner.independent_goal_progress import IndependentGoalProgress


POSES = ((-1.,1.,0.),(-1.,-1.,0.),(0.,0.,0.))


def test_leader_advances_when_both_follower_join_routes_fail():
    motion = IndependentGoalProgress([(0.,0.),(2.,0.)],POSES,(2,1,0),
                                    lambda *args:None,lambda *args:True)
    rows = motion.rows(POSES,.1,8,.15)
    assert rows[-1][2][0] > 0.
    assert rows[-1][0] == POSES[0] and rows[-1][1] == POSES[1]


def test_follower_outside_map_clearance_does_not_freeze_clear_leader():
    def free(a,b):
        return a[0]>-.5 and b[0]>-.5
    motion = IndependentGoalProgress([(0.,0.),(2.,0.)],POSES,(2,1,0),
                                    lambda *args:None,free)
    rows = motion.rows(POSES,.1,8,.15)
    assert rows[-1][2][0] > 0.
    assert rows[-1][0] == POSES[0]


def test_leader_cannot_drive_through_a_stationary_follower():
    poses = ((1.,1.,0.),(.40,0.,0.),(0.,0.,0.))
    motion = IndependentGoalProgress([(0.,0.),(2.,0.)],poses,(2,1,0),
                                    lambda *args:None,lambda *args:True)
    rows = motion.rows(poses,.1,8,.15)
    assert rows is None or all(math.dist(r[2][:2],poses[1][:2])>=.32-1e-9 for r in rows)


def test_new_wall_blocks_reference_even_if_old_route_was_clear():
    free = lambda a,b:max(a[0],b[0]) <= .001
    motion = IndependentGoalProgress([(0.,0.),(2.,0.)],POSES,(2,1,0),
                                    lambda *args:None,free)
    assert motion.rows(POSES,.1,8,.15) is None
    assert 'blocked' in motion.failure_reason


def test_followers_can_join_without_holding_leader_for_spacing():
    joins = lambda a,b,peers:[a[:2],b[:2]]
    motion = IndependentGoalProgress([(0.,0.),(2.,0.)],POSES,(2,1,0),joins,
                                    lambda *args:True)
    rows = motion.rows(POSES,.1,8,.15)
    assert rows[-1][2][0] > 0.
    assert any(math.dist(rows[-1][i][:2],POSES[i][:2])>0 for i in (0,1))


def test_coordinator_selects_independent_mode_after_avoidance():
    pytest.importorskip('rclpy')
    from test_mpc_formation_motion import coordinator
    from test_moving_obstacle_safety import empty_grid
    node = coordinator(POSES,empty_grid())
    node.goal_progress_without_formation = True
    node.formation_disrupted = True
    node.goal_xy = (2.,0.)
    node.approach_goal_xy = None
    node.goal_progress = None
    node.publish_global_path = lambda *args:None
    node.publish_formation_paths = lambda:None
    node.plan()
    assert node.goal_progress is not None
    assert node.convoy is None and node.maneuver is None and node.structure is None
    assert node.goal_xy == (2.,0.)
    assert not node.replan_required


def test_recovery_prioritizes_shortest_safe_connector_over_robot_number():
    poses = ((-.4, 0., 0.), (-1.5, 0., 0.), (0., 0., 0.))
    motion = IndependentGoalProgress([(0., 0.), (2., 0.)], poses, (2, 1, 0),
                                    lambda a,b,peers:[a[:2], b[:2]], lambda *args:True)
    assert motion.order == (2, 0, 1)
    assert 0 in motion.joins
    motion.rows(poses, .1, 2, .15)
    assert motion.order == (2, 0, 1)


def test_blocked_nearer_follower_yields_priority_to_reachable_follower():
    poses = ((-.4, 0., 0.), (-1.5, 0., 0.), (0., 0., 0.))
    def route(a, b, peers):
        return None if a[0] == -.4 else [a[:2], b[:2]]
    motion = IndependentGoalProgress([(0., 0.), (2., 0.)], poses, (2, 0, 1),
                                    route, lambda *args:True)
    assert motion.order == (2, 1, 0)
