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
    # A virtual leader is defined by the mean of leader pose and its planned pose.
    virtual_x=.65*leader[0]+.35*lead_goal[0]
    virtual_y=.65*leader[1]+.35*lead_goal[1]
    offset_x=goal[0]-lead_goal[0];offset_y=goal[1]-lead_goal[1]
    # Smooth, repulsive team-agent interaction; person effects handled by social grid.
    dx=own[0]-leader[0];dy=own[1]-leader[1]
    d=max(.01,math.hypot(dx,dy))
    f=.035*math.exp((.45-d)/.18)
    return goal[0]+bound(.40*(virtual_x+offset_x-goal[0])+f*dx/d,-.20,.20),goal[1]+bound(.40*(virtual_y+offset_y-goal[1])+f*dy/d,-.20,.20),goal[2]
