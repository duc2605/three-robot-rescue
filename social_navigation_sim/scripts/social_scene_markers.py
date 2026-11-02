#!/usr/bin/env python3
"""Display authored scenario annotations; this node does not detect people."""

import json
import math
from pathlib import Path

import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from visualization_msgs.msg import Marker, MarkerArray
from scenario_motion import sample_motion


class SocialSceneMarkers(Node):
    def __init__(self):
        super().__init__('social_scene_markers')
        self.declare_parameter('scene_file', '')
        self.scene = json.loads(Path(self.get_parameter('scene_file').value).read_text())
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.people_pub = self.create_publisher(MarkerArray, '/social_scene/people', qos)
        self.zones_pub = self.create_publisher(MarkerArray, '/social_scene/ground_truth_zones', qos)
        self.create_timer(1.0, self.publish)
        self.publish()
        self.get_logger().info('Publishing authored /social_scene annotations; camera perception and social navigation use separate nodes.')

    def marker(self, index, namespace, kind, x, y, z, color):
        marker = Marker()
        marker.header.frame_id = self.scene['frame_id']
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns, marker.id, marker.type = namespace, index, kind
        marker.action = Marker.ADD
        marker.pose.position.x, marker.pose.position.y, marker.pose.position.z = float(x), float(y), float(z)
        marker.pose.orientation.w = 1.0
        marker.color.r, marker.color.g, marker.color.b = (float(v) for v in color)
        marker.color.a = 0.9
        return marker

    def publish(self):
        people = MarkerArray(markers=[Marker(action=Marker.DELETEALL)])
        zones = MarkerArray(markers=[Marker(action=Marker.DELETEALL)])
        colors = {z['name']: z['color'] for z in self.scene['zones']}
        for i, person in enumerate(self.scene['people']):
            x, y = person['x'], person['y']
            heading = person['yaw']
            offset = 0.
            motions = [m for m in self.scene.get('motions', []) if m['model'] == person['name']]
            if motions:
                current = next((p for m in motions if (p := sample_motion(
                    m, self.get_clock().now().nanoseconds/1e9)) is not None), None)
                if current is None:
                    continue
                x, y, offset, heading = current
            color = colors[person['group']]
            height = person.get('height', 1.7)
            body = self.marker(i, 'scenario_people', Marker.CYLINDER, x, y, height / 2, color)
            body.scale.x = body.scale.y = 2.0 * person['radius']
            body.scale.z = float(height)
            body.pose.position.z += offset
            if person.get('posture') == 'lying':
                body.type = Marker.CUBE
                body.scale.x, body.scale.y, body.scale.z = 1.85, .65, .45
                body.pose.position.z = .71
            people.markers.append(body)
            arrow = self.marker(i, 'scenario_gaze', Marker.ARROW, x, y, 0.08, color)
            arrow.pose.orientation.z = math.sin(heading / 2)
            arrow.pose.orientation.w = math.cos(heading / 2)
            arrow.scale.x, arrow.scale.y, arrow.scale.z = 0.9, 0.10, 0.10
            if person.get('posture') != 'lying':
                people.markers.append(arrow)
            label = self.marker(i, 'scenario_names', Marker.TEXT_VIEW_FACING, x, y, 2.0, color)
            label.scale.z = 0.22
            label.text = person['name'] + '\n[scenario] ' + person['activity']
            people.markers.append(label)
        for i, zone in enumerate(self.scene['zones']):
            x, y = zone['center']
            sx, sy = zone['size']
            if min(sx, sy) <= 0:
                continue
            outline = self.marker(i, 'scenario_zone_bounds', Marker.LINE_STRIP, 0, 0, 0.02, zone['color'])
            outline.scale.x = 0.035
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)):
                outline.points.append(Point(x=float(x + dx * sx / 2), y=float(y + dy * sy / 2), z=0.0))
            zones.markers.append(outline)
            label = self.marker(i, 'scenario_zone_names', Marker.TEXT_VIEW_FACING,
                                x, y + sy / 2 + 0.2, 0.1, zone['color'])
            label.scale.z = 0.22
            label.text = '[GROUND TRUTH] ' + zone['name']
            zones.markers.append(label)
        self.people_pub.publish(people)
        self.zones_pub.publish(zones)


def main(args=None):
    rclpy.init(args=args)
    node = SocialSceneMarkers()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
