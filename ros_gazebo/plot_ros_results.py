"""
Plot and compare event-triggered vs continuous PID controller logs from Phase 2 (ROS2/Gazebo).
Run this on your Ubuntu/WSL machine after collecting both CSV logs:
    python3 plot_ros_results.py

Requires: pip install pandas matplotlib --break-system-packages
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

LOG_DIR = os.path.expanduser('~/ros2_logs')

# --- Load data ---
event_df = pd.read_csv(os.path.join(LOG_DIR, 'event_triggered_log.csv'))
pid_df = pd.read_csv(os.path.join(LOG_DIR, 'pid_log.csv'))

if event_df.empty or pid_df.empty:
    raise SystemExit("One of the CSV files is empty. Re-run the nodes for longer (15-20s) "
                      "with the flush() fix applied before running this script.")

# --- Normalize time to start at 0 for both logs ---
event_df['t'] = event_df['time'] - event_df['time'].iloc[0]
pid_df['t'] = pid_df['time'] - pid_df['time'].iloc[0]

# --- Compute headline metrics ---
total_event_msgs = event_df['triggered'].sum()
total_event_steps = len(event_df)
total_pid_msgs = len(pid_df)  # PID publishes every callback, so row count = publish count

duration = min(event_df['t'].iloc[-1], pid_df['t'].iloc[-1])
event_rate_hz = total_event_msgs / duration
pid_rate_hz = total_pid_msgs / duration

savings_pct = (1 - event_rate_hz / pid_rate_hz) * 100 if pid_rate_hz > 0 else float('nan')

print(f"Duration compared: {duration:.1f}s")
print(f"PID publishes: {total_pid_msgs}  (~{pid_rate_hz:.2f} Hz)")
print(f"Event-triggered publishes: {int(total_event_msgs)}  (~{event_rate_hz:.2f} Hz)")
print(f"Communication savings: {savings_pct:.1f}%")
print(f"PID steady-state mean |error|: {pid_df['error'].abs().mean():.4f}")
print(f"Event-triggered steady-state mean |error|: {event_df['error'].abs().mean():.4f}")

# --- Plot 1: Error over time ---
fig, axs = plt.subplots(3, 1, figsize=(9, 10))

axs[0].plot(pid_df['t'], pid_df['error'], 'b-', label='Continuous PID', linewidth=1)
axs[0].plot(event_df['t'], event_df['error'], 'r-.', label='Event-Triggered', linewidth=1)
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Error (m/s)')
axs[0].set_title('Tracking Error Comparison (ROS2/Gazebo, live data)')
axs[0].legend()
axs[0].grid(True)

# --- Plot 2: Command signal over time ---
axs[1].plot(pid_df['t'], pid_df['cmd_vel'], 'b-', label='u_PID', linewidth=1)
event_cmds = event_df[event_df['triggered'] == 1]
axs[1].scatter(event_cmds['t'], event_cmds['cmd_vel'], color='r', s=10, label='u_Event (on trigger)')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Command (linear.x)')
axs[1].set_title('Control Command Comparison')
axs[1].legend()
axs[1].grid(True)

# --- Plot 3: Trigger instances ---
axs[2].stem(event_df['t'], event_df['triggered'], linefmt='r-', markerfmt=' ', basefmt=' ')
axs[2].set_xlabel('Time (s)')
axs[2].set_ylabel('Triggered (1/0)')
axs[2].set_title(f'Event Trigger Instances ({savings_pct:.1f}% fewer publishes than PID)')
axs[2].set_ylim(-0.2, 1.2)
axs[2].grid(True)

plt.tight_layout()
out_path = os.path.join(LOG_DIR, 'ros2_comparison_plot.png')
plt.savefig(out_path, dpi=150)
print(f"\nPlot saved to: {out_path}")
plt.show()