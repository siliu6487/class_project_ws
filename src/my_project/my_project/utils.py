import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState

from pymoveit2 import MoveIt2
from tf2_ros import Buffer, TransformListener

from rclpy.action import ActionClient
from control_msgs.action import GripperCommand

import json
import time

import numpy as np
import pickle


from perception_interfaces.srv import PerceptionCheck

from pymoveit2 import MoveIt2
from tf2_ros import Buffer, TransformListener

from geometry_msgs.msg import Pose

tf_buffer = Buffer()


def call_perception(node, path, mode):
    client = node.create_client(PerceptionCheck, 'perception_check')

    while not client.wait_for_service(timeout_sec=1.0):
        print("Waiting for perception service...")

    req = PerceptionCheck.Request()
    req.file_path = path
    req.mode = mode

    future = client.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    return future.result().result


def control_gripper(position, gripper_client, node, effort=1.0):
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


def get_current_joint_positions(target_joint_names=None):
    global joint_state

    name_to_pos = dict(zip(joint_state.name, joint_state.position))

    if target_joint_names is None:
        target_joint_names = [
            "joint_1",
            "joint_2",
            "joint_3",
            "joint_4",
            "joint_5",
            "joint_6",
        ]

    return [name_to_pos[name] for name in target_joint_names]

    

def reached_joint_pose(target, current=None, tol=0.08):
    if current is None:
        current = get_current_joint_positions()
        
    errors = [abs(t - c) for t, c in zip(target, current)]

    return max(errors) < tol


def get_pose():
    spin_some(1.0)
    try:
        trans = tf_buffer.lookup_transform(
            "base_link",
            "tool_frame",
            rclpy.time.Time()
        )

        pose = Pose()
        pose.position.x = trans.transform.translation.x
        pose.position.y = trans.transform.translation.y
        pose.position.z = trans.transform.translation.z
        pose.orientation = trans.transform.rotation

        return pose
    except Exception as e:
        print("TF error:", e)
        return None
    
def print_pose(pose):
    print("Translation:",
          [pose.position.x, pose.position.y, pose.position.z])
    print("Quaternion:",
          [pose.orientation.x,
           pose.orientation.y,
           pose.orientation.z,
           pose.orientation.w])
    

def make_pose(pos_xyz, orient_xyzw):
    pose = Pose()
    
    pose.position.x, pose.position.y, pose.position.z = pos_xyz
    pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w = orient_xyzw
    
    return pose



