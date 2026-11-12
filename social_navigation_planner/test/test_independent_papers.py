"""Numerical and isolation regressions. Authored in NK120; not yet executed."""
import ast
import math
from pathlib import Path
import pytest
from social_navigation_planner.paper_models.catalog import require_paper
from social_navigation_planner.paper_models.kinematic import v_targets, pursuit, vo_collision, Impedance
from social_navigation_planner.paper_models.environment import separated, social_physical_gate


def test_fixed_v_comes_from_measured_leader_not_coordinator_references():
    poses=[(0.,0.,0.),(0.,0.,0.),(2.,3.,math.pi/2)]
    targets=v_targets(poses,2,(8.,9.))
    assert targets[0]==pytest.approx((1.5,2.3))
    assert targets[1]==pytest.approx((2.5,2.3))
    assert targets[2]==(8.,9.)


def test_pursuit_curvature_and_behind_target():
    vx,vy,w=pursuit((0.,0.,0.),(1.,1.))
    assert vy==0.
    assert w==pytest.approx(2*vx*math.sin(math.pi/4)/math.sqrt(2))
    assert pursuit((0.,0.,0.),(-1.,0.))[:2]==(0.,0.)


def test_velocity_obstacle_depends_on_relative_motion():
    pose=(0.,0.,0.)
    assert vo_collision(pose,(.2,0.,0.),(1.,0.,-.3,0.,.2))
    assert not vo_collision(pose,(.2,0.,0.),(1.,0.,.4,0.,.2))


def test_impedance_force_points_away():
    poses=[(0.,0.,0.),(2.,0.,0.),(4.,0.,0.)]
    targets=[p[:2] for p in poses]
    result=Impedance().commands(poses,targets,[(0.,0.,0.)]*3,[[(.4,0.,0.,0.,.1)],[],[]],.1)
    assert result[0][0]<0.
    assert result[1][:2]==(0.,0.)


def test_crossing_segments_are_not_safe_endpoints():
    assert not separated((-1.,0.),(1.,0.),(0.,-1.),(0.,1.),.36)


def test_social_veto_does_not_substitute_baseline_escape():
    class Free:
        def segment_free(self,a,b):return True
    class Social:
        def segment_free(self,a,b):return b[0]<.05
    result,reason=social_physical_gate([(0.,0.,0.),(0.,2.,0.),(0.,4.,0.)],[(.2,0.,0.)]*3,[[],[],[]],Free(),Social())
    assert result==[(0.,0.,0.)]*3
    assert reason==['social_map_veto']*3


@pytest.mark.parametrize('paper',[0,9,10,11,12])
def test_unavailable_papers_do_not_fall_back(paper):
    with pytest.raises(ValueError,match='No legacy fallback'):require_paper(paper)


def test_new_controller_does_not_import_baseline_navigation():
    root=Path(__file__).parents[1]/'social_navigation_planner'
    for path in [root/'paper_experiment_node.py',*sorted((root/'paper_models').glob('*.py'))]:
        tree=ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                assert not any(s in (node.module or '') for s in ('dstar_mpc_controller','local_escape','comparison_controller','independent_goal_progress'))


def test_deform_assignments_are_bijective():
    from social_navigation_planner.paper_models.deform import Deform
    class Free:
        def point_free(self,p):return True
        def segment_free(self,a,b):return True
        def clearance(self,p,limit):return limit
    controller=Deform(2)
    targets=controller.targets([(0.,-.5,0.),(0.,.5,0.),(.7,0.,0.)],(1.2,0.),Free(),0.)
    assert sorted(controller.assignment)==[0,1,2]
    assert len(targets)==3
    assert all(math.isfinite(v) for target in targets for v in target)
