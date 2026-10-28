"""Paper-1 integration on the existing RGB-D/LiDAR social scene."""
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
        LogInfo(msg='PAPER1_V1: independent adaptation; GWO-WOA + DWA + Eq32. '
                'Active camera turns disabled; camera perception/social keepout remain enabled.'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'social_navigation.launch.py')),
            launch_arguments={
                **{k: LaunchConfiguration(k) for k in defaults},
                'navigation_backend': 'paper1',
                'social_auto_observe': 'false', 'social_observation': 'false',
            }.items()),
    ])
