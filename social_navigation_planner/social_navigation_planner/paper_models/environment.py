"""Experiment utilities, NOT algorithms attributed to any paper."""
import heapq
import math
from .kinematic import clip
from ..peer_safety import CONTROL_SEPARATION
from ..moving_obstacles import tracking_motion_free


def waypoint_route(grid, start, goal, spacing=.12, max_expansions=12000):
    """Ordinary bounded A* for a common leader reference, never emergency escape.

    Continuous segment checks include footprint and social cells. Exhaustion
    returns no route rather than a partial path represented as reaching goal.
    """
    if not grid.point_free(goal): return []
    if grid.segment_free(start, goal): return [tuple(start), tuple(goal)]
    def position(cell): return start[0]+spacing*cell[0], start[1]+spacing*cell[1]
    queue = [(math.dist(start,goal), 0., (0,0))]
    distance, previous = {(0,0):0.}, {}
    end = None
    for _ in range(max_expansions):
        if not queue: break
        _, cost, cell = heapq.heappop(queue)
        if cost > distance[cell]+1e-9: continue
        p = position(cell)
        if math.dist(p, goal) <= spacing*1.5 and grid.segment_free(p,goal):
            end = cell; break
        for dx,dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
            neighbor = cell[0]+dx,cell[1]+dy
            q = position(neighbor)
            new = cost+spacing*math.hypot(dx,dy)
            if new >= distance.get(neighbor,math.inf) or not grid.segment_free(p,q): continue
            distance[neighbor], previous[neighbor] = new, cell
            heapq.heappush(queue,(new+math.dist(q,goal),new,neighbor))
    if end is None: return []
    route = [tuple(goal),position(end)]
    while end in previous:
        end = previous[end]; route.append(position(end))
    return route[::-1]


def clusters(points, gap=.23):
    groups = []
    for point in points:
        if point is None: continue
        if not groups or math.dist(point,groups[-1][-1]) > gap: groups.append([])
        groups[-1].append(point)
    output = []
    for group in groups:
        # Large walls are represented by short surface disks, not one huge
        # enclosing circle. This is a LiDAR approximation, not person labels.
        for first in range(0,len(group),8):
            part = group[first:first+8]
            x,y = (sum(p[k] for p in part)/len(part) for k in range(2))
            radius = max(.06,max(math.hypot(p[0]-x,p[1]-y) for p in part))
            output.append((x,y,radius))
    return output


def associate(current, previous, dt):
    """One-to-one nearest-cluster association in map frame, capped1.5m/s."""
    used, result = set(), []
    for x,y,r in current:
        options = [(math.hypot(x-p[0],y-p[1]),j,p) for j,p in enumerate(previous) if j not in used]
        vx=vy=0.
        if options and .03 <= dt <= .5:
            d,j,p = min(options)
            if d < .08+1.5*dt:
                used.add(j)
                vx,vy = clip((x-p[0])/dt,-1.5,1.5),clip((y-p[1])/dt,-1.5,1.5)
        result.append((x,y,vx,vy,r))
    return result


def separated(a0,a1,b0,b1,distance):
    rx,ry=a0[0]-b0[0],a0[1]-b0[1]
    dx,dy=a1[0]-a0[0]-b1[0]+b0[0],a1[1]-a0[1]-b1[1]+b0[1]
    t=clip(-(rx*dx+ry*dy)/max(dx*dx+dy*dy,1e-12),0.,1.)
    return (rx+t*dx)**2+(ry+t*dy)**2 >= distance**2


def social_physical_gate(poses, commands, obstacles, physical, social, horizon=.4, tracked=None, now=0.):
    """Common veto only: no substituted path or baseline evasive command.

    Recheck peers after each veto: replacing motion by zero changes another
    robot's swept clearance. A stopped robot can STILL be hit by a human.
    """
    def obstacle_free(index, end):
        for k,(x,y,vx,vy,radius) in enumerate(obstacles[index]):
            if tracked is not None and k < len(tracked[index]):
                if not tracking_motion_free(tracked[index][k],poses[index],end,now,now+horizon,.15):
                    return False
            elif not separated(poses[index],end,(x,y),(x+vx*horizon,y+vy*horizon),.18+radius):
                return False
        return True

    result, reasons = list(commands), ['policy']*3
    for _ in range(4):
        changed=False
        ends=[(p[0]+v[0]*horizon,p[1]+v[1]*horizon) for p,v in zip(poses,result)]
        for i in range(3):
            reason=None
            if not physical.segment_free(poses[i][:2],ends[i]): reason='physical_map_veto'
            elif not social.segment_free(poses[i][:2],ends[i]): reason='social_map_veto'
            elif not obstacle_free(i,ends[i]): reason='lidar_swept_veto'
            elif any(not separated(poses[i],ends[i],poses[j],ends[j],CONTROL_SEPARATION) for j in range(3) if j!=i): reason='peer_swept_veto'
            if reason:
                if result[i] != (0.,0.,0.): changed=True
                result[i]=(0.,0.,0.);reasons[i]=reason
        if not changed: break
    return result,reasons
