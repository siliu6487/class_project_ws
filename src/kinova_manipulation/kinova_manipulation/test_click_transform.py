import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
import cv2

from tf2_ros import Buffer, TransformListener
from geometry_msgs.msg import PointStamped


class ClickTester(Node):

    def __init__(self):
        super().__init__("click_tester")

        self.bridge = CvBridge()

        self.color = None
        self.depth = None
        self.K = None

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(Image,
            '/camera/camera/color/image_raw',
            self.color_cb, 10)

        self.create_subscription(Image,
            '/camera/camera/depth/image_rect_raw',
            self.depth_cb, 10)

        self.create_subscription(CameraInfo,
            '/camera/camera/color/camera_info',
            self.info_cb, 10)

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.click_cb)

    def info_cb(self, msg):
        if self.K is None:
            k = msg.k
            self.K = np.array([
                [k[0], 0, k[2]],
                [0, k[4], k[5]],
                [0, 0, 1]
            ])

    def color_cb(self, msg):
        self.color = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def depth_cb(self, msg):
        self.depth = self.bridge.imgmsg_to_cv2(msg)

    def click_cb(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        if self.depth is None or self.K is None:
            print("No depth or K yet")
            return

        z = self.depth[y, x] / 1000.0  # mm → meters
        if z == 0:
            print("Invalid depth, try nearby pixel")
            return
        
        fx = self.K[0,0]
        fy = self.K[1,1]
        cx = self.K[0,2]
        cy = self.K[1,2]

        X = (x - cx) * z / fx
        Y = (y - cy) * z / fy

        print(f"\nCamera frame: {X:.3f}, {Y:.3f}, {z:.3f}")

        pt = PointStamped()
        pt.header.frame_id = "camera_link"
        pt.point.x = X
        pt.point.y = Y
        pt.point.z = z

        try:
            pt_base = self.tf_buffer.transform(pt, "base_link")
            print(f"Base frame: {pt_base.point}")
        except Exception as e:
            print("TF error:", e)

    def spin(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.01)

            if self.color is not None:
                cv2.imshow("image", self.color)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


def main():
    rclpy.init()
    node = ClickTester()
    node.spin()
    node.destroy_node()
    rclpy.shutdown()