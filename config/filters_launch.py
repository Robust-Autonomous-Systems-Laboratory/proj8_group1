import os
from launch import LaunchDescription
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.realpath(__file__))

    keepout_mask_yaml = os.path.join(pkg_dir, 'keepout_mask.yaml')
    speed_mask_yaml   = os.path.join(pkg_dir, 'speed_mask.yaml')
    keepout_params    = os.path.join(pkg_dir, 'keepout_filter_params.yaml')
    speed_params      = os.path.join(pkg_dir, 'speed_filter_params.yaml')

    configured_keepout_params = RewrittenYaml(
        source_file=keepout_params,
        param_rewrites={'yaml_filename': keepout_mask_yaml},
        convert_types=True,
    )

    configured_speed_params = RewrittenYaml(
        source_file=speed_params,
        param_rewrites={'yaml_filename': speed_mask_yaml},
        convert_types=True,
    )

    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='keepout_filter_mask_server',
            output='screen',
            parameters=[configured_keepout_params],
        ),
        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='keepout_filter_info_server',
            output='screen',
            parameters=[configured_keepout_params],
        ),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='speed_filter_mask_server',
            output='screen',
            parameters=[configured_speed_params],
        ),
        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='speed_filter_info_server',
            output='screen',
            parameters=[configured_speed_params],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_costmap_filters',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'node_names': [
                    'keepout_filter_mask_server',
                    'keepout_filter_info_server',
                    'speed_filter_mask_server',
                    'speed_filter_info_server',
                ],
            }],
        ),
    ])
