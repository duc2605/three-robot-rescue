"""DEFORM, DOI10.1109/LRA.2025.3552998, Eqs2–8; explicit three-omni port.

Same nonholonomic prediction, reduced horizon12 (author40), SLSQP rather
than CasADi/IPOPT. Formation library is V/column for THREE robots, not the
four-robot author library. Central transport of snapshots emulates peer
messages; this is not a distributed scheduling/network experiment.
"""
import math
import numpy as np
from scipy.optimize import linear_sum_assignment, minimize
from .kinematic import clip, wrap


class Deform:
    def __init__(self, leader):
        self.leader = leader
        self.assignment = list(range(3))
        self.warm = [None] * 3
        self.previous_prediction = [None] * 3
        self.last_assignment = -math.inf
        self.status = ['uninitialized'] * 3

    def targets(self, poses, waypoint, grid, now):
        anchor = poses[self.leader][:2]
        angle = math.atan2(waypoint[1] - anchor[1], waypoint[0] - anchor[0])
        tangent = np.array([math.cos(angle), math.sin(angle)])
        normal = np.array([-tangent[1], tangent[0]])
        goal = np.asarray(waypoint, dtype=float)
        # Eqs2/4: goal attraction + obstacle-distance penalty. Bounded local
        # numerical minimization; failure leaves the original waypoint.
        def refine(center, clearance):
            def cost(p):
                return 4. * max(clearance - grid.clearance(p, clearance), 0.) ** 2 + float(np.sum((p-center)**2))
            result = minimize(cost, center, method='Powell',
                              bounds=[(center[k]-.3, center[k]+.3) for k in range(2)],
                              options={'maxiter': 12})
            return result.x if result.success and grid.point_free(result.x) else center
        goal = refine(goal, .65)
        # Eq3 corridor width: scan parallel free lines, along local reference.
        # Grid sampling at5cm is an explicit discretization of width geometry.
        extent = []
        for sign in (-1., 1.):
            distance = 0.
            for value in np.arange(.05, .81, .05):
                offset = sign * value * normal
                if not grid.segment_free(np.asarray(anchor)+offset, goal+offset):
                    break
                distance = float(value)
            extent.append(distance)
        goal = refine(goal + .5 * (extent[1]-extent[0]) * normal, .22)
        width = min(.5, .5 * sum(extent))
        local = [(0., 0.), (-.7, width), (-.7, -width)] if width >= .24 else [(0., 0.), (-.7, 0.), (-1.4, 0.)]
        offsets = [a*tangent+b*normal for a,b in local]
        slots = [goal + offset for offset in offsets]
        # Eq5 Hungarian assignment. Hysteresis/rate limit avoids swapping on
        # noisy widths; these are integration choices, not author guarantees.
        if now - self.last_assignment >= 1.:
            cost = np.array([[np.sum((np.asarray(p[:2])-s)**2) for s in slots] for p in poses])
            rows, cols = linear_sum_assignment(cost)
            candidate = [0]*3
            for r,c in zip(rows, cols): candidate[int(r)] = int(c)
            old = sum(cost[i, self.assignment[i]] for i in range(3))
            new = sum(cost[i, candidate[i]] for i in range(3))
            if new < old - .08:
                self.assignment = candidate
                self.leader = self.assignment.index(0)
            self.last_assignment = now
        # Eq6, complete neighbor graph. Offset correction plus virtual slot.
        targets = []
        for i in range(3):
            si = self.assignment[i]
            target = slots[si].copy()
            for j in range(3):
                if j != i:
                    target += np.asarray(poses[j][:2]) + offsets[si] - offsets[self.assignment[j]]
            targets.append(tuple(target/3.))
        return targets

    def commands(self, poses, targets, velocities, obstacles, dt, grid):
        horizon, step = 12, .1
        predictions = list(self.previous_prediction)
        answers, new_predictions = [], []
        for i in range(3):
            def rollout(flat):
                controls = flat.reshape(horizon, 2)
                state = np.asarray(poses[i], dtype=float).copy()
                path = []
                for v,w in controls:
                    state = state + step*np.array([v*math.cos(state[2]),v*math.sin(state[2]),w])
                    path.append(state.copy())
                return np.array(path)
            distance = math.dist(poses[i][:2], targets[i])
            vref = .28 * min(distance/.6, 1.)
            heading_error = wrap(math.atan2(targets[i][1]-poses[i][1],targets[i][0]-poses[i][0])-poses[i][2])
            wref = 1.2/math.pi*heading_error
            def cost(flat):
                path = rollout(flat)
                controls = flat.reshape(horizon,2)
                # Eq8, theta weight0 as author; no negative slack permitted
                # for this contact-sensitive experiment (stricter than paper).
                return float(.1*np.sum((path[:,:2]-targets[i])**2)
                             + .02*np.sum((controls-[vref,wref])**2))
            def constraints(flat):
                path = rollout(flat)
                values = []
                previous = poses[i][:2]
                for k,p in enumerate(path):
                    values.append(grid.segment_clearance(previous,p[:2],.5)-.18)
                    previous = p[:2]
                    for j in range(3):
                        if j == i: continue
                        peer = predictions[j][min(k+1,horizon-1),:2] if predictions[j] is not None else np.array(poses[j][:2])+step*(k+1)*np.array(velocities[j][:2])
                        values.append(float(np.linalg.norm(p[:2]-peer))-.36)
                    for ox,oy,vx,vy,r in obstacles[i]:
                        values.append(math.hypot(p[0]-ox-(k+1)*step*vx,p[1]-oy-(k+1)*step*vy)-r-.18)
                return np.array(values)
            guess = self.warm[i] if self.warm[i] is not None else np.tile([vref,wref],horizon)
            result = minimize(cost,guess,method='SLSQP',bounds=[(0.,.28),(-1.2,1.2)]*horizon,
                              constraints=[{'type':'ineq','fun':constraints}],
                              options={'maxiter':20,'ftol':1e-4})
            valid = result.success and np.all(np.isfinite(result.x)) and np.min(constraints(result.x)) >= -1e-5
            if valid:
                path = rollout(result.x)
                v,w = result.x[:2]
                answers.append((v*math.cos(poses[i][2]),v*math.sin(poses[i][2]),float(w)))
                self.warm[i] = np.r_[result.x[2:],result.x[-2:]]
                self.status[i] = 'mpc_feasible'
            else:
                answers.append((0.,0.,0.))
                path = np.tile(poses[i],(horizon,1))
                self.warm[i] = None
                self.status[i] = 'mpc_infeasible_or_iteration_limit'
            new_predictions.append(path)
        self.previous_prediction = new_predictions
        return answers
