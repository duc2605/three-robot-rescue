"""Independent paper comparison ROS adapter; baseline navigation never imported."""
import json
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time
from geometry_msgs.msg import Pose, PoseArray, PoseStamped, TransformStamped, Twist
from nav_msgs.msg import OccupancyGrid, Odometry, Path
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformListener, TransformBroadcaster, TransformException
from visualization_msgs.msg import Marker, MarkerArray

from .grid_clearance import GridClearance
from .scan_pose_history import ScanPoseHistory
from .paper_models.catalog import require_paper
from .paper_models.kinematic import Impedance, v_targets, vo_command, wrap
from .paper_models.environment import waypoint_route
from .paper_behavior import PaperBehavior


def yaw(q):
    return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))


def seconds(stamp):
    return stamp.sec+1e-9*stamp.nanosec


class PaperExperiment(Node):
    def __init__(self):
        super().__init__('paper_experiment')
        self.declare_parameter('paper',3)
        self.declare_parameter('leader_robot','robot3')
        self.declare_parameter('motion_enabled',True)
        self.declare_parameter('planning_map_topic','/social_navigation/map')
        self.paper=int(self.get_parameter('paper').value)
        self.info=require_paper(self.paper)
        self.names=['robot1','robot2','robot3']
        self.leader=self.names.index(self.get_parameter('leader_robot').value)
        self.enabled=bool(self.get_parameter('motion_enabled').value)
        self.shared = PaperBehavior(self,self.leader,self.now,subscribe_search=True)
        self.policy=self.make_policy()
        self.poses=[None]*3;self.pose_times=[-math.inf]*3
        self.odometry=[None]*3;self.scans=[[] for _ in range(3)]
        self.scan_times=[-math.inf]*3;self.scan_wall=[-math.inf]*3
        self.history=ScanPoseHistory(3)
        self.goal=None;self.route=[];self.route_time=-math.inf
        self.physical=None;self.social=None;self.map_signatures={}
        self.previous_time=None
        self.tf=Buffer();self.tf_listener=TransformListener(self.tf,self)
        self.broadcaster=TransformBroadcaster(self)
        self.cmd=[self.create_publisher(Twist,f'/{n}/cmd_vel',1) for n in self.names]
        self.decisions=[self.create_publisher(String,f'/{n}/escape_decision',10) for n in self.names]
        self.status=[self.create_publisher(String,f'/comparison/{n}/status',10) for n in self.names]
        self.paths=[self.create_publisher(Path,f'/{n}/desired_path',1) for n in self.names]
        self.leader_route = self.create_publisher(Path,'/dstar_lite/path',1)
        self.states=self.create_publisher(PoseArray,'/formation/robot_states',1)
        self.markers=self.create_publisher(MarkerArray,'/three_robot_dstar_mpc/markers',1)
        self.create_subscription(TFMessage,'/gazebo/world_poses',self.world_pose,1)
        self.create_subscription(PoseStamped,'/goal_pose',self.set_goal,1)
        map_qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(OccupancyGrid,'/map',lambda m:self.map_received(m,'physical'),map_qos)
        self.create_subscription(OccupancyGrid,str(self.get_parameter('planning_map_topic').value),lambda m:self.map_received(m,'social'),map_qos)
        for i,name in enumerate(self.names):
            self.create_subscription(Odometry,f'/{name}/odom',lambda m,i=i:self.odom(m,i),qos_profile_sensor_data)
            self.create_subscription(LaserScan,f'/{name}/scan',lambda m,i=i:self.scan(m,i),qos_profile_sensor_data)
        self.create_timer(.1,self.tick)
        self.get_logger().info(f'Paper{self.paper}: independent adapted controller; {self.info[0]}; no baseline emergency fallback')

    def make_policy(self):
        if self.paper==5:
            from .paper_models.ho_mpc import HierarchicalOmni
            return HierarchicalOmni(self.leader)
        if self.paper==6:
            from .paper_models.drivetrains import DifferentDrivetrains
            return DifferentDrivetrains(self.leader)
        if self.paper==7:
            from .paper_models.robile import RobileFormation
            return RobileFormation(self.leader)
        if self.paper==4:return Impedance()
        if self.paper==8:
            from .paper_models.deform import Deform
            return Deform(self.leader)
        return None

    def now(self): return self.get_clock().now().nanoseconds*1e-9

    def map_received(self,msg,kind):
        origin=msg.info.origin
        signature=(msg.info.width,msg.info.height,msg.info.resolution,origin.position.x,origin.position.y,yaw(origin.orientation),bytes((int(v)+1)%256 for v in msg.data))
        if signature==self.map_signatures.get(kind):return
        self.map_signatures[kind]=signature
        setattr(self,kind,GridClearance(msg.info.width,msg.info.height,msg.info.resolution,
            (origin.position.x,origin.position.y,yaw(origin.orientation)),[v<0 or v>=50 for v in msg.data],.18))
        self.route=[];self.route_time=-math.inf

    def world_pose(self,msg):
        now=self.now()
        for t in msg.transforms:
            if t.child_frame_id not in self.names:continue
            i=self.names.index(t.child_frame_id);p=t.transform.translation
            captured=seconds(t.header.stamp) or now
            self.poses[i]=(p.x,p.y,yaw(t.transform.rotation));self.pose_times[i]=captured
            self.history.add(i,captured,self.poses[i])

    def odom(self,msg,i):
        self.odometry[i]=msg
        if self.poses[i] is None or abs(self.now()-self.pose_times[i])>.5:return
        x,y,heading=self.poses[i];p=msg.pose.pose
        angle=wrap(heading-yaw(p.orientation));c,s=math.cos(angle),math.sin(angle)
        t=TransformStamped();t.header.stamp=msg.header.stamp;t.header.frame_id='map'
        t.child_frame_id=self.names[i]+'/odom'
        t.transform.translation.x=x-c*p.position.x+s*p.position.y
        t.transform.translation.y=y-s*p.position.x-c*p.position.y
        t.transform.rotation.z=math.sin(angle/2);t.transform.rotation.w=math.cos(angle/2)
        self.broadcaster.sendTransform(t)

    def scan(self,msg,i):
        captured=seconds(msg.header.stamp)
        if not -.05<=self.now()-captured<=.4:return
        pose=self.history.at(i,captured)
        if pose is None:return
        base=self.names[i]+'/base_footprint';frame=msg.header.frame_id.lstrip('/')
        extrinsic=None
        for candidate in (frame,self.names[i]+'/'+frame):
            try:
                extrinsic=self.tf.lookup_transform(base,candidate,Time()).transform;break
            except TransformException:pass
        if extrinsic is None:return
        peers=[self.history.at(j,captured) for j in range(3)]
        c,s=math.cos(pose[2]),math.sin(pose[2])
        ox=pose[0]+c*extrinsic.translation.x-s*extrinsic.translation.y
        oy=pose[1]+s*extrinsic.translation.x+c*extrinsic.translation.y
        heading=pose[2]+yaw(extrinsic.rotation)
        points=[]
        for beam in range(0,len(msg.ranges),max(1,len(msg.ranges)//180)):
            d=float(msg.ranges[beam])
            if not math.isfinite(d) or not max(.05,msg.range_min)<d<min(2.,msg.range_max):continue
            angle=heading+msg.angle_min+beam*msg.angle_increment
            p=ox+d*math.cos(angle),oy+d*math.sin(angle)
            if any(q is not None and math.dist(p,q[:2])<.22 for q in peers):continue
            points.append(p)
        self.shared.observe(i,points,pose,captured)
        self.scan_times[i]=captured;self.scan_wall[i]=time.monotonic()

    def set_goal(self,msg):
        if msg.header.frame_id.lstrip('/') not in ('','map'):
            self.get_logger().error('Goal must be in map frame');return
        p=msg.pose.position
        if not all(math.isfinite(v) for v in (p.x,p.y)):return
        self.goal=(p.x,p.y);self.route=[];self.route_time=-math.inf
        self.policy=self.make_policy()

    def emit(self,commands,reasons,targets=None,raw=None):
        stamp=self.get_clock().now().to_msg()
        states=PoseArray();states.header.stamp=stamp;states.header.frame_id='map'
        markers=MarkerArray()
        for i,name in enumerate(self.names):
            heading=self.poses[i][2] if self.poses[i] else 0.
            vx,vy,w=commands[i];msg=Twist()
            msg.linear.x=math.cos(heading)*vx+math.sin(heading)*vy
            msg.linear.y=-math.sin(heading)*vx+math.cos(heading)*vy;msg.angular.z=w
            self.cmd[i].publish(msg)
            payload=dict(robot=name,project_paper=self.paper,reason=reasons[i],t=self.now(),stamp=self.now(),stops=commands[i]==(0.,0.,0.),terminal_safe=False,
                command_body=[msg.linear.x,msg.linear.y,w],raw_command_world=list((raw or commands)[i]),
                target=list(targets[i]) if targets else None,goal=None,
                shared_emergency_escape=False,controller='independent_paper_adapter',
                source_doi=self.info[0],status='adaptation_not_author_reproduction',
                safety_status=reasons[i],motion_tracks=self.shared.telemetry(i,self.poses[i],self.now()))
            if self.paper in (5,6,7):
                from .paper_models.upstream_sources import SOURCES
                payload['upstream']=SOURCES[self.paper]
            payload['search']={'paper':self.paper,'policy_target':payload['target'],
                'navigation_goal':list(self.goal) if self.goal else None,
                'raw_command_world':payload['raw_command_world'],'command_body':payload['command_body'],
                'baseline_escape':False,'reason':reasons[i]}
            if 'upstream' in payload:payload['search']['upstream']=payload['upstream']
            audit=String();audit.data=json.dumps(payload,allow_nan=False)
            self.decisions[i].publish(audit);self.status[i].publish(audit)
            if self.poses[i] is None:continue
            p=Pose();p.position.x,p.position.y=self.poses[i][:2]
            p.orientation.z=math.sin(heading/2);p.orientation.w=math.cos(heading/2);states.poses.append(p)
            marker=Marker();marker.header=states.header;marker.ns='paper_robots';marker.id=i
            marker.type=Marker.ARROW;marker.action=Marker.ADD;marker.pose=p
            marker.scale.x=.3;marker.scale.y=.12;marker.scale.z=.1
            marker.color.a=1.;marker.color.r=float(i==0);marker.color.b=float(i==1);marker.color.g=float(i==2)
            markers.markers.append(marker)
            path=Path();path.header=states.header
            for point in ([self.poses[i][:2],targets[i]] if targets else []):
                entry=PoseStamped();entry.header=states.header;entry.pose.position.x=float(point[0]);entry.pose.position.y=float(point[1]);entry.pose.orientation.w=1.;path.poses.append(entry)
            self.paths[i].publish(path)
        if len(states.poses)==3:self.states.publish(states)
        if self.goal is not None:
            marker=Marker();marker.header=states.header;marker.ns='paper_goal';marker.id=10
            marker.type=Marker.SPHERE;marker.action=Marker.ADD;marker.pose.orientation.w=1.
            marker.pose.position.x=float(self.goal[0]);marker.pose.position.y=float(self.goal[1])
            marker.scale.x=.16;marker.scale.y=.16;marker.scale.z=.08
            marker.color.r=1.;marker.color.g=.8;marker.color.a=1.;markers.markers.append(marker)
        self.markers.publish(markers)

    def tick(self):
        now=self.now()
        zero=[(0.,0.,0.)]*3
        if self.previous_time is not None and now<self.previous_time:
            self.shared.clear()
            self.history.clear();self.poses=[None]*3;self.pose_times=[-math.inf]*3
            self.scans=[[] for _ in range(3)];self.scan_times=[-math.inf]*3
            self.goal=None;self.route=[];self.policy=self.make_policy()
        dt=.1 if self.previous_time is None else max(.02,min(.2,now-self.previous_time))
        self.previous_time=now
        if not self.enabled:self.emit(zero,['motion_disabled']*3);return
        if self.goal is None:self.emit(zero,['no_goal']*3);return
        if self.physical is None or self.social is None or self.shared.physical is None:self.emit(zero,['waiting_maps']*3);return
        if any(p is None or not -.05<=now-t<=.4 for p,t in zip(self.poses,self.pose_times)):
            self.emit(zero,['stale_pose']*3);return
        if any(not -.05<=now-t<=.4 or time.monotonic()-w>3. for t,w in zip(self.scan_times,self.scan_wall)):
            self.emit(zero,['stale_scan_or_missing_extrinsic']*3);return
        obstacles=[self.shared.obstacles(i,now) for i in range(3)]
        observation=self.shared.camera_commands(self.poses,now)
        if observation is not None:
            commands,reasons=self.shared.gate(self.poses,observation,obstacles,self.social)
            self.emit(commands,['camera_observation' if r=='policy' else r for r in reasons])
            return
        leader=self.policy.leader if self.paper==8 else self.leader
        start=self.poses[leader][:2]
        if now-self.route_time>=1.:
            if self.paper==6:
                from .paper_models.drivetrains import hybrid_route
                self.route=hybrid_route(self.social,self.poses[leader],self.goal)
            else:
                self.route=waypoint_route(self.social,start,self.goal)
            self.route_time=now
            message=Path();message.header.frame_id='map';message.header.stamp=self.get_clock().now().to_msg()
            for point in self.route:
                pose=PoseStamped();pose.header=message.header
                pose.pose.position.x,pose.pose.position.y=map(float,point[:2]);pose.pose.orientation.w=1.
                message.poses.append(pose)
            self.leader_route.publish(message)
        if not self.route:
            reason='hybrid_route_unavailable_or_budget' if self.paper==6 else 'no_common_reference_route'
            self.emit(zero,[reason]*3);return
        nearest=min(range(len(self.route)),key=lambda k:math.dist(start,self.route[k][:2]))
        waypoint=self.route[-1]
        for point in self.route[nearest:]:
            if math.dist(start,point[:2])>=.55:waypoint=point;break
        velocities=[self.history.velocity(i,now) for i in range(3)]
        targets=v_targets(self.poses,leader,waypoint[:2])
        if self.paper==7:targets=self.policy.targets(self.poses,waypoint[:2])
        calculation_started=time.monotonic()
        try:
            if self.paper==3:
                raw=[]
                for i in range(3):
                    peer=[(*self.poses[j][:2],*velocities[j][:2],.15) for j in range(3) if j!=i]
                    raw.append(vo_command(self.poses[i],targets[i],obstacles[i]+peer))
            elif self.paper==4:
                obs=[obstacles[i]+[(*self.poses[j][:2],*velocities[j][:2],.15) for j in range(3) if j!=i] for i in range(3)]
                raw=self.policy.commands(self.poses,targets,velocities,obs,dt)
            elif self.paper in (5,6,7):
                raw=self.policy.commands(self.poses,targets,velocities,obstacles,dt,self.social)
            else:
                targets=self.policy.targets(self.poses,waypoint,self.social,now)
                raw=self.policy.commands(self.poses,targets,velocities,obstacles,dt,self.social)
            if not all(math.isfinite(v) for command in raw for v in command):raise ValueError('nonfinite command')
            if time.monotonic()-calculation_started>1.:
                self.emit(zero,['policy_wall_time_limit']*3,targets,raw);return
            commands,reasons=self.shared.gate(self.poses,raw,obstacles,self.social)
            if self.paper in (5,6,7,8):
                reasons=[self.policy.status[i] if r=='policy' else r for i,r in enumerate(reasons)]
            self.emit(commands,reasons,targets,raw)
        except Exception as exc:
            self.emit(zero,['policy_exception']*3)
            self.get_logger().error(f'Paper controller stopped: {type(exc).__name__}: {exc}')


def main(args=None):
    rclpy.init(args=args);node=PaperExperiment()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:
        if rclpy.ok():node.emit([(0.,0.,0.)]*3,['shutdown']*3)
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
