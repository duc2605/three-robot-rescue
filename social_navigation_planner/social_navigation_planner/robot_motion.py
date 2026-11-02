"""Measured robot coasting/braking envelope; no actor ground truth."""
import math


def braking_pose(pose, velocity, seconds, reaction=.3, deceleration=.4):
    """Engineering reserve, not a measured guarantee of the drive response."""
    vx,vy,w=velocity; speed=math.hypot(vx,vy);t=max(0.,seconds)
    if speed<.03:return tuple(pose)
    coast=min(t,reaction);brake=min(max(0.,t-reaction),speed/deceleration)
    distance=speed*coast+speed*brake-.5*deceleration*brake*brake
    return (pose[0]+distance*vx/speed,pose[1]+distance*vy/speed,
            pose[2]+w*min(t,reaction))
