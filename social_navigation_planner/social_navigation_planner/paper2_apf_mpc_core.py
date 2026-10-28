"""Independent APF-MPC integration, based on She et al., Drones 9(1):39.

DOI 10.3390/drones9010039. Not author code or a validated reproduction.
Planar world-velocity inputs replace four Mecanum wheel inputs; reduced
horizons and explicit swept-footprint validation are integration choices.
"""
import math
import time
import numpy as np
from scipy.optimize import minimize


def limit(v, maximum):
    v = np.asarray(v, dtype=float)
    norm = float(np.linalg.norm(v))
    return v*min(1., maximum/max(norm, 1e-12))


def wrap(a):
    return (a+math.pi) % (2*math.pi)-math.pi


def virtual_target(leader, back, side):
    x, y, yaw = leader
    return np.array([x-back*math.cos(yaw)-side*math.sin(yaw),
                     y-back*math.sin(yaw)+side*math.cos(yaw)])


def leader_potential(positions, velocities, goal, obstacles, times,
                     rho=1.5, d0=.35, t0=.6, rep_gain=.012):
    """Eq10 and Eq11 functional form, a=rep_gain, b=1, c=2.

    Positive lower clipping of Ds (Eq12) and clearance distances instead of
    center distances are conservative integration adaptations. Obstacles are
    rows x,y,vx,vy,radius. Unknown velocity is zero, not invented motion.
    """
    p = np.atleast_2d(positions)
    v = np.atleast_2d(velocities)
    goal_distance = np.linalg.norm(p-np.asarray(goal), axis=1)
    value = goal_distance.copy()  # Katt=1, Eq10
    if len(obstacles) == 0:
        return value
    obs = np.asarray(obstacles, dtype=float)
    predicted = obs[None, :, :2]+np.asarray(times)[:, None, None]*obs[None, :, 2:4]
    delta = predicted-p[:, None, :]
    center_distance = np.maximum(np.linalg.norm(delta, axis=2), 1e-6)
    direction = delta/center_distance[:, :, None]
    speed = np.linalg.norm(v, axis=1)
    obs_speed = np.linalg.norm(obs[:, 2:4], axis=1)
    ca = np.sum(v[:, None, :]*direction, axis=2)/np.maximum(speed[:, None], 1e-9)
    cb = np.sum(-obs[None, :, 2:4]*direction, axis=2)/np.maximum(obs_speed[None, :], 1e-9)
    alpha = np.arccos(np.clip(ca, -1, 1))
    beta = np.arccos(np.clip(cb, -1, 1))
    ds = np.maximum(d0*.5, d0+t0*(obs_speed[None, :]*np.cos(beta/2)
                                   -speed[:, None]*abs(np.sin(alpha/2))))
    distance = np.maximum(center_distance-obs[None, :, 4]-.18, .025)
    rep = rep_gain*ds*np.log1p(goal_distance[:, None])/distance**2
    value += np.sum(np.where(center_distance < rho, rep, 0), axis=1)
    return value


def follower_potential(position, velocity, target, obstacles, rho=.85):
    """Position and approaching-velocity potentials, Eq30 and Eq32 forms."""
    if len(obstacles) == 0:
        return 0.
    p, velocity, target = map(np.asarray, (position, velocity, target))
    obs = np.asarray(obstacles)
    delta = obs[:, :2]-p
    center = np.maximum(np.linalg.norm(delta, axis=1), 1e-6)
    distance = np.maximum(center-obs[:, 4]-.18, .04)
    goal_distance = np.linalg.norm(p-target)
    factor = math.log1p(goal_distance)
    inv = np.maximum(0., 1/distance-1/rho)
    position_term = .5*.012*inv**2*factor
    # Closing projection is |v_rel|cos(theta). This avoids a finite-difference
    # derivative of a normalized zero relative velocity.
    closing = np.maximum(0., np.sum((velocity-obs[:, 2:4])*delta/center[:, None], axis=1))
    velocity_term = .12*closing*factor
    return float(np.sum(np.where(distance < rho, position_term+velocity_term, 0)))


def follower_velocity(position, velocity, target, target_velocity, obstacles,
                      dt=.1, vmax=.22, amax=.5):
    """Enhanced APF follower: Eq22 attraction + Eq29 repulsion.

    Vector gradients, rather than ambiguous unsigned scalar distances in the
    printed force equations. Gains and force-to-acceleration map are adapted.
    """
    p, velocity, target, target_velocity = map(np.asarray,
        (position, velocity, target, target_velocity))
    desired = limit(target-p, vmax)
    force = .9*(target-p)+1.2*(target_velocity-velocity)+.8*(desired-velocity)
    gradient = np.zeros(2)
    eps = .002
    for j in range(2):
        shift = np.zeros(2)
        shift[j] = eps
        gradient[j] = (follower_potential(p+shift, velocity, target, obstacles)
                       -follower_potential(p-shift, velocity, target, obstacles))/(2*eps)
    force -= gradient
    return limit(velocity+dt*limit(force, amax), vmax)


def predict_controls(start, controls, horizon=16, dt=.1):
    controls = np.asarray(controls).reshape(-1, 2)
    velocities = controls[np.minimum(np.arange(horizon), len(controls)-1)]
    points = np.asarray(start)+dt*np.cumsum(velocities, axis=0)
    return points, velocities


def project_controls(controls, current, vmax, delta):
    out, prev = [], np.asarray(current)
    for control in np.asarray(controls).reshape(-1, 2):
        control = limit(np.clip(control, prev-delta, prev+delta), vmax)
        out.append(control)
        prev = control
    return np.asarray(out)


def solve_mpc(start, goal, current, obstacles, warm=None, horizon=16,
              control_horizon=5, dt=.1, vmax=.18, amax=.5, budget=.15):
    """Continuous SLSQP receding-horizon optimizer, Eq21 structure.

    Optimizes the entire control sequence (not a one-step DWA). Objective:
    reference tracking + input increments + predicted APF. XY integrator is
    exact for world-frame holonomic velocities, replacing wheel-space model.
    An iteration-limited solve may return a feasible, explicitly marked
    suboptimal result. Budget exhaustion returns no seed-only command.
    Post-solve swept safety is mandatory in the ROS adapter.
    """
    started = time.monotonic()
    start, goal, current = map(lambda x: np.asarray(x, float), (start, goal, current))
    distance = float(np.linalg.norm(goal-start))
    if distance < .08:
        return np.zeros((control_horizon, 2)), {'solver': 'AT_GOAL', 'solve_ms': 0.}
    direction = (goal-start)/distance
    normal = np.array([-direction[1], direction[0]])
    times = dt*np.arange(1, horizon+1)
    reference = start+np.minimum(times*vmax, distance)[:, None]*direction
    seeds = []
    if warm is not None and np.asarray(warm).shape == (control_horizon, 2):
        seeds.append(np.vstack([warm[1:], warm[-1:]]))
    seeds.extend([np.tile(vmax*direction, (control_horizon, 1)),
                  np.tile(vmax*limit(direction+.85*normal, 1), (control_horizon, 1)),
                  np.tile(vmax*limit(direction-.85*normal, 1), (control_horizon, 1))])
    seeds = [project_controls(s, current, vmax, amax*dt).ravel() for s in seeds]
    def objective(flat):
        controls = flat.reshape(control_horizon, 2)
        positions, velocities = predict_controls(start, controls, horizon, dt)
        increments = np.diff(np.vstack([current, controls]), axis=0)
        return float(2*np.sum((positions-reference)**2)
                     +.35*np.sum(increments**2)
                     +.22*np.sum(leader_potential(positions, velocities, goal, obstacles, times)))
    def admissible(flat):
        controls = np.asarray(flat).reshape(control_horizon, 2)
        increments = np.diff(np.vstack([current, controls]), axis=0)
        return np.r_[vmax**2-np.sum(controls**2, axis=1),
                     amax*dt-abs(increments).ravel()]
    best, best_cost, best_kind = None, math.inf, 'NO_FEASIBLE_OPTIMIZER_RESULT'
    class Deadline(Exception):
        pass
    def callback(x):
        if time.monotonic()-started > budget:
            raise Deadline()
    successful = 0
    for seed in seeds:
        if time.monotonic()-started > budget:
            break
        candidate, kind = None, None
        try:
            result = minimize(objective, seed, method='SLSQP', bounds=[(-vmax, vmax)]*len(seed),
                              constraints=[{'type': 'ineq', 'fun': admissible}],
                              callback=callback, options={'maxiter': 22, 'ftol': 1e-5})
            if np.all(np.isfinite(result.x)) and np.min(admissible(result.x)) >= -1e-6:
                candidate = result.x
                kind = 'SLSQP_CONVERGED' if result.success else 'SLSQP_FEASIBLE_SUBOPTIMAL'
                successful += int(result.success)
        except Deadline:
            continue
        if candidate is None:
            continue
        cost = objective(candidate)
        if cost < best_cost and np.min(admissible(candidate)) >= -1e-6:
            best, best_cost, best_kind = candidate.copy(), cost, kind
    return (None if best is None else best.reshape(control_horizon, 2)), {
        'solver': best_kind, 'cost': best_cost if math.isfinite(best_cost) else None,
        'solve_ms': round(1000*(time.monotonic()-started), 2),
        'converged_seeds': successful, 'prediction_horizon': horizon,
        'control_horizon': control_horizon,
    }


def distance_segment(p, a, b):
    a, b, p = np.asarray(a[:2]), np.asarray(b[:2]), np.asarray(p[:2])
    d = b-a
    t = float(np.clip(np.dot(p-a, d)/max(np.dot(d, d), 1e-12), 0, 1))
    return float(np.linalg.norm(p-a-t*d))


def velocity_trace(position, velocity, dt=.1, horizon=1.6, amax=.5):
    p, velocity = np.asarray(position[:2], float), np.asarray(velocity, float)
    trace = [p.copy()]
    for _ in range(int(math.ceil(horizon/dt))):
        p = p+dt*velocity
        trace.append(p.copy())
    speed = float(np.linalg.norm(velocity))
    while speed > 1e-8:
        new_speed = max(0., speed-amax*dt)
        p = p+dt*(velocity+velocity*new_speed/speed)/2
        velocity = velocity*new_speed/speed
        trace.append(p.copy())
        speed = new_speed
    return trace


def trace_safe(trace, grid, obstacles, peers=(), dt=.1, margin=.20):
    """Swept map cells, relative obstacle motion and relative peer segments."""
    obs = np.asarray(obstacles).reshape(-1, 5)
    for k, (a, b) in enumerate(zip(trace, trace[1:])):
        if grid.segment_clearance(a, b, margin) < margin-1e-9:
            return False
        for row in obs:
            oa = row[:2]+row[2:4]*k*dt
            ob = row[:2]+row[2:4]*(k+1)*dt
            if distance_segment((0, 0), a-oa, b-ob) < margin+row[4]+.03:
                return False
        for peer in peers:
            pa, pb = peer[min(k, len(peer)-1)], peer[min(k+1, len(peer)-1)]
            if distance_segment((0, 0), a-pa, b-pb) < 2*margin+.03:
                return False
    return True
