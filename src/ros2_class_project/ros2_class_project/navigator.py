from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class Navigator:

    def __init__(self, node):
        self.node = node
        self.client = ActionClient(node, NavigateToPose, 'navigate_to_pose')

        self._goal_handle = None
        self._done = False
        self._status = None

    def go_to_pose(self, x, y, z, w):
        goal_msg = NavigateToPose.Goal()
        pose = PoseStamped()

        pose.header.frame_id = 'map'
        pose.header.stamp = self.node.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = z
        pose.pose.orientation.w = w

        goal_msg.pose = pose

        self.node.get_logger().info(
            f"Navigating to: x={x}, y={y}, z={z}, w={w}"
        )

        self.client.wait_for_server()

        send_goal_future = self.client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_callback)

        self._done = False
        self._status = None

    def _goal_response_callback(self, future):
        self._goal_handle = future.result()

        if not self._goal_handle.accepted:
            self.node.get_logger().error("Goal rejected!")
            self._done = True
            self._status = "rejected"
            return

        self.node.get_logger().info("Goal accepted")

        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future):
        result = future.result()
        self._status = result.status
        self._done = True

        self.node.get_logger().info(
            f"Navigation finished with status: {self._status}"
        )

    def is_done(self):
        return self._done

    def get_status(self):
        return self._status