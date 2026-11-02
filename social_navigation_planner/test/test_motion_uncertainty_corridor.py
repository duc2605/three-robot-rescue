"""NK078 regressions: restart lag, lost speed, crossing and coasting."""
import math
import pytest
from social_navigation_planner.moving_obstacles import (
    MovingObstacle,MotionTracks,collision_risk,motion_hypotheses,
    crosses_approach_corridor,select_lidar_tracks)
from test_moving_obstacle_safety import stopped_leader


def test_slow_fit_is_not_amplified_by_a_synthetic_walking_speed_prior():
    tracks=MotionTracks(padding=.02,persistence=.4,pause_reserve=True)
    for k in range(8):tracks.observe([(1.6,-2.,.32)],k*.1)
    for k in range(1,4):tracks.observe([(1.6-.014*k,-2.,.32)],.7+.1*k)
    o=tracks.recent(1.)[0]
    assert .05<math.hypot(*o.velocity)<.2
    assert o.velocity_hint is None
    assert motion_hypotheses([o])==[o]
    assert len(tracks.tracks)==1


def test_recorded_leader_crossing_ahead_is_rejected_but_same_side_or_behind_is_allowed():
    o=MovingObstacle((1.420905885,-1.98390478),(-.140225248,-.003290976),.43,82.9)
    start=(.62324736,-1.80034359)
    assert crosses_approach_corridor(o,start,(.62000668,-2.63974345),83.,86.,.15)
    assert not crosses_approach_corridor(o,start,(.52725360,-1.26108132),83.,86.,.15)
    assert not crosses_approach_corridor(o,(2.4,-1.8),(2.4,-2.64),83.,86.,.15)


def test_zero_fit_with_motion_evidence_still_triggers_escape_instead_of_pause():
    node,clock=stopped_leader();node.camera_motion.clear()
    nominal=MovingObstacle((1.1,.05),(0.,0.),.32,clock[0],(-.45,0.))
    assert collision_risk(nominal,node.own_pose,clock[0],node.robot_radius) is None
    checked=motion_hypotheses([nominal])
    assert collision_risk(checked[1],node.own_pose,clock[0],node.robot_radius) is not None
    assert node.yield_to_moving_obstacles(clock[0],checked)
    assert math.hypot(*node.last_command[:2])>0.
    assert 'brief motion pause' not in node.safety_state


def test_confirmed_stationary_or_expired_evidence_does_not_keep_a_phantom_velocity():
    tracks=MotionTracks(padding=.02,persistence=.4,pause_reserve=True)
    for k in range(7):tracks.observe([(1.-.035*k,0.,.32)],k*.1)
    for k in range(7,16):tracks.observe([(.79,0.,.32)],k*.1)
    assert tracks.recent(1.5)[0].velocity_hint is None
    assert tracks.recent(2.4)==[]


def test_peer_fusion_does_not_erase_uncertainty_or_count_it_as_an_extra_vote():
    local=MovingObstacle((1.,0.),(0.,0.),.32,1.)
    remote=[MovingObstacle((1.01,0.),(0.,0.),.32,1.,(-.45,0.)),
            MovingObstacle((1.02,0.),(0.,0.),.32,1.)]
    fused=select_lidar_tracks([local],remote,1.,[0,1])
    assert len(fused)==1 and fused[0].velocity==(0.,0.)
    assert fused[0].velocity_hint==(-.45,0.)


def test_escape_rollout_starts_from_measured_coast_after_command_zero():
    node,clock=stopped_leader();node.last_command=(0.,0.,0.)
    node.own_pose=(0.,0.,math.pi/2)
    node.measured_velocity=lambda i:(.12,0.,.03)
    vx,vy,w=node.escape_initial_velocity()
    assert vx==pytest.approx(0.,abs=1e-9) and vy==pytest.approx(-.12) and w==.03
    node.last_command=(.1,.02,0.)
    assert node.escape_initial_velocity()==node.last_command


def test_measured_overspeed_never_generates_an_over_limit_escape_command():
    node,clock=stopped_leader()
    node.measured_velocity=lambda i:(.9,0.,0.)
    node.last_command=(0.,0.,0.)
    assert node.yield_to_moving_obstacles(clock[0],node.camera_motion.recent(clock[0]))
    assert node.last_command==(0.,0.,0.)
    assert 'overspeed' in node.safety_state


def test_lost_fit_preserves_only_a_recent_measured_velocity_then_expires():
    tracks=MotionTracks(padding=.02,persistence=.4,pause_reserve=True)
    for k in range(7):tracks.observe([(1.-.04*k,0.,.32)],k*.1)
    track=next(iter(tracks.tracks.values()))
    # Reproduce a failed current fit while the recent capture history still
    # contains measured translation; do not inject any authored human speed.
    last=track.last_velocity
    track.velocity=(0.,0.)
    o=tracks.recent(.7)[0]
    assert o.velocity==(0.,0.) and o.velocity_hint==last
    assert motion_hypotheses([o])[1].velocity==last
    assert tracks.recent(1.41)==[]
