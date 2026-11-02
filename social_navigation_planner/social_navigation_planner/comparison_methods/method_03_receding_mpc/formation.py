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
    # SSOS: two followers maintain relative offsets to leader and to each other.
    if index==2: return goal
    sx=sy=0.; n=0
    for j in range(3):
        if j==index: continue
        other=poses[j]; expected=ref_at(refs,2,j)
        dx,dy=goal[0]-expected[0],goal[1]-expected[1]
        sx+=(other[0]+dx)-own[0]
        sy+=(other[1]+dy)-own[1];n+=1
    return goal[0]+bound(.30*sx/max(1,n),-.18,.18),goal[1]+bound(.30*sy/max(1,n),-.18,.18),goal[2]
