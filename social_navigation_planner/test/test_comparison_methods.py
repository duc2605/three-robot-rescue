"""User-run numerical checks of ten prototypes; no Gazebo or paper benchmark."""
import math
from pathlib import Path

import pytest
from social_navigation_planner.comparison_methods.common import Memory
from social_navigation_planner.comparison_methods.registry import METHODS, load_method


def fixture():
    poses=[(-.5,-.4,0.),(-.5,.4,0.),(0.,0.,0.)]
    refs=[[(x+.03*k,y,a) for x,y,a in poses] for k in range(9)]
    return poses,refs


@pytest.mark.parametrize('method_id',range(1,11))
@pytest.mark.parametrize('index',range(3))
def test_all_three_stages_produce_finite_bounded_commands(method_id,index):
    pipeline,_=load_method(method_id)
    poses,refs=fixture()
    twist,stages=pipeline.compute_three_stages(index,poses,refs,Memory(),safe=lambda *args:True)
    assert all(math.isfinite(v) for v in twist)
    assert math.hypot(*twist[:2])<=.24+1e-9
    assert abs(twist[2])<=1.+1e-9
    assert set(stages)=={'formation_target','trajectory_twist','control_twist'}
    assert all(len(v)==3 and all(math.isfinite(x) for x in v) for v in stages.values())


@pytest.mark.parametrize('method_id',range(1,11))
def test_invalid_reference_holds(method_id):
    pipeline,_=load_method(method_id)
    poses,refs=fixture()
    for states,reference in [([],refs),(poses,[]),(poses,[[(0,0,0)]]),
                             ([(float('nan'),0,0),*poses[1:]],refs)]:
        twist,stages=pipeline.compute_three_stages(2,states,reference,Memory())
        assert twist==(0.,0.,0.) and 'error' in stages


@pytest.mark.parametrize('method_id',[3,5,9])
def test_sampled_trackers_honor_rejected_candidates(method_id):
    pipeline,_=load_method(method_id)
    poses,refs=fixture();calls=[]
    def reject(*args):calls.append(args);return False
    twist,stages=pipeline.compute_three_stages(2,poses,refs,Memory(),safe=reject)
    assert calls
    assert stages['trajectory_twist'][:2]==(0.,0.)
    # Low-level control may add feedback; adapter still has to reject any
    # nonzero motion. Do not confuse a sampler callback with final safety.
    assert all(math.isfinite(v) for v in twist)


def test_registry_matches_ten_launches_and_unique_modules():
    assert set(METHODS)==set(range(1,11))
    assert len({m['module'] for m in METHODS.values()})==10
    root=Path(__file__).resolve().parents[2]
    for m in METHODS.values():
        assert (root/'social_navigation_sim/launch'/f"paper{m['paper_number']}_{m['slug']}.launch.py").exists()
