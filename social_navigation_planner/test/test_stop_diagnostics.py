"""Bounded windows and production-command equivalence with diagnostics enabled."""
import json
import time

from social_navigation_planner.stop_diagnostics import StopDiagnostics, finite_json


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_disabled_mode_creates_no_writer_or_files(monkeypatch, tmp_path):
    monkeypatch.delenv('SOCIAL_STOP_DIAGNOSTICS_DIRECTORY', raising=False)
    assert StopDiagnostics.from_environment('robot3') is None
    assert list(tmp_path.iterdir()) == []


def test_stop_flushes_pre_history_and_post_window_without_mutable_aliases(tmp_path):
    wall = [0.]
    recorder = StopDiagnostics(tmp_path, 'robot3', lambda: wall[0])
    state = {'nested': {'value': 1}, 'age': float('inf')}
    for i in range(30):
        wall[0] = i*.1
        recorder.observe(i*.1, state, i >= 10)
    state['nested']['value'] = 2
    recorder.close()
    rows = read(recorder.path)
    assert rows[0]['event'] == 'stop_window'
    samples = rows[1:]
    assert samples[0]['t'] == 0.
    assert any(row['t'] < 1 and not row['commanded_stop'] for row in samples)
    assert all(row['nested']['value'] == 1 and row['age'] is None for row in samples)
    assert len({row['sequence'] for row in samples}) == len(samples)


def test_nonzero_command_but_fresh_stationary_pose_triggers_window(tmp_path):
    wall = [0.]
    recorder = StopDiagnostics(tmp_path, 'robot2', lambda: wall[0])
    for i in range(20):
        wall[0] = .1*i
        recorder.observe(.1*i, {'pose': (1.,2.,0.), 'state_age_sim': 0.,
                                'command': (.2,0.,0.)}, False)
    recorder.close()
    rows = read(recorder.path)
    assert rows[0]['trigger'] == 'team_pose_stall_under_command'
    assert any(row.get('measured_team_pose_stall_under_command') for row in rows)
    assert not any(row.get('commanded_stop') for row in rows)


def test_reset_starts_new_epoch_and_discards_old_pre_history(tmp_path):
    wall = [0.]
    recorder = StopDiagnostics(tmp_path, 'robot1', lambda: wall[0])
    for i in range(10):
        wall[0] = .1*i
        recorder.observe(100+i, {}, False)
    for i in range(10):
        wall[0] = 1+.1*i
        recorder.observe(.1*i, {}, True)
    recorder.close()
    assert all(row['epoch'] == 1 for row in read(recorder.path))


def test_no_sustained_stop_leaves_no_file_and_io_failure_does_not_raise(tmp_path):
    wall = [0.]
    recorder = StopDiagnostics(tmp_path, 'idle', lambda: wall[0])
    recorder.observe(0., {}, False)
    recorder.close()
    assert not recorder.path.exists()
    broken = StopDiagnostics(tmp_path/'missing', 'robot3', lambda: wall[0])
    for i in range(10):
        wall[0] = i*.1
        broken.observe(i, {}, True)
    broken.close()
    assert broken.error
    broken.observe(11., {}, True)


def test_nonfinite_json_is_explicit_missing_not_false_zero():
    assert finite_json({'x': [float('nan'), -float('inf'), .3]}) == {'x':[None,None,.3]}


class DiagnosticCapture:
    error = None
    def __init__(self): self.records = []
    def observe(self, stamp, context, stopped):
        self.records.append(finite_json(dict(context, t=stamp, stopped=stopped)))


def enable(node):
    node.robot_name = 'robot3'
    node.stop_diagnostics = DiagnosticCapture()
    node.diagnostic_sensors = {}
    node.diagnostic_rejections = {}
    node.diagnostic_started = None
    return node.stop_diagnostics


def test_instrumented_production_escape_keeps_same_command_and_rollout():
    from test_moving_obstacle_safety import stopped_leader
    baseline, _ = stopped_leader()
    instrumented, _ = stopped_leader()
    capture = enable(instrumented)
    baseline.control_tick()
    instrumented.control_tick()
    assert baseline.last_command == instrumented.last_command
    assert baseline.prediction_pub.messages == instrumented.prediction_pub.messages
    assert capture.records[-1]['reason'] == 'checked_escape_command'
    assert capture.records[-1]['tracks']


def test_rejected_escape_reports_map_and_preserves_stop():
    from test_moving_obstacle_safety import stopped_leader
    node, _ = stopped_leader()
    capture = enable(node)
    node.physical_grid.segment_clearance = lambda *args: 0.
    node.control_tick()
    row = capture.records[-1]
    assert node.last_command == (0.,0.,0.)
    assert row['reason'] == 'escape_all_rollouts_rejected'
    assert row['rejected_checks']['escape.map'] > 0
    assert row['rejected_checks']['astar.map'] > 0


def test_stale_scan_capture_rejection_and_watchdog_reason():
    from test_moving_obstacle_safety import stopped_leader
    from sensor_msgs.msg import LaserScan
    node, clock = stopped_leader()
    capture = enable(node)
    msg = LaserScan()
    msg.header.frame_id = 'robot3/base_link'
    node.last_scan_time = -10.
    node.scan_callback(msg)
    assert node.diagnostic_sensors['lidar']['accepted'] is False
    assert node.diagnostic_sensors['lidar']['reason'] == 'capture_age_or_nonincreasing_stamp'
    node.state_wall = time.monotonic()-3.
    node.watchdog()
    assert capture.records[-1]['reason'] == 'watchdog_wall_freshness'


def test_continued_hold_extends_window_and_stops_after_recovery(tmp_path):
    wall = [0.]
    recorder = StopDiagnostics(tmp_path, 'long_hold', lambda: wall[0])
    for i in range(160):
        wall[0] = i*.1
        recorder.observe(i*.1, {}, i < 80)
    recorder.close()
    samples = [r for r in read(recorder.path) if 'sequence' in r]
    assert any(11 < r['t'] < 12 for r in samples)
    assert not any(r['t'] > 13 for r in samples)
    assert len({r['sequence'] for r in samples}) == len(samples)


import pytest


@pytest.mark.parametrize('index',[0,1,2])
def test_enabled_tracking_diagnostics_preserves_each_robot_command(index):
    from test_mpc_formation_motion import controller
    from test_moving_obstacle_safety import empty_grid
    poses=[(-1.,1.,0.),(0.,0.,0.),(1.,1.,0.)]
    reference=[[(x+.02*k,y,yaw) for x,y,yaw in poses] for k in range(9)]
    nodes=[controller(index,empty_grid(),[.1]) for _ in range(2)]
    for node in nodes:
        node.own_pose=poses[index]
        node.peer_poses=poses
        node.reference=reference
    capture=enable(nodes[1])
    for node in nodes:node.control_tick()
    assert nodes[0].last_command == nodes[1].last_command
    assert nodes[0].prediction_pub.messages == nodes[1].prediction_pub.messages
    assert capture.records[-1]['reason']=='mpc_tracking_command'


def test_coordinator_keeps_goal_context_when_one_robot_stops_with_valid_reference():
    from test_mpc_formation_motion import coordinator
    from test_moving_obstacle_safety import empty_grid
    node=coordinator([(0.,0.,0.),(1.,0.,0.),(2.,0.,0.)],empty_grid())
    capture=DiagnosticCapture();node.stop_diagnostics=capture
    node.observation=None
    node.observation_frame_time=node.observation_frame_wall=-float('inf')
    node.pose_times=[100.]*3
    node.diagnostic_reference([[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.)]])
    node.now_seconds=lambda:100.6
    node.pose_times=[100.6]*3
    node.robot_state[0]=(.3,0.,0.,True)
    node.robot_state[1]=(1.3,0.,0.,True)
    node.diagnostic_reference([[(.3,0.,0.),(1.3,0.,0.),(2.,0.,0.)]])
    assert capture.records[-1]['stationary_robots']==['robot3']
    assert capture.records[-1]['stopped'] is True
    assert capture.records[-1]['goal']==list(node.goal_xy)
