import rclpy
from rclpy.node import Node

from ros2_class_project.navigator import Navigator 


# --- Define your poses here ---
MY_TABLE = (0.332364, 0.577014, -0.49963, 0.866239)
ARM_TABLE = (-0.702617, 3.0207, 0.934316, 0.356445)


class NavTest(Node):

    def __init__(self):
        super().__init__('nav_test')

        self.navigator = Navigator(self)

        self.sequence = [
            ("my_table", MY_TABLE),
            ("arm_table", ARM_TABLE),
            ("my_table", MY_TABLE),
        ]

        self.current_goal_index = 0
        self.waiting_for_result = False

        # run loop every 0.5 sec
        self.timer = self.create_timer(0.5, self.run)

    def run(self):

        # If all goals done
        if self.current_goal_index >= len(self.sequence):
            self.get_logger().info("✅ Navigation sequence complete!")
            rclpy.shutdown()
            return

        # If not currently navigating → send next goal
        if not self.waiting_for_result:
            name, pose = self.sequence[self.current_goal_index]

            self.get_logger().info(f"Sending goal: {name}")

            self.navigator.go_to_pose(*pose)
            self.waiting_for_result = True
            return

        # If waiting → check completion
        if self.navigator.is_done():
            status = self.navigator.get_status()

            if status == 4:  # SUCCEEDED
                self.get_logger().info("✅ Goal reached")
            else:
                self.get_logger().warn(f"⚠️ Goal failed with status: {status}")

            self.current_goal_index += 1
            self.waiting_for_result = False


def main():
    rclpy.init()
    node = NavTest()
    rclpy.spin(node)


if __name__ == '__main__':
    main()