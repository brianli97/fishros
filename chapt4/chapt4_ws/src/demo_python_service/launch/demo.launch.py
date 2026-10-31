import launch
import launch_ros

def generate_launch_description():
    action_node_face_detect_node = launch_ros.actions.Node(
        package="demo_python_service",
        executable="face_detect_node",
        output="screen",
    )
    action_node_face_detect_client_node = launch_ros.actions.Node(
        package="demo_python_service",
        executable="face_detect_client_node",
        output="log",
    )
    # 合成启动描述并返回
    launch_description = launch.LaunchDescription([
       action_node_face_detect_node,
       action_node_face_detect_client_node
    ])
    return launch_description