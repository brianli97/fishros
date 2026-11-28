# 基于 ROS 2 和 Navigation2 的自动巡检机器人

## 1. 项目介绍

本项目基于 ROS 2 Humble、Navigation2 和 Gazebo Classic 实现自动巡检机器人仿真。

机器人按配置顺序前往各个目标点，出发前通过语音播报目标坐标；成功到达后，接收摄像头图像并保存到本地。当前程序执行一轮后退出，不会自动循环巡逻。某个目标导航失败时停止本轮巡逻；拍照失败时记录日志并继续后续目标。

源码仓库：[brianli97/fishros](https://github.com/brianli97/fishros)

本章代码位于仓库的 `chapt7/chapt7_ws/src` 目录，各功能包如下：

| 功能包 | 用途 |
| --- | --- |
| `fishbot_description` | 机器人描述、传感器、仿真环境和控制器配置 |
| `fishbot_navigation2` | 地图、Navigation2 参数和导航启动文件 |
| `fishbot_application` | Python 导航示例 |
| `fishbot_application_c` | C++ 导航示例 |
| `autopatrol_interfaces` | 自动巡检自定义接口，包括 `SpeachText.srv` |
| `autopatrol_robot` | 巡逻、语音服务和图像保存 |

## 2. 使用方法

开发环境：Ubuntu 22.04、ROS 2 Humble、Gazebo Classic。

### 2.1 获取源码和安装依赖

尚未获取源码时执行：

```bash
git clone https://github.com/brianli97/fishros.git
cd fishros/chapt7/chapt7_ws
```

已有源码时，直接进入本地的 `chapt7/chapt7_ws`。以下构建与运行命令均在该工作空间目录执行。

以下安装命令使用 `$ROS_DISTRO` 表示当前 ROS 2 发行版，请确保终端已加载对应的 ROS 2 环境。不同发行版的依赖包可用性可能不同。

先更新软件包索引：

```bash
sudo apt update
```

1. 安装建图和导航功能包：

```bash
sudo apt install ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-bringup \
  ros-$ROS_DISTRO-slam-toolbox
```

2. 安装机器人描述、仿真和运动控制功能包：

```bash
sudo apt install ros-$ROS_DISTRO-robot-state-publisher \
  ros-$ROS_DISTRO-joint-state-publisher ros-$ROS_DISTRO-gazebo-ros-pkgs \
  ros-$ROS_DISTRO-gazebo-ros2-control ros-$ROS_DISTRO-ros2-control \
  ros-$ROS_DISTRO-ros2-controllers ros-$ROS_DISTRO-xacro
```

3. 安装图像处理和坐标变换依赖：

```bash
sudo apt install ros-$ROS_DISTRO-cv-bridge ros-$ROS_DISTRO-tf-transformations \
  python3-opencv python3-transforms3d
```

4. 安装语音合成依赖：

```bash
sudo apt install python3-pip espeak-ng
python3 -m pip install --user espeakng
```

5. 安装 colcon 构建工具：

```bash
sudo apt install python3-colcon-common-extensions
```

当前导航默认加载已保存的 `fishbot_navigation2/maps/room.yaml`，无需在每次巡检前重新建图；SLAM Toolbox 用于建图场景。

### 2.2 构建

```bash
colcon build
source install/setup.bash
```

修改 Python 代码、launch 文件或源码中的 YAML 配置后，重新构建以更新安装目录。

### 2.3 运行

分别打开三个终端，每个终端都进入 `chapt7/chapt7_ws` 并加载环境。

终端 1：启动仿真，等待机器人和控制器加载完成，确保仿真未暂停。

```bash
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

终端 2：启动导航和 RViz。

```bash
source install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

终端 3：启动巡逻节点和语音服务。

```bash
source install/setup.bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

`autopatrol.launch.py` 只启动巡逻和语音节点，不包含 Gazebo 和 Navigation2。

### 2.4 巡逻配置与图片

配置文件：`src/autopatrol_robot/config/patrol_config.yaml`。

- `initial_point`：初始位姿 `[x, y, yaw]`。位置单位为米，角度单位为弧度，使用 `map` 坐标系。
- `target_points`：按 `[x1, y1, yaw1, x2, y2, yaw2, ...]` 排列的目标点。
- `use_sim_time`：仿真环境下设置为 `true`。
- `image_save_path`：可选的图片保存目录。未设置或为空时，保存到启动目录下的 `patrol_images/`。

例如，在 `patrol_node.ros__parameters` 下添加：

```yaml
patrol_node:
  ros__parameters:
    image_save_path: '/home/brian/ros2/patrol_images'
```

以上仅展示保存路径参数，添加时保留原有巡逻参数。launch 默认读取安装目录中的配置，修改源码 YAML 后需重新构建。

每个目标成功到达后，程序最多等待约 5 秒接收图像，文件名包含目标编号和时间。图像话题为 `/camera_sensor/image_raw`。`patrol_images/` 已加入 Git 忽略规则。

当前地图覆盖范围约为 `-4.53 ≤ x < 3.22`、`-3.20 ≤ y < 1.60`，范围内仍有墙壁和未知区域，目标和路径还需结合 RViz 中的地图及代价地图确认。

每次启动巡逻都会设置 `initial_point`，它只影响定位，不会移动机器人。重复启动前应确认初始位姿与机器人的实际位置、朝向一致，不能在机器人移动后仍盲目沿用原初始位姿。

## 3. 作者与仓库

- 作者：[Brian](https://github.com/brianli97)
- Git 仓库：[fishros](https://github.com/brianli97/fishros)
