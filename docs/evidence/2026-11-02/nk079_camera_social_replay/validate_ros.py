"""Read-only recorder smoke using controlled messages, never Gazebo/commands."""
import json,os,sys,time
from pathlib import Path
import numpy as np
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from visualization_msgs.msg import Marker,MarkerArray
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'social_navigation_sim/scripts'))
from replay_sensor_recorder import ReplaySensorRecorder
folder=OUT/'ros_fixture';folder.mkdir(exist_ok=False)
rclpy.init(args=['--ros-args','-p',f'directory:={folder}','-p','use_sim_time:=true'])
recorder=ReplaySensorRecorder();emitter=Node('perception_fixture')
executor=SingleThreadedExecutor();executor.add_node(recorder);executor.add_node(emitter)
clock=emitter.create_publisher(Clock,'/clock',10)
raw=emitter.create_publisher(Image,'/leader/camera/image_raw',10)
detection=emitter.create_publisher(Image,'/leader/people/image',10)
regions=emitter.create_publisher(MarkerArray,'/social_navigation/markers',10)
status=emitter.create_publisher(String,'/social_navigation/status',10)
def spin(seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:executor.spin_once(timeout_sec=.02)
try:
    spin(1.)
    c=Clock();c.clock.sec=2;c.clock.nanosec=300000000;clock.publish(c);spin(.2)
    image=CvBridge().cv2_to_imgmsg(np.full((16,24,3),120,np.uint8),'bgr8');image.header.stamp.sec=2
    raw.publish(image);detection.publish(image)
    line=Marker();line.header.frame_id='map';line.header.stamp.sec=2;line.ns='camera_social_regions';line.id=0;line.type=Marker.LINE_STRIP
    line.points=[Point(x=x,y=y) for x,y in [(0.,0.),(1.,0.),(0.,1.),(0.,0.)]]
    label=Marker();label.header=line.header;label.ns=line.ns;label.id=1;label.type=Marker.TEXT_VIEW_FACING;label.text='fixture_viewing_tv'
    regions.publish(MarkerArray(markers=[line,label]));status.publish(String(data='fixture only'))
    spin(.6);regions.publish(MarkerArray(markers=[]));spin(.3)
finally:
    recorder.writer.close();recorder.perception_writer.close();executor.shutdown()
    recorder.destroy_node();emitter.destroy_node();rclpy.shutdown()
rows=[json.loads(l) for l in (folder/'perception.jsonl').read_text().splitlines()]
images=[r for r in rows if r['kind']=='camera']
social=[r for r in rows if r['kind']=='social']
assert {r['source'] for r in images}=={'raw','detection'}
assert all(r['stamp']==2. and abs(r['t']-2.3)<1e-6 and r['image'].startswith('data:image/jpeg;base64,') for r in images)
assert social[0]['regions'][0]['label']=='fixture_viewing_tv' and social[-1]['regions']==[]
result={'camera_sources':['raw','detection'],'capture_vs_receipt':True,'social_and_clear':True,'writer_status':json.loads((folder/'perception_status.json').read_text()),'gazebo_started':False,'commands_published':False,'domain':os.environ.get('ROS_DOMAIN_ID')}
assert not result['writer_status']['error']
(OUT/'ros_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS actual ROS read-only recorder JPEG, social snapshots, clear and clean writer shutdown')
