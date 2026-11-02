"""Launch one of ten approximate policies with shared ROS/safety infrastructure."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def comparison_launch(method=None):
    share = get_package_share_directory('social_navigation_sim')
    defaults = dict(social_scene='static', leader_robot='robot3', motion_enabled='true',
                    simulation='true', gazebo_gui='true', leader_camera='true',
                    person_detection='true', head_pose_enabled='true', body_pose_enabled='true',
                    social_avoidance='true', social_observation='false', social_auto_observe='false',
                    camera_width='480', camera_height='360', camera_rate='8.0',
                    rviz_rendering='auto', gazebo_rendering='auto')
    declarations = [DeclareLaunchArgument(k, default_value=v) for k,v in defaults.items()]
    if method is None:
        declarations.append(DeclareLaunchArgument('method', default_value='01',
                           choices=[f'{i:02d}' for i in range(1,11)]))
        backend = PythonExpression(["'compare' + '", LaunchConfiguration('method'), "'"])
    else:
        backend = f'compare{method:02d}'
    return LaunchDescription([
        *declarations,
        LogInfo(msg='THREE_STAGE_COMPARISON: approximate policy; D* references, '
                    'camera/social map and common safety/escape retained; no paper replication claim.'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(share,'launch','social_navigation.launch.py')),
            launch_arguments={**{k:LaunchConfiguration(k) for k in defaults},
                              'navigation_backend':backend}.items()),
    ])
