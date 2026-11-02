"""ROS adapter for the independently implemented paper-1 experiment."""
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor

import rclpy
from rclpy.clock import Clock, ClockType
from geometry_msgs.msg import Twist
from std_msgs.msg import String

from .grid_clearance import GridClearance
from .paper1_gwo_woa_core import gwo_woa, dwa, virtual_target, follower_control, rollout
from .dstar_mpc_controller import ThreeRobotDStarMPC


class Paper1Controller(ThreeRobotDStarMPC):
    """Reuse only existing pose/TF/scan/marker infrastructure, not D*/MPC."""

    def __init__(self):
        super().__init__()
        self.declare_parameter('motion_enabled', True)
        self.declare_parameter('paper1_seed', 7)
        self.declare_parameter('paper1_plan_budget', 2.0)
        self.enabled = bool(self.get_parameter('motion_enabled').value)
        self.cmd_pubs = [self.create_publisher(Twist, f'/{n}/cmd_vel', 1)
                         for n in self.robot_names]
        self.status_pub = self.create_publisher(String, '/paper1/status', 10)
        self.executor_pool = ThreadPoolExecutor(max_workers=1)
        self.pending = None
        self.goal_version = 0
        self.route = None
        self.route_index = 0
        self.last_plan_wall = -math.inf
        self.last_tick_wall = time.monotonic()
        self.last_run_sim = None
        self.scan_wall = [-math.inf]*3
        self.scan_time = [-math.inf]*3
        self.commands = [(0., 0.)]*3
        self.last_status_wall = -math.inf
        self.state = 'WAIT_GOAL'
        self.plan_info = {}
        self.plan_trial = 0
        self.distance = [0.]*3
        self.previous_poses = None
        self.errors = [0.]*3
        self.goal_start = None
        self.goal_reached = None
        self.observation_enabled = False
        self.create_timer(.2, self.safety_watchdog,
                          clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.get_logger().info('PAPER1_V1: GWO-WOA + leader DWA + follower Eq32; '
                               'camera/social map and LiDAR enabled; D*/MPC disabled.')

    def map_callback(self, msg):
        info = msg.info
        from .dstar_mpc_controller import quaternion_yaw
        geometry = (info.width, info.height, info.resolution,
                    info.origin.position.x, info.origin.position.y,
                    quaternion_yaw(info.origin.orientation))
        if (self.map_msg is not None and geometry == self.map_geometry
                and msg.data == self.map_msg.data):
            return
        self.map_msg = msg
        self.width, self.height, self.resolution, self.origin_x, self.origin_y, self.origin_yaw = geometry
        self.blocked = self.make_inflated_grid(msg.data)
        if self.map_geometry is not None and self.map_geometry != geometry:
            self.route = None
            self.goal_version += 1
            self.stop()
        self.map_geometry = geometry

    def scan_callback(self, msg, index):
        now = self.now_seconds()
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
        if self.poses_ready() and 0 <= now-stamp <= .3:
            self.scan_wall[index], self.scan_time[index] = time.monotonic(), stamp
        super().scan_callback(msg, index)

    def set_goal(self, x, y):
        if not math.isfinite(x) or not math.isfinite(y):
            return
        self.goal_xy = (float(x), float(y))
        self.goal_version += 1
        self.route, self.route_index = None, 0
        self.publish_global_path([], [])
        self.plan_trial = 0
        self.distance, self.previous_poses = [0.]*3, None
        self.goal_start, self.goal_reached = self.now_seconds(), None
        self.stop()
        self.state = 'NEW_GOAL'

    def stop(self):
        if hasattr(self, 'cmd_pubs'):
            self.commands = [(0., 0.)]*3
            for pub in self.cmd_pubs:
                pub.publish(Twist())

    def safety_watchdog(self):
        wall = time.monotonic()
        if (wall-self.last_tick_wall > 1.0 or not self.poses_ready()
                or any(wall-t > 5.0 for t in self.scan_wall)):
            self.stop()

    def update_dynamic_layer(self, force=False):
        # The baseline routine is intentionally unused by this backend.
        pass

    def plan(self):
        # Parent methods must never silently invoke D* in the paper backend.
        raise RuntimeError('D* planner is not available in PAPER1_V1')

    def search_callback(self, msg):
        # Active camera turns would need another paper-compatible task layer.
        # Return a response instead of allowing the social requester to hang.
        try:
            ident = json.loads(msg.data).get('id')
            self.search_status(ident, 'rejected', 'PAPER1_V1: active observation unsupported')
        except (ValueError, AttributeError):
            pass

    def start_observation(self, *args, **kwargs):
        return False

    def status(self):
        if time.monotonic()-self.last_status_wall < .5:
            return
        self.last_status_wall = time.monotonic()
        elapsed = None if self.goal_start is None else self.now_seconds()-self.goal_start
        msg = String()
        msg.data = json.dumps({
            'backend': 'PAPER1_V1', 'state': self.state,
            'global_planner': 'GWO_WOA_1D', 'leader_control': 'DWA',
            'follower_control': 'Eq32_with_DWA_safety_filter',
            'goal': self.goal_xy, 'plan': self.plan_info,
            'goal_elapsed_sim_s': elapsed, 'goal_reached_sim_s': self.goal_reached,
            'travelled_m': self.distance, 'formation_error_m': self.errors,
            'command_v_w': self.commands,
            'active_observation': False,
            'scan_age_sim_s': [round(self.now_seconds()-t, 3)
                               if math.isfinite(t) else None for t in self.scan_time],
        }, allow_nan=False)
        self.status_pub.publish(msg)

    def tick(self):
        now = self.now_seconds()
        self.publish_team_states()
        self.publish_markers()
        if not self.enabled:
            self.state = 'MOTION_DISABLED'
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
        if self.goal_xy is None:
            self.state = 'WAIT_GOAL'
            self.stop()
            return
        poses = [self.get_robot_pose(i)[:3] for i in range(3)]
        if self.previous_poses is not None:
            for i in range(3):
                self.distance[i] += math.dist(poses[i][:2], self.previous_poses[i][:2])
        self.previous_poses = poses
        leader, middle, tail = self.convoy_order
        targets = [None]*3
        targets[leader] = (*self.goal_xy, poses[leader][2])
        targets[middle] = virtual_target(poses[leader], self.follow_gap, self.triangle_half_width)
        targets[tail] = virtual_target(poses[leader], self.follow_gap, -self.triangle_half_width)
        self.errors = [math.dist(poses[i][:2], targets[i][:2]) for i in range(3)]
        if not self.collision_grid.point_free(self.goal_xy):
            self.state = 'GOAL_BLOCKED_IN_CURRENT_MAP'
            self.route = None
            self.publish_global_path([], [])
            self.stop()
            return
        # Collect results even if goal changed. Never run multiple planners.
        if self.pending is not None and self.pending[1].done():
            version, future = self.pending
            self.pending = None
            self.last_plan_wall = time.monotonic()
            route, info = future.result()
            if version == self.goal_version:
                self.plan_info = info
                if route and all(self.collision_grid.segment_free(a, b)
                                 for a, b in zip(route, route[1:])):
                    self.route, self.route_index = route, 0
                    self.publish_global_path(route, self.path_geometry(route)[0])
        if self.route is not None:
            # Verify remaining route on the latest social map. Newly observed
            # LiDAR points are also enforced by DWA at every control tick.
            remaining = [poses[leader][:2]] + self.route[self.route_index:]
            if not all(self.collision_grid.segment_free(a, b)
                       for a, b in zip(remaining, remaining[1:])):
                self.route = None
                self.publish_global_path([], [])
        if self.route is None:
            self.stop()
            if self.pending is None and time.monotonic()-self.last_plan_wall > 1.0:
                g = self.collision_grid
                snapshot = GridClearance(g.width, g.height, g.resolution,
                                         (g.origin_x, g.origin_y, self.origin_yaw),
                                         g.occupied, g.radius)
                seed = int(self.get_parameter('paper1_seed').value)+self.plan_trial
                self.plan_trial += 1
                self.pending = (self.goal_version, self.executor_pool.submit(
                    gwo_woa, poses[leader], self.goal_xy, snapshot, tuple(self.blocked), seed,
                    budget=float(self.get_parameter('paper1_plan_budget').value)))
                self.last_plan_wall = time.monotonic()
            self.state = 'PLANNING_GWO_WOA' if self.pending else 'WAIT_RETRY_GWO_WOA'
            return
        # Advance only along measured leader progress, not a free-running clock.
        begin = self.route_index
        end = min(len(self.route), begin+150)
        self.route_index = min(range(begin, end),
                               key=lambda j: math.dist(poses[leader][:2], self.route[j]))
        target_index, walk = self.route_index, 0.
        while target_index < len(self.route)-1 and walk < .65:
            walk += math.dist(self.route[target_index], self.route[target_index+1])
            target_index += 1
        targets[leader] = (*self.route[target_index], poses[leader][2])
        if (math.dist(poses[leader][:2], self.goal_xy) < .12
                and max(self.errors[middle], self.errors[tail]) < .18):
            self.state = 'GOAL_REACHED'
            if self.goal_reached is None:
                self.goal_reached = now-self.goal_start
            self.stop()
            return
        points = [p[:2] for scan in self.scan_points for p in scan if p[2] > now]
        traces = [rollout(p, 0, 0) for p in poses]
        commands, modes = [(0., 0.)]*3, ['']*3
        # Limit leader progress if followers lag. Added integration safeguard.
        leader_vmax = .08 if max(self.errors[middle], self.errors[tail]) > .5 else .16
        for i in self.convoy_order:
            peers = [traces[j] for j in range(3) if j != i]
            desired = None if i == leader else follower_control(
                poses[i], targets[i], *commands[leader])
            if i != leader and abs(commands[leader][0]) < .015 and self.errors[i] > .18:
                # Eq32 has no lateral convergence authority at v_ref=0.
                # Added DWA recovery for final assembly, explicitly not Eq32.
                desired = None
            if i == leader and math.dist(poses[i][:2], self.goal_xy) < .12:
                commands[i], traces[i], modes[i] = (0., 0.), rollout(poses[i], 0, 0), 'LEADER_AT_GOAL'
            else:
                commands[i], traces[i], modes[i] = dwa(
                    poses[i], self.commands[i], targets[i], self.collision_grid,
                    points, peers, desired=desired,
                    vmax=leader_vmax if i == leader else .22,
                    forward_only=(i == leader))
        self.commands = commands
        for i, (v, w) in enumerate(commands):
            msg = Twist()
            msg.linear.x, msg.angular.z = v, w
            self.cmd_pubs[i].publish(msg)
        self.state = 'TRACKING: '+','.join(modes)

    def control_tick(self):
        if not hasattr(self, 'pending'):
            return
        self.last_tick_wall = time.monotonic()
        now = self.now_seconds()
        if self.last_run_sim is not None and now < self.last_run_sim:
            self.goal_version += 1
            self.route = None
            self.scan_time, self.scan_wall = [-math.inf]*3, [-math.inf]*3
            self.goal_start, self.goal_reached = now, None
            self.previous_poses = None
            self.distance = [0.]*3
            self.stop()
        self.last_run_sim = now
        try:
            self.tick()
        except Exception as exc:
            self.stop()
            self.state = 'ERROR: '+str(exc)
            self.get_logger().error(self.state, throttle_duration_sec=3.)
        self.status()

    def destroy_node(self):
        self.stop()
        self.executor_pool.shutdown(wait=True, cancel_futures=True)
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = Paper1Controller()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
