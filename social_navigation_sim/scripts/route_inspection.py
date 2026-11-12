"""Bounded camera attention to unclassified map geometry near a planned route.

No authored bed/person labels are used, and these proposals never create zones.
"""
import cv2
import numpy as np


def inspection_targets(raw, resolution, origin, rotation):
    _, _, stats, _ = cv2.connectedComponentsWithStats((raw >= 65).astype(np.uint8), 8)
    targets = []
    for x, y, width, height, count in stats[1:]:
        major, minor = max(width, height)*resolution, min(width, height)*resolution
        if not (1.2 <= major <= 3. and .35 <= minor <= 1.4):
            continue
        local = np.array([x+width/2., y+height/2.])*resolution
        targets.append((origin+rotation @ local, .5*np.hypot(width, height)*resolution))
    return targets


def upcoming_targets(leader, path, targets):
    if len(path) < 2:
        return []
    points = np.asarray(path, float)
    first = int(np.argmin(np.linalg.norm(points-leader, axis=1)))
    ahead = [np.asarray(leader)]
    length = 0.
    for p in points[first+1:]:
        length += np.linalg.norm(p-ahead[-1])
        ahead.append(p)
        if length >= 3.:
            break
    if len(ahead) < 2:
        return []
    forward = ahead[-1]-leader
    result = []
    for center, radius in targets:
        distance = np.linalg.norm(center-leader)
        if not .16 < distance <= 3.0 or (center-leader) @ forward < 0:
            continue
        nearest = float('inf')
        for a, b in zip(ahead, ahead[1:]):
            d = b-a
            fraction = np.clip((center-a) @ d/max(float(d @ d), 1e-9), 0., 1.)
            nearest = min(nearest, np.linalg.norm(center-a-fraction*d))
        if nearest-radius < .6:
            result.append(center)
    return sorted(result, key=lambda p: np.linalg.norm(p-leader))


def scan_targets(ranges, angle_min, angle_increment, range_min, range_max):
    """Measured clusters in sensor XY; proposals only, never semantic regions."""
    ranges = np.asarray(ranges, float)
    angles = angle_min + np.arange(len(ranges)) * angle_increment
    points = np.column_stack((ranges * np.cos(angles), ranges * np.sin(angles)))
    valid = np.isfinite(ranges) & (ranges >= range_min) & (ranges <= min(3., range_max))
    groups, current = [], []
    for i in range(len(ranges)):
        if not valid[i]:
            if current:
                groups.append(current)
            current = []
            continue
        if current and np.linalg.norm(points[i] - points[current[-1]]) > .20:
            groups.append(current)
            current = []
        current.append(i)
    if current:
        groups.append(current)
    result = []
    for group in groups:
        if len(group) < 3:
            continue
        cluster = points[group]
        center = np.mean(cluster, axis=0)
        radius = float(np.max(np.linalg.norm(cluster-center, axis=1)))
        if radius <= 1.5:
            result.append((center, max(.05, radius)))
    return result
