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
    desired_sep=math.hypot(goal[0]-lead_goal[0],goal[1]-lead_goal[1])
    actual_sep=math.hypot(own[0]-leader[0],own[1]-leader[1])
    desired_bearing=math.atan2(goal[1]-lead_goal[1],goal[0]-lead_goal[0])
    tx=leader[0]+desired_sep*math.cos(desired_bearing)
    ty=leader[1]+desired_sep*math.sin(desired_bearing)
    # Social-force-style repulsion of nearby team members; human rules remain in costmap.
    fx=fy=0.
    for j,(x,y,_) in enumerate(poses):
        if j==index: continue
        dx,dy=own[0]-x,own[1]-y
        d=max(.01,math.hypot(dx,dy));strength=.08*math.exp((.48-d)/.20)
        fx+=strength*dx/d;fy+=strength*dy/d
    gain=bound(.35+0.25*abs(desired_sep-actual_sep),.35,.65)
    return goal[0]+bound(gain*(tx-goal[0])+fx,-.20,.20),goal[1]+bound(gain*(ty-goal[1])+fy,-.20,.20),goal[2]
