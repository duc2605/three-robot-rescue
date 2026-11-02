import math
from types import SimpleNamespace
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC
from social_navigation_planner.local_escape import plan_escape


def test_rear_is_relative_to_body_heading():
    node=SimpleNamespace(own_pose=(0,0,math.pi/2))
    rank=lambda p:DistributedRobotMPC.escape_rear_rank(node,p)
    assert rank((0,-.6)) == 0
    assert rank((0,.6)) == 1
    assert rank((.6,0)) == 1
    assert rank((0,0)) == 1


def test_rear_selected_in_open_space():
    plan=plan_escape((0,0,0),0,.28,lambda *args:True,lambda *args:True,prefer_rear=True)
    assert plan.side=='rear' and plan.goal[0]<0


def test_blocked_rear_keeps_side_escape_available():
    plan=plan_escape((0,0,0),0,.28,lambda a,b,*args:b[0]>=-.01,
                     lambda *args:True,prefer_rear=True)
    assert plan is not None and plan.side in ('left','right')


def test_unsafe_rear_holding_is_rejected():
    plan=plan_escape((0,0,0),0,.28,lambda *args:True,
                     lambda p,*args:p[0]>=-.01,prefer_rear=True)
    assert plan is not None and plan.side!='rear'
