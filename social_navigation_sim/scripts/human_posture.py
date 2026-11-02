"""Measured lying-posture candidates; stillness does not establish sleep."""
import math
import cv2
import numpy as np


def lying_footprint(joints):
    points = {int(k): np.asarray(v, float) for k, v in joints.items()
              if len(v) == 4 and np.isfinite(v).all() and v[3] >= .25}
    strong = {k for k, p in points.items() if p[3] >= .35}
    hips = [points[k][:3] for k in (8, 11) if k in strong]
    if len(points) < 5 or len(strong) < 4 or 1 not in strong or not hips:
        return None
    # A profile/occluded head must not invalidate an otherwise measured torso
    # and legs. Without a nose, require two strong shoulders plus a plausible
    # distal leg aligned with the torso; a flat furniture surface is insufficient.
    if 0 not in strong and not {2, 5} <= strong:
        return None
    hip = np.mean(hips, axis=0)
    torso = points[1][:3]-hip
    if np.linalg.norm(torso[:2]) < .4 or abs(torso[2]) > .25:
        return None
    legs = [points[k][:3]-hip for k in (9, 10, 12, 13) if k in points]
    if not any(.3 < np.linalg.norm(v[:2]) < 1.4 and
               v[:2] @ -torso[:2] > .65*np.linalg.norm(v[:2])*np.linalg.norm(torso[:2]) for v in legs):
        return None
    cloud = np.array([p[:3] for p in points.values()])
    if (np.ptp(cloud[:, 2]) > .45 or np.median(cloud[:, 2]) > 1.1
            or not .8 < np.linalg.norm(np.ptp(cloud[:, :2], axis=0)) < 2.4):
        return None
    return cv2.convexHull(cloud[:, :2].astype(np.float32)).reshape(-1, 2).astype(float)


class LyingPeople:
    def __init__(self):
        self.tracks, self.next_id, self.last_stamp = {}, 0, -math.inf

    def observe(self, bodies, stamp):
        if stamp <= self.last_stamp:
            return
        self.last_stamp = stamp
        used = set()
        for body in bodies:
            polygon = lying_footprint(body['keypoints'])
            if polygon is None:
                continue
            center = polygon.mean(axis=0)
            if any(np.linalg.norm(self.tracks[k]['center']-center) < .3 for k in used):
                continue
            choices = [(np.linalg.norm(t['center']-center), k) for k, t in self.tracks.items()
                       if k not in used and stamp-t['stamp'] < 2.]
            distance, key = min(choices, default=(math.inf, -1))
            if distance > .75:
                key = self.next_id
                self.next_id += 1
                self.tracks[key] = dict(center=center, polygon=polygon, first=stamp, stamp=stamp, hits=0)
            self.tracks[key].update(center=center, polygon=polygon, stamp=stamp,
                                    hits=self.tracks[key]['hits']+1)
            used.add(key)

    def regions(self, now):
        self.tracks = {k: t for k, t in self.tracks.items() if 0 <= now-t['stamp'] < 2.}
        return {('lying_person', k): dict(polygon=t['polygon'], margin=.55, stamp=t['stamp'],
                    source='RGB-D lying-posture candidate; sleep not established')
                for k, t in self.tracks.items() if t['hits'] >= 2 and t['stamp']-t['first'] >= .2}
