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
    # Virtual normalized-camera feature residual (not real camera image coordinates).
    # Produces a vector in world coordinates; feature extraction from camera is
    # unavailable in the current ROS interface, so it is NOT true image servoing.
    dx,dy=e;phi=math.atan2(dy,dx) if math.hypot(dx,dy)>.001 else yaw
    projection=math.hypot(dx,dy)
    gain=.80*math.tanh(projection/.35)
    return gain*math.cos(phi)+.30*ff[0],gain*math.sin(phi)+.30*ff[1],1.1*angle_diff(target[2],yaw)
