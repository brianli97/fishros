import launch
import launch_ros

def generate_launch_description():
    action_node_turtle_control = launch_ros.actions.Node(
        package="demo_cpp_service",
        executable="turtle_control",
        output="screen",
    )
    action_node_partol_client = launch_ros.actions.Node(
        package="demo_cpp_service",
        executable="partol_client",
        output="log",
    )
    action_node_turtlesim_node = launch_ros.actions.Node(
        package="turtlesim",
        executable="turtlesim_node",
        output="both",
    )
    # 合成启动描述并返回
    launch_description = launch.LaunchDescription([
       action_node_turtle_control,
       action_node_partol_client,
       action_node_turtlesim_node
    ])
    return launch_description