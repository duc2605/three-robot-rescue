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
    # Virtual structure anchor is geometric center of the observed team.
    cx=sum(p[0] for p in poses)/3.;cy=sum(p[1] for p in poses)/3.
    target_cx=sum(ref_at(refs,2,j)[0] for j in range(3))/3.
    target_cy=sum(ref_at(refs,2,j)[1] for j in range(3))/3.
    virtual_x=cx+(goal[0]-target_cx)
    virtual_y=cy+(goal[1]-target_cy)
    return goal[0]+bound(.40*(virtual_x-own[0]),-.16,.16),goal[1]+bound(.40*(virtual_y-own[1]),-.16,.16),goal[2]
