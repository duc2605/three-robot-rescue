"""OpenPose MobileNet keypoints and RGB-D torso orientation (not Part-HOE).

Run one pose inference per YOLO crop. Never take heatmap maxima over a scene
containing multiple people, which can join shoulders from different people.
"""
import math
import cv2
import numpy as np
from vision_regions import unrotate_point


PAIRS = [(1, 2), (2, 3), (3, 4), (1, 5), (5, 6), (6, 7),
         (1, 8), (8, 9), (9, 10), (1, 11), (11, 12), (12, 13),
         (1, 0), (0, 14), (14, 16), (0, 15), (15, 17)]


def estimate_bodies(net, image, boxes, size=256, maximum=3, threshold=0.25):
    result = {}
    # Give horizontal bodies a slot instead of permanently starving them in
    # favour of large standing people. Total crops stay bounded.
    order = sorted(range(len(boxes)), key=lambda i: (
        boxes[i][2]-boxes[i][0] > 1.3*(boxes[i][3]-boxes[i][1]),
        (boxes[i][2]-boxes[i][0])*(boxes[i][3]-boxes[i][1])), reverse=True)[:maximum]
    for index in order:
        x1, y1, x2, y2, _ = boxes[index]
        if max(y2-y1, x2-x1) < 48 or min(y2-y1, x2-x1) < 16:
            continue
        padx, pady = 0.08 * (x2 - x1), 0.04 * (y2 - y1)
        left, right = max(0, int(x1 - padx)), min(image.shape[1], int(x2 + padx + 1))
        top, bottom = max(0, int(y1 - pady)), min(image.shape[0], int(y2 + pady + 1))
        crop = image[top:bottom, left:right]
        horizontal = x2-x1 > 1.3*(y2-y1)
        rotations = (1, -1) if horizontal else (0,)
        best, best_score = {}, -1.
        for rotation in rotations:
            rotated = (cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE if rotation == 1
                                 else cv2.ROTATE_90_COUNTERCLOCKWISE) if rotation else crop)
            target_size = max(size, 256) if horizontal else size
            ratio = min(target_size/rotated.shape[1], target_size/rotated.shape[0])
            width, height = round(rotated.shape[1]*ratio), round(rotated.shape[0]*ratio)
            dx, dy = (target_size-width)//2, (target_size-height)//2
            padded = np.full((target_size, target_size, 3), 127, np.uint8)
            padded[dy:dy+height, dx:dx+width] = cv2.resize(rotated, (width, height))
            net.setInput(cv2.dnn.blobFromImage(padded, 1., (target_size, target_size),
                                              (127.5, 127.5, 127.5), swapRB=True))
            heatmaps = net.forward()
            if heatmaps.ndim != 4 or heatmaps.shape[1] < 18:
                raise ValueError('Body model must output NCHW COCO-18 heatmaps')
            points = {}
            for joint, heatmap in enumerate(heatmaps[0, :18]):
                _, confidence, _, peak = cv2.minMaxLoc(heatmap)
                if not math.isfinite(confidence) or confidence < threshold:
                    continue
                u = ((peak[0]+.5)*target_size/heatmap.shape[1]-dx)/ratio
                v = ((peak[1]+.5)*target_size/heatmap.shape[0]-dy)/ratio
                px, py = unrotate_point(u, v, crop.shape[1], crop.shape[0], rotation)
                if 0 <= px < crop.shape[1] and 0 <= py < crop.shape[0]:
                    points[joint] = (float(px+left), float(py+top), min(1., float(confidence)))
            score = sum(p[2] for p in points.values())
            if score > best_score:
                best, best_score = points, score
        result[index] = best
    return result


def locate_joints(points, depth, info, transform, transform_point, body_depth):
    result = {}
    if depth is None or transform is None:
        return result
    for joint, (u, v, score) in points.items():
        x, y = round(u), round(v)
        patch = depth[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
        valid = patch[np.isfinite(patch) & (patch > 0.25) & (patch < 7.5)]
        if len(valid) < 9 or np.percentile(valid, 80) - np.percentile(valid, 20) > 0.25:
            continue
        z = float(np.median(valid))
        if abs(z - body_depth) > 0.75:
            continue
        optical = np.array([(u - info.k[2]) * z / info.k[0], (v - info.k[5]) * z / info.k[4], z])
        world = transform_point(optical, transform)
        if np.all(np.isfinite(world)) and 0.02 < world[2] < 2.5:
            result[joint] = [*map(float, world), score]
    return result


def face_landmark_orientation(joints):
    """Approximate head forward from RGB-D nose, eye and ear landmarks.

    A profile may have no detectable frontal face and no visible hips. Require
    actual facial landmarks rather than pointing an unknown person at a TV.
    One-sided profiles have lateral bias; this is a head-direction cue only.
    """
    if 0 not in joints or joints[0][3] < .4:
        return None, 0.
    nose = np.asarray(joints[0][:3])
    if not .65 < nose[2] < 2.5:
        return None, 0.
    ears, scores = [], [joints[0][3]]
    for eye, ear in ((14, 16), (15, 17)):
        if eye not in joints or ear not in joints or min(joints[eye][3], joints[ear][3]) < .4:
            continue
        e, side = np.asarray(joints[eye][:3]), np.asarray(joints[ear][:3])
        forward = nose-side
        length = np.linalg.norm(forward[:2])
        if (not .06 < length < .24 or abs(forward[2]) > .10 or abs(e[2]-nose[2]) > .10
                or (e-side)[:2] @ forward[:2] <= 0
                or np.linalg.norm(e-nose) > .16):
            continue
        ears.append(side)
        scores.extend((joints[eye][3], joints[ear][3]))
    if not ears:
        return None, 0.
    forward = nose-np.mean(ears, axis=0)
    if np.linalg.norm(forward[:2]) < .04:
        return None, 0.
    return math.atan2(forward[1], forward[0]), min(.8, .45+min(scores))


def torso_orientation(joints, head_yaw=None):
    """Semantic left/right shoulder and hip baselines give a planar forward.

One baseline alone is ambiguous; require both to agree or a visible face to
confirm the sign. The quality is a gate, not a calibrated probability.
"""
    face_quality = .85
    if head_yaw is None:
        head_yaw, face_quality = face_landmark_orientation(joints)
    forwards, quality = [], []
    for right, left, minimum_height in ((2, 5, 0.85), (8, 11, 0.4)):
        if right not in joints or left not in joints:
            continue
        a, b = np.asarray(joints[right][:3]), np.asarray(joints[left][:3])
        axis = b - a
        width = float(np.linalg.norm(axis[:2]))
        if not 0.16 < width < 0.65 or abs(axis[2]) > 0.22 or min(a[2], b[2]) < minimum_height:
            continue
        forwards.append(np.array([axis[1], -axis[0]]) / width)
        quality.append(min(joints[right][3], joints[left][3]))
    if not forwards:
        return (head_yaw, face_quality) if head_yaw is not None else (None, 0.0)
    if len(forwards) == 2 and forwards[0] @ forwards[1] < math.cos(math.radians(35)):
        return None, 0.0
    direction = np.mean(forwards, axis=0)
    angle = math.atan2(direction[1], direction[0])
    if head_yaw is not None:
        alignment = math.cos(angle - head_yaw)
        if alignment < 0:
            angle = math.atan2(-direction[1], -direction[0])
        if abs(math.atan2(math.sin(angle - head_yaw), math.cos(angle - head_yaw))) > math.radians(70):
            return None, 0.0
    elif len(forwards) < 2:
        return None, 0.0
    # Both torso baselines, or one plus head evidence, passed the geometry gate.
    return angle, float(min(0.85, 0.45 + min(quality)))


def visibility(joints):
    upper = sum(j in joints for j in (1, 2, 3, 4, 5, 6, 7))
    lower = sum(j in joints for j in (8, 9, 10, 11, 12, 13))
    if upper >= 3:
        return 'full' if lower >= 3 else 'upper_body'
    return 'legs_only' if lower >= 2 else 'insufficient'
