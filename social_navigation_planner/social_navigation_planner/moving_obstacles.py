"""Short, bounded motion estimates from measured map-frame points only."""

from collections import deque
from dataclasses import dataclass, replace
import math

from .adaptive_structure import swept_separation


@dataclass(frozen=True)
class MovingObstacle:
    position: tuple
    velocity: tuple
    radius: float
    stamp: float
    velocity_hint: tuple | None = None

    def at(self, seconds):
        dt = max(0.0, min(4.5, seconds - self.stamp))
        return tuple(p + dt * v for p, v in zip(self.position, self.velocity))

    def clearance(self, a, b, start, end, robot_radius):
        return (swept_separation(a, b, self.at(start), self.at(end))
                - self.radius - robot_radius)


class MotionTracks:
    """One-to-one association; motion needs three consistent timed captures.

    This estimates moving obstacles, not identities or intended destinations.
    Radius bounds and expiry keep extrapolation local to recent observations.
    """

    def __init__(self, padding=.08, persistence=0., pause_reserve=False):
        self.pause_reserve = pause_reserve
        self.persistence = float(persistence)
        self.padding = float(padding)
        self.tracks = {}
        self.sequence = 0
        self.last_stamp = -math.inf

    def clear(self):
        self.tracks.clear()
        self.last_stamp = -math.inf

    def observe(self, observations, stamp):
        if not math.isfinite(stamp) or stamp <= self.last_stamp:
            return
        self.last_stamp = stamp
        points = []
        for x, y, radius in observations:
            if (all(math.isfinite(v) for v in (x, y, radius))
                    and 0.05 <= radius <= 0.6
                    and not any(math.hypot(x-p[0], y-p[1]) < .12 for p in points)):
                points.append((x, y, radius))
        self.tracks = {k: t for k, t in self.tracks.items() if 0 <= stamp-t.stamp <= 1.2}
        edges = []
        for key, track in self.tracks.items():
            dt = stamp-track.stamp
            predicted = track.at(stamp)
            for i, point in enumerate(points):
                distance = math.dist(predicted, point[:2])
                if distance <= min(.7, .18 + 1.7*dt):
                    edges.append((distance, key, i))
        used, assignments = set(), {}
        for _, key, i in sorted(edges):
            if key not in used and i not in assignments:
                used.add(key)
                assignments[i] = key
        for i, (x, y, radius) in enumerate(points):
            key = assignments.get(i)
            if key is None:
                key = self.sequence
                self.sequence += 1
                self.tracks[key] = _Track()
            track = self.tracks[key]
            track.history.append((stamp, x, y))
            while len(track.history) > 1 and stamp-track.history[0][0] > 1.0:
                track.history.popleft()
            track.position, track.radius, track.stamp = (x, y), radius, stamp
            velocity=estimate_velocity(track.history)
            if math.hypot(*velocity)>=.15:
                track.motion_bound=max(math.hypot(*velocity),track.motion_bound
                                       if stamp-track.motion_seen<=2. else 0.)
                track.motion_seen=stamp
            if math.hypot(*velocity)>=.05:
                track.last_moving_stamp,track.last_velocity=stamp,velocity
            elif stamp-track.last_moving_stamp <= self.persistence:
                velocity=track.last_velocity
            track.velocity = velocity

    def recent(self, now):
        result=[]
        for t in self.tracks.values():
            if not -1e-9<=now-t.stamp<=.8:continue
            speed=math.hypot(*t.velocity)
            recent=list(t.history)[-4:]
            stationary=(len(recent)==4 and recent[-1][0]-recent[0][0]>=.299999
                        and max(math.dist(p[1:],recent[-1][1:]) for p in recent)<.018)
            hint=None
            # An uncertain fit is not an observation that motion stopped.
            # Keep one bounded alternative, while retaining the nominal fit.
            uncertain=(self.pause_reserve and not stationary and speed<.05
                       and now-t.last_moving_stamp<=.8)
            if uncertain and math.hypot(*t.last_velocity)>=.05:
                # Retain an actual recently measured direction/speed. Do not
                # amplify a noisy fit using a synthetic pedestrian-speed prior.
                hint=t.last_velocity
            radius=(t.radius+self.padding+.10*max(0.,now-t.stamp)
                    +(min(.4,t.motion_bound) if self.pause_reserve and now-t.motion_seen<=2.
                      and speed<.12 else 0.))
            result.append(MovingObstacle(t.position,t.velocity,radius,t.stamp,hint))
        return result


class _Track:
    def __init__(self):
        self.history = deque(maxlen=8)
        self.position = self.velocity = (0.0, 0.0)
        self.radius = .32
        self.stamp = -math.inf
        self.last_moving_stamp = -math.inf
        self.last_velocity = (0.,0.)
        self.motion_bound=0.
        self.motion_seen=-math.inf

    def at(self, seconds):
        dt = max(0.0, min(.5, seconds-self.stamp))
        return tuple(p+dt*v for p, v in zip(self.position, self.velocity))


def estimate_velocity(history, allow_recent=True):
    if len(history) < 3 or history[-1][0]-history[0][0] < .2-1e-9:
        return (0.0, 0.0)
    n = len(history)
    mean = [sum(row[i] for row in history)/n for i in range(3)]
    denominator = sum((row[0]-mean[0])**2 for row in history)
    velocity = tuple(sum((row[0]-mean[0])*(row[i]-mean[i]) for row in history)
                     / max(denominator, 1e-9) for i in (1, 2))
    residual = math.sqrt(sum(sum((row[i]-mean[i] - velocity[i-1]*(row[0]-mean[0]))**2
                                 for i in (1, 2)) for row in history)/n)
    displacement = math.dist(history[0][1:], history[-1][1:])
    if not .05 <= math.hypot(*velocity) <= 1.7 or displacement < .03 or residual > .08:
        velocity=(0.,0.)
    if allow_recent and len(history)>3:
        recent=list(history)[-3:]
        short=estimate_velocity(recent,False)
        dx1,dy1=recent[1][1]-recent[0][1],recent[1][2]-recent[0][2]
        dx2,dy2=recent[2][1]-recent[1][1],recent[2][2]-recent[1][2]
        # Two coherent recent displacements override a lagging long-window
        # estimate after a turn; a single jump does not change the direction.
        coherent=dx1*dx2+dy1*dy2 > .85*math.hypot(dx1,dy1)*math.hypot(dx2,dy2)
        if coherent and math.hypot(*short)>=.12 and math.dist(short,velocity)>.15:
            return short
    return velocity


def collision_risk(obstacle, robot, now, robot_radius):
    """Measured speed band and time to entering the stationary robot envelope.

    Thresholds are engineering defaults, not learned pedestrian classes.
    Faster objects trigger a longer lookahead; time to contact still decides
    whether a nearby person is approaching or simply passing safely.
    """
    speed = math.hypot(*obstacle.velocity)
    if speed < .05:
        return None
    fast = speed >= .5
    # A 0.28 m/s robot needs time to move a body width sideways, especially
    # when its other side is occupied by a teammate. Trigger before braking.
    horizon, reserve = (3.0, .16) if fast else (3.0, .12)
    p = obstacle.at(now)
    r = (p[0]-robot[0], p[1]-robot[1])
    # Earlier activation reserves time for noisy velocity/turn updates. This
    # expands the trigger only; rollout collision geometry stays unchanged.
    reserve += min(.35,.35*speed)
    radius = obstacle.radius+robot_radius+reserve
    c = r[0]*r[0]+r[1]*r[1]-radius*radius
    if c <= 0:
        ttc = 0.
    else:
        dot = sum(a*b for a,b in zip(r,obstacle.velocity))
        discriminant = dot*dot-speed*speed*c
        if dot >= 0:
            return None
        if discriminant < 0:
            # Near an approaching object, a short turn invalidates a straight
            # velocity forecast. Reserve lateral room before that turn.
            nearby = obstacle.radius+robot_radius+.25+min(.4,speed)
            if math.hypot(*r) > nearby:
                return None
            ttc = 0.
        else:
            ttc = (-dot-math.sqrt(discriminant))/(speed*speed)
    if ttc > horizon:
        return None
    return dict(speed=speed, band='fast' if fast else 'slow', ttc=ttc, horizon=horizon)


def scan_clusters(points, observer=None):
    """Retain sparse leg returns; temporal tracking rejects isolated noise.

    A narrow leg may occupy just one beam at 240 samples per revolution.
    It must still accumulate three consistent captures to gain velocity.
    Static walls are filtered using the physical map by the caller.
    """
    groups = []
    for point in points:
        if observer is None:
            if not groups or math.dist(groups[-1][-1],point)>.18:groups.append([])
            groups[-1].append(point)
        else:
            # Spatial components reconnect an object split by ray ordering,
            # wraparound, or an intervening occluder. No identity/class label.
            nearby=[i for i,g in enumerate(groups) if any(math.dist(point,q)<=.35 for q in g)]
            if not nearby:groups.append([point])
            else:
                first=nearby[0];groups[first].append(point)
                for i in reversed(nearby[1:]):groups[first].extend(groups.pop(i))
    observations = []
    for group in groups:
        center = tuple(sum(p[i] for p in group)/len(group) for i in (0, 1))
        extent = max(math.dist(center, p) for p in group)
        if extent <= .45:
            # A visible leg surface underestimates the person's whole body.
            radius = max(.40,min(.55,extent+.15))
            if observer is not None and len(group)>=3:
                a,b,c = group[0],group[len(group)//2],group[-1]
                ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=c[0]-a[0],c[1]-a[1]
                denominator=2*(ux*vy-uy*vx)
                if abs(denominator)>1e-5:
                    u2,v2=ux*ux+uy*uy,vx*vx+vy*vy
                    candidate=(a[0]+(u2*vy-v2*uy)/denominator,
                               a[1]+(ux*v2-vx*u2)/denominator)
                    fitted_radius=math.dist(candidate,a)
                    if (.08<=fitted_radius<=.45
                            and math.dist(candidate,observer[:2])>=math.dist(center,observer[:2])
                            and all(abs(math.dist(candidate,p)-fitted_radius)<.025 for p in group)):
                        center,radius=candidate,(max(.32,fitted_radius+.03) if fitted_radius>=.18 else .40)
            # A non-circular/sparse return does not justify shifting an
            # unknown object centre behind its visible surface. Keep a
            # conservative disk around the grouped returns instead.
            observations.append((*center,radius))
    return observations


def escape_motion_free(obstacle, a, b, start, end, robot_radius, margin=.03, gap=None):
    """Strict outside buffers; risk-reducing exit if already inside a buffer.

    Recovery is not a promise of collision-free motion from an overlapping
    estimate. It must beat holding, move away from the current measured
    centre, and never sweep the robot centre across the obstacle return.
    Static-map, raw-scan and peer checks remain separate hard constraints.
    """
    if gap is None:
        gap = obstacle.clearance(a,b,start,end,robot_radius)
    if gap >= margin:
        return True
    q0,q1 = obstacle.at(start),obstacle.at(end)
    initial = math.dist(a[:2],q0)-obstacle.radius-robot_radius
    if initial >= margin or math.dist(a[:2],b[:2]) < 1e-8:
        return False
    holding = obstacle.clearance(a,a,start,end,robot_radius)
    return (gap >= holding-1e-8
            and math.dist(b[:2],q1) > math.dist(a[:2],q1)+1e-5
            and math.dist(b[:2],q0) >= math.dist(a[:2],q0)-1e-8
            and gap+obstacle.radius+robot_radius >= min(
                math.dist(a[:2],q0),robot_radius+min(obstacle.radius,.30)+margin)-1e-9)


def select_lidar_tracks(local, remote, now, remote_sources=None):
    """Prefer local geometry; use peers for objects absent from local scans.

    This suppresses conflicting copies within 45 cm, not person identities.
    Dense adjacent objects can still merge; raw local rays remain hard checks.
    """
    result=list(local)
    for obstacle in sorted(remote,key=lambda o:o.stamp,reverse=True):
        if any(math.dist(obstacle.at(now),existing.at(now))<.45 for existing in result):
            continue
        result.append(obstacle)
    if remote_sources is None:
        return result
    # Each robot gets at most one vote for a nearby object. Two agreeing
    # fresh observers can correct a contradictory local velocity, while the
    # local geometry remains the preferred footprint measurement.
    observations = [('local', o) for o in local] + list(zip(remote_sources, remote))
    fused = []
    for chosen in result:
        nearby = {}
        for source, obstacle in observations:
            if (0 <= now-obstacle.stamp <= .35
                    and math.dist(obstacle.at(now), chosen.at(now)) < .45):
                old = nearby.get(source)
                if old is None or obstacle.stamp > old.stamp:
                    nearby[source] = obstacle
        votes = list(nearby.values())
        agreement = max(([b for b in votes if math.dist(a.velocity,b.velocity) <= .20]
                         for a in votes), key=len, default=[])
        if len(agreement) >= 2:
            velocity = tuple(sum(o.velocity[i] for o in agreement)/len(agreement) for i in (0,1))
            if math.dist(velocity,chosen.velocity) > .20:
                chosen=replace(chosen,velocity=velocity,radius=chosen.radius+.04)
        hints=[o for o in nearby.values() if o.velocity_hint is not None
               and (math.hypot(*chosen.velocity)<.05
                    or sum(a*b for a,b in zip(o.velocity_hint,chosen.velocity))>0)]
        if hints:
            candidate=max(hints,key=lambda o:o.stamp)
            chosen=replace(chosen,velocity_hint=candidate.velocity_hint)
        fused.append(chosen)
    return fused


def motion_hypotheses(obstacles):
    """Bounded safety alternatives, not additional measured people/track votes."""
    result=[]
    for o in obstacles:
        result.append(o)
        if o.velocity_hint is not None and math.dist(o.velocity_hint,o.velocity)>.025:
            result.append(replace(o,velocity=o.velocity_hint,velocity_hint=None))
    return result


def crosses_approach_corridor(obstacle,a,b,start,end,robot_radius):
    """Reject crossing in front of a flow; crossing safely behind remains valid."""
    vx,vy=obstacle.velocity;speed=math.hypot(vx,vy)
    if speed<.05:return False
    q=obstacle.at(start)
    side0=(a[0]-q[0])*vy-(a[1]-q[1])*vx
    side1=(b[0]-q[0])*vy-(b[1]-q[1])*vx
    if side0*side1>=0:return False
    fraction=side0/(side0-side1)
    point=tuple(a[i]+fraction*(b[i]-a[i]) for i in (0,1))
    future=obstacle.at(start+fraction*(end-start))
    longitudinal=((point[0]-future[0])*vx+(point[1]-future[1])*vy)/speed
    return longitudinal>-(obstacle.radius+robot_radius+.03)
