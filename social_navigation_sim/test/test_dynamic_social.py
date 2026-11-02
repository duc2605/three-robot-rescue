"""Scenario continuity, map isolation and sensor-derived state transitions."""
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

import cv2
import numpy as np

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE/'scripts'))
from scenario_motion import sample_motion
from generate_social_dynamic_world import generate
from human_posture import lying_footprint, LyingPeople
from color_attention import ColorAttention
from camera_people_tracking import CameraPeople


class DynamicSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = json.loads((PACKAGE/'config/social_dynamic_scene.json').read_text())

    def test_static_scene_assets_are_not_changed_by_generator(self):
        paths = [PACKAGE/p for p in ('worlds/social_static.sdf', 'map/social_static.pgm',
                                    'config/social_static_scene.json')]
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        generate(PACKAGE)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])

    def test_one_tv_avatar_at_every_phase_including_boundaries(self):
        motions = [m for m in self.scene['motions'] if m['model'].startswith('tv_viewer_a')]
        samples = list(np.arange(0., self.scene['timeline']['cycle']*2., .1))
        samples.extend(m['start'] for m in motions)
        samples.extend(m['end'] for m in motions)
        for t in samples:
            self.assertEqual(sum(sample_motion(m, t) is not None for m in motions), 1)

    def test_routes_are_continuous_bounded_speed_and_loop_on_clock_reset(self):
        for motion in self.scene['motions']:
            keys = motion['keyframes']
            self.assertTrue(all(b[0] > a[0] for a, b in zip(keys, keys[1:])))
            for a, b in zip(keys, keys[1:]):
                self.assertLessEqual(math.dist(a[1:3], b[1:3])/(b[0]-a[0]), .401)
            self.assertEqual(sample_motion(motion, 0.), sample_motion(motion, motion['period']))

    def test_walking_corridors_avoid_furniture(self):
        grid = cv2.imread(str(PACKAGE/'map/social_dynamic.pgm'), cv2.IMREAD_GRAYSCALE)
        # Include the person's 0.32 m radius plus a small route tolerance.
        blocked = cv2.dilate((grid < 128).astype(np.uint8),
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        for m in self.scene['motions']:
            if not any(word in m['model'] for word in ('walking', 'returning', 'patrol')):
                continue
            for a, b in zip(m['keyframes'], m['keyframes'][1:]):
                # The initial/final 0.9 m is the deliberate chair exit/entry.
                for fraction in np.linspace(0., 1., max(2, int(math.dist(a[1:3], b[1:3])/.05))):
                    p = np.array(a[1:3])+(np.array(b[1:3])-a[1:3])*fraction
                    if np.linalg.norm(p-np.array([-1., -3.85])) < 1.0:
                        continue
                    x, y = np.floor((p-[-6.5, -5.5])/.05).astype(int)
                    self.assertEqual(blocked[grid.shape[0]-1-y, x], 0, (m['model'], p))

    def test_dynamic_people_have_collision_and_do_not_enter_static_map(self):
        world = ET.parse(PACKAGE/'worlds/social_dynamic.sdf').getroot().find('world')
        for m in self.scene['motions']:
            model = world.find(f"model[@name='{m['model']}']")
            self.assertIsNotNone(model.find('link/collision'))
        # A patrol start must be free in the static occupancy grid.
        grid = cv2.imread(str(PACKAGE/'map/social_dynamic.pgm'), 0)
        x, y = np.floor((np.array([-5.6, -4.8])-[-6.5, -5.5])/.05).astype(int)
        self.assertGreater(grid[grid.shape[0]-1-y, x], 200)


class SensorTransitions(unittest.TestCase):
    def test_departing_viewer_invalidates_only_its_own_region_even_after_large_step(self):
        memory = ColorAttention()
        memory.people = {
            4: dict(p=np.array([0., 0.]), d=np.array([0., 1.]), camera_id=8),
            5: dict(p=np.array([2., 0.]), d=np.array([0., 1.]), camera_id=9)}
        observation = dict(p=np.array([0., 1.1]), stamp=3., hits=5, since=0., velocity=np.array([0., .35]))
        memory.observe_people({8: observation}, (), 3.)
        self.assertNotIn(4, memory.people)
        self.assertIn(5, memory.people)
        self.assertIn(4, memory.invalidated)

    def test_walk_velocity_and_prediction_come_from_measured_positions(self):
        camera = CameraPeople()
        for t in np.arange(0., 2., .2):
            camera.observe([(float(t*.4), 0.)], float(t))
        self.assertAlmostEqual(next(iter(camera.tracks.values()))['velocity'][0], .4)
        region = next(iter(camera.regions(1.8, 1.5).values()))
        self.assertAlmostEqual(region['polygon'][1, 0]-region['polygon'][0, 0], .6)

    def test_lying_skeleton_is_distinguished_from_seated_or_incomplete_body(self):
        joints = {0: [0., 0., .7, .9], 1: [.2, 0., .65, .9], 8: [.8, -.1, .6, .9],
                  11: [.8, .1, .6, .9], 9: [1.2, -.1, .6, .9], 12: [1.2, .1, .6, .9]}
        self.assertIsNotNone(lying_footprint(joints))
        self.assertIsNone(lying_footprint({0: joints[0], 1: joints[1]}))
        seated = dict(joints, **{})
        seated[1] = [.2, 0., 1.1, .9]
        self.assertIsNone(lying_footprint(seated))
        tracks = LyingPeople()
        tracks.observe([dict(keypoints=joints)], 1.)
        self.assertFalse(tracks.regions(1.))
        tracks.observe([dict(keypoints=joints)], 1.3)
        self.assertEqual(len(tracks.regions(1.3)), 1)
        self.assertFalse(tracks.regions(3.4))


if __name__ == '__main__':
    unittest.main()
