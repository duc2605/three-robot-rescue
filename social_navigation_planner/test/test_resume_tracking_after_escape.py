"""Full safe horizons before search breadth, without changing escape policy."""
import math
import time

import pytest
from social_navigation_planner import dstar_mpc_controller as module
from test_mpc_formation_motion import controller
from test_moving_obstacle_safety import empty_grid


def fixture():
    clock=[10.]
    node=controller(2,empty_grid(),clock)
    node.own_pose=(0.,0.,0.)
    node.peer_poses=[(-3.,2.,0.),(-3.,-2.,0.),node.own_pose]
    rows=[tuple(node.peer_poses[:2]+[(.2+.2*k*node.mpc_dt,0.,0.)])
          for k in range(node.mpc_horizon+1)]
    predictions=[{i:node.peer_poses[i] for i in [0,1]} for _ in rows]
    return node,clock,rows,predictions


def test_complete_horizon_fits_bounded_candidate_work_before_wide_beam(monkeypatch):
    node,clock,rows,predictions=fixture()
    count=[0]
    def work_clock():
        count[0]+=1
        return count[0]
    monkeypatch.setattr(module.time,'perf_counter',work_clock)
    best,reason=node.bounded_tracking_beam(clock[0],.1,rows,predictions,[],[],[0,1],False,100.)
    assert reason is None and best is not None
    assert len(best[6])==node.mpc_horizon+1
    assert best[4][0]>0. and count[0]<100


def test_deadline_never_publishes_partial_horizon(monkeypatch):
    node,clock,rows,predictions=fixture()
    monkeypatch.setattr(module.time,'perf_counter',lambda:2.)
    best,reason=node.bounded_tracking_beam(clock[0],.1,rows,predictions,[],[],[0,1],False,1.)
    assert best is None and reason=='mpc_compute_budget_exhausted'
    assert node.cmd_pub.messages==[]


def test_raw_obstacle_and_peer_checks_still_reject_blocked_departure():
    node,clock,rows,predictions=fixture()
    node.segment_free=lambda *args:False
    best,reason=node.bounded_tracking_beam(clock[0],.1,rows,predictions,[(.1,0.)],[],[0,1],False,time.perf_counter()+1.)
    assert best is None and reason=='mpc_beam_empty_step_1'
    assert node.cmd_pub.messages==[]


def test_returns_to_reference_after_existing_pause_expires():
    node,clock,rows,predictions=fixture()
    node.reference=rows;node.reference_time=node.state_time=clock[0]
    node.moving_pause_until=clock[0]+1.25
    node.control_tick()
    assert node.last_command==(0.,0.,0.)
    clock[0]+=1.3
    node.reference_time=node.state_time=node.last_scan_stamp=clock[0]
    node.state_wall=node.reference_wall=node.scan_wall=time.monotonic()
    node.control_tick()
    assert node.last_command[0]>0.
    assert not node.guard_active
