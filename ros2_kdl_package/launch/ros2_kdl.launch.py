from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    kdl_node = Node(
        package='ros2_kdl_package',
        executable='ros2_kdl_node',
        name='ros2_kdl_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([
                FindPackageShare('ros2_kdl_package'),
                'config',
                'args.yaml'
            ])
        ],
    )

    gz_service_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_service_bridge',
        arguments=[
            '/world/default/set_pose@ros_gz_interfaces/srv/SetEntityPose',
        ],
        output='screen'
    )

    return LaunchDescription([
        kdl_node,
        gz_service_bridge,
    ])
