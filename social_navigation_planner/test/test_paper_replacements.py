"""NK121 regressions. Commands in README; not executed by the editing task."""
import math
import pytest
from social_navigation_planner.paper_models.catalog import require_paper
from social_navigation_planner.paper_models.drivetrains import DifferentDrivetrains, hybrid_route
from social_navigation_planner.paper_models.robile import RobileFormation
from social_navigation_planner.paper_models.kinematic import v_targets
from social_navigation_planner.paper_models.upstream_sources import SOURCES


class FreeMap:
    def point_free(self,p):return -5<p[0]<5 and -5<p[1]<5
    def segment_free(self,a,b):return self.point_free(a) and self.point_free(b)


@pytest.mark.parametrize('paper',[5,6,7])
def test_new_papers_resolve_to_new_sources(paper):
    assert require_paper(paper)[1]=='implemented_adaptation'
    assert len(SOURCES[paper]['commit'])==40
    assert SOURCES[paper]['repository'].startswith('https://github.com/')


def test_hybrid_search_uses_continuous_heading_and_reverse():
    route=hybrid_route(FreeMap(),(0.,0.,0.),(-.64,0.),wall_budget=5.)
    assert route
    assert math.dist(route[-1][:2],(-.64,0.))<.12
    assert all(len(p)==3 for p in route)
    assert all(FreeMap().segment_free(a[:2],b[:2]) for a,b in zip(route,route[1:]))
    assert any(b[0]<a[0] for a,b in zip(route,route[1:]))


def test_no_partial_hybrid_path_after_search_exhaustion():
    assert hybrid_route(FreeMap(),(0.,0.,0.),(2.,2.),max_expansions=0)==[]


def test_mecanum_follower_tracks_translation_without_formation_error():
    poses=[(-.7,.5,0.),(-.7,-.5,0.),(0.,0.,0.)]
    targets=v_targets(poses,2,(1.,0.))
    commands=DifferentDrivetrains(2).commands(poses,targets,[(0.,0.,0.)]*3,[[],[],[]],.1,FreeMap())
    assert commands[0]==pytest.approx(commands[2])
    assert commands[1]==pytest.approx(commands[2])


def test_robile_integral_uses_elapsed_time_and_resets_on_new_instance():
    poses=[(-.9,1.,0.),(-1.,-1.,0.),(0.,0.,0.)]
    a,b=RobileFormation(2),RobileFormation(2)
    targets=a.targets(poses,(0.,0.))
    a.commands(poses,targets,[],[],.1,None)
    for _ in range(2):b.commands(poses,targets,[],[],.05,None)
    assert a.integral[0]==pytest.approx(b.integral[0])
    assert RobileFormation(2).integral[0]==[0.,0.]


def test_robile_outputs_are_covariant_world_velocities():
    poses=[(-1.1,1.,0.),(-1.,-1.,0.),(0.,0.,0.)]
    a=RobileFormation(2)
    targets=a.targets(poses,(1.,0.))
    commands=a.commands(poses,targets,[],[],.1,None)
    rotated=[(-p[1],p[0],math.pi/2) for p in poses]
    b=RobileFormation(2)
    rotated_targets=b.targets(rotated,(0.,1.))
    turned=b.commands(rotated,rotated_targets,[],[],.1,None)
    for first,second in zip(commands,turned):
        assert second[:2]==pytest.approx((-first[1],first[0]))
