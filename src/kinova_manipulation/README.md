website: https://github.com/Kinovarobotics/ros2_kortex/tree/humble

Robot modle: Gen 3 Lite
Robot IP: 192.168.1.10

To launch and view any of the robot's URDF run:
```
ros2 launch kortex_description view_robot.launch.py robot_type:=gen3_lite dof:=6 gripper:=gen3_lite_2f
```
make sure to define dof:=6 for gen3_lite argument

# bringup
physical robot: 
```
ros2 launch kortex_bringup gen3_lite.launch.py robot_ip:=192.168.1.10 launch_rviz:=false

```
# moveit 2:
```
ros2 launch kinova_gen3_lite_moveit_config robot.launch.py  robot_ip:=192.168.1.10
```  

# sim:  
```
ros2 launch kortex_bringup kortex_sim_control.launch.py \
  sim_ignition:=false \
  use_sim_time:=true \
  launch_rviz:=false \
  robot_type:=gen3_lite \
  dof:=6 \
  gripper:=gen3_lite_2f
```

# MoveIt2
Physical robot:
```
ros2 launch kinova_gen3_lite_moveit_config robot.launch.py  robot_ip:=192.168.1.10
```  
sim:  
```
ros2 launch kinova_gen3_lite_moveit_config sim.launch.py \
  use_sim_time:=true

```
# PyMoveit2
for python scripts
```
source ~/workspace/moveit2_ws/install/setup.bash
```

# teleop (should hear engine sound)
```
ros2 run joy joy_node
source ~/workspace/moveit2_ws/install/setup.bash
source ~/workspace/class_project_ws/install/setup.bash
ros2 run kinova_manipulation joy_teleop
```
# microphone  (/audio topic)
```
source ~/workspace/respeaker_ws/install/setup.bash
ros2 run audio_capture audio_capture_node   --ros-args   -p device:="plughw:2,0"   -p channels:=1   -p sample_rate:=16000

```

# RealSense Camera  
The camera driver is included in the system ROS 2 packages, so no additional workspace sourcing is needed.
```
ros2 run realsense2_camera realsense2_camera_node  
```

# drop pose
```
saved_pose = [
    0.0,
    1.8326,
    -0.5236,
    1.5708,
    -0.7854,
    0.0
]

moveit2.move_to_configuration(saved_pose)
```



# tf
```
ros2 run tf2_ros static_transform_publisher \
0.314 0.416 0.190 \
0.0 0.9239 0.3827 0.0 \
base_link camera_link
```