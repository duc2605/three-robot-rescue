"""Paper-2 APF/MPC ROS adapter using existing perception and robot sensing."""
import json
import math
import time
import numpy as np
import rclpy
from rclpy.clock import Clock, ClockType
from geometry_msgs.msg import Twist, PoseArray
from std_msgs.msg import String

from .dstar_mpc_controller import ThreeRobotDStarMPC, quaternion_yaw
from .paper2_apf_mpc_core import (solve_mpc, predict_controls, follower_velocity,
                          virtual_target, limit, wrap, velocity_trace, trace_safe)


class Paper2Controller(ThreeRobotDStarMPC):
    def __init__(self):
        super().__init__()
        self.declare_parameter('motion_enabled', True)
        self.declare_parameter('paper2_solver_budget', .15)
        self.enabled = bool(self.get_parameter('motion_enabled').value)
        self.cmd_pubs = [self.create_publisher(Twist, f'/{n}/cmd_vel', 1) for n in self.robot_names]
        self.status_pub = self.create_publisher(String, '/paper2/status', 10)
        self.create_subscription(PoseArray, '/leader/people/poses', self.people_callback, 1)
        self.world_velocity = [np.zeros(2) for _ in range(3)]
        self.previous_measurements = [None]*3
        self.scan_time, self.scan_wall = [-math.inf]*3, [-math.inf]*3
        self.static_obstacles = np.empty((0, 5))
        self.people_obstacles = []
        self.people_time = -math.inf
        self.warm = None
        self.commands = [[0., 0., 0.] for _ in range(3)]
        self.state, self.solve_info = 'WAIT_GOAL', {}
        self.last_tick_wall, self.last_status = time.monotonic(), -math.inf
        self.distance = [0.]*3
        self.errors = [0.]*3
        self.goal_start = self.goal_reached = None
        self.sim_previous = None
        self.observation_enabled = False
        self.create_timer(.2, self.watchdog,
                          clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.get_logger().info('PAPER2_V1_ADAPTED: continuous APF-MPC leader; enhanced APF followers; '
                               'no D*/GWO/DWA/distributed-MPC controller in this backend.')

    def record_pose(self, index, x, y, yaw):
        if hasattr(self, 'previous_measurements') and all(math.isfinite(v) for v in (x, y, yaw)):
            now = self.now_seconds()
            previous = self.previous_measurements[index]
            if previous is not None:
                dt = now-previous[0]
                if .005 <= dt <= .5:
                    displacement = np.array((x, y))-previous[1]
                    self.world_velocity[index] = .6*limit(displacement/dt, .5)+.4*self.world_velocity[index]
                    if self.goal_start is not None:
                        self.distance[index] += float(np.linalg.norm(displacement))
            self.previous_measurements[index] = (now, np.array((x, y)))
        super().record_pose(index, x, y, yaw)

    def scan_callback(self, msg, index):
        now = self.now_seconds()
        stamp = msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        if self.poses_ready() and 0 <= now-stamp <= .3:
            self.scan_time[index], self.scan_wall[index] = stamp, time.monotonic()
        super().scan_callback(msg, index)

    def people_callback(self, msg):
        stamp = msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        if msg.header.frame_id != 'map' or not 0 <= self.now_seconds()-stamp <= .8:
            return
        self.people_obstacles = [(p.position.x, p.position.y, 0., 0., .22)
                                 for p in msg.poses
                                 if math.isfinite(p.position.x) and math.isfinite(p.position.y)]
        # No identity association: do not manufacture person velocities.
        self.people_time = stamp

    def map_callback(self, msg):
        info = msg.info
        geometry = (info.width, info.height, info.resolution,
                    info.origin.position.x, info.origin.position.y,
                    quaternion_yaw(info.origin.orientation))
        if self.map_msg is not None and self.map_geometry == geometry and msg.data == self.map_msg.data:
            return
        self.width, self.height, self.resolution, self.origin_x, self.origin_y, self.origin_yaw = geometry
        self.blocked = self.make_inflated_grid(msg.data)
        self.map_geometry, self.map_msg = geometry, msg
        points = {}
        c, s = math.cos(self.origin_yaw), math.sin(self.origin_yaw)
        for index, occupied in enumerate(self.collision_grid.occupied):
            if occupied:
                x, y = (index % self.width+.5)*self.resolution, (index//self.width+.5)*self.resolution
                wx, wy = self.origin_x+c*x-s*y, self.origin_y+s*x+c*y
                points.setdefault((round(wx/.15), round(wy/.15)),
                                  (wx, wy, 0., 0., self.resolution*.71))
        self.static_obstacles = np.array(list(points.values()), dtype=float).reshape(-1, 5)
        self.warm = None

    def set_goal(self, x, y):
        if not math.isfinite(x) or not math.isfinite(y):
            return
        self.goal_xy = (float(x), float(y))
        self.goal_start, self.goal_reached = self.now_seconds(), None
        self.distance, self.warm = [0.]*3, None
        self.state = 'NEW_GOAL'
        self.publish_global_path([], [])
        self.stop()

    def update_dynamic_layer(self, force=False):
        pass

    def plan(self):
        raise RuntimeError('Baseline planner disabled in PAPER2')

    def search_callback(self, msg):
        try:
            self.search_status(json.loads(msg.data).get('id'), 'rejected',
                               'PAPER2: active observation is not implemented')
        except (ValueError, AttributeError):
            pass

    def start_observation(self, *args, **kwargs):
        return False

    def stop(self):
        if hasattr(self, 'cmd_pubs'):
            self.commands = [[0., 0., 0.] for _ in range(3)]
            for pub in self.cmd_pubs:
                pub.publish(Twist())

    def watchdog(self):
        if (time.monotonic()-self.last_tick_wall > 1.
                or not self.poses_ready()
                or any(time.monotonic()-t > 5. for t in self.scan_wall)):
            self.stop()

    def obstacles(self, poses):
        rows = list(self.static_obstacles)
        now = self.now_seconds()
        rows += [(x, y, 0., 0., .03) for scan in self.scan_points for x, y, expiry in scan if expiry > now]
        if 0 <= now-self.people_time < .8:
            rows += self.people_obstacles
        # Merge nearby samples; exact grid checks remain independent of this
        # potential-field approximation. Preserve larger people radii.
        merged = {}
        for row in rows:
            key = (round(row[0]/.12), round(row[1]/.12))
            if key not in merged or row[4] > merged[key][4]:
                merged[key] = row
        rows = sorted(merged.values(),
                      key=lambda p: min(math.dist(p[:2], q[:2]) for q in poses))
        return np.asarray(rows[:100], float).reshape(-1, 5)

    def tick(self):
        self.publish_team_states()
        self.publish_markers()
        now = self.now_seconds()
        if not self.enabled or self.goal_xy is None:
            self.state = 'WAIT_GOAL' if self.enabled else 'MOTION_DISABLED'
            self.stop()
            return
        if not self.poses_ready() or self.collision_grid is None:
            self.state = 'WAIT_MAP_OR_FRESH_POSES'
            self.stop()
            return
        if any(not 0 <= now-t < .65 or time.monotonic()-w > 5
               for t, w in zip(self.scan_time, self.scan_wall)):
            self.state = 'WAIT_FRESH_LIDAR'
            self.stop()
            return
        if not self.collision_grid.point_free(self.goal_xy):
            self.state = 'GOAL_BLOCKED_IN_CURRENT_MAP'
            self.publish_global_path([], [])
            self.warm = None
            self.stop()
            return
        poses = [self.get_robot_pose(i)[:3] for i in range(3)]
        leader, middle, tail = self.convoy_order
        targets = {middle: virtual_target(poses[leader], self.follow_gap, self.triangle_half_width),
                   tail: virtual_target(poses[leader], self.follow_gap, -self.triangle_half_width)}
        self.errors = [0.]*3
        self.errors[leader] = math.dist(poses[leader][:2], self.goal_xy)
        for i in (middle, tail):
            self.errors[i] = math.dist(poses[i][:2], targets[i])
        if self.errors[leader] < .12 and max(self.errors[middle], self.errors[tail]) < .18:
            self.state = 'GOAL_REACHED'
            if self.goal_reached is None:
                self.goal_reached = now-self.goal_start
            self.stop()
            return
        environment = self.obstacles(poses)
        peer_obs = [(poses[j][0], poses[j][1], *self.world_velocity[j], .18)
                    for j in range(3) if j != leader]
        leader_obs = np.vstack([environment, np.asarray(peer_obs)])
        vmax = .08 if max(self.errors[middle], self.errors[tail]) > .5 else .18
        # When current measured velocity exceeds a reduced limit, use the old
        # physical limit in the optimizer and decelerate through the safety gate.
        solver_vmax = max(vmax, min(.28, float(np.linalg.norm(self.world_velocity[leader]))))
        controls, self.solve_info = solve_mpc(
            poses[leader][:2], self.goal_xy, self.world_velocity[leader], leader_obs,
            warm=self.warm, vmax=solver_vmax,
            budget=float(self.get_parameter('paper2_solver_budget').value))
        if controls is None:
            self.state = 'MPC_NO_FEASIBLE_RESULT'
            self.stop()
            return
        self.warm = controls
        positions, _ = predict_controls(poses[leader][:2], controls)
        self.publish_global_path([tuple(poses[leader][:2])]+[tuple(p) for p in positions],
                                 [poses[leader][2]]*(len(positions)+1))
        desired = limit(controls[0], vmax)
        bearing = math.atan2(desired[1], desired[0]) if np.linalg.norm(desired) > .005 else poses[leader][2]
        heading_error = wrap(bearing-poses[leader][2])
        yaw_rate = float(np.clip(1.5*heading_error, -.7, .7))
        if abs(heading_error) > .65:
            desired = np.zeros(2)
        if self.errors[leader] < .12:
            desired, yaw_rate = np.zeros(2), 0.
        traces = [velocity_trace(p, (0, 0)) for p in poses]
        world_commands = [np.zeros(2) for _ in range(3)]
        modes = ['']*3
        for i in self.convoy_order:
            peer_rows = np.asarray([(poses[j][0], poses[j][1], *self.world_velocity[j], .18)
                                    for j in range(3) if j != i])
            obstacles = np.vstack([environment, peer_rows])
            if i == leader:
                candidate = desired
            else:
                offset = targets[i]-np.asarray(poses[leader][:2])
                target_velocity = world_commands[leader]+yaw_rate*np.array([-offset[1], offset[0]])
                candidate = follower_velocity(poses[i][:2], self.world_velocity[i],
                                              targets[i], target_velocity, obstacles)
            selected = None
            peers = [traces[j] for j in range(3) if j != i]
            # This is an added safety gate, not DWA or another local planner.
            for factor in (1., .75, .5, .25, 0.):
                velocity = candidate*factor
                trace = velocity_trace(poses[i], velocity)
                if trace_safe(trace, self.collision_grid, obstacles, peers):
                    selected = velocity, trace, factor
                    break
            if selected is None:
                selected = np.zeros(2), velocity_trace(poses[i], (0, 0)), 0.
                modes[i] = 'EMERGENCY_HOLD'
            else:
                modes[i] = ('APF_MPC' if i == leader else 'ENHANCED_APF') if selected[2] == 1 else 'SAFETY_BRAKE'
            world_commands[i], traces[i], _ = selected
        self.state = 'TRACKING: '+','.join(modes)
        if abs(heading_error) > .65:
            self.state += '; LEADER_ALIGN_CAMERA'
        for i, velocity in enumerate(world_commands):
            yaw = poses[i][2]
            msg = Twist()
            msg.linear.x = float(math.cos(yaw)*velocity[0]+math.sin(yaw)*velocity[1])
            msg.linear.y = float(-math.sin(yaw)*velocity[0]+math.cos(yaw)*velocity[1])
            msg.angular.z = yaw_rate if i == leader else float(np.clip(wrap(poses[leader][2]-yaw), -.7, .7))
            self.commands[i] = [msg.linear.x, msg.linear.y, msg.angular.z]
            self.cmd_pubs[i].publish(msg)

    def control_tick(self):
        if not hasattr(self, 'warm'):
            return
        self.last_tick_wall = time.monotonic()
        now = self.now_seconds()
        if self.sim_previous is not None and now < self.sim_previous:
            self.warm = None
            self.scan_time, self.scan_wall = [-math.inf]*3, [-math.inf]*3
            self.previous_measurements = [None]*3
            self.world_velocity = [np.zeros(2) for _ in range(3)]
            self.distance = [0.]*3
            self.people_obstacles, self.people_time = [], -math.inf
            self.goal_start, self.goal_reached = now, None
            self.stop()
        self.sim_previous = now
        try:
            self.tick()
        except Exception as exc:
            self.stop()
            self.state = 'ERROR: '+str(exc)
            self.get_logger().error(self.state, throttle_duration_sec=3.)
        if time.monotonic()-self.last_status >= .5:
            self.last_status = time.monotonic()
            msg = String()
            msg.data = json.dumps({
                'backend': 'PAPER2_V1_ADAPTED', 'state': self.state,
                'leader': self.robot_names[self.leader_index], 'goal': self.goal_xy,
                'solver': self.solve_info, 'travelled_m': self.distance,
                'formation_error_m': self.errors, 'commands_body_vx_vy_w': self.commands,
                'goal_elapsed_sim_s': None if self.goal_start is None else now-self.goal_start,
                'goal_reached_sim_s': self.goal_reached,
                'obstacle_velocity_model': 'peers_measured;people_and_lidar_stationary_unknown',
                'active_observation': False,
            }, allow_nan=False)
            self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = Paper2Controller()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
