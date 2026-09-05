# Event-Triggered Control Architecture for Consumer-Grade Differential-Drive Robots
### A Simulink + ROS2/Gazebo Approach

Course project for Control Systems — patent-disclosure-style project demonstrating an event-triggered
adaptive controller applied to low-cost, consumer-grade mobile robotics, benchmarked against a continuous
PID baseline across two independent validation environments (Simulink simulation, and live ROS2/Gazebo
message traffic), with an ESP32-based physical demo planned as final validation.

---

## Project Summary

Most mobile robot controllers recompute and transmit control signals continuously, regardless of whether
the tracking error has actually changed enough to warrant a correction — wasting onboard computation and,
in networked robots, wireless communication bandwidth. This project implements and validates an
**event-triggered controller** that only updates when a dynamic error threshold is crossed, and quantifies
the resulting savings against a standard continuous PID baseline under identical test conditions.

**Novelty claim:** A control method for wheeled mobile robots wherein control signal updates are triggered
adaptively based on a dynamic error threshold rather than fixed-interval sampling, reducing onboard
computation and wireless communication load by a measurable percentage, applied specifically to low-cost
consumer-grade mobile robotics platforms.

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Simulink model — 1D plant (DC motor speed control), PID vs. event-triggered | ✅ Complete |
| **Phase 2** | ROS2 + Gazebo — live implementation, real message traffic, differential-drive robot | ✅ Complete |
| **Phase 3** | Advanced Simulink — full 2D differential-drive kinematics, waypoint navigation | 🔧 In progress |
| **Phase 4** | Physical demo — ESP32 + 2-wheel chassis kit, running the same controller logic | ⏳ Pending (hardware ordered) |
| **Final report** | Patent-style disclosure document (background, technical description, claims) | 📝 Draft in progress |

---

## Key Results So Far

### Phase 1 — Simulink (idealized plant)
- PID RMSE (steady-state): 0.7294
- Event-Triggered RMSE (steady-state): 0.7523
- **Update savings vs. realistic 50Hz PID baseline: 79.9%**

### Phase 2 — ROS2 / Gazebo (live simulation, real message traffic)
Repeated across 3 independent runs for consistency:

| Run | Duration | Savings | PID RMSE | Event-Triggered RMSE |
|---|---|---|---|---|
| 1 | 33.3s | 90.7% | 0.0261 | 0.0295 |
| 2 | 62.0s | 94.4% | 0.0177 | 0.0165 |
| 3 | 101.9s | 95.4% | 0.0107 | 0.0103 |

Both phases independently confirm the core claim: comparable or better tracking accuracy alongside a large
(~80-95%) reduction in control update frequency.

---

## Repository Structure

```
control-systems-project/
├── README.md                          → this file
├── simulink/
│   ├── event_triggered_vs_pid.slx          → Phase 1 model (1D plant)
│   └── event_triggered_2d_navigation.slx   → Phase 3 model (2D kinematics, in progress)
├── ros_gazebo/
│   ├── event_triggered_control/            → ROS2 package (Phase 2)
│   │   ├── event_triggered_node.py
│   │   └── pid_node.py
│   ├── diff_drive_world_modified.sdf       → Gazebo world with equalized sensor rates
│   └── plot_ros_results.py                 → post-run comparison plotting script
├── firmware/                           → ESP32 code (Phase 4, pending hardware)
├── results/
│   ├── phase1_controller_comparison.png
│   ├── phase2_controller_comparison.png
│   ├── ros_results.txt
│   ├── ros_results.png
│   └── results_log.txt
|    
└── docs/
    ├── theory_notes_phase1.md            → Phase 1 theory (block-by-block explanation)
    ├── Theory_notes_Phase2.md              → Phase 2 theory (ROS2/Gazebo architecture)
    ├── Problems-and-solutions_phase1.md
    ├── simulink_phase3_theory_notes.md     → Phase 3 theory (2D kinematics, go-to-goal control)
    └── debugging_challenges_log_phase2.md         → full record of issues found & fixed during Phase 2
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| MATLAB / Simulink | Controller design, PID vs. event-triggered comparison (Phases 1 & 3) |
| ROS2 Humble | Middleware connecting controller nodes to the simulated robot (Phase 2) |
| Gazebo (Ignition Fortress) | Physics-based robot simulation (Phase 2) |
| Python (rclpy) | ROS2 node implementation |
| ESP32 + micro-ROS | Physical robot control (Phase 4, planned) |
| 2-wheel smart car chassis kit | Physical hardware platform (Phase 4, planned) |

---

## How to Reproduce

### Phase 1 (Simulink)
1. Open `simulink/event_triggered_vs_pid.slx` in MATLAB
2. Run the simulation (Fixed-step, `ode4`, step size `0.001`, stop time `20`)
3. Run the plotting/metrics code in `docs/simulink_theory_notes.md` (Command Window section)

### Phase 2 (ROS2 / Gazebo)
```bash
source /opt/ros/humble/setup.bash
ros2 launch ros_gz_sim_demos diff_drive.launch.py   # uses diff_drive_world_modified.sdf

# In separate terminals:
source ~/ros2_ws/install/setup.bash
ros2 run event_triggered_control event_triggered_node
ros2 run event_triggered_control pid_node

# After ~30-60s, Ctrl+C both nodes, then:
python3 ros_gazebo/plot_ros_results.py
```


## Notes

- All comparisons use identical plant/robot conditions for both controllers (same reference signal,
  same disturbance, same sensor rate) to ensure a fair, apples-to-apples measurement of savings.
- See `docs/debugging_challenges_log.md` for a full account of issues encountered and fixed during
  Phase 2 development (integral windup, sensor-rate asymmetry, noise-driven integral cancellation, etc.)
  — this is considered part of the project's technical contribution, not just implementation detail.
