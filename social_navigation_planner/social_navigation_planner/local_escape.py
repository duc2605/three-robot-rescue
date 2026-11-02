"""Bounded space-time A* for a temporary rear/left/right yielding waypoint.

The global goal is never changed. Paths only propose a local heading; MPC
must still check the acceleration-limited rollout before issuing a command.
"""
from dataclasses import dataclass
import heapq
import math
import time


@dataclass(frozen=True)
class EscapePlan:
    side: str
    goal: tuple
    points: tuple
    stamp: float

    def heading(self, pose):
        nearest = min(range(len(self.points)), key=lambda i:math.dist(pose[:2],self.points[i]))
        index = min(nearest+2,len(self.points)-1)
        return math.atan2(self.points[index][1]-pose[1],self.points[index][0]-pose[0])


def plan_escape(pose, now, max_speed, edge_safe, holding_safe, max_expansions=1200, deadline=None, escape_angles=None, goal_score=None, prefer_rear=False):
    """A* on an 8-cm local lattice and 0.3-s arrival-time bins.

    Physical clearance and simultaneous pedestrian/peer motion are supplied
    by callbacks. Waiting is a checked transition, never assumed harmless.
    Search is limited to 3 simulation seconds and 0.8 m from the start.
    """
    cell, tick, last = .08, .3, 10
    if not math.isfinite(max_speed) or max_speed <= 0:
        return None
    goals = {}
    for side,angle in (escape_angles or [('rear',pose[2]+math.pi),('left',pose[2]+math.pi/2),
                       ('right',pose[2]-math.pi/2)]):
        for distance in (.56,.72):
            key=(round(distance*math.cos(angle)/cell),round(distance*math.sin(angle)/cell))
            goals[key]=side
    def xy(key):return pose[0]+key[0]*cell,pose[1]+key[1]*cell
    def heuristic(key):
        return min(math.dist(xy(key),xy(goal))/max_speed for goal in goals)
    # Cheap fully checked straight connectors before the space-time lattice.
    # This preserves left/right/rear choices without spending a full search
    # budget in an open room. A blocked connector still falls back to A*.
    connector_checks = 0
    best_plan,best_score = None,math.inf
    for goal,side in sorted(goals.items(),key=lambda item:(item[1]!='rear') if prefer_rear else (item[1]=='rear')):
        endpoint=xy(goal)
        count=max(1,math.ceil(math.dist(pose[:2],endpoint)/(max_speed*tick)))
        if count>last: continue
        chain=[tuple(pose[:2])]+[tuple(pose[i]+(endpoint[i]-pose[i])*k/count for i in range(2))
                                for k in range(1,count+1)]
        valid=True
        for k,(a,b) in enumerate(zip(chain,chain[1:])):
            if deadline is not None and time.perf_counter()>=deadline: return best_plan
            if connector_checks >= max_expansions*9: return None
            connector_checks += 1
            if not edge_safe(a,b,now+k*tick,now+(k+1)*tick):
                valid=False;break
        if valid and holding_safe(endpoint,now+count*tick,now+count*tick+.6):
            candidate=EscapePlan(side,endpoint,tuple(chain),now)
            if goal_score is None:return candidate
            score=goal_score(endpoint)
            if score<best_score:best_plan,best_score=candidate,score
    if best_plan is not None:return best_plan
    start=(0,0,0)
    queue=[(heuristic(start),0.,start)]
    costs={start:0.};parents={start:None};expanded=0
    moves=[(x,y) for x in (-1,0,1) for y in (-1,0,1)]
    while queue and expanded<max(0,max_expansions-math.ceil(connector_checks/9)):
        if deadline is not None and time.perf_counter() >= deadline:
            return None
        _,cost,key=heapq.heappop(queue)
        if cost>costs.get(key,math.inf)+1e-9:
            continue
        expanded+=1
        position=xy(key);arrival=now+key[2]*tick
        if key[:2] in goals and holding_safe(position,arrival,arrival+.6):
            chain=[];current=key
            while current is not None:
                chain.append(xy(current));current=parents[current]
            return EscapePlan(goals[key[:2]],position,tuple(reversed(chain)),now)
        for dx,dy in moves:
            if deadline is not None and time.perf_counter() >= deadline:
                return None
            steps=max(1,math.ceil(math.hypot(dx,dy)*cell/(max_speed*tick)-1e-9))
            target=(key[0]+dx,key[1]+dy,key[2]+steps)
            if target[2]>last or math.hypot(target[0],target[1])*cell>.8:
                continue
            end=xy(target)
            if not edge_safe(position,end,arrival,now+target[2]*tick):
                continue
            new_cost=target[2]*tick+.1*math.dist(xy(start),end)
            if new_cost>=costs.get(target,math.inf)-1e-9:
                continue
            costs[target]=new_cost;parents[target]=key
            heapq.heappush(queue,(new_cost+heuristic(target),new_cost,target))
    return None
