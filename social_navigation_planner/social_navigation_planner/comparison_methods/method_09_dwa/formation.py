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
    # Bearing/range constraint from leader pose, as in car-like leader following.
    dx=goal[0]-lead_goal[0];dy=goal[1]-lead_goal[1]
    tx=leader[0]+dx;ty=leader[1]+dy
    return goal[0]+bound(.48*(tx-goal[0]),-.18,.18),goal[1]+bound(.48*(ty-goal[1]),-.18,.18),goal[2]
