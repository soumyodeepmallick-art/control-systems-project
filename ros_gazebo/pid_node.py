import os
LOG_DIR = os.path.expanduser('~/ros2_logs')
os.makedirs(LOG_DIR, exist_ok=True)
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import time, csv

class ContinuousPIDController(Node):
    def __init__(self):
        super().__init__('continuous_pid_controller')
        self.robot_name = 'vehicle_green'
        self.sub = self.create_subscription(
            Odometry, f'/model/{self.robot_name}/odometry', self.odom_callback, 10)
        self.pub = self.create_publisher(
            Twist, f'/model/{self.robot_name}/cmd_vel', 10)

        self.target_speed = 0.5
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = time.time()
        self.Kp, self.Ki, self.Kd = 1.5, 0.5, 0.05
        self.publish_count = 0

        self.log_file = open(os.path.join(LOG_DIR, 'pid_log.csv'), 'w', newline='')
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(['time', 'error', 'cmd_vel'])

    def odom_callback(self, msg):
        actual_speed = msg.twist.twist.linear.x
        error = self.target_speed - actual_speed
        now = time.time()
        dt = max(now - self.prev_time, 1e-3)
        self.prev_time = now

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        u = self.Kp*error + self.Ki*self.integral + self.Kd*derivative
        u = max(min(u, 1.0), -1.0)
        twist = Twist()
        twist.linear.x = u
        self.pub.publish(twist)
        self.publish_count += 1
        self.logger.writerow([now, error, u])
        self.log_file.flush()

def main(args=None):
    rclpy.init(args=args)
    node = ContinuousPIDController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.get_logger().info(f'Total publishes: {node.publish_count}')
    node.log_file.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
