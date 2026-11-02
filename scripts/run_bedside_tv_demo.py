#!/usr/bin/env python3
"""Publish one bedside goal, freeze its actual first D* path, and log ROS data.

Reference TV polygons are authored geometry for visualization/evaluation only.
This helper never writes the planning map or publishes velocity commands.
"""
import argparse
import json
import math
from pathlib import Path
import time

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import Point, PoseArray, PoseStamped
from nav_msgs.msg import OccupancyGrid, Path as NavPath
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String
from visualization_msgs.msg import Marker, MarkerArray


class Demo(Node):
    def __init__(self, opts):
        super().__init__('bedside_tv_demo')
        self.opts = opts
        self.start = time.monotonic()
        self.team = []
        self.have_map = False
        self.sent = False
        self.first = None
        self.last_report = -1e9
        self.reached_at = None
        self.status = ''
        self.min_distance = math.inf
        self.out = opts.output
        self.out.mkdir(parents=True, exist_ok=True)
        self.log = (self.out/'telemetry.jsonl').open('w')
        self.reference = [np.array([[-1.12,-3.85],[-.88,-3.85],[.445,-.857],[-1.095,-.857]],np.float32),
                          np.array([[.23,-3.85],[.47,-3.85],[.445,-.857],[-1.095,-.857]],np.float32)]
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.initial_pub = self.create_publisher(NavPath, '/demo/initial_path', qos)
        self.markers = self.create_publisher(MarkerArray, '/demo/references', qos)
        self.create_subscription(PoseArray, '/formation/robot_states', self.on_team, 10)
        self.create_subscription(OccupancyGrid, '/map', self.on_map, qos)
        self.create_subscription(NavPath, '/dstar_lite/path', self.on_path, 10)
        self.create_subscription(String, '/social_navigation/status', self.on_status, 10)
        self.create_subscription(String, '/social_navigation/observation_status',
                                 lambda msg: self.event('observation', text=msg.data), 10)
        self.create_timer(.25, self.tick, clock=Clock(clock_type=ClockType.STEADY_TIME))

    def event(self, kind, **data):
        row=dict(wall_s=round(time.monotonic()-self.start,3),
                 sim_s=round(self.get_clock().now().nanoseconds/1e9,3), event=kind, **data)
        self.log.write(json.dumps(row,ensure_ascii=False)+'\n')
        self.log.flush()
        return row

    def on_map(self, _):
        self.have_map = True

    def on_team(self, msg):
        self.team = [(p.position.x,p.position.y) for p in msg.poses]

    def on_status(self, msg):
        self.status = msg.data
        self.event('social_status',text=msg.data)

    def on_path(self, msg):
        points=[(p.pose.position.x,p.pose.position.y) for p in msg.poses]
        if not self.sent or len(points)<2:
            return
        if math.dist(points[-1],(self.opts.x,self.opts.y)) > .2:
            return
        crossing=False
        for a,b in zip(points,points[1:]):
            for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.025))):
                point=(a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1]))
                crossing |= any(cv2.pointPolygonTest(poly,point,False)>=0 for poly in self.reference)
        self.event('live_path',points=points,crosses_reference_tv=bool(crossing))
        if self.first is None:
            self.first=msg
            self.initial_pub.publish(msg)
            row=self.event('initial_path',points=points,crosses_reference_tv=bool(crossing),
                           reference='authored geometric viewing corridor; NOT camera detection')
            (self.out/'initial_path.json').write_text(json.dumps(row,indent=2)+'\n')
            print('INITIAL_PATH '+json.dumps(row),flush=True)

    def references(self):
        out=MarkerArray()
        for i,poly in enumerate(self.reference):
            m=Marker();m.header.frame_id='map';m.ns='reference_tv_not_perception';m.id=i
            m.type=Marker.LINE_STRIP;m.action=Marker.ADD;m.pose.orientation.w=1.
            m.scale.x=.035;m.color.r=1.;m.color.b=1.;m.color.a=.7
            m.points=[Point(x=float(p[0]),y=float(p[1]),z=.04) for p in [*poly,poly[0]]]
            out.markers.append(m)
        for i,(x,y,text) in enumerate([(-.3,-4.45,'TV corridor REFERENCE'),
                                       (self.opts.x,self.opts.y,'GOAL: bedside')],10):
            m=Marker();m.header.frame_id='map';m.ns='demo_labels';m.id=i
            m.type=Marker.TEXT_VIEW_FACING;m.pose.position.x=x;m.pose.position.y=y
            m.pose.position.z=.15;m.pose.orientation.w=1.;m.scale.z=.23
            m.color.r=1.;m.color.g=.85;m.color.a=1.;m.text=text;out.markers.append(m)
        m=Marker();m.header.frame_id='map';m.ns='goal';m.id=30;m.type=Marker.CYLINDER
        m.pose.position.x=self.opts.x;m.pose.position.y=self.opts.y;m.pose.orientation.w=1.
        m.scale.x=m.scale.y=.25;m.scale.z=.03;m.color.r=1.;m.color.g=.85;m.color.a=.9
        out.markers.append(m);self.markers.publish(out)

    def tick(self):
        elapsed=time.monotonic()-self.start
        self.references()
        if not self.sent and elapsed>5 and self.have_map and len(self.team)>=3:
            goal=PoseStamped();goal.header.frame_id='map';goal.header.stamp=self.get_clock().now().to_msg()
            goal.pose.position.x=self.opts.x;goal.pose.position.y=self.opts.y;goal.pose.orientation.w=1.
            self.goal_pub.publish(goal);self.sent=True
            print('GOAL '+json.dumps(self.event('goal',xy=[self.opts.x,self.opts.y],team=self.team)),flush=True)
        if self.sent and len(self.team)>=3:
            distance=math.dist(self.team[2],(self.opts.x,self.opts.y));self.min_distance=min(self.min_distance,distance)
            if elapsed-self.last_report>10:
                self.last_report=elapsed
                print('PROGRESS '+json.dumps(self.event('progress',team=self.team,leader_goal_distance=distance,status=self.status)),flush=True)
            if distance<.16 and self.reached_at is None:self.reached_at=time.monotonic()
        if elapsed>self.opts.seconds or (self.reached_at and time.monotonic()-self.reached_at>15):
            self.finish()
            raise SystemExit

    def finish(self):
        result=self.event('summary',goal=[self.opts.x,self.opts.y],team=self.team,
                          initial_path_received=self.first is not None,
                          min_leader_goal_distance=None if math.isinf(self.min_distance) else self.min_distance,
                          leader_within_016m=self.reached_at is not None,
                          note='Leader distance alone does not establish team completion or collision freedom.')
        (self.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print('SUMMARY '+json.dumps(result),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--x',type=float,default=-3.9);p.add_argument('--y',type=float,default=-1.35)
    p.add_argument('--seconds',type=float,default=750)
    p.add_argument('--output',type=Path,default=Path('recordings/2026-10-28_bedside_tv'))
    opts,ros=p.parse_known_args();rclpy.init(args=ros);node=Demo(opts)
    try:rclpy.spin(node)
    except KeyboardInterrupt:node.finish()
    finally:node.log.close();node.destroy_node();rclpy.shutdown()


if __name__=='__main__':main()
