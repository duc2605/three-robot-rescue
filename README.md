# Three Robot Rescue

ROS 2 Humble simulation of three omni robots in Gazebo.

Based on: https://github.com/ngohoanglong220905/three-robot-rescue

This version includes the provisional viewer lane and early viewer detection.
See the documentation and licenses inside each ROS package.

## Build

source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select astar_planner ros2_omni_robot_sim
source install/setup.bash

## Run

ros2 launch ros2_omni_robot_sim three_robot_social.launch.py \
  person_input_size:=416 person_confidence:=0.25
