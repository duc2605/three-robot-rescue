"""Opt-in dynamic social experiment using the original D* Lite + MPC backend."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    defaults = dict(motion_enabled='true', simulation='true', scenario_annotations='true',
                    camera_width='480', camera_height='360', camera_rate='6.0',
                    person_detection_rate='2.0', person_cpu_threads='1',
                    body_input_size='224', body_max_people='2',
                    horizontal_scan_every='4',
                    detection_wall_budget='3.0',
                    social_inspect_obstacles='true',
                    dds_udp_only='true',
                    rviz_rendering='auto', gazebo_rendering='auto')
    share = get_package_share_directory('social_navigation_sim')
    return LaunchDescription([
        *[DeclareLaunchArgument(k, default_value=v) for k, v in defaults.items()],
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', os.path.join(share, 'config', 'fastdds_udp.xml'),
                               condition=IfCondition(LaunchConfiguration('dds_udp_only'))),
        SetEnvironmentVariable('FASTDDS_DEFAULT_PROFILES_FILE', os.path.join(share, 'config', 'fastdds_udp.xml'),
                               condition=IfCondition(LaunchConfiguration('dds_udp_only'))),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('social_navigation_sim'), 'launch', 'social_navigation.launch.py')),
            launch_arguments={**{k: LaunchConfiguration(k) for k in defaults},
                              'navigation_backend': 'baseline', 'social_scene': 'dynamic'}.items()),
    ])
