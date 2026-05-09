#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

import cv2
import numpy as np

from tf2_ros import Buffer, TransformListener
import tf_transformations


class CameraArmCalibrator(Node):

    def __init__(self):
        super().__init__('camera_arm_calibrator')

        self.bridge = CvBridge()

        self.image = None
        self.K = None

        self.points_2d = []
        self.points_3d = []

        self.last_click = None

        # --- TF (same as your working code) ---
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # --- Subscriptions ---
        self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.image_callback,
            10
        )

        self.create_subscription(
            CameraInfo,
            '/camera/camera/color/camera_info',
            self.camera_info_callback,
            10
        )

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.mouse_callback)

        self.get_logger().info("Calibration node ready.")

    # -----------------------------
    # Camera callbacks
    # -----------------------------
    def camera_info_callback(self, msg):
        if self.K is None:
            k = msg.k
            self.K = np.array([
                [k[0], 0, k[2]],
                [0, k[4], k[5]],
                [0, 0, 1]
            ])
            self.get_logger().info(f"Camera intrinsics received:\n{self.K}")

    def image_callback(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    # -----------------------------
    # Mouse click
    # -----------------------------
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.last_click = (x, y)
            self.get_logger().info(f"Clicked pixel: {x}, {y}")

    # -----------------------------
    # Get end-effector position (TF-based)
    # -----------------------------
    def get_ee_position(self):
        try:
            trans = self.tf_buffer.lookup_transform(
                "base_link",
                "tool_frame",   # same as your working script
                rclpy.time.Time()
            )

            x = trans.transform.translation.x
            y = trans.transform.translation.y
            z = trans.transform.translation.z

            return [x, y, z]

        except Exception as e:
            self.get_logger().warn(f"TF lookup failed: {e}")
            return None

    # -----------------------------
    # Save correspondence
    # -----------------------------
    def save_point(self):
        if self.last_click is None:
            self.get_logger().warn("No click yet.")
            return

        if self.K is None:
            self.get_logger().warn("No camera intrinsics yet.")
            return

        point_3d = self.get_ee_position()
        if point_3d is None:
            return

        u, v = self.last_click

        self.points_2d.append([u, v])
        self.points_3d.append(point_3d)

        self.get_logger().info(
            f"Saved pair #{len(self.points_2d)}: 2D={u,v}, 3D={point_3d}"
        )

    # -----------------------------
    # Compute calibration
    # -----------------------------
    def compute_calibration(self):
        if len(self.points_2d) < 6:
            self.get_logger().warn("Need at least 6 points.")
            return

        pts2d = np.array(self.points_2d, dtype=np.float32)
        pts3d = np.array(self.points_3d, dtype=np.float32)

        success, rvec, tvec = cv2.solvePnP(
            pts3d,
            pts2d,
            self.K,
            None
        )

        if not success:
            self.get_logger().error("PnP failed.")
            return

        R, _ = cv2.Rodrigues(rvec)

        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = tvec.flatten()

        self.get_logger().info("\n=== RESULT ===")
        self.get_logger().info(f"T (base -> camera):\n{T}")

        quat = tf_transformations.quaternion_from_matrix(T)

        self.get_logger().info("\n=== USE THIS TF ===")
        self.get_logger().info(
            f"ros2 run tf2_ros static_transform_publisher "
            f"{T[0,3]} {T[1,3]} {T[2,3]} "
            f"{quat[0]} {quat[1]} {quat[2]} {quat[3]} "
            f"base_link camera_link"
        )

    # -----------------------------
    # Main loop
    # -----------------------------
    def spin(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.01)

            if self.image is not None:
                display = self.image.copy()

                if self.last_click:
                    cv2.circle(display, self.last_click, 5, (0, 0, 255), -1)

                cv2.imshow("image", display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                self.save_point()

            elif key == ord('c'):
                self.compute_calibration()

            elif key == ord('q'):
                break

        cv2.destroyAllWindows()


def main():
    rclpy.init()
    node = CameraArmCalibrator()
    node.spin()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()