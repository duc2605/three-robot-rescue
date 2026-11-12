#!/usr/bin/env python3
"""Pedestrian permissions applied only to the outdoor robot command topics."""
import copy
import json
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage

from social_navigation_planner.grid_clearance import GridClearance
from street_rules import walkable, entry_axes, signal_allows_entry


class StreetRules(Node):
    def __init__(self):
        super().__init__('street_navigation_rules')
        self.grid = None
        self.poses, self.commands = {}, {}
        self.signal = None
        self.signal_wall = -math.inf
        self.last_status = -math.inf
        self.cmd_publishers = [self.create_publisher(Twist,f'/robot{i+1}/cmd_vel',1) for i in range(3)]
        qos = QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.map_pub = self.create_publisher(OccupancyGrid,'/street_navigation/map',qos)
        self.status_pub = self.create_publisher(String,'/street/rules_status',10)
        self.create_subscription(OccupancyGrid,'/map',self.on_map,qos)
        self.create_subscription(TFMessage,'/gazebo/world_poses',self.on_poses,qos_profile_sensor_data)
        self.create_subscription(String,'/street/traffic_state',self.on_signal,10)
        for i in range(3):
            self.create_subscription(Twist,f'/robot{i+1}/navigation_cmd_vel',
                                     lambda msg,i=i:self.on_command(msg,i),1)
        self.create_timer(.05,self.tick)

    def now(self):
        return self.get_clock().now().nanoseconds*1e-9

    def on_map(self,msg):
        result = copy.deepcopy(msg)
        q=msg.info.origin.orientation
        yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        c,s=math.cos(yaw),math.sin(yaw)
        data=list(msg.data)
        for index in range(len(data)):
            x=(index%msg.info.width+.5)*msg.info.resolution
            y=(index//msg.info.width+.5)*msg.info.resolution
            wx=msg.info.origin.position.x+c*x-s*y
            wy=msg.info.origin.position.y+s*x+c*y
            if not walkable(wx,wy):
                data[index]=100
        result.data=data
        self.grid=GridClearance(msg.info.width,msg.info.height,msg.info.resolution,
            (msg.info.origin.position.x,msg.info.origin.position.y,yaw),[v<0 or v>=50 for v in data],.18)
        self.map_pub.publish(result)

    def on_poses(self,msg):
        now=self.now()
        for transform in msg.transforms:
            name=transform.child_frame_id
            if name not in ('robot1','robot2','robot3'):
                continue
            stamp=transform.header.stamp.sec+transform.header.stamp.nanosec*1e-9
            # Some Pose_V bridge versions omit individual transform stamps.
            if stamp==0.:
                stamp=now
            if not 0 <= now-stamp <= .4:
                continue
            q=transform.transform.rotation;p=transform.transform.translation
            yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
            if all(math.isfinite(v) for v in (p.x,p.y,yaw)):
                self.poses[name]=(stamp,p.x,p.y,yaw)

    def on_signal(self,msg):
        try:
            data=json.loads(msg.data)
            if data.get('version')==1 and 0 <= self.now()-float(data['stamp']) <= .6:
                self.signal=data
                self.signal_wall=time.monotonic()
        except (ValueError,TypeError,KeyError):
            return

    def on_command(self,msg,index):
        values=(msg.linear.x,msg.linear.y,msg.angular.z)
        if all(math.isfinite(v) for v in values):
            self.commands[index]=(self.now(),time.monotonic(),copy.deepcopy(msg))

    def tick(self):
        now=self.now();status=[]
        for i,publisher in enumerate(self.cmd_publishers):
            name=f'robot{i+1}';pose=self.poses.get(name);command=self.commands.get(i)
            missing=[]
            if pose is None or not 0 <= now-pose[0] <= .4:
                missing.append('pose')
            if (command is None or not 0 <= now-command[0] <= .4
                    or time.monotonic()-command[1] > 3.):
                missing.append('command')
            if self.grid is None:
                missing.append('map')
            output=Twist();reason='waiting_fresh_pose_command_map';entering=set()
            if not missing:
                _,x,y,yaw=pose;candidate=command[2]
                points=[(x,y)]
                heading=yaw
                for _ in range(8):
                    mid=heading+.025*candidate.angular.z
                    x+=.05*(math.cos(mid)*candidate.linear.x-math.sin(mid)*candidate.linear.y)
                    y+=.05*(math.sin(mid)*candidate.linear.x+math.cos(mid)*candidate.linear.y)
                    heading+=.05*candidate.angular.z
                    points.append((x,y))
                fresh=(self.signal is not None and 0 <= now-self.signal['stamp'] <= .6
                       and time.monotonic()-self.signal_wall <= 3.)
                entering=set()
                for a,b in zip(points,points[1:]):
                    entering.update(entry_axes(a,b))
                green=fresh and all(signal_allows_entry(self.signal,axis,now) for axis in entering)
                if not all(self.grid.segment_free(a,b) for a,b in zip(points,points[1:])):
                    reason='sidewalk_or_crosswalk_route_required'
                elif entering and not green:
                    reason='waiting_pedestrian_green'
                else:
                    output=candidate;reason='pedestrian_route_permitted'
            publisher.publish(output)
            status.append(dict(robot=name,reason=reason,mode='pedestrian',missing_inputs=missing,
                pose_age=now-pose[0] if pose else None,
                command_age=now-command[0] if command else None,
                command=[output.linear.x,output.linear.y,output.angular.z],entry_axes=sorted(entering),
                pedestrian_green_axes=self.signal.get('pedestrian_green_axes',[]) if self.signal else []))
        if now < self.last_status or now-self.last_status >= .2:
            self.last_status=now
            self.status_pub.publish(String(data=json.dumps(dict(stamp=now,robots=status))))


def main():
    rclpy.init();node=StreetRules()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        for publisher in node.cmd_publishers:
            publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__=='__main__':main()
