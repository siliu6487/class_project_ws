#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PointStamped, Pose
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

from pymoveit2 import MoveIt2

import sys
import termios
import tty
import time


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


class CameraFrameMover(Node):

    def __init__(self):
        super().__init__("camera_frame_mover")

        # TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # MoveIt2
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=[
                "joint_1","joint_2","joint_3",
                "joint_4","joint_5","joint_6",
            ],
            base_link_name="base_link",
            end_effector_name="tool_frame",
            group_name="arm",
        )

        # current target in camera frame
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.cam_z = 0.3   # start 30 cm in front of camera

        self.step = 0.05   # 5 cm step

        self.get_logger().info("Ready. Use WASD + RF to move.")

    def move(self):
        pt = PointStamped()
        pt.header.frame_id = "camera_color_optical_frame"
        pt.point.x = self.cam_x
        pt.point.y = self.cam_y
        pt.point.z = self.cam_z

        try:
            pt_base = self.tf_buffer.transform(pt, "base_link")
        except Exception as e:
            self.get_logger().error(f"TF failed: {e}")
            return

        pose = Pose()
        pose.position = pt_base.point

        # keep orientation fixed (simple)
        pose.orientation.w = 1.0

        self.get_logger().info(
            f"Cam: ({self.cam_x:.2f},{self.cam_y:.2f},{self.cam_z:.2f}) → "
            f"Base: ({pose.position.x:.2f},{pose.position.y:.2f},{pose.position.z:.2f})"
        )

        self.moveit2.move_to_pose(pose)

    def run(self):
        while rclpy.ok():
            key = get_key()

            if key == 'w':
                self.cam_z += self.step   # forward
            elif key == 's':
                self.cam_z -= self.step   # backward
            elif key == 'd':
                self.cam_x += self.step   # right
            elif key == 'a':
                self.cam_x -= self.step   # left
            elif key == 'r':
                self.cam_y -= self.step   # up (remember Y down!)
            elif key == 'f':
                self.cam_y += self.step   # down
            elif key == 'q':
                break
            else:
                continue

            self.move()

            # allow execution time
            for _ in range(20):
                rclpy.spin_once(self, timeout_sec=0.05)


def main():
    rclpy.init()
    node = CameraFrameMover()

    time.sleep(3)  # wait for TF

    node.run()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()