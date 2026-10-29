import rclpy
from rclpy.node import Node
from status_interfaces.msg import SystemStatus # 导入消息接口
import psutil # 导入psutil库，用于获取系统状态信息
import platform # 导入platform库，用于获取系统平台信息

class SysStatusPub(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.status_publisher = self.create_publisher(SystemStatus, 'system_status', 10) # 创建消息发布者
        self.timer = self.create_timer(1.0, self.publish_status) # 创建定时器，每秒调用一次publish_status方法

    def publish_status(self):
        cpu_percent = psutil.cpu_percent() # 获取CPU使用率
        memory_info = psutil.virtual_memory() # 获取内存使用情况
        net_io_counters = psutil.net_io_counters() # 获取网络I/O统计信息

        # 创建SystemStatus消息
        status_msg = SystemStatus()
        status_msg.stamp = self.get_clock().now().to_msg() # 获取当前时间戳
        status_msg.host_name = platform.node() # 获取主机名
        status_msg.cpu_percent = cpu_percent
        status_msg.memory_percent = memory_info.percent
        status_msg.memory_total = memory_info.total / 1024 / 1024 # 转换为MB
        status_msg.memory_available = memory_info.available / 1024 / 1024 # 转换为MB
        status_msg.net_sent = net_io_counters.bytes_sent / 1024 / 1024 # 转换为MB
        status_msg.net_recv = net_io_counters.bytes_recv / 1024 / 1024 # 转换为MB

        self.get_logger().info(f"发布：{status_msg}") # 打印发布的消息内容
        # 发布消息
        self.status_publisher.publish(status_msg)

def main():
    rclpy.init() # 初始化ROS2客户端库
    node = SysStatusPub('sys_status_pub') # 创建SysStatusPub节点
    rclpy.spin(node) # 进入循环，等待回调函数执行
    rclpy.shutdown() # 关闭ROS2客户端库