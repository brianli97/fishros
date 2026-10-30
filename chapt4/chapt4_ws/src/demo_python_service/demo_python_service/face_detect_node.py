import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge # 用于转换格式
import cv2
import face_recognition
import time
import os
from rcl_interfaces.msg import SetParametersResult

class FaceDetectorionNode(Node):
    def __init__(self):
        super().__init__("face_detection_node")
        self.bridge = CvBridge()
        self.service = self.create_service(FaceDetector, "/face_detect", self.detect_face_callback)
        self.default_image_path = os.path.join(get_package_share_directory("demo_python_service"), "resource/default.jpg")
        self.declare_parameter("number_of_times_to_upsample", 1)
        self.declare_parameter("model", "hog")
        self.number_of_times_to_upsample = self.get_parameter("number_of_times_to_upsample").value
        self.model = self.get_parameter("model").value
        self.get_logger().info(f"图像路径:{self.default_image_path}")
        self.add_on_set_parameters_callback(self.parameters_callback)

    def parameters_callback(self, parameters):
        for parameter in parameters:
            self.get_logger().info(f"{parameter.name}->{parameter.value}")
            if parameter.name == "number_of_times_to_upsample":
                self.number_of_times_to_upsample = parameter.value
            if parameter.name == "model":
                self.model = parameter.value
        return SetParametersResult(successful=True)

    def detect_face_callback(self, request, response):
        if request.image.data:
            cv_image = self.bridge.imgmsg_to_cv2(request.image)
        else:
            cv_image = cv2.imread(self.default_image_path)
        start_time = time.time()    
        self.get_logger().info("加载完图像，开始检测")
        face_locations = face_recognition.face_locations(cv_image, number_of_times_to_upsample=self.number_of_times_to_upsample, model=self.model)
        end_time = time.time()
        self.get_logger().info(f"检测完成，耗时{end_time-start_time}")
        response.number = len(face_locations)
        response.use_time = end_time - start_time
        for top, right, bottom, left in face_locations:
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)

        return response

def main(args=None):
    rclpy.init(args=args)
    node = FaceDetectorionNode()
    rclpy.spin(node)
    rclpy.shutdown()

