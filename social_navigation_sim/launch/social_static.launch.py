"""Static social scene with the project's D* Lite + MPC backend."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    share = get_package_share_directory('social_navigation_sim')
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(share, 'launch', 'social_navigation.launch.py')),
            launch_arguments={
                'navigation_backend': 'baseline',
                'social_scene': 'static',
            }.items(),
        ),
    ])
