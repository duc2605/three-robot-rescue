"""Social planning constraints rank ahead of escape convenience."""
from types import SimpleNamespace
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC


def rank(points):
    # A social strip x in [1,2], with physically free space on either side.
    def free(a,b,margin):
        return max(a[0],b[0]) < 1 or min(a[0],b[0]) > 2
    node=SimpleNamespace(segment_free=free,inflation_radius=.2)
    return DistributedRobotMPC.escape_social_rank(node,points)


def test_clear_detour_beats_short_social_crossing():
    assert rank([(0,0),(0,1)]) < rank([(0,0),(3,0)])


def test_exit_beats_parking_inside_social_region():
    assert rank([(1.5,0),(3,0)]) < rank([(1.5,0),(1.6,0)])


def test_emergency_crossing_is_ranked_not_discarded():
    assert rank([(0,0),(3,0)]) == (1,0,1.)


def test_less_exposure_preferred_when_endpoints_clear():
    assert rank([(1.5,0),(3,0),(4,0)]) < rank([(1.5,0),(1.6,0),(3,0)])
