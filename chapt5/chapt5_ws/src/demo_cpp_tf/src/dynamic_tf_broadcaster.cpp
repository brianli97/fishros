#include <memory>
#include "geometry_msgs/msg/transform_stamped.hpp"  // 提供消息接口
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"  // 提供 tf2::Quaternion 类
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"    // 提供消息类型转换函数
#include "tf2_ros/transform_broadcaster.h"   // 提供坐标广播器类
#include <chrono>   // 引入时间相关头文件
// 使用时间单位的字面量，可以在代码中使用 s 和 ms 表示时间
using namespace std::chrono_literals;

class DynamicTFBroadcaster : public rclcpp::Node {
public:
    DynamicTFBroadcaster() : Node("dynamic_tf_broadcaster") {
        // 创建动态广播发布器并发布
        dynamic_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        timer_ = this->create_wall_timer(10ms, std::bind(&DynamicTFBroadcaster::publishTransform, this));
    }

    void publishTransform() {
        geometry_msgs::msg::TransformStamped transform_stamped;
        transform_stamped.header.stamp = this->get_clock()->now();
        transform_stamped.header.frame_id = "map";
        transform_stamped.child_frame_id = "base_link";
        transform_stamped.transform.translation.x = 2.0;
        transform_stamped.transform.translation.y = 3.0;
        transform_stamped.transform.translation.z = 0.0;
        tf2::Quaternion q;
        q.setRPY(0, 0, 30*M_PI/180);    // 弧度制欧拉角转四元数
        transform_stamped.transform.rotation = tf2::toMsg(q);   // 转成消息接口类型
        // transform_stamped.transform.rotation.x = q.x();
        // transform_stamped.transform.rotation.y = q.y();
        // transform_stamped.transform.rotation.z = q.z();
        // transform_stamped.transform.rotation.w = q.w();
        RCLCPP_INFO(this->get_logger(), "Publishing dynamic transform from 'map' to 'base_link': x=%.2f, y=%.2f, z=%.2f, qx=%.2f, qy=%.2f, qz=%.2f, qw=%.2f",
                    transform_stamped.transform.translation.x,
                    transform_stamped.transform.translation.y,
                    transform_stamped.transform.translation.z,
                    transform_stamped.transform.rotation.x,
                    transform_stamped.transform.rotation.y,
                    transform_stamped.transform.rotation.z,
                    transform_stamped.transform.rotation.w
                    );
        dynamic_broadcaster_->sendTransform(transform_stamped);
    }

private:
    std::shared_ptr<tf2_ros::TransformBroadcaster> dynamic_broadcaster_;
    rclcpp::TimerBase::SharedPtr timer_;

};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DynamicTFBroadcaster>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
