#include "rclcpp/rclcpp.hpp"
#include "chapt4_interfaces/srv/partol.hpp"
#include <chrono>
#include <ctime>
using Partol = chapt4_interfaces::srv::Partol;
using namespace std::chrono_literals;   // 可以使用 10s 100ms

class PartolClient : public rclcpp::Node
{
public:
        PartolClient() : Node("turtle_controller")
        {
            srand(time(NULL));  // 初始化随机数种子
            partol_client_ = this->create_client<Partol>("partol");
            timer_ = this->create_wall_timer(5s, [&]() -> void{
                // 1.检测服务端是否上线
                while(!this->partol_client_->wait_for_service(1s)) {
                    if(rclcpp::ok()) {
                        RCLCPP_ERROR(this->get_logger(), "等待服务上线过程中,rclcpp挂了,我退下了");
                        return;
                    }
                    RCLCPP_INFO(this->get_logger(), "等待服务上线中......");
                }

                // 2. 构造请求的对象
                auto request = std::make_shared<Partol::Request>();
                request->target_x = rand() % 15;
                request->target_y = rand() % 15;
                RCLCPP_INFO(this->get_logger(), "准备好目标点%f,%f", request->target_x, request->target_y);
                
                // 3. 发送请求
                this->partol_client_->async_send_request(request, 
                    [&](rclcpp::Client<Partol>::SharedFuture result_future) -> void {
                    auto response = result_future.get();
                    if(response->result == Partol::Response::SUCCESS) {
                        RCLCPP_INFO(this->get_logger(), "请求巡逻目标点成功");
                    }
                    if(response->result == Partol::Response::FAIL) {
                        RCLCPP_INFO(this->get_logger(), "请求巡逻目标点失败");
                    }
                });
            });
        }

private:
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Client<Partol>::SharedPtr partol_client_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PartolClient>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}