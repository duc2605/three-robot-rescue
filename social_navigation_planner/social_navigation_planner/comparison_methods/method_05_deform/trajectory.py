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
    # Distributed MPC-inspired predicted local tracking with peer separation cost.
    x,y,_=poses[index]; best=(float('inf'),0.,0.)
    ref2=ref_at(refs,2,index); ox,oy=target[0]-ref2[0],target[1]-ref2[1]
    for mag in (0.,speed*.35,speed*.7,speed):
        for j in range(20):
            th=math.tau*j/20;vx,vy=mag*math.cos(th),mag*math.sin(th)
            if safe is not None and not safe(vx,vy,.60): continue
            cost=.12*((vx-mem.last_vx)**2+(vy-mem.last_vy)**2)
            for k in range(1,6):
                t=k*horizon_dt;p=ref_at(refs,k,index)
                fx,fy=x+vx*t,y+vy*t
                cost+=(fx-p[0]-ox)**2+(fy-p[1]-oy)**2
                for a,peer in enumerate(poses):
                    if a==index:continue
                    d=math.hypot(fx-peer[0],fy-peer[1])
                    cost+=2.*max(0.,.52-d)**2
            if cost<best[0]:best=(cost,vx,vy)
    return best[1],best[2],1.35*angle_diff(target[2],yaw)
