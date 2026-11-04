import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster # 动态坐标发布器
from geometry_msgs.msg import TransformStamped # 消息接口
from tf_transformations import quaternion_from_euler # 欧拉角转四元数函数

class DynamicTFBroadcaster(Node):
    def __init__(self):
        super().__init__('dynamic_tf2_broadcaster')
        self.tf_broadcaster = TransformBroadcaster(self)
        # 动态TF需要持续发布，这里发布频率设置为 100 Hz
        self.timer = self.create_timer(0.01, self.publish_transform)

    def publish_transform(self):
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'camera_link'
        transform.child_frame_id = 'bottle_link'
        transform.transform.translation.x = 0.2
        transform.transform.translation.y = 0.0
        transform.transform.translation.z = 0.5
        # 欧拉角转四元数
        q = quaternion_from_euler(0, 0, 0)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        # 发送动态坐标变换
        self.tf_broadcaster.sendTransform(transform)
        self.get_logger().info(f'发布 TF:{transform}')

def main():
    rclpy.init()
    node = DynamicTFBroadcaster()
    rclpy.spin(node)
    rclpy.shutdown()