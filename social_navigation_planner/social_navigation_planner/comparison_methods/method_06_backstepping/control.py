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
    # Fuzzy-PID-inspired continuous gain scheduling on tracking error.
    x,y,_=poses[index];vx,vy,w=desired
    ex,ey=target[0]-x,target[1]-y
    norm=math.hypot(ex,ey)
    kp=.3+.32*math.tanh(norm/.35)
    ki=.05 if norm<.35 else .015
    mem.ex_int=bound(mem.ex_int+ex*dt,-.3,.3)
    mem.ey_int=bound(mem.ey_int+ey*dt,-.3,.3)
    outx=vx+kp*ex+ki*mem.ex_int+.1*(ex-mem.prev_ex)/max(.04,dt)
    outy=vy+kp*ey+ki*mem.ey_int+.1*(ey-mem.prev_ey)/max(.04,dt)
    mem.prev_ex=ex;mem.prev_ey=ey
    return outx,outy,w
