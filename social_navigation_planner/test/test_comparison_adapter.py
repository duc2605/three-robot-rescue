"""Adapter and launch regression fixtures; user executes after build."""
import math
import time
from copy import deepcopy

import pytest
pytest.importorskip('rclpy')
from social_navigation_planner.comparison_controller import ComparisonRobotController
from social_navigation_planner.comparison_methods.common import Memory
from social_navigation_planner.comparison_methods.registry import load_method
from test_moving_obstacle_safety import stopped_leader


def policy_node():
    node,clock=stopped_leader()
    node.policy_memory=Memory();node.pending_memory=None;node.stages={}
    node.canonical=[0,1,2];node.policy_index=2
    node.pipeline,node.method_info=load_method(1)
    return node,clock


def rollout(node,clock):
    now=clock[0]
    refs=[[(*p[:2],p[2]) for p in node.peer_poses] for _ in range(node.mpc_horizon+1)]
    for row in refs:row[2]=(.4,0.,0.)
    peers=[0,1]
    pred=[{i:node.peer_poses[i] for i in peers} for _ in refs]
    return ComparisonRobotController.checked_tracking_rollout(
        node,now,.1,refs,pred,[],[],peers,time.perf_counter()+1.)


def test_planning_map_rejection_does_not_commit_policy_memory():
    node,clock=policy_node()
    before=deepcopy(node.policy_memory)
    node.segment_free=lambda *args:False
    assert rollout(node,clock) is None
    assert node.policy_memory==before
    assert node.pending_memory is None


def test_no_silent_baseline_tracking_fallback():
    assert ComparisonRobotController.bounded_tracking_beam(None)==(
        None,'comparison_policy_rollout_rejected')


def test_finite_limited_first_command_and_horizon():
    node,clock=policy_node()
    result=rollout(node,clock)
    assert result is not None
    first,trajectory=result
    assert len(trajectory)==node.mpc_horizon+1
    assert math.hypot(*first[:2])<=min(node.max_linear_speed,.8*.1)+1e-9
    assert abs(first[2])<=.2+1e-9
    assert node.pending_memory is not None
