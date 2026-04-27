from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import TimerAction
import os

def generate_launch_description():

    pkg_dir = get_package_share_directory('ros2_class_project')
    nav2_dir = get_package_share_directory('nav2_bringup')

    map_file = os.path.join(pkg_dir, 'maps', 'lab_final_drawn.yaml')
    params_file = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(pkg_dir, 'config', 'nav.rviz')

    return LaunchDescription([
        # relay /cmd_vel → /commands/velocity
        Node(
            package='topic_tools',
            executable='relay',
            name='cmd_vel_relay',
            arguments=['/cmd_vel', '/commands/velocity'],
            output='screen'
        ),

        # Static TF: base_link → laser
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0.30', '0', '0', '0', 'base_link', 'laser'],
            name='tf_base_to_laser'
        ),

        # Static TF: base_footprint → base_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link'],
            name='tf_footprint_to_base'
        ),

        # Localization (map + AMCL)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_dir, 'launch', 'localization_launch.py')
            ),
            launch_arguments={
                'map': map_file,
                'params_file': params_file,
                'use_sim_time': 'false',
                'autostart': 'true'
            }.items()
        ),

        # Navigation (planner + controller)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
            ),
            launch_arguments={
                'params_file': params_file,
                'use_sim_time': 'false',
                'autostart': 'true'
            }.items()
        ),

        # RViz, wait a little
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    arguments=['-d', rviz_config],
                    output='screen'
                )
            ]
        ),

    ])