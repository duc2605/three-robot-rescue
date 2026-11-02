"""Unclassified low surfaces to inspect with pose estimation, not person labels."""
import cv2
import numpy as np


def low_surface_boxes(depth, info, transform, transform_point, maximum=1):
    if depth is None or transform is None or info is None:
        return []
    step = 4
    vv, uu = np.mgrid[0:depth.shape[0]:step, 0:depth.shape[1]:step]
    ranges = depth[vv, uu]
    valid = np.isfinite(ranges) & (ranges > .3) & (ranges < 6.)
    optical = np.column_stack(((uu[valid]-info.k[2])*ranges[valid]/info.k[0],
                               (vv[valid]-info.k[5])*ranges[valid]/info.k[4], ranges[valid]))
    if len(optical) < 30:
        return []
    world = transform_point(optical, transform)
    results = []
    # First inspect elevated surfaces (beds), then low floor-level bodies.
    for low, high in ((.48, 1.1), (.12, .45)):
        mask = np.zeros_like(ranges, np.uint8)
        mask[valid] = (np.isfinite(world).all(axis=1) & (world[:, 2] >= low) & (world[:, 2] <= high))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        _, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        for x, y, w, h, area in sorted(stats[1:], key=lambda s: int(s[4]), reverse=True):
            width, height = w*step, h*step
            if not (area >= 35 and width >= 64 and height >= 16 and width > 1.3*height
                    and width*height < .5*depth.size):
                continue
            x1, y1 = max(0, (x-1)*step), max(0, (y-1)*step)
            x2, y2 = min(depth.shape[1]-1, (x+w+1)*step), min(depth.shape[0]-1, (y+h+1)*step)
            results.append((float(x1), float(y1), float(x2), float(y2), 0.))
            if len(results) >= maximum:
                return results
    return results
