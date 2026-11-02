"""Replay data are measurements/proposals, not additional navigation inputs."""
import importlib.util
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'social_navigation_sim/scripts'),str(ROOT/'social_navigation_planner/test')]
from replay_sensor_recorder import EventWriter,ReplaySensorRecorder
from view_replay import complete_navigation,export
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Path as RosPath
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


class Capture:
    def __init__(self):self.rows=[]
    def put(self,row):self.rows.append(row)


def observer(clock):
    node=ReplaySensorRecorder.__new__(ReplaySensorRecorder)
    node.writer=Capture();node.epoch=0;node.previous=None
    node.get_clock=lambda:SimpleNamespace(now=lambda:SimpleNamespace(nanoseconds=int(clock[0]*1e9)))
    node.extrinsic=lambda *args:{'xyz':[0.,0.,.1],'q':[0.,0.,0.,1.]}
    return node


def scan(t):
    msg=LaserScan();msg.header.stamp.sec=int(t);msg.header.stamp.nanosec=round((t-int(t))*1e9)
    msg.header.frame_id='robot1/lidar_link_1';msg.range_min=.08;msg.range_max=2.
    msg.angle_min=-math.pi;msg.angle_increment=.1;msg.ranges=[1.,math.inf,math.nan,1.8]
    return msg


def test_raw_scan_is_finite_json_with_capture_and_receipt_and_no_invented_returns():
    node=observer([1.1]);node.scan(scan(1.),'robot1');row=node.writer.rows[0]
    assert row['stamp']==1. and row['t']==pytest.approx(1.1)
    assert row['range_max']==2. and row['ranges']==[1.,None,None,1.8]
    assert row['invalid_beams']==1
    json.dumps(row,allow_nan=False)


def test_missing_extrinsic_is_explicit_and_invalid_metadata_is_not_written():
    node=observer([1.]);node.extrinsic=lambda *args:None;node.scan(scan(1.),'robot1')
    assert node.writer.rows[0]['extrinsic'] is None
    msg=scan(1.);msg.angle_increment=math.nan;node.scan(msg,'robot1')
    assert len(node.writer.rows)==1


def test_clock_reset_rejects_late_future_scan_and_plans():
    clock=[10.];node=observer(clock);node.scan(scan(10.),'robot1');clock[0]=.1
    node.scan(scan(10.),'robot1');node.scan(scan(.1),'robot1')
    assert len(node.writer.rows)==2 and node.writer.rows[-1]['epoch']==1
    msg=RosPath();msg.header.frame_id='map';msg.header.stamp.sec=10
    node.astar(msg,'robot1')
    node.decision(String(data=json.dumps({'stamp':10.,'goal':[0.,0.]})),'robot1')
    assert len(node.writer.rows)==2


def test_astar_empty_path_clears_goal_and_mpc_decision_is_separate():
    node=observer([1.]);msg=RosPath();msg.header.frame_id='map';msg.header.stamp.sec=1
    for x in [0.,.7]:
        p=PoseStamped();p.pose.position.x=x;msg.poses.append(p)
    node.astar(msg,'robot1');msg.poses=[];node.astar(msg,'robot1')
    node.decision(String(data=json.dumps(dict(stamp=1.,goal=[0.,-.7],stops=True,terminal_safe=True))),'robot1')
    assert node.writer.rows[0]['goal']==[.7,0.]
    assert node.writer.rows[1]['goal'] is None
    assert node.writer.rows[2]['kind']=='decision' and node.writer.rows[2]['goal']==[0.,-.7]


def test_async_writer_refuses_overwrite_and_reports_limit(tmp_path):
    writer=EventWriter(tmp_path,maximum_bytes=16);writer.put({'long':'x'*100});writer.close()
    status=json.loads((tmp_path/'navigation_status.json').read_text())
    assert status['writer_finished'] and status['error']=='navigation byte limit reached'
    with pytest.raises(FileExistsError):EventWriter(tmp_path)


def test_async_writer_preserves_complete_json_lines(tmp_path):
    writer=EventWriter(tmp_path)
    for i in range(20):writer.put({'t':i,'kind':'scan'})
    writer.close()
    assert [r['t'] for r in complete_navigation(tmp_path)]==list(range(20))
    assert json.loads((tmp_path/'navigation_status.json').read_text())['error'] is None


def test_navigation_export_old_missing_and_partial_new_line(tmp_path):
    assert complete_navigation(tmp_path)==[]
    (tmp_path/'scene.json').write_text('{"objects":{},"bounds":[-1,-1,1,1]}')
    (tmp_path/'world_frames.jsonl').write_text('{"t":1,"epoch":0,"objects":[]}\n')
    row={'t':1.,'stamp':1.,'kind':'astar','robot':'robot1','goal':[.4,.6]}
    (tmp_path/'navigation.jsonl').write_text(json.dumps(row)+'\n'+ '{"partial":')
    assert complete_navigation(tmp_path)==[row]
    export(tmp_path,tmp_path/'replay.html')
    assert '"navigation": [{' in (tmp_path/'replay.html').read_text()


def test_recorder_launch_is_opt_in(monkeypatch,tmp_path):
    spec=importlib.util.spec_from_file_location('replay_launch',ROOT/'social_navigation_sim/launch/three_robot_sim.launch.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.delenv('SOCIAL_REPLAY_DIRECTORY',raising=False)
    assert module.launch_replay_sensor_recorder(None)==[]
    monkeypatch.setenv('SOCIAL_REPLAY_DIRECTORY',str(tmp_path))
    assert len(module.launch_replay_sensor_recorder(None))==1


def test_optional_telemetry_does_not_change_escape_command_or_rollout():
    from test_moving_obstacle_safety import stopped_leader
    from test_mpc_formation_motion import Capture as Publisher
    a,_=stopped_leader();b,_=stopped_leader()
    a.escape_wall_budget=b.escape_wall_budget=1.
    b.escape_decision_pub=Publisher();a.control_tick();b.control_tick()
    assert a.last_command==b.last_command
    assert a.poses_from(a.prediction_pub.messages[-1])==b.poses_from(b.prediction_pub.messages[-1])
    data=json.loads(b.escape_decision_pub.messages[-1].data)
    assert data['goal']==list(b.selected_escape_goal)
    class Broken:
        def publish(self,*args):raise OSError('fixture')
    b.escape_decision_pub=Broken();b.replay_escape_decision(.4,'fixture',True)
    assert a.last_command==b.last_command


def test_writer_limit_is_reported_while_observer_still_running(tmp_path):
    writer=EventWriter(tmp_path,maximum_bytes=2);writer.put({'kind':'scan'})
    writer.thread.join(timeout=2.)
    status=json.loads((tmp_path/'navigation_status.json').read_text())
    assert status['error']=='navigation byte limit reached'
    assert status['writer_finished']
    writer.close()
