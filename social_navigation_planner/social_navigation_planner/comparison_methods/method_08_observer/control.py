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
    # Observed task-space motion vs requested speed estimates effective slip.
    x,y,_=poses[index]
    if mem.last_pose is not None:
        actual=math.hypot(x-mem.last_pose[0],y-mem.last_pose[1])/max(dt,.04)
        commanded=math.hypot(mem.last_vx,mem.last_vy)
        if commanded>.04:
            estimate=bound(1.-actual/commanded,0.,.65)
            mem.slip_ratio=.92*mem.slip_ratio+.08*estimate
    mem.last_pose=(x,y)
    factor=1./max(.55,1.-mem.slip_ratio)
    vx,vy,w=desired
    return vx*factor,vy*factor,w
