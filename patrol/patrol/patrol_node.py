import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import argparse

def main()->None:
    # Get args
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", default=3, type=int)
    args, other = parser.parse_known_args()
    cycles = args.cycles

    rclpy.init(args=other)
    navigator = BasicNavigator()

    # Wait for the navigation stack to be ready
    navigator.waitUntilNav2Active()

    # Define patrol points
    patrol_points = [
        PoseStamped(),  # Point 0
        PoseStamped(),  # Point 1
        PoseStamped(),  # Point 2
        PoseStamped(),  # Point 3
        PoseStamped()   # Point 4 - Start Point
    ]

    # Load patrol points (replace with actual coordinates)
    # Waypoint 0
    patrol_points[0].header.frame_id = 'map'
    patrol_points[0].header.stamp = navigator.get_clock().now().to_msg()
    patrol_points[0].pose.position.x = 5.481
    patrol_points[0].pose.position.y = 0.697
    patrol_points[0].pose.orientation.z = 0.646
    patrol_points[0].pose.orientation.w = 0.763
    # Waypoint 1
    patrol_points[1].header.frame_id = 'map'
    patrol_points[1].header.stamp = navigator.get_clock().now().to_msg()
    patrol_points[1].pose.position.x = 5.099
    patrol_points[1].pose.position.y = 4.019
    patrol_points[1].pose.orientation.z = 0.999
    patrol_points[1].pose.orientation.w = 0.038
    # Waypoint 2
    patrol_points[2].header.frame_id = 'map'
    patrol_points[2].header.stamp = navigator.get_clock().now().to_msg()
    patrol_points[2].pose.position.x = -1.785
    patrol_points[2].pose.position.y = 2.106
    patrol_points[2].pose.orientation.z = -0.748
    patrol_points[2].pose.orientation.w = 0.664
    # Waypoint 3
    patrol_points[3].header.frame_id = 'map'
    patrol_points[3].header.stamp = navigator.get_clock().now().to_msg()
    patrol_points[3].pose.position.x = -0.984
    patrol_points[3].pose.position.y = -3.599
    patrol_points[3].pose.orientation.z = -0.833
    patrol_points[3].pose.orientation.w = 0.554
    # Waypoint 4
    patrol_points[4].header.frame_id = 'map'
    patrol_points[4].header.stamp = navigator.get_clock().now().to_msg()
    patrol_points[4].pose.position.x = 2.764
    patrol_points[4].pose.position.y = -4.074
    patrol_points[4].pose.orientation.z = 0.826
    patrol_points[4].pose.orientation.w = 0.562

    # Start patrol loop
    for i in range(cycles):
        task = navigator.followWaypoints(patrol_points)
        while not navigator.isTaskComplete(task=follow_waypoints_task):
            feedback = navigator.getFeedback(task=follow_waypoints_task)
            navigator.get_logger().info(f"Navigating to waypoint {feedback.current_waypoint}")

        result = navigator.getResult();
        if result == TaskResult.SUCCEEDED:
            navigator.get_logger().info('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            navigator.get_logger().info('Goal was canceled!')
        elif result == TaskResult.FAILED:
            (error_code, error_msg) = navigator.getTaskError()
            navigator.get_logger().error('Goal failed!{error_code}:{error_msg}')
        else:
            navigator.get_logger().error('Goal has an invalid return status!')

    navigator.lifecycleShutdown()

