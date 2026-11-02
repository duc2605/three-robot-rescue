"""Camera capture/receipt, bounded stream, zone clearing and replay export."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import numpy as np
from cv_bridge import CvBridge
from visualization_msgs.msg import Marker,MarkerArray

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'social_navigation_sim/scripts'))
from replay_perception import encode_camera,social_regions
from replay_sensor_recorder import EventWriter
from test_replay_sensors import observer,Capture
from view_replay import complete_perception,export


def test_jpeg_encoding_and_camera_throttle_reset_and_capture_receipt():
    node=observer([1.2]);node.last_images={};node.perception_writer=Capture()
    msg=CvBridge().cv2_to_imgmsg(np.zeros((20,30,3),np.uint8),'bgr8')
    msg.header.stamp.sec=1
    node.camera(msg,'detection');node.camera(msg,'detection')
    assert len(node.perception_writer.rows)==1
    row=encode_camera(node.perception_writer.rows[0].copy())
    assert row['stamp']==1. and row['t']==pytest.approx(1.2) and row['capture_known']
    assert row['image'].startswith('data:image/jpeg;base64,') and row['width']==30
    node.previous=10.;node.get_clock=lambda:SimpleNamespace(now=lambda:SimpleNamespace(nanoseconds=100000000))
    msg.header.stamp.sec=10;node.camera(msg,'detection')  # pre-reset future frame
    assert len(node.perception_writer.rows)==1
    msg.header.stamp.sec=0;node.camera(msg,'detection')
    assert node.perception_writer.rows[-1]['epoch']==1


def test_social_world_regions_labels_and_empty_snapshot_clear():
    node=observer([1.2]);node.perception_writer=Capture()
    line=Marker();line.header.frame_id='map';line.header.stamp.sec=1
    line.ns='camera_social_regions';line.type=Marker.LINE_STRIP;line.id=2
    from geometry_msgs.msg import Point
    line.points=[Point(x=x,y=y) for x,y in [(0.,0.),(1.,0.),(0.,1.),(0.,0.)]]
    label=Marker();label.header=line.header;label.ns=line.ns;label.id=3;label.type=Marker.TEXT_VIEW_FACING;label.text='viewing_tv'
    node.social(MarkerArray(markers=[line,label]))
    assert node.perception_writer.rows[-1]['regions'][0]['label']=='viewing_tv'
    assert node.perception_writer.rows[-1]['stamp']==1.
    node.social(MarkerArray(markers=[]))
    assert node.perception_writer.rows[-1]['regions']==[]
    assert social_regions([dict(id=0,type=4,frame='odom',points=[[0,0],[1,0],[0,1]])])==[]


def test_perception_stream_separate_status_partial_tail_and_export(tmp_path):
    writer=EventWriter(tmp_path,filename='perception.jsonl',prepare=encode_camera,queue_size=4)
    writer.put({'t':1.,'epoch':0,'kind':'social','regions':[]});writer.close()
    assert json.loads((tmp_path/'perception_status.json').read_text())['writer_finished']
    with (tmp_path/'perception.jsonl').open('a') as f:f.write('{"t":')
    assert len(complete_perception(tmp_path))==1
    (tmp_path/'scene.json').write_text('{"objects":{},"bounds":[-1,-1,1,1]}')
    (tmp_path/'world_frames.jsonl').write_text('{"t":1,"epoch":0,"objects":[]}\n')
    export(tmp_path,tmp_path/'replay.html')
    assert '"perception": [{' in (tmp_path/'replay.html').read_text()
