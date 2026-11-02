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
    # Continuous saturation sliding mode; no proof of finite-time convergence.
    x,y,yaw=poses[index];vx,vy,w=desired
    sx=target[0]-x+.22*(vx-mem.last_vx)
    sy=target[1]-y+.22*(vy-mem.last_vy)
    return vx+.12*math.tanh(sx/.16),vy+.12*math.tanh(sy/.16),w+.18*math.tanh(angle_diff(target[2],yaw)/.25)
