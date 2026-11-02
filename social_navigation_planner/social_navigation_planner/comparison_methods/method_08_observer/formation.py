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
    if mem.last_leader is not None:
        mx=(leader[0]-mem.last_leader[0])/max(.05,dt)
        my=(leader[1]-mem.last_leader[1])/max(.05,dt)
        mem.leader_vx=.75*mem.leader_vx+.25*bound(mx,-.3,.3)
        mem.leader_vy=.75*mem.leader_vy+.25*bound(my,-.3,.3)
    mem.last_leader=leader
    if index==2: return goal
    dx=goal[0]-lead_goal[0];dy=goal[1]-lead_goal[1]
    tx=leader[0]+dx+mem.leader_vx*.20
    ty=leader[1]+dy+mem.leader_vy*.20
    # Distributed observer: bounded leader position/velocity prediction.
    return goal[0]+bound(.40*(tx-goal[0]),-.18,.18),goal[1]+bound(.40*(ty-goal[1]),-.18,.18),goal[2]
