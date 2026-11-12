"""Paper6: independent adaptation of the Different Drivetrains project.

Source/commit: upstream_sources.py. Implements continuous bicycle Hybrid A*,
Pure Pursuit and a rigid-offset mecanum follower law. Re-derived for normal
ROS body axes and two followers; no ArUco, pallet, or Reeds–Shepp claim.
"""
import heapq
import math
import time
from .kinematic import clip, limit, wrap, v_targets


def hybrid_route(grid, start, goal, max_expansions=8000, wall_budget=.3):
    """SE(2) search with forward/reverse bicycle primitives and swept footprint.

    16cm x/y, 15deg yaw bins;32cm primitives sampled every4cm, wheelbase50cm,
    steering±20deg. Goal is XY within12cm; final heading is unconstrained.
    Returns no partial route when the budget or feasibility check fails.
    """
    began=time.monotonic()
    if not grid.point_free(start[:2]) or not grid.point_free(goal):return []
    if math.dist(start[:2],goal)<.06:return [tuple(start)]
    def key(p,direction):
        return (round(p[0]/.16),round(p[1]/.16),round(wrap(p[2])/math.radians(15)),direction)
    first=key(start,1)
    queue=[(math.dist(start[:2],goal),0,0.,first)]
    costs={first:0.};poses={first:tuple(start)};parents={};edges={}
    serial=0;end=None
    for _ in range(max_expansions):
        if not queue or time.monotonic()-began>wall_budget:break
        _,_,cost,cell=heapq.heappop(queue)
        if cost>costs[cell]+1e-9:continue
        p=poses[cell]
        if math.dist(p[:2],goal)<.12:
            end=cell;break
        for direction in (1,-1):
            for steering in (-math.radians(20),0.,math.radians(20)):
                segment=[];q=p
                for _ in range(8):
                    ds=direction*.04
                    turn=ds*math.tan(steering)/.5
                    nxt=(q[0]+ds*math.cos(q[2]+turn/2),
                         q[1]+ds*math.sin(q[2]+turn/2),wrap(q[2]+turn))
                    if not grid.segment_free(q[:2],nxt[:2]):break
                    segment.append(nxt);q=nxt
                if len(segment)!=8:continue
                dest=key(q,direction)
                new=cost+.32*(1. if direction==1 else 1.3)+(.4 if direction!=cell[3] else 0.)+.02*abs(steering)
                if new>=costs.get(dest,math.inf):continue
                serial+=1;costs[dest]=new;poses[dest]=q;parents[dest]=cell;edges[dest]=segment
                heapq.heappush(queue,(new+math.dist(q[:2],goal),serial,new,dest))
    if end is None:return []
    segments=[]
    while end in parents:
        segments.append(edges[end]);end=parents[end]
    return [tuple(start)]+[p for segment in reversed(segments) for p in segment]


class DifferentDrivetrains:
    def __init__(self,leader):
        self.leader=leader
        self.status=['not_commanded']*3

    def commands(self,poses,targets,velocities,obstacles,dt,grid):
        p=poses[self.leader];target=targets[self.leader]
        dx,dy=target[0]-p[0],target[1]-p[1]
        distance=math.hypot(dx,dy)
        alpha=wrap(math.atan2(dy,dx)-p[2])
        direction=1. if abs(alpha)<=math.pi/2 else -1.
        # Steering follows the signed bicycle curvature, including reverse.
        steering=clip(math.atan2(2*.5*math.sin(alpha),max(.15,distance)),
                      -math.radians(20),math.radians(20))
        v=direction*min(.2,distance) if distance>.06 else 0.
        w=v/.5*math.tan(steering)
        lead=(v*math.cos(p[2]),v*math.sin(p[2]),w)
        result=[None]*3;result[self.leader]=lead
        for i in range(3):
            if i==self.leader:continue
            pose=poses[i];heading=pose[2];c,s=math.cos(heading),math.sin(heading)
            ex,ey=targets[i][0]-pose[0],targets[i][1]-pose[1]
            # Different Drivetrains mecanum gains kx=1, ky=.2, kyaw=1.
            # Rigid offset feedforward replaces upstream's opposite-facing
            # pallet geometry/signs: v_ref=vL+wL x R(thetaL)*offset.
            ox,oy=targets[i][0]-p[0],targets[i][1]-p[1]
            fx,fy=lead[0]-w*oy,lead[1]+w*ox
            bx=c*fx+s*fy+(c*ex+s*ey)
            by=-s*fx+c*fy+.2*(-s*ex+c*ey)
            vx,vy=limit(c*bx-s*by,s*bx+c*by,.28)
            error_heading=wrap(p[2]-heading)
            turn=clip(w+error_heading,-.5,.5) if math.hypot(ex,ey)<.2 else 0.
            result[i]=(vx,vy,turn)
        self.status=['hybrid_pursuit_mecanum_adapter']*3
        return result
