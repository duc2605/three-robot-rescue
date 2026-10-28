"""Paper 1 integration: GWO/WOA path search, DWA and virtual followers.

Reference: Zhou et al., JACIII 26(3), 342-354 (2022),
doi:10.20965/jaciii.2022.p0342. Independent implementation, not author code.
See README_PAPER1_GWO_WOA.md for the explicit adaptations and limits.
"""
import math
import time
import numpy as np


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def spline_matrix(knots, samples):
    """Natural cubic spline basis on equally spaced knots (integration choice)."""
    t = np.linspace(0.0, knots - 1, samples)
    j = np.minimum(t.astype(int), knots - 2)
    u = t - j
    eye = np.eye(knots)
    a = np.zeros((knots, knots))
    a[0, 0] = a[-1, -1] = 1
    for k in range(1, knots - 1):
        a[k, k - 1:k + 2] = (1, 4, 1)
    rhs = np.zeros((knots, knots))
    rhs[1:-1] = 6 * (eye[2:] - 2 * eye[1:-1] + eye[:-2])
    second = np.linalg.solve(a, rhs)
    return ((1-u[:, None]) * eye[j] + u[:, None] * eye[j+1]
            + (((1-u)**3-(1-u))[:, None] * second[j]
               + (u**3-u)[:, None] * second[j+1]) / 6)


def gwo_woa(start, goal, grid, inflated, seed=7, population=48,
            iterations=70, interior=4, budget=2.0):
    """One-dimensional search in start-goal coordinates, Sec. 4.2.2.

    Tent initialization, three elites and spiral / random-prey updates.
    No A* or D* fallback. A failed search returns None, not an unsafe route.
    Grid footprint checking replaces the paper's circular-obstacle model.
    """
    begin = time.monotonic()
    start, goal = np.array(start[:2], float), np.array(goal[:2], float)
    length = float(np.linalg.norm(goal-start))
    if not grid.point_free(start) or not grid.point_free(goal):
        return None, {'reason': 'ENDPOINT_BLOCKED', 'iterations': 0}
    if length < 1e-6:
        return [tuple(start), tuple(goal)], {'reason': 'AT_GOAL', 'iterations': 0}
    tangent = (goal-start)/length
    normal = np.array([-tangent[1], tangent[0]])
    # Permit transverse detours across the map; monotone longitudinal progress
    # remains a limitation of the paper's one-dimensional representation.
    span = max(grid.width, grid.height)*grid.resolution
    low, high = -span, span
    rng = np.random.default_rng(seed)
    chaos = rng.uniform(0.01, 0.99, (population, interior))
    for _ in range(5):
        chaos = np.where(chaos < .5, 2*chaos, 2*(1-chaos))
    wolves = low+(high-low)*chaos
    # Extra feasible initial candidates near the straight line. This is an
    # engineering adaptation, not an equation claimed from the paper.
    wolves[0] = 0
    for i, offset in enumerate(np.linspace(-2, 2, min(population-1, 15)), 1):
        wolves[i] = offset*np.sin(np.linspace(0, math.pi, interior+2)[1:-1])
    samples = max(64, int((length+2*span)/(grid.resolution*.4)))
    samples = min(samples, 1800)
    basis = spline_matrix(interior+2, samples)
    along = np.linspace(0, length, samples)
    inflated = np.array(inflated, dtype=bool).reshape(grid.height, grid.width)
    def curves(values):
        offsets = np.pad(values, ((0, 0), (1, 1))) @ basis.T
        return start + along[None, :, None]*tangent + offsets[:, :, None]*normal
    def evaluate(values):
        paths = curves(values)
        dx, dy = paths[:, :, 0]-grid.origin_x, paths[:, :, 1]-grid.origin_y
        xx = grid.cosine*dx+grid.sine*dy
        yy = -grid.sine*dx+grid.cosine*dy
        gx = np.floor(xx/grid.resolution).astype(int)
        gy = np.floor(yy/grid.resolution).astype(int)
        outside = ((gx < 0) | (gy < 0) | (gx >= grid.width) | (gy >= grid.height))
        hits = outside | inflated[np.clip(gy, 0, grid.height-1), np.clip(gx, 0, grid.width-1)]
        lengths = np.linalg.norm(np.diff(paths, axis=1), axis=2).sum(axis=1)
        return hits.sum(axis=1)*10000.0 + lengths
    best_value, best = float('inf'), None
    completed = 0
    for step in range(iterations+1):
        fitness = evaluate(wolves)
        order = np.argsort(fitness)
        if fitness[order[0]] < best_value:
            best_value, best = float(fitness[order[0]]), wolves[order[0]].copy()
        completed = step
        if step == iterations or time.monotonic()-begin >= budget:
            break
        elite = wolves[order[:3]].copy()
        alpha = 2*(1-step/max(1, iterations))
        updated = np.empty_like(wolves)
        for i, current in enumerate(wolves):
            A = 2*alpha*rng.random(interior)-alpha
            C = 2*rng.random(interior)
            if rng.random() < .5:
                # Follow Sec. 4.1.4: exploration uses random prey at |A|>=1.
                prey = wolves[rng.integers(population)] if np.max(abs(A)) >= 1 else elite[0]
                updated[i] = prey-A*abs(C*prey-current)
            else:
                candidates = []
                for prey in elite:
                    l = rng.random()
                    distance = abs(C*prey-current)
                    candidates.append(prey-A*distance if rng.random() < .5 else
                                      prey+distance*math.exp(l)*math.cos(2*math.pi*l))
                updated[i] = np.mean(candidates, axis=0)
        wolves = np.clip(updated, low, high)
        wolves[0] = best  # Elitism is an explicit integration choice.
    route = curves(best[None])[0]
    # Exact swept-circle checks, including between samples, on the final path.
    valid = best_value < 10000 and all(grid.segment_free(a, b) for a, b in zip(route, route[1:]))
    return ([tuple(p) for p in route] if valid else None), {
        'reason': 'ROUTE_READY' if valid else 'GWO_SEARCH_FAILED',
        'iterations': completed, 'plan_ms': round(1000*(time.monotonic()-begin), 2),
        'seed': seed, 'cost': best_value,
    }


def virtual_target(leader, back, side):
    x, y, yaw = leader[:3]
    c, s = math.cos(yaw), math.sin(yaw)
    return (x-back*c-side*s, y-back*s+side*c, yaw)


def follower_control(actual, desired, vref, wref, k1=.8, k2=1.5):
    """Paper Eq. (32), with errors in Eq. (3); saturation applied by caller."""
    x, y, yaw = actual[:3]
    dx, dy = desired[0]-x, desired[1]-y
    ex = math.cos(yaw)*dx+math.sin(yaw)*dy
    ey = -math.sin(yaw)*dx+math.cos(yaw)*dy
    ephi = wrap(desired[2]-yaw)
    return vref*math.cos(ephi)+k1*ex, wref+vref*ey+k2*math.sin(ephi)


def rollout(pose, v, w, horizon=1.8, dt=.15, brake=.5):
    """Constant command prediction plus an explicit linear/angular stop tail."""
    x, y, yaw = map(float, pose[:3])
    result = [(x, y, yaw)]
    for _ in range(int(math.ceil(horizon/dt))):
        x += v*math.cos(yaw+w*dt/2)*dt
        y += v*math.sin(yaw+w*dt/2)*dt
        yaw = wrap(yaw+w*dt)
        result.append((x, y, yaw))
    vv, ww = v, w
    while abs(vv) > 1e-9 or abs(ww) > 1e-9:
        vn = math.copysign(max(0, abs(vv)-brake*dt), vv)
        wn = math.copysign(max(0, abs(ww)-2*dt), ww)
        vm, wm = (vv+vn)/2, (ww+wn)/2
        x += vm*math.cos(yaw+wm*dt/2)*dt
        y += vm*math.sin(yaw+wm*dt/2)*dt
        yaw = wrap(yaw+wm*dt)
        result.append((x, y, yaw))
        vv, ww = vn, wn
    return result


def point_segment_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = dx*dx+dy*dy
    t = min(1, max(0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)) if length else 0
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)


def pair_clear(first, second, separation):
    """Continuous pair separation over synchronous piecewise-linear sweeps."""
    n = max(len(first), len(second))
    previous = None
    for k in range(n):
        a, b = first[min(k, len(first)-1)], second[min(k, len(second)-1)]
        relative = (a[0]-b[0], a[1]-b[1])
        if math.hypot(*relative) < separation:
            return False
        if previous is not None and point_segment_distance((0, 0), previous, relative) < separation:
            return False
        previous = relative
    return True


def trajectory_safe(trajectory, grid, points, peers, radius=.18):
    """Static/social grid, live LiDAR endpoints and swept peer footprints."""
    # Small chord margin accounts for curved motion between .15 s samples.
    margin = radius + .003
    for a, b in zip(trajectory, trajectory[1:]):
        if grid.segment_clearance(a, b, margin) < margin-1e-9:
            return False
        if any(point_segment_distance(p, a, b) < margin+.04 for p in points):
            return False
    return all(pair_clear(trajectory, peer, 2*margin+.04) for peer in peers)


def dwa(pose, current, target, grid, points, peers, dt=.1, desired=None,
        vmax=.22, wmax=.9, accel=.5, angular_accel=2.0, forward_only=False):
    """Dynamic window, rollout and normalized Eq. (31)-style scoring.

    Followers use Eq. (32) directly if admissible; DWA is an added safety
    filter when that command is not collision-free. No lateral velocity.
    """
    vlo, vhi = max(-.10, current[0]-accel*dt), min(vmax, current[0]+accel*dt)
    wlo, whi = max(-wmax, current[1]-angular_accel*dt), min(wmax, current[1]+angular_accel*dt)
    # PAPER1_FORWARD_CAMERA_V1: leader faces the direction of travel.
    # A backward goal requires a checked turn, never a reverse command.
    if forward_only:
        if current[0] < 0:
            return (0., 0.), rollout(pose, 0., 0.), 'BRAKE_REVERSE'
        vlo, vhi = max(0., vlo), max(0., vhi)
        bearing = math.atan2(target[1]-pose[1], target[0]-pose[0])
        if abs(wrap(bearing-pose[2])) > .65:
            # Decelerate before the turn; allow only pure rotation at rest.
            vlo = vhi = max(0., current[0]-accel*dt)
    vs, ws = list(np.linspace(vlo, vhi, 5)), list(np.linspace(wlo, whi, 11))
    if desired is not None:
        dv, dw = np.clip(desired[0], vlo, vhi), np.clip(desired[1], wlo, whi)
        trace = rollout(pose, dv, dw)
        if trajectory_safe(trace, grid, points, peers):
            return (float(dv), float(dw)), trace, 'EQ32'
        vs.append(float(dv))
        ws.append(float(dw))
    candidates, features = [], []
    # Include reachable zero values; an emergency stop is handled separately.
    if vlo <= 0 <= vhi:
        vs.append(0.)
    if wlo <= 0 <= whi:
        ws.append(0.)
    for v in vs:
        for w in ws:
            trajectory = rollout(pose, v, w)
            if not trajectory_safe(trajectory, grid, points, peers):
                continue
            end = trajectory[min(12, len(trajectory)-1)]
            goal_heading = math.atan2(target[1]-end[1], target[0]-end[0])
            heading = math.pi-abs(wrap(goal_heading-end[2]))
            progress = math.dist(pose[:2], target[:2])-math.dist(end[:2], target[:2])
            clearance = min(grid.clearance(p[:2], .6) for p in trajectory[::3])
            candidates.append(((float(v), float(w)), trajectory))
            # Progress is an integration addition to reduce spinning at the goal.
            features.append((heading, clearance, float(v), progress))
    if not candidates:
        return (0., 0.), rollout(pose, 0., 0.), 'NO_SAFE_COMMAND'
    f = np.array(features)
    f = (f-f.min(axis=0))/np.maximum(np.ptp(f, axis=0), 1e-9)
    best = int(np.argmax(f @ np.array([.20, .15, .10, .55])))
    command, trace = candidates[best]
    return command, trace, 'DWA' if desired is None else 'DWA_SAFETY_FILTER'
