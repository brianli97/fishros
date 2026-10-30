#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"
#include "chapt4_interfaces/srv/partol.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"
using Partol = chapt4_interfaces::srv::Partol;
using SetParametersResult = rcl_interfaces::msg::SetParametersResult;

class TurtleController : public rclcpp::Node
{
public:
        TurtleController() : Node("turtle_controller")
        {
            this->declare_parameter("k", 1.0);
            this->declare_parameter("max_speed", 1.0);
            this->get_parameter("k", k_);
            this->get_parameter("max_speed", max_speed_);
            this->set_parameter(rclcpp::Parameter("k", 2.0));
            parameter_callback_handle_ = this->add_on_set_parameters_callback([&](const std::vector<rclcpp::Parameter> & parameters) 
            -> rcl_interfaces::msg::SetParametersResult {

                rcl_interfaces::msg::SetParametersResult result;
                result.successful = true;
                for (const auto & parameter : parameters) {
                    RCLCPP_INFO(this->get_logger(), "更新参数的值%s=%f", parameter.get_name().c_str(), parameter.as_double());
                    if (parameter.get_name()=="k") {
                        k_ = parameter.as_double();
                    }
                    if (parameter.get_name()=="max_speed") {
                        max_speed_ = parameter.as_double();
                    }
                }
                return result;
            });

            partol_service_ = this->create_service<Partol>("partol", [&](
                const Partol::Request::SharedPtr request, Partol::Response::SharedPtr response) -> void {

                    if(0<request->target_x && request->target_x<12.0f &&
                       0<request->target_y && request->target_y<12.0f) {
                        this->target_x_ = request->target_x;
                        this->target_y_ = request->target_y;
                        response->result = Partol::Response::SUCCESS;
                    }else{
                        response->result = Partol::Response::FAIL;
                    }
                    // 额外调用我们添加的回调函数，这样做到第一时间更新参数

            });
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
    OnSetParametersCallbackHandle::SharedPtr parameter_callback_handle_;
    rclcpp::Service<Partol>::SharedPtr partol_service_;
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