"""Isolated ROS test: production MPC ingress receives while its control group waits."""
import json, threading, time
from pathlib import Path
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from social_navigation_planner.dstar_mpc_controller import DistributedRobotMPC
rclpy.init()
node=DistributedRobotMPC();sender=Node('isolated_ingress_probe')
blocked=threading.Event();received=threading.Event();release=threading.Event()
original=node._inputs.put

def put(topic,message,callback):
    original(topic,message,callback)
    if topic=='/robot1/scan' and blocked.is_set() and not release.is_set():received.set()
node._inputs.put=put

def hold():
    if not blocked.is_set():
        blocked.set();release.wait(timeout=4.)
timer=node.create_timer(.05,hold)
pub=sender.create_publisher(LaserScan,'/robot1/scan',qos_profile_sensor_data)
executor=MultiThreadedExecutor(num_threads=2);executor.add_node(node)
thread=threading.Thread(target=executor.spin);thread.start()
try:
    assert blocked.wait(timeout=3.),'Control-group probe did not run'
    start=time.monotonic()
    while time.monotonic()-start<3. and not received.is_set():
        pub.publish(LaserScan());received.wait(timeout=.02)
    result={'ingress_received_while_control_group_blocked':received.is_set(),
            'domain':99,'scope':'Production MPC subscription/executor, no Gazebo or live robot domain. Blocking probe releases Python GIL; does not benchmark CPU-bound GIL contention.'}
    Path('docs/evidence/2026-11-01/early_reaction/ingress_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    assert received.is_set()
finally:
    release.set();executor.shutdown();thread.join(timeout=3.)
    sender.destroy_node();node.destroy_node();rclpy.shutdown()
