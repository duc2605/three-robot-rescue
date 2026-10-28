"""Authored simulation motion only; never imported by perception/navigation."""
import bisect
import math


def wrap(angle):
    return (angle+math.pi) % (2*math.pi)-math.pi


def route(start, points, speed, initial_yaw=0.):
    """Piecewise constant speed, with bounded in-place turns at corners."""
    if speed <= 0 or len(points) < 2:
        raise ValueError('A route needs positive speed and two points')
    t, yaw = float(start), initial_yaw
    keys = [[t, *points[0], 0., yaw]]
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        if length < 1e-9:
            continue
        bearing = math.atan2(b[1]-a[1], b[0]-a[0])
        turn = abs(wrap(bearing-yaw))/.75
        if turn > 1e-8:
            t += turn
            keys.append([t, *a, 0., bearing])
        t += length/speed
        keys.append([t, *b, 0., bearing])
        yaw = bearing
    return keys


def sample_motion(motion, now):
    """Same half-open intervals and shortest yaw interpolation as the plugin."""
    phase = max(0., now) % motion['period']
    if not motion['start'] <= phase < motion['end']:
        return None
    keys = motion['keyframes']
    index = bisect.bisect_right([k[0] for k in keys], phase)
    if index == 0:
        return keys[0][1:]
    if index == len(keys):
        return keys[-1][1:]
    a, b = keys[index-1:index+1]
    fraction = (phase-a[0])/(b[0]-a[0])
    xyz = [x+(y-x)*fraction for x, y in zip(a[1:4], b[1:4])]
    return [*xyz, wrap(a[4]+fraction*wrap(b[4]-a[4]))]
