import math # 角度转弧度函数
import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster # 静态坐标发布器
from geometry_msgs.msg import TransformStamped # 消息接口
from tf_transformations import quaternion_from_euler # 欧拉角转四元数函数

class StaticTFBroadcaster(Node):
    def __init__(self):
        super().__init__('static_tf2_broadcaster')
        self.tf_broadcaster = StaticTransformBroadcaster(self)
        self.publish_static_tf()

    def publish_static_tf(self):
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'base_link'
        transform.child_frame_id = 'camera_link'
        transform.transform.translation.x = 0.5
        transform.transform.translation.y = 0.3
        transform.transform.translation.z = 0.6
        # 欧拉角转四元数
        q = quaternion_from_euler(math.radians(180), 0, 0)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        # 发送静态坐标变换
        self.tf_broadcaster.sendTransform(transform)
        self.get_logger().info(f'发布 TF:{transform}')

def main():
    rclpy.init()
    node = StaticTFBroadcaster()
    rclpy.spin(node)
    rclpy.shutdown()