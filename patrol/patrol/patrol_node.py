import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped

def main()->None:
    rclpy.init()
    navigator = BasicNavigator()

    # Wait for the navigation stack to be ready
    navigator.waitUntilNav2Active()

    # Define patrol points
    patrol_points = [
        PoseStamped(header=None, pose=navigator.getCurrentPose().pose),  # Start point
        PoseStamped(header=None, pose=navigator.getCurrentPose().pose),  # Point 1
        PoseStamped(header=None, pose=navigator.getCurrentPose().pose),  # Point 2
        PoseStamped(header=None, pose=navigator.getCurrentPose().pose)   # Point 3
    ]

    # Load patrol points (replace with actual coordinates)
    # TODO - load yaml of patrol points

    # Start patrol loop
    task = navigator.followWaypoints(patrol_points)
    # TODO - check task progress

