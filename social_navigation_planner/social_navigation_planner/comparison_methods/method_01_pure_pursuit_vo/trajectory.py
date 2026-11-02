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
    # Pure Pursuit lookahead, preserving formation target offset.
    r2=ref_at(refs,2,index);look=ref_at(refs,5,index)
    x,y,_=poses[index]
    px=look[0]+bound(target[0]-r2[0],-.2,.2)
    py=look[1]+bound(target[1]-r2[1],-.2,.2)
    dx,dy=px-x,py-y; norm=max(.18,math.hypot(dx,dy))
    vx,vy=speed*dx/norm,speed*dy/norm
    return vx,vy,1.2*angle_diff(target[2],yaw)
