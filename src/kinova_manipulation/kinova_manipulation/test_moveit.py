import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from tf2_ros import Buffer, TransformListener
from tf_transformations import quaternion_multiply, quaternion_from_euler
from rclpy.action import ActionClient
from control_msgs.action import GripperCommand

from pymoveit2 import MoveIt2
import time


class KinovaMoveItTest(Node):
    def __init__(self):
        super().__init__("kinova_moveit_test")

        # --- TF setup ---
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # --- MoveIt2 setup ---
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=[
                "joint_1",
                "joint_2",
                "joint_3",
                "joint_4",
                "joint_5",
                "joint_6",
            ],
            base_link_name="base_link",        # adjust if needed
            end_effector_name="tool_frame",    # adjust if needed
            group_name="arm",
        )

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            "/gen3_lite_2f_gripper_controller/gripper_cmd"
        )

    def wait_for_tf(self):
        self.get_logger().info("Waiting for TF...")

        for _ in range(30):  # ~3 seconds
            rclpy.spin_once(self, timeout_sec=0.1)
            try:
                trans = self.tf_buffer.lookup_transform(
                    "base_link",
                    "tool_frame",   # change if needed
                    rclpy.time.Time()
                )
                self.get_logger().info("TF is ready!")
                return trans
            except Exception:
                time.sleep(0.1)

        self.get_logger().error("TF not available!")
        return None
    
    def wait(self, duration=8.0):
            for _ in range(int(duration * 10)):
                rclpy.spin_once(self, timeout_sec=0.1)

    def control_gripper(self, position, effort=1.0):
        """
        position:
            0.0 = open
            ~0.8–1.0 = closed (depends on gripper)
        """
        self.get_logger().info(f"Gripper command: {position}")

        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = effort

        # wait for server
        self.gripper_client.wait_for_server()

        send_goal_future = self.gripper_client.send_goal_async(goal_msg)

        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Gripper goal rejected")
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info("Gripper action done")

    def open_gripper(self):
        self.control_gripper(0.0)

    def close_gripper(self):
        self.control_gripper(0.8)  # adjust if needed

    def run(self):
        # --- wait for TF ---
        trans = self.wait_for_tf()
        if trans is None:
            return

        # --- build current pose ---
        current_pose = Pose()
        current_pose.position.x = trans.transform.translation.x
        current_pose.position.y = trans.transform.translation.y
        current_pose.position.z = trans.transform.translation.z
        current_pose.orientation = trans.transform.rotation

        self.get_logger().info(f"Current pose: {current_pose}")

        # --- apply small rotation ---
        roll = 0.0
        pitch = 0.0
        yaw = 0.3  # small change first


        # current orientation
        current_q = [
            current_pose.orientation.x,
            current_pose.orientation.y,
            current_pose.orientation.z,
            current_pose.orientation.w,
        ]

        # very small rotation
        delta_q = quaternion_from_euler(0.0, 0.0, 0.1)

        # combine
        new_q = quaternion_multiply(delta_q, current_q)

        current_pose.orientation.x = new_q[0]
        current_pose.orientation.y = new_q[1]
        current_pose.orientation.z = new_q[2]
        current_pose.orientation.w = new_q[3]

        self.get_logger().info("Planning and executing motion...")

        # --- execute ---
        
        self.get_logger().info("Opening gripper...")
        self.close_gripper()
        self.wait(2.0)

        print("rotate end effector...")
        self.moveit2.move_to_pose(current_pose)
        self.wait()

        self.get_logger().info("Closing gripper...")
        self.open_gripper()
        self.wait(2.0)
        



def main():
    rclpy.init()

    node = KinovaMoveItTest()

    # Give MoveIt time to fully start
    node.get_logger().info("Waiting for MoveIt...")
    time.sleep(5)

    node.run()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()