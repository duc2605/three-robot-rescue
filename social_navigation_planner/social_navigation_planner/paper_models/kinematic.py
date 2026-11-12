"""Paper3 Eqs3–6/12 and Paper4 Eq9, with documented omni conversions.

All poses/velocities and obstacles are WORLD frame. A command is (vx, vy, w).
No D*, emergency A*, baseline MPC, formation coordinator, or ground-truth humans.
Numerical gains/sampling are experiment parameters, not author benchmark values.
"""
import math


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def clip(x, lo, hi):
    return max(lo, min(hi, x))


def limit(x, y, maximum):
    scale = min(1., maximum / max(1e-12, math.hypot(x, y)))
    return x * scale, y * scale


def v_targets(poses, leader, waypoint, gap=.7, width=.5):
    """Paper3 Eq5–6: fixed separation/bearing from the MEASURED leader."""
    x, y, heading = poses[leader]
    targets = [None] * len(poses)
    targets[leader] = tuple(waypoint)
    for rank, i in enumerate(j for j in range(len(poses)) if j != leader):
        side = width if rank == 0 else -width
        targets[i] = (x - gap * math.cos(heading) - side * math.sin(heading),
                      y - gap * math.sin(heading) + side * math.cos(heading))
    return targets


def pursuit(pose, target, speed=.28, max_w=1.2):
    dx, dy = target[0] - pose[0], target[1] - pose[1]
    distance = math.hypot(dx, dy)
    if distance < .06:
        return (0., 0., 0.)
    alpha = wrap(math.atan2(dy, dx) - pose[2])
    if abs(alpha) > math.pi / 2:
        return (0., 0., clip(2 * alpha, -max_w, max_w))
    v = min(speed, distance) * max(0., math.cos(alpha))
    w = clip(2 * v * math.sin(alpha) / max(.18, distance), -max_w, max_w)
    return v * math.cos(pose[2]), v * math.sin(pose[2]), w


def vo_collision(pose, velocity, obstacle, horizon=3., radius=.18):
    """Finite-horizon ray / Minkowski disk intersection (Paper3 Eq12).

    obstacle=(x,y,vx,vy,r). The finite horizon and disk fit are adaptations.
    """
    x, y, vx, vy, r = obstacle
    px, py = x - pose[0], y - pose[1]
    rx, ry = velocity[0] - vx, velocity[1] - vy
    speed2 = rx * rx + ry * ry
    t = clip((px * rx + py * ry) / max(speed2, 1e-12), 0., horizon)
    return (px - rx * t) ** 2 + (py - ry * t) ** 2 < (radius + r) ** 2


def vo_command(pose, target, obstacles, speed=.28, max_w=1.2):
    preferred = pursuit(pose, target, speed, max_w)
    # Holonomic candidate velocities exploit the SAME omni platform. This is
    # an explicit conversion of the paper's nonholonomic VO output interface.
    candidates = [preferred, (0., 0., preferred[2])]
    for scale in (.4, .7, 1.):
        for k in range(24):
            angle = pose[2] + 2 * math.pi * k / 24
            candidates.append((speed * scale * math.cos(angle),
                               speed * scale * math.sin(angle), preferred[2]))
    feasible = [v for v in candidates if not any(vo_collision(pose, v, o) for o in obstacles)]
    if not feasible:
        return (0., 0., 0.)
    def score(v):
        deviation = (v[0] - preferred[0]) ** 2 + (v[1] - preferred[1]) ** 2
        progress = math.hypot(target[0] - pose[0] - v[0], target[1] - pose[1] - v[1])
        return deviation + .15 * progress
    return min(feasible, key=score)


class Impedance:
    """Paper4 Eq9 outer acceleration law; I=1, B=2, K=1 experiment gains.

    Human reference becomes robot reference. The Pioneer theta-model inverse
    is NOT reproduced: an ideal omni velocity actuator integrates acceleration.
    """
    def __init__(self):
        self.previous_targets = None
        self.previous_velocity = [(0., 0.)] * 3

    def commands(self, poses, targets, velocities, obstacles, dt):
        output, reference_velocity = [], []
        for i, (pose, target) in enumerate(zip(poses, targets)):
            rd = (0., 0.) if self.previous_targets is None else tuple(
                (target[k] - self.previous_targets[i][k]) / dt for k in range(2))
            rd = limit(*rd, .28)
            rdd = tuple(clip((rd[k] - self.previous_velocity[i][k]) / dt, -.8, .8) for k in range(2))
            # Repulsive fictitious force is subtracted in Eq9. Use positive
            # direction toward each obstacle so the acceleration points away.
            force = [0., 0.]
            for ox, oy, _, _, radius in obstacles[i]:
                dx, dy = ox - pose[0], oy - pose[1]
                d = math.hypot(dx, dy)
                clearance = max(0., d - radius - .15)
                if clearance < .6 and d > 1e-8:
                    strength = .8 * (1. - (clearance / .6) ** 2)
                    force[0] += strength * dx / d
                    force[1] += strength * dy / d
            acc = [rdd[k] + 2 * (rd[k] - velocities[i][k])
                   + (target[k] - pose[k]) - force[k] for k in range(2)]
            vx, vy = limit(*(velocities[i][k] + dt * clip(acc[k], -.8, .8) for k in range(2)), .28)
            heading = math.atan2(vy, vx) if math.hypot(vx, vy) > .02 else pose[2]
            output.append((vx, vy, clip(2 * wrap(heading - pose[2]), -1.2, 1.2)))
            reference_velocity.append(rd)
        self.previous_targets = list(targets)
        self.previous_velocity = reference_velocity
        return output
