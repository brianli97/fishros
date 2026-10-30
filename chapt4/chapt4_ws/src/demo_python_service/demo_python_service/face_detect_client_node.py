import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
from sensor_msgs.msg import Image
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge # 用于转换格式
import cv2
import os
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType

# 普通变量开关：True 使用异步回调，False 使用阻塞等待
USE_ASYNC = False

class FaceDetectorClient(Node):
    def __init__(self):
        super().__init__("face_detect_client")
        self.client = self.create_client(FaceDetector, "/face_detect")
        self.bridge = CvBridge()
        self.test1_image_path = os.path.join(get_package_share_directory("demo_python_service"), "resource/test1.png")
        self.image = cv2.imread(self.test1_image_path)

    def call_set_parameters(self, parameters):
        """
        调用服务，修改参数值
        """
        # 1.创建一个客户端，等待服务上线
        update_param_client = self.create_client(SetParameters, "/face_detection_node/set_parameters")
        while update_param_client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info(f"等待参数更新服务端上线......")
        # 2.创建request
        request = SetParameters.Request()
        request.parameters = parameters
        # 3.调用服务端更新参数
        future = update_param_client.call_async(request)
        rclpy.spin_until_future_complete(self, future) # 等待服务端返回响应
        response = future.result()
        return response

    def update_detect_model(self, model="hog"):
        """
            根据传入的model, 构造Parameters, 然后调用call_set_parameters更新服务端的参数
        """
        # 1.创建参数对象
        param = Parameter()
        param.name = "model"
        # 2.赋值 创建 param_value (消息接口嵌套很多)
        param_value = ParameterValue()
        param_value.string_value = model
        param_value.type = ParameterType.PARAMETER_STRING
        param.value = param_value
        # 3. 请求更新参数
        response = self.call_set_parameters([param])
        for result in response.results:
            self.get_logger().info(f"设置参数结果：{result.successful} {result.reason}")

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
            # self.show_face_locations(response)

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
    face_detect_client.update_detect_model("hog")
    face_detect_client.send_request()
    face_detect_client.update_detect_model("cnn")
    face_detect_client.send_request()

    # 异步模式需要持续 spin，回调才有机会被执行
    if USE_ASYNC:
        rclpy.spin(face_detect_client)


    rclpy.spin(face_detect_client)
    rclpy.shutdown()

