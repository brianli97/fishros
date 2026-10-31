import launch
import launch_ros

def generate_launch_description():
    # 创建参数声明 action, 用于解析launch 命令后的参数
    # ros2 launch demo_cpp_service demo.launch.py launch_max_speed:=5.0
    action_declare_arg_max_speed = launch.actions.DeclareLaunchArgument('launch_max_speed', default_value='2.0')

    action_node_turtle_control = launch_ros.actions.Node(
        package="demo_cpp_service",
        executable="turtle_control",
        # 使用 launch 中参数 launch_max_speed 值替换节点中的 max_speed 参数值
        parameters=[{'max_speed': launch.substitutions.LaunchConfiguration('launch_max_speed', default='2.0')}],
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
        action_declare_arg_max_speed,
        action_node_turtle_control,
        action_node_partol_client,
        action_node_turtlesim_node
    ])
    return launch_description