# Control-Systems-Project

# Event-Triggered Adaptive Control for a Low-Cost Mobile Robot

## 1. Project Title
**Event-Triggered Control Architecture for Consumer-Grade Differential-Drive Robots: A Simulink + ROS/Gazebo Approach**

## 2. Problem Statement
Most mobile robot controllers (PID, LQR, etc.) recompute and send control signals at a fixed, continuous sampling rate — regardless of whether the robot's error has actually changed enough to need a correction. This wastes onboard computation and, in wirelessly networked robots, wastes bandwidth and battery. **Event-triggered control** instead updates the controller only when the tracking error crosses a dynamic threshold, cutting unnecessary updates while keeping performance comparable to continuous control.

This technique is well-studied in academic control theory but has few patents specifically applied to **low-cost consumer mobile robotics** (as opposed to industrial or large-scale networked systems) — making it a good "novel application" angle for a patent-style disclosure.

## 3. Objectives
- Design and simulate a differential-drive robot control system in **Simulink**, comparing:
  - Baseline: continuous/fixed-rate PID controller
  - Proposed: event-triggered adaptive controller
- Quantify improvement in: control update frequency, communication load, tracking error, robustness to disturbance
- Validate the same control logic in **Gazebo** (physics simulation) using ROS
- Build a **small physical demo** (2-wheel robot chassis + ESP32) running the same control logic, showing real-world behavior roughly matches simulation trends

## 4. Tools & Tech Stack
| Layer | Tool | Purpose |
|---|---|---|
| Controller design & analysis | MATLAB/Simulink | Core simulation, PID vs. event-triggered comparison, plots/data |
| Physics simulation | Gazebo | 3D physics-based validation of the same controller logic |
| Robot framework | ROS (Noetic, pending version check) | Middleware connecting simulated and physical robot via common topics/messages |
| Microcontroller | ESP32 (via micro-ROS or rosserial) | Runs controller on physical hardware, acts as a real ROS node |
| Hardware | 2-wheel smart car chassis kit, motor driver (L298N/TB6612), battery pack, wheel encoders | Physical proof-of-concept |

## 5. System Architecture (high level)
```
        ┌─────────────────────┐
        │   Simulink Model     │  →  Controller design + comparison plots
        │ (PID vs Event-Trig.) │
        └──────────┬───────────┘
                    │ logic ported to
                    ▼
        ┌─────────────────────┐        ┌─────────────────────┐
        │   ROS Node (Sim)     │◄──────►│  Gazebo (simulated   │
        │  Event-trig control  │  ROS   │  differential-drive  │
        │                       │ topics │  robot + world)      │
        └──────────┬───────────┘        └─────────────────────┘
                    │ same node logic ported to
                    ▼
        ┌─────────────────────┐
        │  ESP32 (micro-ROS)   │  →  Physical 2-wheel robot demo
        │  Same control logic  │
        └─────────────────────┘
```

## 6. Deliverables
- Simulink model files + comparison plots (update frequency, error, robustness)
- ROS workspace + Gazebo simulation demo (video/recording)
- Physical robot demo (short video/log data)
- Patent-style written report: background/prior art, technical description, results, claims section

## 7. Rough Timeline 
| Phase | Duration | Output |
|---|---|---|
| Simulink modeling & controller design | ~1 week | Working model, initial comparison data |
| ROS/Gazebo setup & integration | ~3–5 days | Simulated robot running same logic |
| Hardware assembly & ESP32 firmware | ~3–5 days | Physical robot running controller |
| Data collection, write-up, claims section | ~1 week | Final report + demo recordings |
