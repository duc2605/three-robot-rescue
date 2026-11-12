"""LiDAR motion classification regressions using measured cluster sequences."""
from social_navigation_planner.moving_obstacles import (
    MotionTracks, MovingObstacle, collision_risk, select_lidar_tracks, scan_clusters, tracking_motion_free,
)


def test_oscillating_cluster_retains_geometry_without_approach_velocity():
    tracks = MotionTracks(padding=.02, persistence=.4, pause_reserve=True, classify_in_place=True)
    for i in range(12):
        tracks.observe([(1.0 + (.03 if i % 2 else -.03), 0., .4)], i*.2)
    obstacle = tracks.recent(2.2)[0]
    assert obstacle.motion_state == 'in_place'
    assert obstacle.velocity == (0., 0.)
    assert obstacle.velocity_hint is None
    assert obstacle.radius >= .45
    assert collision_risk(obstacle, (0., 0.), 2.2, .15) is None
    assert obstacle.clearance((0., 0.), (1., 0.), 2.2, 2.5, .15) < 0


def test_stationary_cluster_departure_is_recognized():
    tracks = MotionTracks(classify_in_place=True)
    for i in range(8):
        tracks.observe([(1., 0., .4)], i*.2)
    assert tracks.recent(1.4)[0].motion_state == 'in_place'
    for i in range(1, 5):
        tracks.observe([(1.-i*.08, 0., .4)], 1.4+i*.2)
    obstacle = tracks.recent(2.2)[0]
    assert obstacle.motion_state == 'translating'
    assert obstacle.velocity[0] < -.1
    assert collision_risk(obstacle, (0., 0.), 2.2, .15) is not None


def test_slow_coherent_translation_is_not_classified_as_oscillation():
    tracks = MotionTracks(classify_in_place=True)
    for i in range(12):
        tracks.observe([(1.-.07*i*.2, 0., .4)], i*.2)
    assert tracks.recent(2.2)[0].motion_state == 'translating'
    assert tracks.recent(2.2)[0].velocity[0] < -.05


def test_receding_object_inside_trigger_reserve_does_not_request_escape():
    obstacle = MovingObstacle((.6, 0.), (.1, 0.), .4, 1.)
    assert collision_risk(obstacle, (0., 0.), 1., .15) is None


def test_one_uncertain_peer_cannot_restore_in_place_velocity():
    local = MovingObstacle((1., 0.), (0., 0.), .4, 1., motion_state='in_place')
    remote = MovingObstacle((1., 0.), (-.3, 0.), .4, 1., velocity_hint=(-.3, 0.))
    result = select_lidar_tracks([local], [remote], 1., remote_sources=[1])
    assert result[0].motion_state == 'in_place'
    assert result[0].velocity == (0., 0.)
    assert result[0].velocity_hint is None


def test_narrow_returns_have_measured_footprint_instead_of_40cm_floor():
    points=[(1., -.05), (1., 0.), (1., .05)]
    x,y,radius=scan_clusters(points)[0]
    assert radius < .15
    assert all(((px-x)**2+(py-y)**2)**.5 + .03 <= radius+1e-9 for px,py in points)


def test_old_wide_return_does_not_inflate_stationary_geometry_forever():
    tracks=MotionTracks(padding=.02,classify_in_place=True)
    for i in range(10):
        tracks.observe([(1.,0.,.55 if i==0 else .1)],i*.2)
    obstacle=tracks.recent(1.8)[0]
    assert obstacle.motion_state == 'in_place'
    assert obstacle.radius < .15


def test_outward_step_can_exit_an_inflated_in_place_buffer():
    obstacle=MovingObstacle((0.,0.),(0.,0.),.477,0.,motion_state='in_place')
    assert tracking_motion_free(obstacle,(.586,0.),(.61,0.),0.,.15,.15)
    assert not tracking_motion_free(obstacle,(.586,0.),(.56,0.),0.,.15,.15)
    assert not tracking_motion_free(obstacle,(.586,0.),(-.7,0.),0.,.15,.15)


def test_twenty_centimetre_gap_to_measured_disk_allows_parallel_motion():
    obstacle=MovingObstacle((0.,0.),(0.,0.),.1,0.,motion_state='in_place')
    assert tracking_motion_free(obstacle,(.45,0.),(.45,.1),0.,.15,.15)


def test_translating_track_retains_strict_buffer_check():
    obstacle=MovingObstacle((0.,0.),(.1,0.),.477,0.,motion_state='translating')
    assert not tracking_motion_free(obstacle,(.586,0.),(.61,0.),0.,.15,.15)
