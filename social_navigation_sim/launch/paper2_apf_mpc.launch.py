"""Paper 2 APF-MPC adaptation on existing social RGB-D/LiDAR scene."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory('social_navigation_sim')
    defaults = {
        'social_scene': 'static', 'leader_robot': 'robot3',
        'person_input_size': '416', 'person_confidence': '0.25',
        'camera_width': '480', 'camera_height': '360', 'camera_rate': '8.0',
        'rviz_rendering': 'auto', 'gazebo_rendering': 'auto', 'motion_enabled': 'true',
    }
    return LaunchDescription([
        *[DeclareLaunchArgument(k, default_value=v) for k, v in defaults.items()],
        LogInfo(msg='PAPER2_V1_ADAPTED: independent APF-MPC implementation; '
                'enhanced APF followers; camera/social keepout and LiDAR retained.'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'social_navigation.launch.py')),
            launch_arguments={
                **{k: LaunchConfiguration(k) for k in defaults},
                'navigation_backend': 'paper2',
                'social_auto_observe': 'false', 'social_observation': 'false',
            }.items()),
    ])
