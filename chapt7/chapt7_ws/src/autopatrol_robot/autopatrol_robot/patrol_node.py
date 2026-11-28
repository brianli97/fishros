import math
import time
from pathlib import Path
from datetime import datetime

import rclpy
from geometry_msgs.msg import PoseStamped, Pose
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from tf2_ros import TransformListener, Buffer
from tf_transformations import euler_from_quaternion, quaternion_from_euler
from rclpy.duration import Duration
from autopatrol_interfaces.srv import SpeachText # 添加服务接口

# 导入消息接口和相关定义
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class PatrolNode(BasicNavigator):
    def __init__(self, node_name='patrol_node'):
        super().__init__(node_name)
        # 导航相关定义
        self.declare_parameter('initial_point', [0.0, 0.0, 0.0])
        self.declare_parameter('target_points', [
            0.0, 0.0, 0.0,
            0.7, 0.0, 0.0,
        ])
        self.initial_point_ = self.get_parameter('initial_point').value
        self.target_points_ = self.get_parameter('target_points').value

        # 实时位置获取 TF 相关定义
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_, self)

        # 语音合成客户端
        self.speach_client_ = self.create_client(SpeachText, 'speech_text')

        # 订阅与保存图像相关定义
        self.declare_parameter('image_save_path', '')
        self.image_save_path = self.get_parameter('image_save_path').value
        self.bridge = CvBridge()
        self.latest_image = None
        self.subscriptions_image = self.create_subscription(
            Image, '/camera_sensor/image_raw', self.image_callback, 10)

    def get_pose_by_xyyaw(self, x, y, yaw):
        """
        通过 x, y, yaw 合成 PoseStamped
        """
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        rotation_quat = quaternion_from_euler(0, 0, yaw) # 欧拉角转四元数
        pose.pose.orientation.x = rotation_quat[0]
        pose.pose.orientation.y = rotation_quat[1]
        pose.pose.orientation.z = rotation_quat[2]
        pose.pose.orientation.w = rotation_quat[3]
        return pose

    def init_robot_pose(self):
        """
        初始化机器人位姿
        """
        # 从参数获取初始化点
        self.initial_point_ = self.get_parameter('initial_point').value
        if len(self.initial_point_) != 3 or not all(
                math.isfinite(v) for v in self.initial_point_):
            raise ValueError('initial_point 必须包含有限的 x、y、yaw 三个数')
        self.get_logger().info(
            f'设置初始位姿 {list(self.initial_point_)}，请确认与机器人实际位置一致；'
            f'use_sim_time={self.get_parameter("use_sim_time").value}')
        # 合成位姿并进行初始化
        self.setInitialPose(self.get_pose_by_xyyaw(
            self.initial_point_[0], self.initial_point_[1], self.initial_point_[2],
        ))
        # 等待直到导航激活
        self.waitUntilNav2Active()

    def get_target_points(self):
        """
        通过参数值获取目标点集合
        """
        points = []
        self.target_points_ = self.get_parameter('target_points').value
        if not self.target_points_ or len(self.target_points_) % 3 != 0 or not all(
                math.isfinite(v) for v in self.target_points_):
            raise ValueError('target_points 必须为非空的有限数值数组，长度为 3 的倍数')
        for index in range(len(self.target_points_) // 3):
            x = self.target_points_[index*3]
            y = self.target_points_[index*3+1]
            yaw = self.target_points_[index*3+2]
            points.append([x, y, yaw])
            self.get_logger().info(f'获取到目标点: {index}->({x}, {y}, {yaw})')
        return points

    def nav_to_pose(self, target_pose, target_index=1, target_count=1):
        """
        导航到目标，限频输出反馈并返回是否成功。
        """
        tag = f'目标 {target_index}/{target_count}'
        position = target_pose.pose.position
        self.get_logger().info(
            f'{tag} 开始：x={position.x:.2f}, y={position.y:.2f}')
        started = time.monotonic()
        if not self.goToPose(target_pose):
            self.get_logger().error(f'{tag} 被导航服务拒绝，停止巡逻')
            return False
        last_log = started - 2.0
        while rclpy.ok() and not self.isTaskComplete():
            feedback = self.getFeedback()
            now = time.monotonic()
            if feedback and now - last_log >= 2.0:
                current = feedback.current_pose.pose.position
                eta = Duration.from_msg(
                    feedback.estimated_time_remaining).nanoseconds / 1e9
                self.get_logger().info(
                    f'{tag} 当前位置=({current.x:.2f}, {current.y:.2f}), '
                    f'剩余路径={feedback.distance_remaining:.2f}m, '
                    f'预计剩余={eta:.1f}s, 已耗时={now - started:.1f}s, '
                    f'恢复次数={feedback.number_of_recoveries}')
                last_log = now
        if not rclpy.ok():
            return False
        result = self.getResult()
        message = (
            f'{tag} 结果={result.name}, action_status={self.status}, '
            f'耗时={time.monotonic() - started:.1f}s')
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info(message)
            return True
        self.get_logger().error(message + '；停止巡逻，请同时检查 Nav2 终端日志')
        return False

    def get_current_pose(self):
        """
        通过TF获取当前位姿
        """
        while rclpy.ok():
            try:
                tf = self.buffer_.lookup_transform(
                    'map', 'base_footprint', rclpy.time.Time(seconds=0), rclpy.time.Duration(seconds=1)
                )
                transform = tf.transform
                rotation_euler = euler_from_quaternion([
                    transform.rotation.x,
                    transform.rotation.y,
                    transform.rotation.z,
                    transform.rotation.w,
                ])
                self.get_logger().info(f'平移：{transform.translation}, 旋转四元数：{transform.rotation}: 旋转欧拉角：{rotation_euler}')
                return transform
            except Exception as e:  
                self.get_logger().warn(f'不能够获取坐标变换， 原因： {str(e)}')

    def speach_text(self, text):
        """
        调用服务播放语音
        """
        while not self.speach_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'语音合成服务未上线，等待中...')

        request = SpeachText.Request()
        request.text = text
        future = self.speach_client_.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            result = future.result().result
            if result:
                self.get_logger().info(f'语音合成成功: {text}')
            else:
                self.get_logger().warn(f'语音合成失败: {text}')
        else:
            self.get_logger().warn('语音合成服务请求失败')

    def image_callback(self, msg):
        """
        将最新的消息放到 latest_image 中
        """
        self.latest_image = msg

    def record_image(self, target_index=0):
        """等待到点后收到的下一帧图像，并保存到配置目录。"""
        self.latest_image = None
        deadline = time.monotonic() + 5.0
        while rclpy.ok() and self.latest_image is None:
            if time.monotonic() >= deadline:
                self.get_logger().warn('等待摄像头图像超时，本次未保存图片')
                return False
            rclpy.spin_once(self, timeout_sec=0.1)
        if self.latest_image is None:
            return False
        try:
            directory = Path(self.image_save_path).expanduser() if self.image_save_path else Path.cwd() / 'patrol_images'
            directory.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = directory / f'point_{target_index}_{stamp}.png'
            cv_image = self.bridge.imgmsg_to_cv2(
                self.latest_image, desired_encoding='bgr8')
            if not cv2.imwrite(str(filename), cv_image):
                raise OSError(f'无法写入图片：{filename}')
            self.get_logger().info(f'目标 {target_index} 图片已保存：{filename.resolve()}')
            return True
        except Exception as exc:
            self.get_logger().error(f'保存图片失败：{exc}')
            return False

def main():
    rclpy.init()
    patrol = PatrolNode()
    patrol.speach_text(text='正在初始化位置')
    try:
        points = patrol.get_target_points()
        patrol.init_robot_pose()
        patrol.speach_text(text='位置初始化完成')
        for index, (x, y, yaw) in enumerate(points, start=1):
            patrol.get_logger().info(
                f'准备目标 {index}/{len(points)}: ({x}, {y}, yaw={yaw})')
            target_pose = patrol.get_pose_by_xyyaw(x, y, yaw)
            patrol.speach_text(text=f'准备前往目标点{x},{y}')
            if not patrol.nav_to_pose(target_pose, index, len(points)):
                break
            if not patrol.record_image(target_index=index):
                patrol.get_logger().warn(f'目标 {index} 拍照失败，继续后续巡逻')
        else:
            patrol.get_logger().info('全部巡逻目标完成')
    finally:
        patrol.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
