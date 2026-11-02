"""Shared ROS/safety adapter for ten explicitly approximate three-stage policies.

D* references and the existing LiDAR/peer/physical/social safety and emergency
escape remain shared infrastructure. Normal tracking uses the selected policy;
there is no baseline tracking-MPC fallback when its rollout is rejected.
"""
from copy import deepcopy
import json
import math
import time

import rclpy
from std_msgs.msg import String

from .comparison_methods.common import Memory
from .comparison_methods.registry import load_method
from .dstar_mpc_controller import DistributedRobotMPC, normalize_angle
from .moving_obstacles import swept_separation
from .peer_safety import peer_motion_free


class ComparisonRobotController(DistributedRobotMPC):
    def __init__(self):
        super().__init__()
        self.declare_parameter('comparison_method', 'compare01')
        self.declare_parameter('comparison_leader', 'robot3')
        key = str(self.get_parameter('comparison_method').value)
        if not key.startswith('compare') or not key[7:].isdigit():
            raise ValueError('comparison_method must be compare01..compare10')
        self.method_id = int(key[7:])
        self.pipeline, self.method_info = load_method(self.method_id)
        leader = str(self.get_parameter('comparison_leader').value)
        leader_index = self.robot_names.index(leader)
        # Shared prototype equations use canonical index 2 as leader.
        self.canonical = [i for i in range(3) if i != leader_index] + [leader_index]
        self.policy_index = self.canonical.index(self.robot_index)
        self.policy_memory = Memory()
        self.pending_memory = None
        self.stages = {}
        self.policy_reason = 'waiting'
        self.audit_pub = self.create_publisher(
            String, f'/comparison/{self.robot_name}/status', 10)
        self.get_logger().info(
            f'COMPARISON {self.method_id:02d}: {self.method_info["slug"]}; '
            'three-stage approximate policy + shared safety/escape; not a paper replication')

    def control_tick(self):
        self.pending_memory = None
        self.stages = {}
        super().control_tick()
        msg = String()
        msg.data = json.dumps(dict(
            method_id=self.method_id, project_paper=self.method_info['paper_number'],
            robot=self.robot_name, method=self.method_info['slug'],
            reason=self.policy_reason, stages=self.stages,
            shared_safety=True, shared_emergency_escape=True,
            command_body=self.last_command), allow_nan=False)
        self.audit_pub.publish(msg)

    def diagnostic_command(self, reason, command):
        self.policy_reason = reason
        if reason == 'mpc_tracking_command' and self.pending_memory is not None:
            self.policy_memory = self.pending_memory
        super().diagnostic_command(reason, command)

    def publish_stop(self, reason='unspecified_stop'):
        if hasattr(self, 'policy_memory'):
            # Reset integrators/observers on stale state or a stop; no windup.
            self.policy_memory = Memory()
            self.pending_memory = None
        super().publish_stop(reason)

    def bounded_tracking_beam(self, *args, **kwargs):
        return None, 'comparison_policy_rollout_rejected'

    def checked_tracking_rollout(self, now, command_dt, references, predictions,
                                 obstacles, moving, peers, deadline):
        trajectory = [self.own_pose]
        memory = deepcopy(self.policy_memory)
        previous = self.last_command
        yaw = self.own_pose[2]
        memory.last_vx = previous[0]*math.cos(yaw)-previous[1]*math.sin(yaw)
        memory.last_vy = previous[0]*math.sin(yaw)+previous[1]*math.cos(yaw)
        memory.last_w = previous[2]
        first = None
        first_memory = None
        for step in range(1, self.mpc_horizon+1):
            if time.perf_counter() >= deadline:
                return None
            x, y, yaw = trajectory[-1]
            poses = [tuple(p) for p in self.peer_poses]
            for i in peers:
                poses[i] = predictions[step-1][i]
            poses[self.robot_index] = (x, y, yaw)
            policy_poses = [poses[i] for i in self.canonical]
            policy_refs = [[row[i] for i in self.canonical]
                           for row in references[step-1:]]
            dt = command_dt if step == 1 else self.mpc_dt

            def sample_safe(vx, vy, horizon=.6):
                # Cheap screening for sampled policies; full continuous sweep
                # and all moving/peer checks still follow below.
                if time.perf_counter() >= deadline:
                    return False
                q = (x+vx*horizon, y+vy*horizon)
                return (self.segment_free((x,y), q, self.inflation_radius)
                        and all(swept_separation((x,y),q,o,o) >= self.robot_radius+.03
                                for o in obstacles))

            (wx, wy, spin), stages = self.pipeline.compute_three_stages(
                self.policy_index, policy_poses, policy_refs, memory, dt,
                self.max_linear_speed, self.max_angular_speed, self.mpc_dt, sample_safe)
            if not all(math.isfinite(v) for v in (wx, wy, spin)):
                return None
            vx = math.cos(yaw)*wx+math.sin(yaw)*wy
            vy = -math.sin(yaw)*wx+math.cos(yaw)*wy
            speed_limit = self.max_linear_speed
            if step == 1 and any(math.dist(self.own_pose[:2],self.peer_poses[i][:2])<.38
                                 for i in peers):
                speed_limit = min(speed_limit,.06)
            speed = math.hypot(vx,vy)
            if speed > speed_limit:
                vx,vy = vx*speed_limit/speed,vy*speed_limit/speed
            dvx,dvy = vx-previous[0],vy-previous[1]
            dv = math.hypot(dvx,dvy)
            if dv > .8*dt:
                vx,vy = previous[0]+dvx*.8*dt/dv,previous[1]+dvy*.8*dt/dv
            spin = max(-self.max_angular_speed,min(self.max_angular_speed,spin))
            spin = max(previous[2]-2*dt,min(previous[2]+2*dt,spin))
            # Reject rather than publish if residual measured/old speed is
            # incompatible with both the acceleration and speed limits.
            if math.hypot(vx,vy)>speed_limit+1e-9:
                return None
            mid = yaw+.5*spin*self.mpc_dt
            q = (x+(vx*math.cos(mid)-vy*math.sin(mid))*self.mpc_dt,
                 y+(vx*math.sin(mid)+vy*math.cos(mid))*self.mpc_dt,
                 normalize_angle(yaw+spin*self.mpc_dt))
            clearance = min([self.hard_collision_grid.clearance((x,y),self.inflation_radius)]
                            +[math.hypot(x-ox,y-oy) for ox,oy in obstacles])
            required = max(self.robot_radius,min(self.inflation_radius,clearance))
            start,end = now+(step-1)*self.mpc_dt,now+step*self.mpc_dt
            if (not self.segment_free((x,y),q,required)
                    or any(swept_separation((x,y),q,o,o)<required-1e-9 for o in obstacles)
                    or any(o.clearance((x,y),q,start,end,self.robot_radius)<.03 for o in moving)
                    or any(not self.peer_sweep_safe((x,y),q,i,start,end,now) for i in peers)
                    or (step==1 and any(not peer_motion_free(
                        (x,y),q,self.peer_poses[i],self.peer_poses[i],
                        preferred=.38,physical=2*self.robot_radius+.02) for i in peers))):
                return None
            previous = (vx,vy,spin)
            memory.last_vx = vx*math.cos(yaw)-vy*math.sin(yaw)
            memory.last_vy = vx*math.sin(yaw)+vy*math.cos(yaw)
            memory.last_w = spin
            if first is None:
                first = previous
                first_memory = deepcopy(memory)
                self.stages = stages
            trajectory.append(q)
        if time.perf_counter() >= deadline:
            return None
        self.pending_memory = first_memory
        return first,trajectory


def main(args=None):
    rclpy.init(args=args)
    node = ComparisonRobotController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_stop('comparison_shutdown')
        node.destroy_node()
        rclpy.shutdown()
