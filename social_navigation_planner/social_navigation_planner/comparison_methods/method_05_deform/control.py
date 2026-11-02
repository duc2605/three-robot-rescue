"""STAGE 1 (logical output stage): low-level robot control/velocity regulation.

The actual platform exposes Twist velocity commands rather than wheel torques.
CTC, slip compensation, or nonholonomic control here are *velocity proxies*.
"""
import math
from ..common import bound, limit, angle_diff


def control_motion(index, poses, desired, target, mem, dt, speed, max_w):
    dvx,dvy,dw=desired
    x,y,yaw=poses[index]
    out=_control(index,poses,desired,target,mem,dt,speed,max_w)
    if len(out)!=3 or any(not math.isfinite(v) for v in out): return (0.,0.,0.)
    vx,vy=limit(out[0],out[1],speed)
    return vx,vy,bound(out[2],-max_w,max_w)
def _control(index,poses,desired,target,mem,dt,speed,max_w):
    # Constraint-aware local control via bounded velocity and slew rate.
    vx,vy,w=desired; max_acc=.90
    return bound(vx,mem.last_vx-max_acc*dt,mem.last_vx+max_acc*dt),bound(vy,mem.last_vy-max_acc*dt,mem.last_vy+max_acc*dt),w
