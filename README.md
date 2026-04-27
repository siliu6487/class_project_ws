ssh bee-humble@10.0.60.18   

export ROS_DOMAIN_ID=5

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=commands/velocity

source workspace/class_project_ws/install/setup.bash

ros2 run tf2_tools view_frames

ros2 run topic_tools relay /cmd_vel /commands/velocity

ros2 launch ros2_class_project navigation_bringup.launch.py

goal pose:
table: 
Frame:map, Position(0.332364, 0.577014, 0), Orientation(0, 0, -0.49963, 0.866239) = Angle: -1.04634


arm:
Frame:map, Position(-0.702617, 3.0207, 0), Orientation(0, 0, 0.934316, 0.356445) = Angle: 2.41267


