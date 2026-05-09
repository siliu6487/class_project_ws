import math
import rclpy
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped


# 🔹 Replace tf_transformations with this
def yaw_to_quaternion(yaw):
    return (
        0.0,
        0.0,
        math.sin(yaw / 2.0),
        math.cos(yaw / 2.0)
    )


class Navigator:
    def __init__(self, node):
        self.node = node
        self.client = ActionClient(node, NavigateToPose, 'navigate_to_pose')

        # recorded goals to go to
        self.goals = {
            "arm_table": [-0.50607, 1.92922, 2.47735],
            "user_table": [0.332364, 0.577014, -1.04634]
        }


    def go_to(self, goal_name):
        if goal_name not in self.goals:
            print(f"❌ Unknown goal: {goal_name}")
            return

        x, y, yaw = self.goals[goal_name]

        print(f"🚗 Navigating to {goal_name} → ({x:.2f}, {y:.2f}, yaw={yaw:.2f})")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self._create_pose(x, y, yaw)

        # 🔹 wait for Nav2
        if not self.client.wait_for_server(timeout_sec=5.0):
            print("❌ Nav2 action server not available!")
            return

        send_future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self.node, send_future)

        goal_handle = send_future.result()

        if not goal_handle or not goal_handle.accepted:
            print("❌ Goal rejected")
            return

        print("⏳ Moving...")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future)

        print("✅ Arrived at destination!")

    def _create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.node.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        qx, qy, qz, qw = yaw_to_quaternion(yaw)

        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose