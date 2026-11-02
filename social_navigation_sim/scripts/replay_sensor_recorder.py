#!/usr/bin/env python3
"""Opt-in, read-only ROS sensor/escape telemetry for the Gazebo replay."""
import json
import math
import time
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Thread, get_ident

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan, Image
from visualization_msgs.msg import MarkerArray
from replay_perception import social_regions, encode_camera
from nav_msgs.msg import Path as RosPath
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException


def stamp(header):
    return header.stamp.sec+header.stamp.nanosec*1e-9


class EventWriter:
    """Bound IO in this observer; never block or write inside navigation."""
    def __init__(self, directory, maximum_bytes=128*1024*1024, filename='navigation.jsonl', prepare=None, queue_size=1024):
        self.path=Path(directory)/filename
        self.prepare=prepare
        self.stream=self.path.open('x')
        self.queue=Queue(maxsize=queue_size);self.dropped=0;self.error=None
        self.maximum_bytes=maximum_bytes;self.bytes=0
        self.thread=Thread(target=self.run,daemon=True);self.thread.start()

    def put(self, row):
        if self.error:return
        try:self.queue.put_nowait(row)
        except Full:self.dropped+=1

    def run(self):
        try:
            last_flush=time.monotonic()
            while True:
                try:row=self.queue.get(timeout=.25)
                except Empty:self.stream.flush();continue
                if row is None:break
                if self.prepare:row=self.prepare(row)
                line=json.dumps(row,allow_nan=False,separators=(',',':'))+'\n'
                size=len(line.encode())
                if self.bytes+size>self.maximum_bytes:
                    self.error=self.path.stem+' byte limit reached';break
                self.stream.write(line);self.bytes+=size
                if time.monotonic()-last_flush>=.2:self.stream.flush();last_flush=time.monotonic()
        except (OSError,ValueError,TypeError) as error:self.error=str(error)
        finally:
            self.stream.close()
            self.save_status(True)

    def save_status(self,finished):
        status={'bytes':self.bytes,'dropped':self.dropped,'error':self.error,'writer_finished':finished}
        try:
            target=self.path.with_name(self.path.stem+'_status.json')
            temporary=target.with_name(target.name+f'.{get_ident()}.tmp')
            temporary.write_text(json.dumps(status,indent=2)+'\n');temporary.replace(target)
        except OSError:pass

    def close(self):
        if self.thread.is_alive():
            try:self.queue.put(None,timeout=2.)
            except Full:self.error=self.error or 'queue did not drain on close'
            self.thread.join(timeout=3.)
        self.save_status(not self.thread.is_alive())


class ReplaySensorRecorder(Node):
    def __init__(self):
        super().__init__('replay_sensor_recorder')
        directory=self.declare_parameter('directory','').value
        if not directory:raise ValueError('A manually selected replay directory is required')
        self.writer=EventWriter(directory)
        self.perception_writer=EventWriter(directory,maximum_bytes=256*1024*1024,
            filename='perception.jsonl',prepare=encode_camera,queue_size=32)
        self.last_images={}
        self.epoch=0;self.previous=None;self.transforms=Buffer()
        for source,topic in [('raw','/leader/camera/image_raw'),('detection','/leader/people/image')]:
            self.create_subscription(Image,topic,lambda m,s=source:self.camera(m,s),qos_profile_sensor_data)
        self.create_subscription(MarkerArray,'/social_navigation/markers',self.social,qos_profile_sensor_data)
        self.create_subscription(String,'/social_navigation/status',self.social_status,10)
        self.create_subscription(TFMessage,'/tf_static',self.static_tf,
                                 QoSProfile(depth=100,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        for robot in ['robot1','robot2','robot3']:
            self.create_subscription(LaserScan,f'/{robot}/scan',lambda m,r=robot:self.scan(m,r),qos_profile_sensor_data)
            self.create_subscription(RosPath,f'/{robot}/escape_path',lambda m,r=robot:self.astar(m,r),10)
            self.create_subscription(String,f'/{robot}/escape_decision',lambda m,r=robot:self.decision(m,r),10)
        self.get_logger().info('Replay LiDAR/A* recording: '+str(self.writer.path))

    def camera(self,msg,source):
        if not 0<msg.width<=4096 or not 0<msg.height<=4096:return
        row=self.envelope('leader','camera',stamp(msg.header))
        if not -.05<=row['t']-row['stamp']<=5.:return
        key=(row['epoch'],source);wall=time.monotonic()
        previous=self.last_images.get(key)
        if previous and (row['stamp']-previous[0]<.5 or wall-previous[1]<.5):return
        self.last_images[key]=(row['stamp'],wall)
        row.update(source=source,capture_known=True,frame=msg.header.frame_id,_image=msg)
        self.perception_writer.put(row)

    def social(self,msg):
        markers=[];stamps=[]
        for m in msg.markers:
            if m.ns!='camera_social_regions':continue
            stamps.append(stamp(m.header))
            markers.append(dict(id=m.id,type=m.type,action=m.action,frame=m.header.frame_id,
                points=[[p.x,p.y] for p in m.points],text=m.text,
                color=[m.color.r,m.color.g,m.color.b,m.color.a]))
        # Empty snapshots/DELETEALL clear all regions at receipt time.
        now=self.get_clock().now().nanoseconds*1e-9
        row=self.envelope('leader','social',max(stamps) if stamps else now)
        if not -.05<=row['t']-row['stamp']<=5.:return
        row.update(regions=social_regions(markers),source='camera_social_marker_snapshot')
        self.perception_writer.put(row)

    def social_status(self,msg):
        now=self.get_clock().now().nanoseconds*1e-9
        row=self.envelope('leader','social_status',now);row['text']=msg.data
        self.perception_writer.put(row)

    def static_tf(self,msg):
        for transform in msg.transforms:self.transforms.set_transform_static(transform,'replay')

    def envelope(self,robot,kind,captured):
        now=self.get_clock().now().nanoseconds*1e-9
        if self.previous is not None and now<self.previous-1e-9:self.epoch+=1
        self.previous=now
        return dict(t=now,stamp=captured,epoch=self.epoch,robot=robot,kind=kind)

    def extrinsic(self,robot,frame):
        frame=frame.lstrip('/');base=robot+'/base_footprint'
        if frame==base:return dict(xyz=[0.,0.,0.],q=[0.,0.,0.,1.])
        # This project's low LiDAR link already contains robot_prefix,
        # while robot_state_publisher also adds frame_prefix. Resolve the
        # actual static tree rather than assuming a sensor origin.
        candidates=[frame]+([robot+'/'+frame] if frame.startswith(robot+'/') else [])
        for candidate in candidates:
            try:
                t=self.transforms.lookup_transform(base,candidate,Time()).transform
                return dict(xyz=[t.translation.x,t.translation.y,t.translation.z],
                            q=[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],tf_frame=candidate)
            except TransformException:pass
        return None

    def scan(self,msg,robot):
        if (not all(math.isfinite(v) for v in [msg.range_min,msg.range_max,msg.angle_min,msg.angle_increment])
                or not 0<=msg.range_min<msg.range_max or msg.angle_increment==0):return
        row=self.envelope(robot,'scan',stamp(msg.header))
        # An early/future capture after reset must not be assigned to a new
        # epoch or shown before it existed. Subsequent fresh scans recover.
        if not -.05<=row['t']-row['stamp']<=1. or len(msg.ranges)>32768:return
        row.update(frame=msg.header.frame_id,range_min=float(msg.range_min),range_max=float(msg.range_max),
                   angle_min=float(msg.angle_min),angle_increment=float(msg.angle_increment),
                   extrinsic=self.extrinsic(robot,msg.header.frame_id),
                   ranges=[round(float(v),4) if math.isfinite(v) else None for v in msg.ranges],
                   invalid_beams=sum(math.isnan(v) for v in msg.ranges))
        self.writer.put(row)

    def astar(self,msg,robot):
        if msg.header.frame_id!='map':return
        points=[[p.pose.position.x,p.pose.position.y] for p in msg.poses]
        if not all(math.isfinite(v) for p in points for v in p):return
        row=self.envelope(robot,'astar',stamp(msg.header))
        if not -.05<=row['t']-row['stamp']<=1.:return
        row.update(points=points,goal=points[-1] if points else None)
        self.writer.put(row)

    def decision(self,msg,robot):
        try:
            data=json.loads(msg.data);captured=float(data['stamp']);goal=data.get('goal')
            if not math.isfinite(captured) or (goal is not None and (len(goal)!=2 or not all(math.isfinite(v) for v in goal))):return
            row=self.envelope(robot,'decision',captured)
            if not -.05<=row['t']-row['stamp']<=1.:return
            row.update(goal=goal,stops=bool(data.get('stops')),terminal_safe=bool(data.get('terminal_safe')),
                       reason=str(data.get('reason','')))
            self.writer.put(row)
        except (ValueError,TypeError,KeyError):return


def main():
    rclpy.init();node=None
    try:
        node=ReplaySensorRecorder();rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:
        if node is not None:
            node.writer.close();node.perception_writer.close();node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__=='__main__':main()
