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
    # V-offset from the reference: followers keep their assigned V legs.
    if index == 2: return goal
    dx,dy=goal[0]-lead_goal[0],goal[1]-lead_goal[1]
    tx,ty=leader[0]+dx,leader[1]+dy
    # Separation-bearing response and reactive peer-velocity-obstacle offset.
    px,py=0.,0.
    for j,(x,y,_) in enumerate(poses):
        if j == index: continue
        rx,ry=own[0]-x,own[1]-y
        d=max(.01,math.hypot(rx,ry))
        if d<.55: px+=.09*(.55-d)*rx/d;py+=.09*(.55-d)*ry/d
    return goal[0]+bound(.50*(tx-goal[0])+px,-.18,.18), goal[1]+bound(.50*(ty-goal[1])+py,-.18,.18),goal[2]
