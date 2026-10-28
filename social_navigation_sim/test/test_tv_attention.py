"""Offline regressions for measured TV corridors and temporal attention."""
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from color_attention import ColorAttention
from colorful_targets import locate_tv_screens
from body_pose_estimation import torso_orientation


def person(position, target=(0., 3.), stamp=1.):
    p = np.array(position, float)
    d = np.asarray(target)-p
    return dict(p=p, d=d/np.linalg.norm(d), stamp=stamp, direction_stamp=stamp)


def scene(positions=((0., 0.),), measured=True):
    memory = ColorAttention()
    memory.people = {i: person(p) for i, p in enumerate(positions)}
    memory.objects['screen'] = dict(
        p=np.array([0., 3.]), stamp=1., since=0., hits=4, source='tv',
        footprint=np.array([[-.7, 3.], [.7, 3.]]) if measured else None)
    return memory


def confirm(memory):
    result = {}
    for stamp in (1., 1.35, 1.7):
        for p in memory.people.values():
            p.update(stamp=stamp, direction_stamp=stamp)
        for t in memory.objects.values():
            t['stamp'] = stamp
        result = memory.regions(lambda a, b: True, .2)
    return result


class AttentionTests(unittest.TestCase):
    def test_converging_viewers_do_not_need_parallel_headings(self):
        memory = scene(((-2., 0.), (2., 0.)))
        a, b = memory.people.values()
        self.assertLess(a['d'] @ b['d'], math.cos(math.radians(55)))
        self.assertTrue(memory.viewers_face_target([a, b], memory.objects['screen']))
        regions = confirm(memory)
        self.assertEqual(sum(k[0] == 'viewing_tv' for k in regions), 2)
        self.assertEqual(memory.conversation_groups(lambda a, b: True), [])

    def test_repeated_ticks_cannot_confirm_a_single_capture(self):
        memory = scene()
        for _ in range(30):
            self.assertFalse(memory.regions(lambda a, b: True, .2))

    def test_sustained_evidence_confirms(self):
        regions = confirm(scene())
        self.assertEqual(len(regions), 1)
        self.assertIn('measured TV', next(iter(regions.values()))['source'])

    def test_two_samples_over_a_long_gap_do_not_confirm(self):
        memory = scene()
        memory.regions(lambda a, b: True, .2)
        memory.people[0].update(stamp=4., direction_stamp=4.)
        self.assertFalse(memory.regions(lambda a, b: True, .2))

    def test_looking_away_invalidates_region(self):
        memory = scene()
        key = next(iter(confirm(memory)))
        memory.people[0]['d'] = np.array([0., -1.])
        self.assertTrue(memory.contradicted(key, lambda a, b: True))
        self.assertFalse(memory.regions(lambda a, b: True, .2))

    def test_fifty_degree_passerby_is_not_a_viewer(self):
        memory = scene(measured=False)
        memory.people[0]['d'] = np.array([math.sin(math.radians(50)), math.cos(math.radians(50))])
        self.assertFalse(confirm(memory))

    def test_occluded_target_does_not_create_region(self):
        memory = scene()
        confirm(memory)
        self.assertFalse(memory.regions(lambda a, b: False, .2))

    def test_union_does_not_fill_gap_between_viewers(self):
        regions = confirm(scene(((-2., 0.), (2., 0.))))
        polygons = [v['polygon'].astype(np.float32) for k, v in regions.items() if k[0] == 'viewing_tv']
        self.assertEqual(len(polygons), 2)
        self.assertTrue(all(cv2.pointPolygonTest(p, (0., .3), False) < 0 for p in polygons))
        for polygon in polygons:
            self.assertTrue(any(np.allclose(point, [-.7, 3.]) for point in polygon))
            self.assertTrue(any(np.allclose(point, [.7, 3.]) for point in polygon))

    def test_alignment_wins_over_nearer_off_axis_tv(self):
        memory = scene()
        memory.objects['other'] = dict(p=np.array([1., 2.]), stamp=1., since=0., hits=4,
                                       source='tv', footprint=None)
        key = next(iter(confirm(memory)))
        self.assertEqual(key[-1], 'screen')

    def test_geometry_survives_later_center_only_observation(self):
        memory = ColorAttention()
        track = dict(p=np.array([0., 3.]), stamp=1., since=0., hits=3)
        memory.observe_tv_objects({7: track}, 1.)
        memory.observe_screen_objects([dict(position=[0., 3., 1.], footprint=[[-.7, 3.], [.7, 3.]])], 1.)
        track['stamp'] = 2.
        memory.observe_tv_objects({7: track}, 2.)
        np.testing.assert_allclose(memory.objects[('tv', 7)]['footprint'], [[-.7, 3.], [.7, 3.]])
        self.assertEqual(memory.objects[('tv', 7)]['geometry_stamp'], 1.)

    def test_duplicate_center_does_not_override_measured_screen(self):
        memory = scene()
        memory.objects['center'] = dict(memory.objects['screen'], footprint=None)
        self.assertEqual(next(iter(confirm(memory)))[-1], 'screen')

    def test_missing_direction_is_not_fabricated(self):
        memory = scene()
        memory.people[0]['d'] = None
        self.assertFalse(confirm(memory))

    def test_person_behind_measured_screen_is_not_a_viewer(self):
        memory = scene(((0., 6.),))
        memory.objects['screen']['front'] = np.array([0., -1.])
        self.assertFalse(confirm(memory))

    def test_measured_tv_takes_precedence_over_duplicate_colour_target(self):
        memory = scene()
        memory.objects['colour'] = dict(memory.objects['screen'], source='colour')
        self.assertEqual(next(iter(confirm(memory)))[0], 'viewing_tv')

    def test_viewer_history_can_precede_screen_observation(self):
        memory = ColorAttention()
        # Three stable direction captures arrive before the robot turns to TV.
        for stamp, hits in ((1., 2), (1.4, 3), (1.8, 4)):
            observed = dict(p=np.array([0., 0.]), stamp=stamp, since=0., hits=hits,
                            velocity=np.zeros(2))
            direction = dict(p=np.array([0., 0.]), d=np.array([0., 1.]),
                             stamp=stamp, since=.5, hits=hits)
            memory.observe_people({0: observed}, ({0: direction},), stamp)
            self.assertFalse(memory.regions(lambda a, b: True, .2))
        memory.objects['screen'] = dict(p=np.array([0., 3.]), stamp=14., since=13.,
                                        hits=3, source='tv', footprint=None)
        memory.prune(14.)
        regions = memory.regions(lambda a, b: True, .2)
        self.assertEqual(len(regions), 1)
        # The older person's capture time remains the evidence expiry basis.
        self.assertEqual(next(iter(regions.values()))['stamp'], 1.8)
        self.assertEqual(memory.people[0]['direction_stamp'], 1.8)

    def test_one_brief_heading_before_screen_is_not_confirmed(self):
        memory = scene()
        memory.people[0].update(direction_hits=2, direction_since=.9)
        self.assertFalse(memory.regions(lambda a, b: True, .2))

    def test_changed_heading_does_not_reuse_previous_stable_window(self):
        memory = ColorAttention()
        for stamp, since, hits, heading in ((2., 0., 5, [0., 1.]), (3., 2.9, 2, [1., 0.])):
            observed = dict(p=np.array([0., 0.]), stamp=stamp, since=0., hits=5,
                            velocity=np.zeros(2))
            direction = dict(p=np.array([0., 0.]), d=np.array(heading), stamp=stamp, since=since, hits=hits)
            memory.observe_people({0: observed}, ({0: direction},), stamp)
        memory.objects['screen'] = dict(p=np.array([3., 0.]), stamp=3., since=0.,
                                        hits=3, source='tv', footprint=None)
        self.assertFalse(memory.regions(lambda a, b: True, .2))


class ScreenGeometryTests(unittest.TestCase):
    def setUp(self):
        self.info = SimpleNamespace(k=[100., 0., 100., 0., 100., 75., 0., 0., 1.])
        self.depth = np.full((150, 200), 3., np.float32)
        self.boxes = [(60., 45., 140., 105., .9)]

    @staticmethod
    def world(points, transform):
        # Optical forward -> map Y, optical down -> negative map Z.
        return np.column_stack((points[:, 0], points[:, 2], 1.5-points[:, 1]))

    def locate(self, depth):
        return locate_tv_screens(self.boxes, depth, self.info, object(), self.world)

    def test_front_screen_has_measured_horizontal_endpoints(self):
        screens = self.locate(self.depth)
        self.assertEqual(len(screens), 1)
        endpoints = np.array(screens[0]['footprint'])
        np.testing.assert_allclose(endpoints[:, 1], 3., atol=.01)
        self.assertGreater(np.linalg.norm(endpoints[1]-endpoints[0]), 1.7)

    def test_oblique_screen_retains_measured_angle(self):
        x = (np.arange(200)-100.)/100.
        depth = np.tile(3./(1.-.5*x), (150, 1)).astype(np.float32)
        endpoints = np.array(self.locate(depth)[0]['footprint'])
        delta = endpoints[1]-endpoints[0]
        self.assertAlmostEqual(delta[1]/delta[0], .5, places=2)

    def test_missing_depth_and_clipped_box_are_rejected(self):
        self.assertEqual(self.locate(None), [])
        self.assertEqual(self.locate(np.full_like(self.depth, np.nan)), [])
        self.boxes = [(0., 45., 140., 105., .9)]
        self.assertEqual(self.locate(self.depth), [])

    def test_mixed_depth_surfaces_are_rejected(self):
        rng = np.random.default_rng(7)
        self.assertEqual(self.locate(rng.uniform(1., 6., self.depth.shape)), [])


class SeatedProfileTests(unittest.TestCase):
    def test_profile_landmarks_supply_direction_without_hips(self):
        joints = {0: [0., .13, 1.2, .7], 14: [.02, .09, 1.2, .7], 16: [.06, 0., 1.2, .7]}
        angle, quality = torso_orientation(joints)
        self.assertIsNotNone(angle)
        self.assertGreater(math.sin(angle), .8)
        self.assertGreaterEqual(quality, .65)

    def test_unknown_face_does_not_invent_direction(self):
        joints = {2: [-.15, 0., 1., .8], 5: [.15, 0., 1., .8]}
        self.assertIsNone(torso_orientation(joints)[0])

    def test_implausible_depth_or_weak_landmarks_are_rejected(self):
        for ear in ([1., 0., 1.2, .7], [.06, 0., 1.2, .1]):
            joints = {0: [0., .13, 1.2, .7], 14: [.02, .09, 1.2, .7], 16: ear}
            self.assertIsNone(torso_orientation(joints)[0])

    def test_seated_shoulder_sign_can_be_checked_by_profile(self):
        joints = {0: [0., .13, 1.2, .7], 14: [.02, .09, 1.2, .7], 16: [.06, 0., 1.2, .7],
                  2: [-.15, 0., .95, .8], 5: [.15, 0., .95, .8]}
        angle, quality = torso_orientation(joints)
        self.assertGreater(math.sin(angle), .9)
        self.assertGreaterEqual(quality, .65)


if __name__ == '__main__':
    unittest.main()
