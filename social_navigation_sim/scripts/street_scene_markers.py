#!/usr/bin/env python3
"""Road markings for RViz only; authored geometry is never perception."""
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from visualization_msgs.msg import Marker, MarkerArray


class StreetMarkers(Node):
    def __init__(self):
        super().__init__('street_scene_markers')
        self.pub=self.create_publisher(MarkerArray,'/street/scenario_markers',
            QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_timer(1.,self.publish)

    def publish(self):
        out=MarkerArray()
        def box(x,y,sx,sy,color,yaw=0):
            m=Marker();m.header.frame_id='map';m.header.stamp=self.get_clock().now().to_msg()
            m.ns='authored_street_geometry_not_detection';m.id=len(out.markers);m.type=Marker.CUBE
            m.pose.position.x=float(x);m.pose.position.y=float(y);m.pose.position.z=.025
            m.pose.orientation.z=math.sin(yaw/2);m.pose.orientation.w=math.cos(yaw/2)
            m.scale.x=float(sx);m.scale.y=float(sy);m.scale.z=.01
            m.color.r,m.color.g,m.color.b,m.color.a=map(float,color)
            out.markers.append(m)
        box(0,0,76,12,(.12,.13,.15,.8));box(0,0,12,76,(.12,.13,.15,.8))
        for arm in range(4):
            a=arm*math.pi/2;c,s=math.cos(a),math.sin(a)
            for i in range(-6,7):
                x,y=-8.,i*.85
                box(c*x-s*y,s*x+c*y,1.5,.4,(1,1,1,1),a)
            x,y=-10,-3;box(c*x-s*y,s*x+c*y,.14,6,(1,1,1,1),a)
            for x in range(-35,-10,3):box(c*x,s*x,1.5,.09,(1,.85,.1,1),a)
        self.pub.publish(out)


def main():
    rclpy.init();n=StreetMarkers()
    try:rclpy.spin(n)
    finally:
        n.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__=='__main__':main()
