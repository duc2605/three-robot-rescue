"""Offline checks for the independent paper2 adaptation, not Gazebo validation."""
import ast
import math
from pathlib import Path
import unittest
import numpy as np
from social_navigation_planner.grid_clearance import GridClearance
from social_navigation_planner.paper2_apf_mpc_core import (
    leader_potential, follower_velocity, follower_potential, solve_mpc,
    predict_controls, virtual_target, velocity_trace, trace_safe,
)


class Paper2Checks(unittest.TestCase):
    def test_potential_zero_at_goal(self):
        cost = leader_potential([[2., 0]], [[0., 0]], (2, 0), [(2, .5, 0, 0, .05)], [.1])
        self.assertAlmostEqual(cost[0], 0.)

    def test_potential_increases_near_obstacle(self):
        a = leader_potential([[0., 0]], [[0., 0]], (2, 0), [(.4, 0, 0, 0, .05)], [.1])
        b = leader_potential([[0., 0]], [[0., 0]], (2, 0), [(1.2, 0, 0, 0, .05)], [.1])
        self.assertGreater(a[0], b[0])

    def test_moving_obstacle_predicted_position(self):
        approach = leader_potential([[0., 0]], [[.1, 0]], (2, 0), [(1., 0, -.3, 0, .05)], [1.])
        recede = leader_potential([[0., 0]], [[.1, 0]], (2, 0), [(1., 0, .3, 0, .05)], [1.])
        self.assertGreater(approach[0], recede[0])

    def test_follower_tracks_straight_virtual_target(self):
        p, v = np.array([-.8, .25]), np.zeros(2)
        for k in range(300):
            ref = np.array([.1*k*.1, 0.])
            v = follower_velocity(p, v, ref, (.1, 0), [])
            p += .1*v
        self.assertLess(np.linalg.norm(p-np.array([3, 0])), .12)

    def test_follower_repulsion_and_accel_bound(self):
        a = follower_velocity((0, 0), (0, 0), (2, 0), (.1, 0), [])
        b = follower_velocity((0, 0), (0, 0), (2, 0), (.1, 0), [(.35, .1, 0, 0, .05)])
        self.assertLessEqual(np.linalg.norm(b), .050001)
        self.assertLess(b[1], a[1])

    def test_mpc_open_goal_and_increment_constraints(self):
        current = np.array([.04, 0])
        controls, info = solve_mpc((0, 0), (2, 0), current, [], budget=.5)
        self.assertIsNotNone(controls, info)
        self.assertTrue(info['solver'].startswith('SLSQP'), info)
        self.assertGreater(controls[0, 0], 0)
        self.assertTrue(np.all(np.linalg.norm(controls, axis=1) <= .180001))
        self.assertTrue(np.all(abs(np.diff(np.vstack([current, controls]), axis=0)) <= .050001))

    def test_budget_exhaustion_does_not_execute_an_unoptimized_seed(self):
        controls, info = solve_mpc((0, 0), (2, 0), (0, 0), [], budget=0.)
        self.assertIsNone(controls)
        self.assertEqual(info['solver'], 'NO_FEASIBLE_OPTIMIZER_RESULT')

    def test_mpc_avoids_static_disc_on_prediction(self):
        obs = [(.6, 0, 0, 0, .15)]
        controls, info = solve_mpc((0, 0), (2, 0), (0, 0), obs, budget=.5)
        positions, _ = predict_controls((0, 0), controls)
        clearance = np.linalg.norm(positions-np.array([.6, 0]), axis=1)-.15
        self.assertGreater(float(clearance.min()), .20)
        self.assertGreater(float(np.max(abs(positions[:, 1]))), .02)

    def test_swept_lidar_collision(self):
        grid = GridClearance(100, 80, .05, (-2, -2, 0), [False]*8000, .18)
        trace = [np.array([0., 0]), np.array([1., 0])]
        self.assertFalse(trace_safe(trace, grid, [(.5, 0, 0, 0, .02)]))

    def test_swept_peer_crossing(self):
        grid = GridClearance(100, 80, .05, (-2, -2, 0), [False]*8000, .18)
        self.assertFalse(trace_safe([np.array([0., 0]), np.array([1., 0])], grid, [],
                                   [[np.array([.5, -.5]), np.array([.5, .5])]]))

    def test_map_collision_in_braking_tail(self):
        raw = [False]*8000
        # Cell surface at x=1.0 m. Command plus tail would enter its footprint.
        for y in range(80):
            raw[y*100+20] = True
        grid = GridClearance(100, 80, .05, (0, 0, 0), raw, .18)
        trace = velocity_trace((.7, 2), (.2, 0), horizon=.4)
        self.assertFalse(trace_safe(trace, grid, []))

    def test_virtual_triangle(self):
        np.testing.assert_allclose(virtual_target((3.5, -2.2, math.pi/2), .7, .5), (3, -2.9))

    def test_mpc_receding_horizon_reaches_goal(self):
        position, current, warm = np.zeros(2), np.zeros(2), None
        for _ in range(75):
            if np.linalg.norm(position-np.array([.65, 0])) < .1:
                break
            warm, info = solve_mpc(position, (.65, 0), current, [], warm=warm, budget=.2)
            self.assertIsNotNone(warm, info)
            current = warm[0]
            position += .1*current
        self.assertLess(np.linalg.norm(position-np.array([.65, 0])), .1)


if __name__ == '__main__':
    unittest.main()
