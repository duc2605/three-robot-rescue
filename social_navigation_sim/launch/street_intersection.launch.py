"""Third, independent outdoor scene. Indoor launch/map/controller files unchanged."""
import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, EnvironmentVariable
from launch_ros.actions import Node


def _navigation(context, poses):
    """Select one controller family; never run baseline beside an independent paper."""
    backend=LaunchConfiguration('navigation_backend').perform(context)
    enabled=LaunchConfiguration('motion_enabled').perform(context)=='true'
    command_remaps=[(f'/{name}/cmd_vel',f'/{name}/navigation_cmd_vel') for name in poses]
    common={'use_sim_time':True,'require_gazebo_pose':True,
            'robot_names':['robot1','robot2','robot3'],'leader_robot':'robot3',
            'spawn_poses':[v for p in poses.values() for v in p],
            'social_observation_enabled':False}
    if backend.startswith('paper') and int(backend[5:])>=3:
        from social_navigation_planner.paper_models.catalog import require_runtime
        paper=int(backend[5:])
        require_runtime(paper)
        return [Node(package='social_navigation_planner',executable='paper_experiment',
            name='paper_experiment',output='screen',parameters=[{'paper':paper,
            'leader_robot':'robot3','motion_enabled':enabled,'use_sim_time':True,
            'planning_map_topic':'/street_navigation/map','social_observation_enabled':False}],
            remappings=command_remaps)]
    executable={'baseline':'three_robot_dstar_mpc','paper1':'paper1_controller',
                'paper2':'paper2_controller'}[backend]
    if backend!='baseline':common['motion_enabled']=enabled
    result=[Node(package='social_navigation_planner',executable=executable,
                 name='three_robot_dstar_mpc',output='screen',
                 remappings=[('/map','/street_navigation/map'),('/physical_map','/map'),*command_remaps],parameters=[common])]
    if backend=='baseline':
        for name in poses:
            result.append(Node(package='social_navigation_planner',executable='robot_distributed_mpc',
                name=name+'_distributed_mpc',parameters=[{'use_sim_time':True,'robot_name':name,
                    'robot_names':list(poses),'motion_enabled':enabled,'avoidance_use_camera':False,
                    'planning_map_topic':'/street_navigation/map'}],remappings=command_remaps,output='screen'))
    return result


def generate_launch_description():
    share=get_package_share_directory('social_navigation_sim')
    # Same body/controller, new measured starting positions on an open sidewalk.
    poses={'robot1':(10.0,-12.0,1.57),'robot2':(11.0,-12.0,1.57),'robot3':(10.5,-11.2,1.57)}
    simargs={'world':'street_intersection','bridge_config':os.path.join(share,'config/gz_bridge/street_intersection_bridge.yaml'),
             'leader_robot':'robot3','leader_camera':LaunchConfiguration('leader_camera'),
             'camera_width':'480','camera_height':'360','camera_rate':'6.0',
             'gazebo_gui':LaunchConfiguration('gazebo_gui'),'gazebo_rendering':LaunchConfiguration('gazebo_rendering'),
             'use_sim_time':'true'}
    for n,p in poses.items():
        for k,v in zip(('x','y','yaw'),p):simargs[n+'_'+k]=str(v)
    nodes=[DeclareLaunchArgument('navigation_backend',default_value='baseline',
            choices=['baseline',*[f'paper{i}' for i in range(1,9)]]),
        DeclareLaunchArgument('gazebo_gui',default_value='true',choices=['true','false']),
        DeclareLaunchArgument('gazebo_rendering',default_value='auto',choices=['auto','native','intel','software']),
        DeclareLaunchArgument('rviz',default_value='true',choices=['true','false']),
        DeclareLaunchArgument('motion_enabled',default_value='true',choices=['true','false']),
        DeclareLaunchArgument('leader_camera',default_value='true',choices=['true','false']),
        SetEnvironmentVariable('IGN_GAZEBO_SYSTEM_PLUGIN_PATH',[
            os.path.join(get_package_prefix('social_navigation_sim'),'lib'),os.pathsep,
            EnvironmentVariable('IGN_GAZEBO_SYSTEM_PLUGIN_PATH',default_value='')]),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(share,'launch/three_robot_sim.launch.py')),
            launch_arguments=simargs.items()),
        Node(package='nav2_map_server',executable='map_server',name='map_server',output='screen',
             parameters=[{'use_sim_time':True,'yaml_filename':os.path.join(share,'map/street_intersection.yaml'),'frame_id':'map'}]),
        Node(package='nav2_lifecycle_manager',executable='lifecycle_manager',name='map_lifecycle_manager',
             parameters=[{'use_sim_time':True,'autostart':True,'node_names':['map_server']}]),
        OpaqueFunction(function=_navigation,args=[poses])]
    nodes.append(Node(package='social_navigation_sim',executable='street_navigation_rules.py',
        parameters=[{'use_sim_time':True}],output='screen'))
    nodes.append(Node(package='social_navigation_sim',executable='street_scene_markers.py',
        parameters=[{'use_sim_time':True}],output='screen'))
    nodes.append(Node(package='rviz2',executable='rviz2',name='street_rviz',condition=IfCondition(LaunchConfiguration('rviz')),
        arguments=['-d',os.path.join(share,'rviz/street_intersection.rviz')],parameters=[{'use_sim_time':True}],output='screen'))
    return LaunchDescription(nodes)
