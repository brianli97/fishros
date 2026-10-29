#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"

class TurtleController : public rclcpp::Node
{
public:
        TurtleController() : Node("turtle_controller")
        {
            velocity_publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
            pose_subscriber_ = this->create_subscription<turtlesim::msg::Pose>("turtle1/pose", 10, 
                std::bind(&TurtleController::on_pose_received_, this, std::placeholders::_1));
        }

private:
    void on_pose_received_(const turtlesim::msg::Pose::SharedPtr pose)
    {
        auto message = geometry_msgs::msg::Twist();
        // 1.记录当前位置
        double current_x = pose->x;
        double current_y = pose->y;
        RCLCPP_INFO(this->get_logger(), "当前位置: x=%.2f, y=%.2f", current_x, current_y);

        // 2.计算与目标之间的距离，以及与当前海龟朝向的角度差
        double distance = std::sqrt(std::pow(target_x_ - current_x, 2) + std::pow(target_y_ - current_y, 2)); // 勾股定理
        double angle = std::atan2(target_y_ - current_y, target_x_ - current_x) - pose->theta; // 海龟当前朝向与目标方向之间的角度差

        // 3.控制策略：距离大于0.1继续运动，角度差大于0.2则原地旋转，否则直行
        if (distance > 0.1) {
            if (fabs(angle) > 0.2) {
                message.linear.x = 0.0; // 线速度为0，原地旋转
                message.angular.z = fabs(angle); // 角速度 = 角度差
            } else {
                // 通过比例控制器计算输出速度
                message.linear.x = distance * k_; // 线速度 = 距离 * 比例系数，限制最大速度
            }
        }

        // 限制最大线速度
        if (message.linear.x > max_speed_) {
            message.linear.x = max_speed_; 
        }

        velocity_publisher_->publish(message);
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr velocity_publisher_;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscriber_;
    double target_x_ = 1.0; // 目标位置的 x 坐标，设置默认值1.0
    double target_y_ = 1.0; // 目标位置的 y 坐标，设置默认值1.0
    double k_ = 1.0; // 比例系数，控制输出 = 误差 * 比例系数
    double max_speed_ = 3.0; // 最大线速度，设置默认值3.0
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleController>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}