import math
import pytest
from social_navigation_planner.scan_pose_history import ScanPoseHistory
from social_navigation_planner.moving_obstacles import MotionTracks,scan_clusters


def test_capture_pose_interpolates_position_and_wrapped_yaw():
    history=ScanPoseHistory()
    history.add(0,1.,(0.,0.,math.pi-.1));history.add(0,1.2,(.2,.4,-math.pi+.1))
    p=history.at(0,1.1)
    assert p[:2]==pytest.approx((.1,.2))
    assert abs(abs(p[2])-math.pi)<1e-8


def test_missing_or_old_pose_is_not_replaced_with_current_pose():
    history=ScanPoseHistory()
    assert history.at(0,1.) is None
    history.add(0,1.,(0.,0.,0.));history.add(0,1.1,(.1,0.,0.))
    assert history.at(0,.9) is None
    assert history.at(0,1.2) is None
    assert history.at(0,1.12)[:2]==pytest.approx((.12,0.))
    assert not history.add(0,.5,(10.,10.,0.))
    assert history.at(0,1.1)[:2]==pytest.approx((.1,0.))
    history.clear();assert history.at(0,1.) is None


def test_rotating_robot_does_not_make_a_static_return_move_in_map():
    from test_mpc_formation_motion import controller
    from test_moving_obstacle_safety import empty_grid
    from sensor_msgs.msg import LaserScan
    node=controller(2,empty_grid(),[1.])
    del node.pose_at_scan
    node.scan_pose_history=ScanPoseHistory()
    node.peer_poses=[(-3.,3.,0.),(-3.,-3.,0.),(0.,0.,.2)]
    for stamp,yaw in [(.8,0.),(1.,.2)]:
        for index,pose in enumerate(node.peer_poses):
            node.scan_pose_history.add(index,stamp,(0.,0.,yaw) if index==2 else pose)
    tracks=MotionTracks()
    for stamp in [.8,.9,1.]:
        scan=LaserScan();scan.header.stamp.nanosec=round((stamp-int(stamp))*1e9);scan.header.stamp.sec=int(stamp)
        scan.range_min=.08;scan.range_max=2.;scan.angle_min=-(stamp-.8);scan.ranges=[1.]
        points=node.scan_world_points(scan,2)
        assert points[0]==pytest.approx((1.,0.),abs=1e-7)
        tracks.observe(scan_clusters(points),stamp)
    assert tracks.recent(1.)[0].velocity==(0.,0.)


def test_unaligned_scan_does_not_refresh_local_freshness():
    from test_mpc_formation_motion import controller
    from test_moving_obstacle_safety import empty_grid
    from sensor_msgs.msg import LaserScan
    node=controller(2,empty_grid(),[.4]);node.own_pose=(0.,0.,0.);node.peer_poses=[(-3.,3.,0.),(-3.,-3.,0.),node.own_pose]
    node.state_time=.4;node.last_scan_stamp=-math.inf
    del node.pose_at_scan;node.scan_pose_history=ScanPoseHistory()
    scan=LaserScan();scan.header.stamp.nanosec=400000000;scan.range_min=.08;scan.range_max=2.;scan.ranges=[1.]
    before=node.scan_wall;node.scan_callback(scan)
    assert node.last_scan_stamp==-math.inf and node.scan_wall==before


def test_scan_waits_for_capture_pose_then_retries_without_false_freshness():
    from test_mpc_formation_motion import controller
    from test_moving_obstacle_safety import empty_grid
    from sensor_msgs.msg import LaserScan
    from geometry_msgs.msg import PoseArray,Pose
    node=controller(2,empty_grid(),[.4]);node.own_pose=(0.,0.,0.);node.peer_poses=[(-3.,3.,0.),(-3.,-3.,0.),node.own_pose]
    node.state_time=.4;node.last_scan_stamp=-math.inf
    del node.pose_at_scan;node.scan_pose_history=ScanPoseHistory()
    scan=LaserScan();scan.header.stamp.nanosec=400000000;scan.range_min=.08;scan.range_max=2.;scan.ranges=[1.]
    node.scan_callback(scan)
    assert node.last_scan_stamp==-math.inf
    msg=PoseArray();msg.header.frame_id='map';msg.header.stamp.nanosec=400000000
    for x,y,yaw in node.peer_poses:
        p=Pose();p.position.x=x;p.position.y=y;p.orientation.w=1.;msg.poses.append(p)
    node.team_state_callback(msg)
    assert node.last_scan_stamp==pytest.approx(.4)
    assert node.scan_points
    assert not node.pending_scans


def test_delayed_pose_does_not_starve_ten_hz_scan_captures():
    from test_mpc_formation_motion import controller
    from test_moving_obstacle_safety import empty_grid
    from sensor_msgs.msg import LaserScan
    from geometry_msgs.msg import PoseArray,Pose
    node=controller(2,empty_grid(),[.4]);node.own_pose=(0.,0.,0.);node.peer_poses=[(-3.,3.,0.),(-3.,-3.,0.),node.own_pose]
    node.state_time=.4;node.last_scan_stamp=-math.inf
    del node.pose_at_scan;node.scan_pose_history=ScanPoseHistory()
    for i,p in enumerate(node.peer_poses):node.scan_pose_history.add(i,.1,p)
    for stamp in [.2,.3]:
        scan=LaserScan();scan.header.stamp.nanosec=round(stamp*1e9)
        scan.range_min=.08;scan.range_max=2.;scan.ranges=[1.]
        node.scan_callback(scan)
    assert len(node.pending_scans[2])==2
    msg=PoseArray();msg.header.frame_id='map';msg.header.stamp.nanosec=300000000
    for x,y,yaw in node.peer_poses:
        p=Pose();p.position.x=x;p.position.y=y;p.orientation.w=1.;msg.poses.append(p)
    node.team_state_callback(msg)
    assert node.last_scan_stamp==pytest.approx(.3)
    assert len(next(iter(node.lidar_motion.tracks.values())).history)==2
    assert not node.pending_scans
