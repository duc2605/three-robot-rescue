"""Coordinator-only goal progress; local collision avoidance stays unchanged."""
import math
from .leader_follower import Polyline
from .peer_safety import peer_motion_free


class IndependentGoalProgress:
    """Leader follows its route; each follower joins measured trail independently.

    A failed follower connector never cancels the leader's route. Every moving
    reference is still swept against the planning map and simultaneous peers.
    This is not permission to drive through a stationary teammate.
    """
    mode = 'goal progress / followers rejoin independently'

    def __init__(self, points, actual, order, route_between, segment_free,
                 trail=None, gap=.70, speed=.16, follower_speed=.18, radius=.15):
        self.order = tuple(order)
        self.leader = order[0]
        self.route = Polyline(points)
        self.route_between, self.segment_free = route_between, segment_free
        self.gap, self.speed, self.follower_speed, self.radius = gap, speed, follower_speed, radius
        self.trail = Polyline(trail or [actual[self.leader][:2]])
        if math.dist(self.trail.points[-1],actual[self.leader][:2]) > .4:
            self.trail = Polyline([actual[self.leader][:2]])
        else:
            self.trail.append(actual[self.leader][:2])
        self.progress = 0.
        self.elapsed = 0.
        self.joins = {}
        self.refresh = {}
        # Compare routes to the same first follower slot at recovery start.
        # Keep this order for the lifetime of this recovery instance.
        target = self.trail.sample(max(0., self.trail.length-self.gap))
        ranked = []
        initial_routes = {}
        for previous_rank, index in enumerate(self.order[1:]):
            peers = [pose for i, pose in enumerate(actual) if i != index]
            path = (self.route_between(actual[index], target, peers)
                    if self.segment_free(actual[index], actual[index]) else None)
            route = Polyline(path) if path else None
            initial_routes[index] = route
            ranked.append((route.length if route is not None else math.inf, previous_rank, index))
        followers = [index for _, _, index in sorted(ranked)]
        self.order = (self.leader, *followers)
        first = followers[0]
        if initial_routes[first] is not None:
            self.joins[first] = initial_routes[first]
        self.failure_reason = ''
        self.follower_status = {}
        self.paths = [None]*3
        self.paths[self.leader] = self.route.points

    def rows(self, actual, dt, horizon, step):
        self.elapsed += max(0.,min(.2,dt))
        leader = self.leader
        self.progress,error = self.route.project(actual[leader],self.progress,ahead=1.)
        if error > .30:
            self.failure_reason = 'leader left independent route; replan from measured poses'
            return None
        last = self.trail.points[-1]
        if .015 <= math.dist(last,actual[leader][:2]) <= .4:
            if self.segment_free(last,actual[leader]):
                self.trail.append(actual[leader][:2])
        candidates = [[tuple(p[:3]) for p in actual] for _ in range(horizon+1)]
        for k in range(1,horizon+1):
            candidates[k][leader] = self.route.sample(min(self.route.length,
                self.progress+self.speed*k*step,self.progress+.24))
        join_searches = 0
        for rank,index in enumerate(self.order[1:],1):
            self.follower_status[index] = 'holding: no checked join'
            # A follower already outside map clearance holds locally; it does
            # not force the other robots to reassemble before leader progress.
            if not self.segment_free(actual[index],actual[index]):
                self.follower_status[index] = 'holding: measured pose lacks planning clearance'
                continue
            target = self.trail.sample(max(0.,self.trail.length-rank*self.gap))
            cached = self.joins.get(index)
            rebuild = cached is None or math.dist(cached.points[-1],target[:2]) > .20
            if cached is not None:
                _,err = cached.project(actual[index],0.,behind=0.,ahead=cached.length)
                rebuild |= err > .25
            if rebuild and self.elapsed >= self.refresh.get(index,-1.) and join_searches < 1:
                join_searches += 1
                self.refresh[index] = self.elapsed+1.
                peers = [p for i,p in enumerate(actual) if i!=index]
                path = self.route_between(actual[index],target,peers)
                cached = self.joins[index] = Polyline(path) if path else None
            if cached is None:
                continue
            progress,err = cached.project(actual[index],0.,behind=0.,ahead=cached.length)
            if err > .30:
                continue
            self.paths[index] = cached.points
            self.follower_status[index] = 'joining measured leader trail'
            for k in range(1,horizon+1):
                candidates[k][index] = cached.sample(min(cached.length,
                    progress+self.follower_speed*k*step,progress+.24))
        rows = [tuple(tuple(p[:3]) for p in actual)]
        for proposed in candidates[1:]:
            before = rows[-1]
            after = list(before)
            for index in self.order:
                point = proposed[index]
                if not self.segment_free(before[index],point):
                    if index != leader and math.dist(before[index][:2],point[:2]) > .001:
                        self.joins[index] = None
                        self.follower_status[index] = 'holding: join blocked, retry route'
                    continue
                trial = after.copy()
                trial[index] = point
                if all(peer_motion_free(before[index],point,before[j],trial[j],
                        preferred=.32,physical=2*self.radius+.02)
                       for j in range(3) if j!=index):
                    after[index] = point
            rows.append(tuple(after))
        if (self.progress < self.route.length-.20
                and math.dist(rows[-1][leader][:2],actual[leader][:2]) < .005):
            self.failure_reason = 'independent leader route blocked; replan safely'
            return None
        return rows

    def display_paths(self):
        return [path or [] for path in self.paths]
