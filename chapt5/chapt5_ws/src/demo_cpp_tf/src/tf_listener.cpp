#include <memory>
#include "geometry_msgs/msg/transform_stamped.hpp"  // 提供消息接口
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"  // 提供 tf2::Quaternion 类
#include "tf2/utils.h"  // 提供tf2::getEulerYPR等工具函数
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"    // 提供消息类型转换函数
#include "tf2_ros/buffer.h"   // 提供 TF 缓冲类 Buffer
#include "tf2_ros/transform_listener.h"   // 提供坐标监听器类
#include <chrono>   // 引入时间相关头文件
// 使用时间单位的字面量，可以在代码中使用 s 和 ms 表示时间
using namespace std::chrono_literals;

class TFListener : public rclcpp::Node {
public:
    TFListener() : Node("tf_listener") {
        // 创建 TF 缓冲区和监听器
        tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
        timer_ = this->create_wall_timer(5s, std::bind(&TFListener::getTransform, this));
    }

    void getTransform() {
        try {
            // 等待交换可用
            const auto transform = tf_buffer_->lookupTransform("base_link", "target_point",
                this->get_clock()->now(), rclcpp::Duration::from_seconds(1.0));
            // 转换结果及输出
            const auto &translation = transform.transform.translation;
            const auto &rotation = transform.transform.rotation;
            double yaw, pitch, roll;
            tf2::getEulerYPR(rotation, yaw, pitch, roll);   // 四元数转欧拉角
            RCLCPP_INFO(this->get_logger(), "平移分量：(x=%.2f, y=%.2f, z=%.2f)",
                        translation.x,
                        translation.y,
                        translation.z);
            RCLCPP_INFO(this->get_logger(), "旋转分量：(yaw=%.2f, pitch=%.2f, roll=%.2f)",
                        yaw,
                        pitch,
                        roll);
        } catch (tf2::TransformException &ex) {
            RCLCPP_WARN(this->get_logger(), "异常： %s", ex.what());    // 处理异常
        }
    }

private:
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TFListener>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
