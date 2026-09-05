import os
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import math, csv, time

LOG_DIR = os.path.expanduser('~/ros2_logs')
os.makedirs(LOG_DIR, exist_ok=True)

class EventTriggeredController(Node):
    def __init__(self):
        super().__init__('event_triggered_controller')
        self.robot_name = 'vehicle_blue'
        
        self.sub = self.create_subscription(
            Odometry, f'/model/{self.robot_name}/odometry', self.odom_callback, 10)
        self.pub = self.create_publisher(
            Twist, f'/model/{self.robot_name}/cmd_vel', 10)

        # Control & Event parameters
        self.target_speed = 0.5
        self.threshold = 0.03
        self.max_hold_time = 1.0  # force update at least once per second
        
        # Timing & State variables
        self.current_error = 0.0
        self.e_last = 0.0
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()
        self.last_trigger_time = time.time()
        self.filtered_speed = 0.0
        self.alpha = 0.3  # smoothing factor, tune between 0.1-0.5

        
        # PID Gain Parameters
        self.Kp = 1.5
        self.Ki = 0.5
        self.Kd = 0.1
        
        # Performance Counters & Logging
        self.trigger_count = 0
        self.step_count = 0
        self.log_file = open(os.path.join(LOG_DIR, 'event_triggered_log.csv'), 'w', newline='')
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(['time', 'error', 'triggered', 'cmd_vel'])

        # Timer: evaluate control/event condition at 20 Hz (0.05s)
        self.timer = self.create_timer(0.05, self.control_loop)

    def odom_callback(self, msg):
        actual_speed = msg.twist.twist.linear.x
        self.current_error = self.target_speed - actual_speed
        # State update only ΓÇö no event execution inside callback
        raw_speed = msg.twist.twist.linear.x
        self.filtered_speed = self.alpha * raw_speed + (1 - self.alpha) * self.filtered_speed
        self.current_error = self.target_speed - self.filtered_speed
    def control_loop(self):
        error = self.current_error
        now = time.time()
        dt = max(now - self.prev_time, 1e-3)
        self.prev_time = now
        self.step_count += 1

        self.get_logger().info(f'control_loop actual dt: {dt:.3f}s', throttle_duration_sec=1.0)

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        triggered = 0
        if abs(error - self.e_last) >= self.threshold or (now - self.last_trigger_time) >= self.max_hold_time:
            u = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
            u = max(min(u, 1.0), -1.0)
            
            twist = Twist()
            twist.linear.x = u
            self.pub.publish(twist)
            
            self.e_last = error
            self.last_trigger_time = now
            self.trigger_count += 1
            triggered = 1

        self.logger.writerow([now, error, triggered, self.e_last])
        self.log_file.flush()

def main(args=None):
    rclpy.init(args=args)
    node = EventTriggeredController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        print(f'\n[event_triggered_node] Total triggers: {node.trigger_count} / {node.step_count} steps')
        if hasattr(node, 'log_file') and not node.log_file.closed:
            node.log_file.flush()
            node.log_file.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
