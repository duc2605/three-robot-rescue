import json,time,collections
from pathlib import Path
import rclpy
from rclpy.qos import qos_profile_sensor_data
from tf2_msgs.msg import TFMessage
from rosgraph_msgs.msg import Clock
rclpy.init();n=rclpy.create_node('compact_stream_probe');clocks=[];poses=[]
n.create_subscription(Clock,'/navigation/clock',lambda m:clocks.append(m.clock.sec+m.clock.nanosec/1e9),qos_profile_sensor_data)
n.create_subscription(TFMessage,'/gazebo/world_poses',lambda m:poses.append(dict(names=[t.child_frame_id for t in m.transforms],stamp=(m.transforms[0].header.stamp.sec+m.transforms[0].header.stamp.nanosec/1e9) if m.transforms else None)),qos_profile_sensor_data)
start=time.monotonic()
while time.monotonic()-start<12:rclpy.spin_once(n,timeout_sec=.03)
result=dict(clock_messages=len(clocks),clock_rate_sim=(len(clocks)-1)/(clocks[-1]-clocks[0]) if len(clocks)>1 else None,pose_messages=len(poses),pose_lengths=dict(collections.Counter(len(p['names']) for p in poses)),pose_names=sorted({k for p in poses for k in p['names']}),pose_rate_sim=(len(poses)-1)/(poses[-1]['stamp']-poses[0]['stamp']) if len(poses)>1 and poses[-1]['stamp']>poses[0]['stamp'] else None)
Path('docs/evidence/2026-11-01/avoidance_rework/compact_stream_probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));n.destroy_node();rclpy.shutdown()
