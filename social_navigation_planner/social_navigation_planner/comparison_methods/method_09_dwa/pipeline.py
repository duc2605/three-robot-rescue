"""Explicit 3-stage controller pipeline: formation -> trajectory -> control.

The three output categories requested for EACH paper are separate implementation
modules.  Runtime dependencies work in reverse order from block listing:
formation target first, trajectory desired velocity next, low-level controller
last.  The caller's social safety map/physical safety filter is always applied
AFTER this pipeline, before publishing Twist.
"""
import math
from .formation import formation_target
from .trajectory import trajectory_tracking
from .control import control_motion
from ..common import limit, bound


def compute_three_stages(index, poses, refs, memory, dt=.1, speed=.24,
                         max_w=1.0, horizon_dt=.15, safe=None):
    if (index not in (0,1,2) or len(poses)!=3 or not refs
            or not all(len(row)==3 for row in refs)
            or not all(len(p)==3 and all(math.isfinite(v) for v in p)
                       for row in [poses,*refs] for p in row)
            or not all(math.isfinite(v) for v in (dt,speed,max_w,horizon_dt))
            or dt<=0 or speed<=0 or max_w<=0 or horizon_dt<=0):
        return (0.,0.,0.), {'error':'missing_states_or_references'}
    target=formation_target(index,poses,refs,memory,dt)
    desired=trajectory_tracking(index,poses,refs,target,memory,dt,speed,horizon_dt,safe)
    twist=control_motion(index,poses,desired,target,memory,dt,speed,max_w)
    return twist, {'formation_target':tuple(round(v,5) for v in target),
                   'trajectory_twist':tuple(round(v,5) for v in desired),
                   'control_twist':tuple(round(v,5) for v in twist)}
