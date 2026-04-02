import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.realpath(__file__))

    keepout_mask = os.path.join(pkg_dir, 'keepout_mask.yaml')
    speed_mask   = os.path.join(pkg_dir, 'speed_mask.yaml')

    lifecycle_nodes = [
        'keepout_filter_mask_server',
        'keepout_filter_info_server',
        'speed_filter_mask_server',
        'speed_filter_info_server',
    ]

    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='keepout_filter_mask_server',
            output='screen',
            parameters=[{'use_sim_time': False,
                         'yaml_filename': keepout_mask,
                         'frame_id': 'map',
                         'topic_name': '/keepout_filter_mask'}],
        ),
        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='keepout_filter_info_server',
            output='screen',
            parameters=[{'use_sim_time': False,
                         'filter_info_topic': '/keepout_filter_info',
                         'mask_topic': '/keepout_filter_mask',
                         'type': 0,
                         'base': 0.0,
                         'multiplier': 1.0}],
        ),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='speed_filter_mask_server',
            output='screen',
            parameters=[{'use_sim_time': False,
                         'yaml_filename': speed_mask,
                         'frame_id': 'map',
                         'topic_name': '/speed_filter_mask'}],
        ),
        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='speed_filter_info_server',
            output='screen',
            parameters=[{'use_sim_time': False,
                         'filter_info_topic': '/speed_filter_info',
                         'mask_topic': '/speed_filter_mask',
                         'type': 1,
                         'base': 0.0,
                         'multiplier': 50.0}],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_costmap_filters',
            output='screen',
            parameters=[{'use_sim_time': False,
                         'autostart': True,
                         'node_names': lifecycle_nodes}],
        ),
    ])
