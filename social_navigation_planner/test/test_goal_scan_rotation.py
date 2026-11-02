"""A completed full scan requires measured progress through every heading."""
import math
from social_navigation_planner.social_observation import ObservationSweep, angle


def test_stationary_heading_cannot_complete_a_full_scan():
    actual = ((-1., 0., 0.), (-2., 0., 0.), (0., 0., 0.))
    scan = ObservationSweep(actual, 2, 0., .5, .1)
    for k in range(90):
        scan.rows(actual, k * .1, 8, .15)
    assert not scan.finished or scan.reason != 'completed'


def test_full_scan_crosses_wrap_and_turns_at_least_360_degrees():
    actual = [(-1., 0., 0.), (-2., 0., 0.), (0., 0., 3.0)]
    scan = ObservationSweep(actual, 2, 0., .5, .1)
    total = 0.
    for k in range(800):
        rows = scan.rows(actual, k*.1, 8, .15)
        if scan.finished:
            break
        before = actual[2][2]
        desired = rows[1][2][2]
        delta = angle(desired-before)
        actual[2] = (0., 0., angle(before+delta))
        total += delta
    assert scan.finished and scan.reason == 'completed'
    assert total >= 2*math.pi
