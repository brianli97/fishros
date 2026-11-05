#include <memory>
#include "geometry_msgs/msg/transform_stamped.hpp"  // 提供消息接口
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"  // 提供 tf2::Quaternion 类
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"    // 提供消息类型转换函数
#include "tf2_ros/static_transform_broadcaster.h"   // 提供静态坐标广播器类

class StaticTFBroadcaster : public rclcpp::Node {
public:
    StaticTFBroadcaster() : Node("static_tf_broadcaster") {
        // 创建静态广播发布器并发布
        static_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);
        this->publish_tf();
    }

    void publish_tf() {
        geometry_msgs::msg::TransformStamped transform_stamped;
        transform_stamped.header.stamp = this->get_clock()->now();
        transform_stamped.header.frame_id = "map";
        transform_stamped.child_frame_id = "target_point";
        transform_stamped.transform.translation.x = 5.0;
        transform_stamped.transform.translation.y = 3.0;
        transform_stamped.transform.translation.z = 0.0;
        tf2::Quaternion q;
        q.setRPY(0, 0, 60*M_PI/180);    // 弧度制欧拉角转四元数
        transform_stamped.transform.rotation = tf2::toMsg(q);   // 转成消息接口类型
        // transform_stamped.transform.rotation.x = q.x();
        // transform_stamped.transform.rotation.y = q.y();
        // transform_stamped.transform.rotation.z = q.z();
        // transform_stamped.transform.rotation.w = q.w();
        RCLCPP_INFO(this->get_logger(), "Publishing static transform from 'map' to 'target_point': x=%.2f, y=%.2f, z=%.2f, qx=%.2f, qy=%.2f, qz=%.2f, qw=%.2f",
                    transform_stamped.transform.translation.x,
                    transform_stamped.transform.translation.y,
                    transform_stamped.transform.translation.z,
                    transform_stamped.transform.rotation.x,
                    transform_stamped.transform.rotation.y,
                    transform_stamped.transform.rotation.z,
                    transform_stamped.transform.rotation.w
                    );
        static_broadcaster_->sendTransform(transform_stamped);
    }

private:
    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;

};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<StaticTFBroadcaster>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
