# system (~/.bashrc)

```
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=2 

source ~/workspace/respeaker_ws/install/setup.bash
source ~/workspace/moveit2_ws/install/setup.bash
source ~/workspace/class_project_ws/install/setup.bash
``` 

# ===========Kinova Arm========================
## bring up (terminal A1)
```
ros2 launch kortex_bringup gen3_lite.launch.py robot_ip:=192.168.1.10 launch_rviz:=false
```

## moveit bring up (terminal A2)
```
ros2 launch kinova_gen3_lite_moveit_config robot.launch.py  robot_ip:=192.168.1.10
```

## add table to avoid collision (terminal A3)
```
ros2 run kinova_manipulation add_table_collision
```

# ===========Sensing========================
## microphone (/audio topic) (terminal C1)
audio captuer node is optional if we run subprocess in python script
```
ros2 run audio_capture audio_capture_node   --ros-args   -p device:="plughw:2,0"   -p channels:=1   -p sample_rate:=16000
```

## RealSense Camera  (terminal C2)
```
ros2 run realsense2_camera realsense2_camera_node 
``` 

view image stream:
```
ros2 run rqt_image_view rqt_image_view
```

## perception service (pen and water detection) (terminal C3)
```
cd ~/workspace/class_project_ws/src/perception_module/perception_module
source ml_env/bin/activate
python perception_service.py
```


# ===========Turtlebot========================
## turn on turtlebot
then bring up turtlebot and lidar (terminal B1, B2),  
check: /odom and /scan topics

## nav2 (terminal B3)
```
ros2 launch turtlebot_nav navigation_bringup.launch.py
```
then set up inital pose.

## keyboard teleop (optional terminal B4)
```
ssh bee-humble@10.0.60.18

export ROS_DOMAIN_ID=2

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=commands/velocity
```

# ===========Other========================
## common commands
ros2 run tf2_tools view_frames

ros2 run topic_tools relay /cmd_vel /commands/velocity


goal pose:
table: 
Frame:map, Position(0.332364, 0.577014, 0), Orientation(0, 0, -0.49963, 0.866239) = Angle: -1.04634


arm:
Frame:map, Position(-0.702617, 3.0207, 0), Orientation(0, 0, 0.934316, 0.356445) = Angle: 2.41267