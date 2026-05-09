
from control_msgs.action import GripperCommand

def control_gripper(position, effort=1.0):
    """
    position:
        0.0 = open
        ~0.8–1.0 = closed
    """

    goal_msg = GripperCommand.Goal()
    goal_msg.command.position = position
    goal_msg.command.max_effort = effort

    print(f"Sending gripper command: {position}")

    # wait for server
    gripper_client.wait_for_server()

    send_goal_future = gripper_client.send_goal_async(goal_msg)

    rclpy.spin_until_future_complete(node, send_goal_future)
    goal_handle = send_goal_future.result()

    if not goal_handle.accepted:
        print("Gripper goal rejected")
        return

    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)

    print("Gripper done")

def open_gripper():
    control_gripper(0.0)

def close_gripper():
    control_gripper(0.8)  # adjust if needed