import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
from sensor_msgs.msg import Image
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge # 用于转换格式
import cv2
import os

# 普通变量开关：True 使用异步回调，False 使用阻塞等待
USE_ASYNC = True

class FaceDetectorClient(Node):
    def __init__(self):
        super().__init__("face_detect_client")
        self.client = self.create_client(FaceDetector, "/face_detect")
        self.bridge = CvBridge()
        self.test1_image_path = os.path.join(get_package_share_directory("demo_python_service"), "resource/test1.png")
        self.image = cv2.imread(self.test1_image_path)

    def send_request(self):
        # 1. 判断服务是否上线
        while self.client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info(f"等待服务端上线......")
        # 2. 构造 Request
        request = FaceDetector.Request()
        request.image = self.bridge.cv2_to_imgmsg(self.image, encoding="bgr8")

        future = self.client.call_async(request)

        if USE_ASYNC:
            # 异步模式：注册回调后立即返回
            future.add_done_callback(self.request_callback)
        else:
            # 同步模式：阻塞到服务端返回结果
            rclpy.spin_until_future_complete(self, future)
            response = future.result()
            self.get_logger().info(f"接收到响应：图像中共有：{response.number}张脸，耗时{response.use_time}")
            self.show_face_locations(response)

    def request_callback(self, result_future):
        response = result_future.result()
        self.get_logger().info(f"接收到响应：图像中共有：{response.number}张脸，耗时{response.use_time}")
        self.show_face_locations(response)

    def show_face_locations(self, response):
        for i in range(response.number):
            top = response.top[i]
            right = response.right[i]
            bottom = response.bottom[i]
            left = response.left[i]
            cv2.rectangle(self.image, (left, top), (right, bottom), (255, 0, 0), 2)
        cv2.imshow("Face Detection Result", self.image)
        cv2.waitKey(0)


def main(args=None):
    rclpy.init(args=args)
    face_detect_client = FaceDetectorClient()
    face_detect_client.send_request()

    # 异步模式需要持续 spin，回调才有机会被执行
    if USE_ASYNC:
        rclpy.spin(face_detect_client)

    face_detect_client.destroy_node()
    rclpy.shutdown()

