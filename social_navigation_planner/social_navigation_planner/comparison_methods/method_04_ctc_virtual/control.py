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
    # CTC-style task-space acceleration + disturbance observer VELOCITY PROXY.
    x,y,_=poses[index];vx,vy,w=desired
    error_x=vx-mem.last_vx;error_y=vy-mem.last_vy
    mem.disturbance_x=.80*mem.disturbance_x+.20*error_x
    mem.disturbance_y=.80*mem.disturbance_y+.20*error_y
    ax=3.5*error_x+1.3*(target[0]-x)-.20*mem.disturbance_x
    ay=3.5*error_y+1.3*(target[1]-y)-.20*mem.disturbance_y
    return mem.last_vx+ax*dt,mem.last_vy+ay*dt,w
