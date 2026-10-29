#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include <chrono>   // 引入时间相关头文件

using namespace std::chrono_literals;  // 使用时间单位的字面量，可以再代码中使用 s 和 ms 表示时间

class TurtleCircle : public rclcpp::Node
{
private:
    rclcpp::TimerBase::SharedPtr timer_;  // 定时器对象的智能指针
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_; // 发布者智能指针

public:
    explicit TurtleCircle(const std::string& node_name) : Node(node_name)
    {
        // 调用继承而来的父类函数创建订阅者
        publisher_ =  this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
        
        // 调用继承而来的父类函数创建定时器
        timer_ = this->create_wall_timer(1000ms, std::bind(&TurtleCircle::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = geometry_msgs::msg::Twist();  // 创建一个 Twist 消息对象
        message.linear.x = 1.0;  // 设置线速度为 1.0
        message.angular.z = 2.0; // 设置角速度为 1.0
        publisher_->publish(message); // 发布消息
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv); // 初始化 ROS 2
    auto node = std::make_shared<TurtleCircle>("turtle_circle"); // 创建节点对象
    rclcpp::spin(node); // 进入循环
    rclcpp::shutdown(); // 关闭 ROS 2
    return 0;
}