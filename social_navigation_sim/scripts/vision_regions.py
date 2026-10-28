"""Pixel geometry for bounded horizontal-person inference."""
import numpy as np


def unrotate_point(u, v, width, height, rotation):
    if rotation == 1:
        return v, height-1-u
    if rotation == -1:
        return width-1-v, u
    return u, v


def unrotate_box(box, width, height, rotation):
    x1, y1, x2, y2, score = box
    points = np.array([unrotate_point(x, y, width, height, rotation)
                       for x, y in ((x1, y1), (x1, y2), (x2, y1), (x2, y2))])
    low, high = points.min(0), points.max(0)
    return (*low, *high, score)


def suppress_boxes(boxes):
    kept = []
    for box in sorted(boxes, key=lambda b: b[4], reverse=True):
        a = np.asarray(box[:4])
        area = max(1., (a[2]-a[0])*(a[3]-a[1]))
        duplicate = False
        for old in kept:
            b = np.asarray(old[:4])
            intersection = float(np.prod(np.maximum(0., np.minimum(a[2:], b[2:])-np.maximum(a[:2], b[:2]))))
            other = max(1., (b[2]-b[0])*(b[3]-b[1]))
            if intersection/(area+other-intersection) > .45:
                duplicate = True
                break
        if not duplicate:
            kept.append(tuple(float(v) for v in box))
    return kept
