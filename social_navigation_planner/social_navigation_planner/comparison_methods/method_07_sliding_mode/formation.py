"""STAGE 3 (logical input stage): FORMATION controller.

Computes the formation-adjusted target pose.  It cannot override the social
keepout map; all motion is finally checked by the ROS node safety filter.
"""
import math
from ..common import bound, ref_at


def formation_target(index, poses, refs, mem, dt):
    if len(poses) != 3 or not refs: return (0., 0., 0.)
    own = poses[index]
    goal = ref_at(refs, 2, index)
    leader = poses[2]
    lead_goal = ref_at(refs, 2, 2)
    # Preserve the original D* Lite/team-reference shape; don't change social map.
    return _formation(index, poses, refs, mem, dt, own, goal, leader, lead_goal)
def _formation(index, poses, refs, mem, dt, own, goal, leader, lead_goal):
    if index==2: return goal
    # Pinhole bearing proxy (calibrated image features are NOT available).
    dx,dy=own[0]-leader[0],own[1]-leader[1]
    gd_x,gd_y=goal[0]-lead_goal[0],goal[1]-lead_goal[1]
    # Errors in virtual normalized visual features: bearing + inverse depth.
    b=math.atan2(dy,dx);bg=math.atan2(gd_y,gd_x)
    radius=max(.1,math.hypot(dx,dy));radius_g=max(.1,math.hypot(gd_x,gd_y))
    db=math.atan2(math.sin(bg-b),math.cos(bg-b))
    ddepth=(1./radius_g)-(1./radius)
    delta_x=.11*(-math.sin(b)*db+math.cos(b)*ddepth)
    delta_y=.11*(math.cos(b)*db+math.sin(b)*ddepth)
    return goal[0]+bound(delta_x,-.12,.12),goal[1]+bound(delta_y,-.12,.12),goal[2]
