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
    # Directed graph reference tracking, with consensus velocity feedforward.
    if index == 2:return 1.0*e[0]+.38*ff[0],1.0*e[1]+.38*ff[1],1.4*angle_diff(target[2],yaw)
    parent=2 if index==1 else 1
    own=poses[index];p=poses[parent]
    own_ref=ref_at(refs,2,index);p_ref=ref_at(refs,2,parent)
    px=(p[0]+own_ref[0]-p_ref[0])-own[0]
    py=(p[1]+own_ref[1]-p_ref[1])-own[1]
    return .8*e[0]+.35*px+.23*ff[0],.8*e[1]+.35*py+.23*ff[1],1.4*angle_diff(target[2],yaw)
