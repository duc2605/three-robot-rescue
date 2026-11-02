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
    # Finite-control-set receding horizon with explicit formation endpoint penalty.
    x,y,_=poses[index]; best=(float('inf'),0.,0.)
    ref2=ref_at(refs,2,index)
    ox,oy=target[0]-ref2[0],target[1]-ref2[1]
    for mag in (0.,speed*.30,speed*.65,speed):
        for a in range(16):
            th=a*math.tau/16;vx,vy=mag*math.cos(th),mag*math.sin(th)
            if safe is not None and not safe(vx,vy,.55): continue
            cost=0.
            for k in range(1,6):
                t=k*horizon_dt
                p=ref_at(refs,k,index)
                cost+=(x+vx*t-p[0]-ox)**2+(y+vy*t-p[1]-oy)**2
            cost+=.30*((vx-mem.last_vx)**2+(vy-mem.last_vy)**2)
            if cost<best[0]:best=(cost,vx,vy)
    return best[1],best[2],1.4*angle_diff(target[2],yaw)
