import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
import threading
from queue import Queue
import time
import espeakng

class NovelSubNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.novels_queue_ = Queue() # 创建队列， 存放小说
        self.novels_subscriber_ = self.create_subscription(String, 'novel_topic', self.novel_callback, 10) # 创建话题订阅者，订阅小说
        self.speech_thread_ = threading.Thread(target=self.speak_thread) # 创建语音线程
        self.speech_thread_.start() # 启动语音线程

    def novel_callback(self, msg):
        self.get_logger().info(f"接收到一行小说: {msg.data}") # 打印日志
        self.novels_queue_.put(msg.data) # 将小说内容逐行放入队列

    def speak_thread(self):
        speaker = espeakng.Speaker() # 创建语音对象
        speaker.voice = 'zh' # 设置语音为中文
        while rclpy.ok():
            if self.novels_queue_.qsize() > 0: # 队列中有数据，取出进行语音播报
                novel_line = self.novels_queue_.get() # 取出一行小说
                self.get_logger().info(f"语音播报: {novel_line}") # 打印日志
                speaker.say(novel_line) # 语音播报
                speaker.wait() # 等待语音播报完成
            else:
                time.sleep(1) # 队列为空，休眠一段时间

def main():
    rclpy.init()
    node = NovelSubNode('novel_sub')
    rclpy.spin(node)
    rclpy.shutdown()