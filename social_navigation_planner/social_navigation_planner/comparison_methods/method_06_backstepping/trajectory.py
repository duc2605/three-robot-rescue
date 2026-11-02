"""STAGE 2: path/trajectory tracking, consumes formation-adjusted target.

Output is a desired WORLD-FRAME twist.  Output still passes control and safety.
"""
import math
from ..common import bound, limit, angle_diff, ref_at


def trajectory_tracking(index, poses, refs, target, mem, dt, speed, horizon_dt, safe=None):
    x,y,yaw=poses[index]
    gx,gy,ga=target
    e=(gx-x,gy-y)
    r0=ref_at(refs,0,index)
    r1=ref_at(refs,1,index)
    ff=(bound((r1[0]-r0[0])/max(.05,horizon_dt),-.27,.27),
        bound((r1[1]-r0[1])/max(.05,horizon_dt),-.27,.27))
    return _track(index,poses,refs,target,mem,dt,speed,horizon_dt,safe,e,ff,yaw)
def _track(index,poses,refs,target,mem,dt,speed,horizon_dt,safe,e,ff,yaw):
    # Backstepping-inspired nonlinear stabilization, omnidirectional approximation.
    bx=math.cos(yaw)*e[0]+math.sin(yaw)*e[1]
    by=-math.sin(yaw)*e[0]+math.cos(yaw)*e[1]
    bfx=math.cos(yaw)*ff[0]+math.sin(yaw)*ff[1]
    bfy=-math.sin(yaw)*ff[0]+math.cos(yaw)*ff[1]
    ux=1.2*math.tanh(bx/.35)+.35*bfx
    uy=1.0*math.tanh(by/.35)+.35*bfy
    return math.cos(yaw)*ux-math.sin(yaw)*uy,math.sin(yaw)*ux+math.cos(yaw)*uy,1.5*math.sin(angle_diff(target[2],yaw))
