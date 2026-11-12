"""Requires pinned upstream and its optional dependencies, not just ROS build."""
import math
import pytest
from social_navigation_planner.paper_models.ho_mpc import activate_upstream


def test_author_solver_bridge_returns_finite_bounded_commands():
    try:
        activate_upstream()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    from social_navigation_planner.paper_models.ho_mpc import HierarchicalOmni
    from social_navigation_planner.paper_models.kinematic import v_targets
    poses=[(-.7,.5,0.),(-.7,-.5,0.),(0.,0.,0.)]
    model=HierarchicalOmni(2)
    result=model.commands(poses,v_targets(poses,2,(.3,0.)),[(0.,0.,0.)]*3,[[],[],[]],.1,None)
    assert len(result)==3
    assert all(math.isfinite(v) for row in result for v in row)
    assert all(math.hypot(*row[:2])<=.2801 for row in result)
    assert model.status==['upstream_hierarchical_qp']*3
