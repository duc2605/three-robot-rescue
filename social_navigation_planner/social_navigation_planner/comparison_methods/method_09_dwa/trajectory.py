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
    # DWA: candidate window around last velocity with acceleration constraints.
    x,y,_=poses[index];best=(float('inf'),0.,0.)
    for ax in (-.85,-.4,0.,.4,.85):
        for ay in (-.85,-.4,0.,.4,.85):
            cx,cy=limit(mem.last_vx+ax*dt,mem.last_vy+ay*dt,speed)
            if safe is not None and not safe(cx,cy,.5):continue
            fx,fy=x+cx*.5,y+cy*.5
            cost=2.*((fx-target[0])**2+(fy-target[1])**2)+.12*(cx*cx+cy*cy)
            if cost<best[0]:best=(cost,cx,cy)
    # desired heading aligned with path as a car-like steering approximation
    newyaw=math.atan2(target[1]-y,target[0]-x) if math.hypot(*e)>.1 else target[2]
    return best[1],best[2],1.4*angle_diff(newyaw,yaw)
