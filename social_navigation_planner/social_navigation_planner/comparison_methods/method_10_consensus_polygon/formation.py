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
    # Directed graph 2 -> 1 -> 0 with regular triangle reference offsets.
    if index==2: return goal
    parent=2 if index==1 else 1
    p=poses[parent];gp=ref_at(refs,2,parent)
    dx,dy=goal[0]-gp[0],goal[1]-gp[1]
    target_x=p[0]+dx;target_y=p[1]+dy
    return goal[0]+bound(.52*(target_x-goal[0]),-.20,.20),goal[1]+bound(.52*(target_y-goal[1]),-.20,.20),goal[2]
