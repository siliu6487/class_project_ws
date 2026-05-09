#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from moveit_msgs.msg import PlanningScene, CollisionObject
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose


class AddTable(Node):
    def __init__(self):
        super().__init__("add_table")

        self.client = self.create_client(
            ApplyPlanningScene,
            "/apply_planning_scene"
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for /apply_planning_scene...")

        self.timer = self.create_timer(2.0, self.add_table)

    def add_table(self):
        self.timer.cancel()

        table = CollisionObject()
        table.id = "table_under_arm"

        # Try base_link first if base_libk fails
        table.header.frame_id = "base_link"
        table.header.stamp = self.get_clock().now().to_msg()

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [1.5, 1.0, 0.2]

        pose = Pose()
        pose.orientation.w = 1.0
        pose.position.x = box.dimensions[0] / 2.0 - 0.05
        pose.position.y = 0.0
        pose.position.z = -0.145

        table.primitives.append(box)
        table.primitive_poses.append(pose)
        table.operation = CollisionObject.ADD

        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects.append(table)

        req = ApplyPlanningScene.Request()
        req.scene = scene

        future = self.client.call_async(req)
        future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        result = future.result()

        if result is None:
            self.get_logger().error("No response from /apply_planning_scene")
        elif result.success:
            self.get_logger().info("Table added successfully")
        else:
            self.get_logger().error("MoveIt rejected the table collision object")

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = AddTable()
    rclpy.spin(node)


if __name__ == "__main__":
    main()