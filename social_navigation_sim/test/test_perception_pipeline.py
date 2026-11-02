"""Regressions from the live audit: pairing, duplicate IDs and repeated stops."""
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from rgbd_pairing import newest_pair
from camera_people_tracking import CameraPeople
from color_attention import ColorAttention
from social_search import SocialSearch
from body_pose_estimation import estimate_bodies
from vision_regions import unrotate_box, unrotate_point
from route_inspection import inspection_targets, upcoming_targets
from human_posture import lying_footprint
from posture_proposals import low_surface_boxes


def frame(t, frame_id='optical', encoding='rgb8'):
    ns = int(t*1e9)
    return NS(header=NS(stamp=NS(sec=ns//10**9, nanosec=ns%10**9), frame_id=frame_id),
              width=480, height=360, encoding=encoding)


class PairingTests(unittest.TestCase):
    def setUp(self):
        self.info = NS(header=NS(frame_id='optical'), width=480, height=360,
                       k=[400., 0, 240., 0, 400., 180., 0, 0, 1], d=[0.]*5)

    def test_orphan_latest_rgb_does_not_starve_complete_capture(self):
        older, latest, depth = frame(1.), frame(1.125), frame(1., encoding='32FC1')
        pair = newest_pair([older, latest], [depth], self.info, 1_200_000_000)
        self.assertIs(pair[0], older)
        self.assertIs(pair[1], depth)

    def test_mismatched_frame_geometry_and_old_depth_are_rejected(self):
        for depth in (frame(.8, encoding='32FC1'), frame(1., 'other', '32FC1'), frame(1., encoding='rgb8')):
            self.assertIsNone(newest_pair([frame(1.)], [depth], self.info, 1_100_000_000))
        depth = frame(1., encoding='32FC1')
        depth.width = 640
        self.assertIsNone(newest_pair([frame(1.)], [depth], self.info, 1_100_000_000))

    def test_stale_and_future_capture_are_rejected(self):
        for t in (0., 2.):
            self.assertIsNone(newest_pair([frame(t)], [frame(t, encoding='32FC1')], self.info, 1_000_000_000))


class IdentityTests(unittest.TestCase):
    def test_duplicate_depth_points_create_one_person(self):
        tracks = CameraPeople()
        for t in (1., 1.2, 1.4):
            tracks.observe([(0., 0.), (.1, .05)], t)
        self.assertEqual(len(tracks.tracks), 1)
        self.assertEqual(next(iter(tracks.tracks.values()))['hits'], 3)

    def test_two_nearby_people_remain_distinct_and_assignment_ignores_input_order(self):
        tracks = CameraPeople()
        tracks.observe([(0., 0.), (.6, 0.)], 1.)
        tracks.observe([(.59, 0.), (.02, 0.)], 1.2)
        self.assertEqual(len(tracks.tracks), 2)
        self.assertLess(tracks.tracks[0]['p'][0], .1)
        self.assertGreater(tracks.tracks[1]['p'][0], .5)

    def test_short_occlusion_keeps_id(self):
        tracks = CameraPeople()
        tracks.observe([(0., 0.)], 1.)
        tracks.observe([(.1, 0.)], 2.4)
        self.assertEqual(list(tracks.tracks), [0])

    def test_cached_duplicate_viewers_merge_without_refreshing_evidence(self):
        memory = ColorAttention()
        memory.people = {i: dict(p=np.array([i*.1, 0.]), d=np.array([0., 1.]),
                                stamp=2.+i, direction_stamp=1.+i, direction_since=0., direction_hits=3,
                                camera_id=10+i) for i in (0, 1)}
        memory.merge_people()
        self.assertEqual(list(memory.people), [0])
        self.assertEqual(memory.people[0]['stamp'], 3.)
        self.assertEqual(memory.people[0]['direction_stamp'], 2.)
        self.assertEqual(memory.people[0]['camera_ids'], {10, 11})
        self.assertIn(1, memory.invalidated)

    def test_tv_fragments_and_new_camera_ids_share_one_measured_surface(self):
        memory = ColorAttention()
        tracks = {1: dict(p=np.array([0., 3.]), stamp=1., since=0., hits=3),
                  2: dict(p=np.array([.8, 3.]), stamp=1., since=0., hits=3)}
        memory.observe_tv_objects(tracks, 1.)
        self.assertEqual(len(memory.objects), 2)
        memory.observe_screen_objects([dict(position=[0., 3., 1.], footprint=[[-1., 3.], [1., 3.]])], 1.1)
        self.assertEqual(len(memory.objects), 1)
        canonical = next(iter(memory.objects))
        self.assertEqual(memory.tv_aliases[('tv', 2)], canonical)
        self.assertTrue(memory.contradicted(('viewing_tv', 9, ('tv', 2)), lambda a, b: True))
        tracks[3] = dict(p=np.array([-.8, 3.]), stamp=2., since=1., hits=2)
        memory.observe_tv_objects(tracks, 2.)
        self.assertEqual(len(memory.objects), 1)
        np.testing.assert_allclose(memory.objects[canonical]['p'], [0., 3.])

    def test_distinct_screens_are_not_fused(self):
        memory = ColorAttention()
        memory.observe_screen_objects([
            dict(position=[-1., 3., 1.], footprint=[[-1.5, 3.], [-.5, 3.]]),
            dict(position=[1., 3., 1.], footprint=[[.5, 3.], [1.5, 3.]])], 1.)
        self.assertEqual(len(memory.objects), 2)


class SearchCooldownTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.search = SocialSearch(self.events.append, cooldown=30.)
        self.person = dict(p=np.array([1., 0.]), d=np.array([1., 0.]), stamp=0., direction_stamp=0.)
        self.memory = NS(people={0: self.person}, objects={}, viewer_candidates=lambda visible: [(0,)],
                         viewers_face_target=lambda members, target: True)

    def update(self, now, available=True):
        self.person.update(stamp=now, direction_stamp=now)
        self.search.update(self.memory, {}, {}, {}, lambda a, b: True, np.zeros(2), now, available=available)

    def test_completion_cooldown_blocks_new_targets_and_inspection(self):
        self.update(0.)
        ident = self.search.current['id']
        self.search.feedback(dict(version=1, id=ident, state='completed', reason='unresolved'), 1.)
        self.person['p'] = np.array([3., 0.])  # Different target bypasses spatial attempt history.
        self.update(5.)
        self.assertIsNone(self.search.current)
        self.assertFalse(self.search.inspect_person(np.ones(2), np.zeros(2), 5.))
        self.assertFalse(self.search.inspect_obstacle(np.ones(2), np.zeros(2), 5.))
        self.assertEqual(len(self.events), 1)
        self.update(32.)
        self.assertIsNotNone(self.search.current)

    def test_external_observation_cannot_be_preempted_by_new_search(self):
        self.update(0., available=False)
        self.assertFalse(self.events)

    def test_mapped_inspection_is_not_immediately_replaced_by_tv_search(self):
        self.search.inspect_obstacle(np.array([1., 1.]), np.zeros(2), 0.)
        ident = self.search.current['id']
        self.search.current['active'] = True
        self.update(.5)
        self.assertEqual(self.search.current['id'], ident)
        self.assertEqual(len(self.events), 1)

    def test_mapped_inspection_only_completes_on_actual_lying_region(self):
        self.search.inspect_obstacle(np.array([1., 1.]), np.zeros(2), 0.)
        self.search.current['active'] = True
        self.search.progress(self.memory, {}, {}, lambda a, b: True, .5)
        self.assertFalse(self.search.current['finish_requested'])
        self.search.progress(self.memory, {}, {('lying_person', 1): dict(polygon=np.array([[1., 1.], [1.5, 1.]]))},
                             lambda a, b: True, .8)
        self.assertTrue(self.search.current['finish_requested'])
        self.assertEqual(self.events[-1]['command'], 'complete')


class HorizontalAndRouteTests(unittest.TestCase):
    def test_occluded_head_can_use_strong_torso_and_aligned_distal_legs(self):
        joints = {1: [1.2, 0., .72, .48], 2: [1.1, -.1, .69, .44], 5: [1.3, .06, .82, .48],
                  8: [.7, -.03, .66, .38], 11: [.73, 0., .73, .34],
                  10: [0., .02, .71, .28], 13: [0., .02, .71, .32]}
        self.assertIsNotNone(lying_footprint(joints))
        joints.pop(10)
        joints.pop(13)
        self.assertIsNone(lying_footprint(joints))

    def test_floor_does_not_propose_a_person_and_surface_box_has_no_person_score(self):
        info = NS(k=[100., 0., 80., 0., 100., 60., 0., 0., 1.])
        depth = np.full((120, 160), 2., np.float32)
        self.assertFalse(low_surface_boxes(depth, info, True, lambda p, t: np.c_[p[:, :2], np.zeros(len(p))]))
        depth[:] = np.inf
        depth[40:64, 20:140] = 2.
        boxes = low_surface_boxes(depth, info, True, lambda p, t: np.c_[p[:, :2], np.full(len(p), .7)])
        self.assertEqual(len(boxes), 1)
        self.assertEqual(boxes[0][4], 0.)

    def test_inverse_pixel_rotations_and_boxes(self):
        self.assertEqual(unrotate_point(19., 10., 100, 50, 1), (10., 30.))
        self.assertEqual(unrotate_point(30., 89., 100, 50, -1), (10., 30.))
        np.testing.assert_allclose(unrotate_box((9., 10., 29., 80., .9), 100, 50, 1), [10, 20, 80, 40, .9])

    def test_horizontal_crop_is_not_rejected_for_being_short(self):
        class Net:
            calls = 0
            def setInput(self, blob):
                pass
            def forward(self):
                self.calls += 1
                heatmaps = np.zeros((1, 18, 32, 32), np.float32)
                heatmaps[:, :, 16, 16] = .8
                return heatmaps
        net = Net()
        points = estimate_bodies(net, np.zeros((100, 300, 3), np.uint8), [(20., 25., 280., 55., .9)], size=224)
        self.assertEqual(net.calls, 2)
        self.assertEqual(len(points[0]), 18)
        self.assertTrue(all(20 <= x <= 280 and 25 <= y <= 55 for x, y, score in points[0].values()))

    def test_geometry_proposes_only_nearby_upcoming_obstacles(self):
        raw = np.zeros((100, 100), np.int8)
        raw[25:35, 35:65] = 100
        targets = inspection_targets(raw, .05, np.zeros(2), np.eye(2))
        self.assertEqual(len(targets), 1)
        path = [[1.2, .5], [1.2, 1.5], [1.2, 2.5]]
        self.assertEqual(len(upcoming_targets(np.array([1.2, .5]), path, targets)), 1)
        self.assertFalse(upcoming_targets(np.array([1., 3.5]), [[1., 3.5], [1., 4.5]], targets))


if __name__ == '__main__':
    unittest.main()
