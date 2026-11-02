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
    # Distributed consensus plus bounded artificial repulsion; geometry adapts.
    cx=cy=0.
    for j,peer in enumerate(poses):
        if j==index: continue
        peer_goal=ref_at(refs,2,j)
        cx+=(peer[0]+goal[0]-peer_goal[0])-own[0]
        cy+=(peer[1]+goal[1]-peer_goal[1])-own[1]
        dx,dy=own[0]-peer[0],own[1]-peer[1]
        d=max(.01,math.hypot(dx,dy))
        if d < .75:
            cx+=.10*(.75-d)*dx/d
            cy+=.10*(.75-d)*dy/d
    # Leader remains index 2; temporary leadership election is NOT reproduced.
    gain=.17 if index!=2 else .09
    return goal[0]+bound(gain*cx,-.20,.20),goal[1]+bound(gain*cy,-.20,.20),goal[2]
