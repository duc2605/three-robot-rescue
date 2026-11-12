"""Shared experiment sensing, limits and camera tasks for paper adapters."""
from dataclasses import asdict
import json
import math
import time

from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .grid_clearance import GridClearance
from .moving_obstacles import MotionTracks, scan_clusters, select_lidar_tracks, collision_risk
from .paper_models.environment import clusters, social_physical_gate
from .social_observation import ObservationSweep, angle


class PaperBehavior:
    def __init__(self, node, leader, now, subscribe_search=False):
        self.node, self.leader, self.now = node, leader, now
        self.tracks = [MotionTracks(padding=.02, persistence=.4, pause_reserve=True,
                                    classify_in_place=True) for _ in range(3)]
        self.points = [[] for _ in range(3)]
        self.stamps = [-math.inf]*3
        self.physical = None
        self.sweep = self.request = None
        self.last_observation = -math.inf
        self.wall_deadline = math.inf
        self.image_stamp = self.image_wall = -math.inf
        self.selected = [[] for _ in range(3)]
        self.feedback = node.create_publisher(String, '/social_navigation/search_status', 10)
        self.observation_status = node.create_publisher(String, '/social_navigation/observation_status', 1)
        self.decisions = [node.create_publisher(String, f'/robot{i+1}/escape_decision', 10) for i in range(3)]
        for name, default in [('max_linear_speed', .28), ('formation_speed', .16),
                              ('formation_follower_speed', .22), ('max_angular_speed', 1.0),
                              ('social_observation_enabled', True)]:
            if not node.has_parameter(name):
                node.declare_parameter(name, default)
        self.max_speed = float(node.get_parameter('max_linear_speed').value)
        self.max_angular_speed = float(node.get_parameter('max_angular_speed').value)
        self.leader_speed = float(node.get_parameter('formation_speed').value)
        self.follower_speed = float(node.get_parameter('formation_follower_speed').value)
        self.observation_enabled = bool(node.get_parameter('social_observation_enabled').value)
        if not math.isfinite(self.max_angular_speed) or self.max_angular_speed <= 0:
            raise ValueError('Paper angular speed limit must be positive')
        if not 0 < min(self.leader_speed, self.follower_speed) <= max(self.leader_speed, self.follower_speed) <= self.max_speed:
            raise ValueError('Paper behavior speed limits must be positive and bounded')
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        node.create_subscription(OccupancyGrid, '/map', self.on_map, qos)
        node.create_subscription(Image,'/leader/camera/image_raw',self.on_image,qos_profile_sensor_data)
        node.create_timer(.2,self.check_camera_deadline)
        if subscribe_search:
            node.create_subscription(String, '/social_navigation/search', self.on_search, 10)

    def on_image(self, msg):
        self.image_stamp = msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        self.image_wall = time.monotonic()

    def check_camera_deadline(self):
        if self.request is None:
            return
        now = self.now()
        if self.sweep is None and not 0 <= now-float(self.request['stamp']) < 1.:
            self.finish('rejected','camera task could not start with fresh control inputs')
        elif self.sweep is not None and (now >= self.sweep.deadline or time.monotonic() > self.wall_deadline):
            self.finish('aborted','camera task timed out')

    def on_map(self, msg):
        q = msg.info.origin.orientation
        yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        self.physical = GridClearance(msg.info.width, msg.info.height, msg.info.resolution,
            (msg.info.origin.position.x, msg.info.origin.position.y, yaw),
            [v < 0 or v >= 50 for v in msg.data], .18)

    def clear(self):
        self.finish('cancelled', 'simulation clock reset')
        for tracker in self.tracks:
            tracker.clear()
        self.points = [[] for _ in range(3)]
        self.stamps = [-math.inf]*3
        self.selected = [[] for _ in range(3)]
        self.last_observation = -math.inf
        self.image_stamp = self.image_wall = -math.inf

    def observe(self, index, points, pose, stamp):
        if stamp <= self.stamps[index] or pose is None:
            return
        self.points[index], self.stamps[index] = points, stamp
        observations = scan_clusters(points, pose)
        observations = [o for o in observations if self.physical is None
                        or self.physical.clearance(o[:2], .18) >= .18-1e-9]
        self.tracks[index].observe(observations, stamp)

    def obstacles(self, index, now):
        remote = [(j, o) for j, tracker in enumerate(self.tracks) if j != index
                  for o in tracker.recent(now)]
        chosen = select_lidar_tracks(self.tracks[index].recent(now),
            [o for _, o in remote], now, remote_sources=[j for j, _ in remote])
        self.selected[index] = chosen
        rows = [(*o.at(now), *o.velocity, o.radius) for o in chosen]
        if 0 <= now-self.stamps[index] <= .6:
            for x, y, radius in clusters(self.points[index]):
                if not any(math.dist((x,y),o.at(now)) <= o.radius for o in chosen):
                    rows.append((x,y,0.,0.,radius))
        return rows

    def telemetry(self, index, pose, now):
        return [dict(**asdict(o), risk=collision_risk(o,pose,now,.15) if pose else None)
                for o in self.selected[index][:24]]

    def gate(self, poses, commands, obstacles, social):
        bounded = []
        for i, (vx, vy, spin) in enumerate(commands):
            limit = min(self.max_speed, self.leader_speed if i == self.leader else self.follower_speed)
            factor = min(1., limit/max(math.hypot(vx,vy), 1e-9))
            bounded.append((vx*factor, vy*factor, max(-self.max_angular_speed,min(self.max_angular_speed,spin))))
        return social_physical_gate(poses,bounded,obstacles,self.physical,social,
                                    tracked=self.selected,now=self.now())

    def emit(self, poses, commands, reasons):
        now = self.now()
        for i, publisher in enumerate(self.decisions):
            publisher.publish(String(data=json.dumps(dict(stamp=now, reason=reasons[i], goal=None,
                stops=commands[i] == (0.,0.,0.), terminal_safe=False,
                safety_status=reasons[i], motion_tracks=self.telemetry(i,poses[i],now)),allow_nan=False)))

    def status(self, ident, state, reason):
        self.feedback.publish(String(data=json.dumps(dict(version=1, id=ident,
            stamp=self.now(), state=state, reason=reason))))

    def finish(self, state, reason):
        if self.request is not None:
            self.status(self.request['id'], state, reason)
        self.sweep = self.request = None
        self.observation_status.publish(String(data=state+': '+reason))
        self.last_observation = self.now()

    def on_search(self, msg):
        try:
            data = json.loads(msg.data)
            now = self.now()
            if (data.get('version') != 1 or data.get('frame_id') != 'map'
                    or not isinstance(data.get('id'),str) or not 0 <= now-float(data['stamp']) < 1.):
                return
            command = data['command']
            if command == 'start':
                point = data['point']
                if (len(point) != 2 or not all(math.isfinite(v) for v in point)
                        or data['kind'] not in ('find_screen','find_viewers','inspect_person','inspect_obstacle')):
                    return
                if not self.observation_enabled or self.request is not None or now-self.last_observation < 5.:
                    self.status(data['id'],'rejected','camera task disabled, busy or cooling down')
                else:
                    self.request = data
            elif self.request is not None and data['id'] == self.request['id']:
                if command in ('complete','cancel'):
                    self.finish('completed' if command == 'complete' else 'cancelled', 'social search '+command)
                elif command == 'focus' and self.sweep is not None:
                    point = data['point'];anchor = self.sweep.anchors[self.leader]
                    accepted = len(point)==2 and all(math.isfinite(v) for v in point) and self.sweep.focus_on(
                        math.atan2(point[1]-anchor[1],point[0]-anchor[0]))
                    self.status(data['id'],'focusing' if accepted else 'focus_rejected','camera focus request')
        except (ValueError,KeyError,TypeError,OverflowError):
            return

    def camera_commands(self, poses, now):
        if self.request is None:
            return None
        if (not 0 <= now-self.image_stamp < 1. or time.monotonic()-self.image_wall > 2.):
            self.finish('aborted' if self.sweep is not None else 'rejected','fresh camera frame required')
            return None
        if self.sweep is None:
            if (now-float(self.request['stamp']) >= 1. or self.physical is None
                    or any(math.dist(poses[i][:2],poses[j][:2]) < .32
                           for i,j in ((0,1),(0,2),(1,2)))
                    or any(not self.physical.point_free(p[:2]) for p in poses)):
                self.finish('rejected','camera task requires fresh request and safe clearance')
                return None
            p = self.request['point'];leader = poses[self.leader]
            self.sweep = ObservationSweep(poses,self.leader,now,min(.75,self.max_angular_speed),.8,
                math.atan2(p[1]-leader[1],p[0]-leader[0]),search_kind=self.request['kind'])
            self.wall_deadline = time.monotonic()+60.
            self.status(self.request['id'],'scanning',self.request['kind'])
            self.observation_status.publish(String(data='scanning: '+self.request['kind']))
        if any(collision_risk(o,poses[i],now,.15) is not None
               for i in range(3) for o in self.selected[i]):
            self.finish('aborted','approaching obstacle takes priority')
            return None
        rows = self.sweep.rows(poses,now,1,.1)
        if rows is None or time.monotonic() > self.wall_deadline:
            reason = self.sweep.reason or 'aborted: camera wall timeout'
            self.finish('completed' if reason.startswith('completed') else 'aborted',reason)
            return None
        commands = [(0.,0.,0.)]*3
        commands[self.leader] = (0.,0.,angle(rows[-1][self.leader][2]-poses[self.leader][2])/.1)
        return commands
