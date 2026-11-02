"""Isolated coordinator goal recovery contracts (no ROS runtime required)."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).parents[1] / 'social_navigation_planner/dstar_mpc_controller.py'


def plan_method():
    tree = ast.parse(SOURCE.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ThreeRobotDStarMPC')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'plan')
    namespace = {'math': math, 'minimum_team_distance': lambda _: 1.0}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['plan']


class ReachedRouting(Exception):
    pass


def fixture(goal_free=False, reachable=True):
    goal = (2.0, 2.0)
    state = SimpleNamespace(
        now_seconds=lambda: 10., map_msg=object(), goal_xy=goal,
        poses_ready=lambda: True, get_robot_pose=lambda i: (float(i), 0., 0.),
        is_free_world=lambda x, y: goal_free or (x, y) != goal,
        leader_index=2, route_between=lambda *args: [args[0], args[1]] if reachable else None,
        blocked=[], routing_peers=[],
        get_logger=lambda: SimpleNamespace(warning=lambda *a, **k: None),
    )
    def connect(point, **kwargs):
        state.routing_started = True
        raise ReachedRouting()
    state.connect_to_grid = connect
    return state


def test_blocked_goal_preserved_with_reachable_approach():
    state = fixture()
    with pytest.raises(ReachedRouting):
        plan_method()(state)
    assert state.goal_xy == (2., 2.)
    assert state.approach_goal_xy != state.goal_xy
    assert state.goal_route_status == 'approaching_blocked_goal'
    assert state.is_free_world(*state.approach_goal_xy)


def test_unreachable_approach_does_not_discard_goal():
    state = fixture(reachable=False)
    plan_method()(state)
    assert state.goal_xy == (2., 2.)
    assert state.approach_goal_xy is None
    assert state.goal_route_status == 'blocked_no_reachable_approach'
    assert not hasattr(state, 'routing_started')


def test_clear_goal_returns_to_exact_requested_endpoint():
    state = fixture(goal_free=True)
    state.approach_goal_xy = (1., 2.)
    with pytest.raises(ReachedRouting):
        plan_method()(state)
    assert state.goal_xy == (2., 2.)
    assert state.approach_goal_xy is None
    assert state.goal_route_status == 'original_goal'
