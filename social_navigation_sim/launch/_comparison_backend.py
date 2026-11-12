"""Independent paper controllers; environment/perception shared, navigation isolated."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _start(context, fixed_method):
    from social_navigation_planner.paper_models.catalog import require_runtime
    method=fixed_method if fixed_method is not None else int(LaunchConfiguration('method').perform(context))
    paper=method+2
    info=require_runtime(paper)  # Fail BEFORE spawning Gazebo or legacy policies.
    share=get_package_share_directory('social_navigation_sim')
    keys=('social_scene','leader_robot','motion_enabled','simulation','gazebo_gui','leader_camera',
          'person_detection','head_pose_enabled','body_pose_enabled','social_avoidance',
          'social_observation','social_auto_observe','social_inspect_obstacles','camera_width','camera_height','camera_rate',
          'rviz_rendering','gazebo_rendering')
    args={k:LaunchConfiguration(k) for k in keys}
    topic='/social_navigation/map' if LaunchConfiguration('social_avoidance').perform(context)=='true' else '/map'
    return [
        LogInfo(msg=f'Paper{paper}: {info[2]}; explicit omni adaptation, baseline coordinator/escape DISABLED'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(share,'launch','social_navigation.launch.py')),
                                 launch_arguments={**args,'navigation_backend':'baseline','navigation_enabled':'false'}.items()),
        Node(package='social_navigation_planner',executable='paper_experiment',name='paper_experiment',output='screen',
             parameters=[{'paper':paper,'leader_robot':LaunchConfiguration('leader_robot'),
                          'motion_enabled':ParameterValue(LaunchConfiguration('motion_enabled'),value_type=bool),
                          'use_sim_time':ParameterValue(LaunchConfiguration('simulation'),value_type=bool),
                          'planning_map_topic':topic,
                          'social_observation_enabled':ParameterValue(LaunchConfiguration('social_observation'),value_type=bool)}]),
    ]


def comparison_launch(method=None):
    defaults=dict(social_scene='dynamic',leader_robot='robot3',motion_enabled='true',simulation='true',
                  gazebo_gui='true',leader_camera='true',person_detection='true',head_pose_enabled='true',
                  body_pose_enabled='true',social_avoidance='true',social_observation='true',social_auto_observe='true',social_inspect_obstacles='true',
                  camera_width='480',camera_height='360',camera_rate='8.0',rviz_rendering='auto',gazebo_rendering='auto')
    declarations=[DeclareLaunchArgument(k,default_value=v) for k,v in defaults.items()]
    if method is None:declarations.append(DeclareLaunchArgument('method',default_value='01',choices=['01','02','03','04','05','06']))
    return LaunchDescription([*declarations,OpaqueFunction(function=_start,args=[method])])
