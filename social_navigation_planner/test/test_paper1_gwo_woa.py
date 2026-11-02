"""Offline numerical checks; no ROS/Gazebo runtime is implied by these tests."""
import math
import time
import unittest
from social_navigation_planner.grid_clearance import GridClearance
from social_navigation_planner.paper1_gwo_woa_core import (
    gwo_woa, follower_control, virtual_target, rollout, pair_clear, dwa,
    trajectory_safe, spline_matrix,
)
import numpy as np


def grid(obstacles=()):
    width, height, res = 100, 80, .05
    raw = [False]*(width*height)
    for xmin, ymin, xmax, ymax in obstacles:
        for y in range(height):
            for x in range(width):
                if xmin <= (x+.5)*res <= xmax and ymin <= (y+.5)*res <= ymax:
                    raw[y*width+x] = True
    g = GridClearance(width, height, res, (0, 0, 0), raw, .18)
    # Conservative search occupancy, same geometric footprint as final checker.
    inflated = [not g.point_free(((x+.5)*res, (y+.5)*res))
                for y in range(height) for x in range(width)]
    return g, inflated


class Paper1Checks(unittest.TestCase):
    def test_spline_interpolates_knots(self):
        np.testing.assert_allclose(spline_matrix(5, 5), np.eye(5), atol=1e-12)

    def test_open_route(self):
        g, occupied = grid()
        route, info = gwo_woa((.5, 2), (4.5, 2), g, occupied, iterations=10)
        self.assertIsNotNone(route, info)
        self.assertLess(sum(math.dist(a, b) for a, b in zip(route, route[1:])), 4.01)

    def test_detour_is_swept_collision_free(self):
        g, occupied = grid(((2, 1.4, 2.7, 2.6),))
        route, info = gwo_woa((.5, 2), (4.5, 2), g, occupied, seed=7)
        self.assertIsNotNone(route, info)
        self.assertTrue(all(g.segment_free(a, b) for a, b in zip(route, route[1:])))
        self.assertGreater(max(abs(p[1]-2) for p in route), .7)

    def test_sealed_wall_returns_failure_not_fallback(self):
        g, occupied = grid(((2, 0, 2.3, 4),))
        route, info = gwo_woa((.5, 2), (4.5, 2), g, occupied, iterations=15)
        self.assertIsNone(route)
        self.assertEqual(info['reason'], 'GWO_SEARCH_FAILED')

    def test_blocked_goal(self):
        g, occupied = grid(((4, 1, 4.8, 3),))
        self.assertIsNone(gwo_woa((.5, 2), (4.5, 2), g, occupied)[0])

    def test_eq32_converges_for_moving_straight_reference(self):
        pose = (-.8, .25, .2)
        # Eq32's lateral correction is slow at 0.1 m/s; check asymptotic
        # convergence over 300 simulated seconds, not an invented fast bound.
        for k in range(15000):
            ref = (.1*k*.02, 0, 0)
            v, w = follower_control(pose, ref, .1, 0)
            x, y, yaw = pose
            pose = (x+v*math.cos(yaw)*.02, y+v*math.sin(yaw)*.02, yaw+w*.02)
        self.assertLess(math.dist(pose[:2], (30, 0)), .08)

    def test_virtual_offsets_rotate_with_leader(self):
        p = virtual_target((3.5, -2.2, math.pi/2), .7, .5)
        np.testing.assert_allclose(p[:2], (3, -2.9), atol=1e-9)

    def test_peer_crossing_between_samples_is_rejected(self):
        self.assertFalse(pair_clear([(0, 0), (1, 0)], [(.5, -.5), (.5, .5)], .3))

    def test_dwa_dynamic_window_and_safe_braking(self):
        g, _ = grid(((1.15, .5, 1.3, 3.5),))
        command, trace, mode = dwa((.8, 2, 0), (.1, 0), (4, 2, 0), g, [], [])
        self.assertLessEqual(abs(command[0]-.1), .050001)
        self.assertLessEqual(abs(command[1]), .200001)
        self.assertTrue(trajectory_safe(trace, g, [], []))

    def test_lidar_and_peers_block_eq32(self):
        g, _ = grid()
        command, trace, mode = dwa((1, 2, 0), (.1, 0), (4, 2, 0), g,
                                    [(1.4, 2)], [rollout((1.7, 2, 0), 0, 0)],
                                    desired=(.15, 0))
        self.assertNotEqual(mode, 'EQ32')
        self.assertTrue(trajectory_safe(trace, g, [(1.4, 2)],
                                        [rollout((1.7, 2, 0), 0, 0)]))

    def test_numerical_goal_reaching_with_dwa(self):
        g, _ = grid()
        pose, command = (1, 2, .4), (0, 0)
        for _ in range(160):
            if math.dist(pose[:2], (2, 2)) < .12:
                break
            command, _, _ = dwa(pose, command, (2, 2, 0), g, [], [])
            v, w = command
            pose = (pose[0]+v*math.cos(pose[2]+w*.05)*.1,
                    pose[1]+v*math.sin(pose[2]+w*.05)*.1, pose[2]+w*.1)
        self.assertLess(math.dist(pose[:2], (2, 2)), .12)

    def test_camera_leader_turns_instead_of_reversing(self):
        g, _ = grid()
        command, trace, mode = dwa((2, 2, 0), (0, 0), (1, 2, 0),
                                    g, [], [], forward_only=True)
        self.assertEqual(command[0], 0.)
        self.assertGreater(abs(command[1]), 0.)
        self.assertTrue(trajectory_safe(trace, g, [], []))

    def test_camera_leader_brakes_before_turn(self):
        g, _ = grid()
        command, trace, mode = dwa((2, 2, 0), (.16, 0), (1, 2, 0),
                                    g, [], [], forward_only=True)
        self.assertGreaterEqual(command[0], 0.)
        self.assertLessEqual(command[0], .110001)

    def test_camera_leader_forward_only_reaches_backward_goal(self):
        g, _ = grid()
        pose, command = (2, 2, 0), (0, 0)
        for _ in range(240):
            if math.dist(pose[:2], (1, 2)) < .12:
                break
            command, _, _ = dwa(pose, command, (1, 2, 0), g, [], [], forward_only=True)
            self.assertGreaterEqual(command[0], 0.)
            v, w = command
            pose = (pose[0]+v*math.cos(pose[2]+w*.05)*.1,
                    pose[1]+v*math.sin(pose[2]+w*.05)*.1, pose[2]+w*.1)
        self.assertLess(math.dist(pose[:2], (1, 2)), .12)


if __name__ == '__main__':
    unittest.main()
