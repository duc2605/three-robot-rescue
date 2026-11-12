"""Common adapter behavior regressions, independent of each paper policy."""
import math
import pytest

pytest.importorskip('rclpy')
from social_navigation_planner.paper_behavior import PaperBehavior
from social_navigation_planner.paper_models.environment import social_physical_gate


class FreeMap:
    def segment_free(self, a, b):
        return True


def test_shared_limits_apply_to_world_velocity_without_changing_heading():
    behavior=PaperBehavior.__new__(PaperBehavior)
    behavior.max_speed=.28;behavior.leader_speed=.16;behavior.follower_speed=.22
    behavior.leader=2;behavior.physical=FreeMap();behavior.max_angular_speed=1.0
    behavior.selected=[[],[],[]];behavior.now=lambda:0.
    poses=[(0.,0.,0.),(0.,2.,0.),(0.,4.,0.)]
    commands,_=behavior.gate(poses,[(.3,.4,0.)]*3,[[],[],[]],FreeMap())
    assert math.hypot(*commands[2][:2]) == pytest.approx(.16)
    assert math.hypot(*commands[0][:2]) == pytest.approx(.22)
    assert commands[0][0]/commands[0][1] == pytest.approx(.75)


def test_common_gate_uses_current_32cm_peer_floor():
    poses=[(0.,0.,0.),(.34,0.,0.),(2.,2.,0.)]
    commands,reasons=social_physical_gate(poses,[(0.,.1,0.)]*3,[[],[],[]],FreeMap(),FreeMap())
    assert reasons == ['policy']*3
    assert commands == [(0.,.1,0.)]*3


def test_common_gate_rechecks_peer_motion_after_veto():
    poses=[(0.,0.,0.),(.4,0.,0.),(2.,2.,0.)]
    commands,reasons=social_physical_gate(poses,[(.5,0.,0.),(0.,0.,0.),(0.,0.,0.)],
                                         [[],[],[]],FreeMap(),FreeMap())
    assert commands[0] == (0.,0.,0.)
    assert reasons[0] == 'peer_swept_veto'
