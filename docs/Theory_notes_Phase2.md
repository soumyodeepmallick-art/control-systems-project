# Phase 2 — Event-Triggered Control in ROS2 + Gazebo

## 1. Overview

Phase 1 demonstrated the event-triggered control concept mathematically using a simplified 1D motor-speed plant. The results showed that an event-triggered controller could achieve tracking performance comparable to continuous PID control while updating the control input less frequently.

Phase 2 extends this concept to an actual simulated robotic system using **ROS2 and Gazebo**.

The main objective is to determine whether the same event-triggered control principle can operate on a simulated robot while sending real control commands through ROS2 topics.

This provides a more direct demonstration of the communication-saving aspect of event-triggered control. Instead of measuring savings only as fewer controller updates within simulation timesteps, Phase 2 measures savings through the number of actual control messages published to a ROS2 topic.

Therefore:

> **Phase 1 demonstrates the control concept, while Phase 2 demonstrates its operation within a realistic robotic communication pipeline.**

---

## 2. What Changes Between Phase 1 and Phase 2

### Phase 1

Phase 1 used a simplified mathematical plant:

* 1D motor-speed model
* MATLAB/Simulink-based implementation
* Continuous PID controller
* Event-triggered controller
* Control update savings measured in simulation timesteps

The event-triggered controller reduced the number of control updates while maintaining acceptable tracking performance.

### Phase 2

Phase 2 moves the controller into a simulated robotic environment:

* ROS2 is used for communication
* Gazebo is used as the robot simulator
* Robot state is obtained through odometry
* Velocity commands are sent through ROS2 topics
* The event-triggering condition determines when a new command is published
* Communication savings are measured through actual topic publications

This makes the measurement of communication savings more directly representative of what would matter in a physical robot communicating over a network.

---

## 3. Why ROS2 + Gazebo?

The purpose of Phase 2 is not to develop a new robot model.

The purpose is to test the **event-triggered controller in a realistic robotic software and communication pipeline**.

The `ros_gz_sim_demos` package provides an existing differential-drive demonstration with the required communication pipeline already configured.

The demo provides:

* A differential-drive robot
* Gazebo simulation
* Odometry publishing
* Velocity command input
* ROS2 topic communication

Using this existing setup avoids spending significant effort on:

* URDF creation
* `ros2_control` configuration
* Gazebo plugin configuration
* Robot spawning and integration

These tasks are largely independent of the controller itself.

Therefore, reusing the working differential-drive demo allows the project to focus on its main contribution:

> **The event-triggered control strategy and its communication-saving behavior.**

---

# 4. System Architecture

The Phase 2 architecture consists of a reference source, an event-triggered controller, and a simulated robot.

```text
                 [Waypoint / Reference Node]
                           │
                           │ Target pose / velocity
                           ▼
              [Event-Triggered Controller]
                           ▲
                           │
                    Odometry Input
                           │
                           │
              /model/vehicle_blue/odometry
                           │
                           │
                           ▼
              Error = Target − Actual
                           │
                           ▼
                  Trigger Condition
                           │
                  ┌────────┴────────┐
                  │                 │
               Triggered        Not Triggered
                  │                 │
                  ▼                 │
           Publish Twist            │
                  │                 │
                  └────────┐        │
                           ▼        │
              /model/vehicle_blue/  │
                    cmd_vel         │
                           │        │
                           ▼        │
                    [Gazebo Robot] ◄┘
```

The event-triggered controller continuously receives the robot's current state through the odometry topic.

It calculates the tracking error:

$$
e = r - y
$$

where:

* \(r\) = reference/target
* \(y\) = actual robot state
* \(e\) = tracking error

The controller then checks whether the event-triggering condition has been satisfied.

If the condition is satisfied, a new velocity command is published.

If the condition is not satisfied, no new command is published.

---

# 5. Continuous PID Comparison

A second robot is controlled using a conventional continuously publishing PID controller.

The two controllers therefore operate simultaneously:

### Vehicle Blue

**Event-triggered controller**

```text
Odometry
   ↓
Error calculation
   ↓
Trigger condition
   ↓
Publish only when triggered
   ↓
cmd_vel
```

### Vehicle Green

**Continuous PID controller**

```text
Odometry
   ↓
Error calculation
   ↓
PID calculation
   ↓
Continuous publishing
   ↓
cmd_vel
```

Both robots operate within the same Gazebo environment.

This provides a direct comparison between:

* Continuous control
* Event-triggered control

while keeping the simulation environment consistent.

The comparison mirrors the two-controller structure previously used in the Simulink implementation.

---

# 6. Key ROS2 Concepts

## 6.1 Node

A **node** is a running program that communicates with other components through the ROS2 communication system.

Phase 2 uses two primary controller nodes:

```text
pid_controller_node
event_triggered_controller_node
```

---

## 6.2 Topic

A **topic** is a named communication channel through which ROS2 nodes exchange messages.

The controller receives robot state through an odometry topic and sends velocity commands through a `cmd_vel` topic.

Examples:

```text
/model/vehicle_blue/odometry
/model/vehicle_blue/cmd_vel
```

---

## 6.3 Publisher

A publisher sends messages to a ROS2 topic.

In Phase 2, the controller publishes velocity commands using a `Twist` message.

Conceptually:

```text
Controller
    │
    │ publish()
    ▼
cmd_vel topic
```

---

## 6.4 Subscriber

A subscriber receives messages from a ROS2 topic.

The controller subscribes to the robot's odometry:

```text
odometry topic
      │
      ▼
Controller
```

This allows the controller to obtain the robot's current state.

---

## 6.5 Message Type

ROS2 topics transmit specific message types.

The primary message types used in Phase 2 are:

### Odometry

```text
nav_msgs/msg/Odometry
```

Used to obtain the robot's state.

### Velocity command

```text
geometry_msgs/msg/Twist
```

Used to send velocity commands to the robot.

---

## 6.6 Timer Callback

The controller periodically checks the system state using a timer callback.

This is analogous to the fixed simulation timestep used in the Phase 1 Simulink implementation.

At each timer execution, the controller can:

1. Read the latest robot state
2. Calculate the error
3. Evaluate the trigger condition
4. Publish a command if required
5. Log the result

The important distinction is that the controller **checks periodically**, but does not necessarily **publish periodically**.

---

# 7. Event-Triggering Logic

The fundamental event-triggering condition is carried directly from Phase 1.

The controller compares the current error with the error at the previous trigger event.

The condition is:

$$
\boxed{|e-e_{last}| \geq \text{threshold}}
$$

where:

* \(e\) = current error
* \(e_{last}\) = error at the last trigger
* `threshold` = event-triggering threshold

### If the condition is satisfied:

```text
|e - e_last| >= threshold
```

then:

1. A trigger event occurs.
2. A new control command is calculated.
3. The command is published.
4. `e_last` is updated.

### If the condition is not satisfied:

```text
|e - e_last| < threshold
```

then:

1. No trigger event occurs.
2. No new command is published.
3. The previous command remains in effect.

---

# 8. Zero-Order-Hold Behavior

In Phase 1, the event-triggered controller effectively held the previous control signal between trigger events.

In ROS2, this behavior is represented by simply **not publishing a new command** when the trigger condition is not satisfied.

Conceptually:

```text
Trigger
   │
   ├── YES → publish new command
   │
   └── NO  → publish nothing
```

The simulated robot continues using the last received velocity command.

This provides the ROS2 equivalent of the **Zero-Order-Hold (ZOH)** behavior used in Phase 1.

Therefore, the event-triggering mechanism itself remains conceptually unchanged:

> **The controller only communicates a new control command when the change in error is large enough to justify an update.**

---

# 9. What "Savings" Means in Phase 2

The definition of savings changes slightly between the two phases.

### Phase 1

Savings were measured as:

> Fewer control calculations/updates within simulation timesteps.

### Phase 2

Savings are measured as:

> **Fewer velocity-command publications on the `cmd_vel` topic.**

This is a more direct communication-oriented metric.

For example, if a controller checks the error 100 times but publishes only 20 commands:

```text
Controller checks = 100
Published commands = 20

Communication reduction = 80%
```

The controller still observes the system regularly, but it communicates only when a meaningful change occurs.

---

# 10. Measuring Communication Savings

ROS2 provides tools for observing topic behavior.

The publishing rate can be examined using:

```bash
ros2 topic hz /model/vehicle_blue/cmd_vel
```

The corresponding continuous controller can be measured through its command topic.

The comparison is therefore based on the actual rate of command messages being published.

Conceptually:

```text
Continuous PID
      │
      ▼
High publication rate
      │
      │
      ▼
More communication


Event-Triggered
      │
      ▼
Lower publication rate
      │
      │
      ▼
Reduced communication
```

The exact reduction depends on the selected triggering threshold and the behavior of the robot.

---

# 11. Logging and Data Analysis

Both controllers will log relevant information during the simulation.

The primary logged quantities are:

* Timestamp
* Current error
* Trigger status
* Published command

The event-triggered controller should additionally make it possible to identify when a trigger event occurred.

The data will be stored in CSV format.

The resulting data can then be analyzed and plotted using Python and Matplotlib.

This allows Phase 2 to reproduce the comparison performed in MATLAB during Phase 1, while using ROS2-generated data as the source.

---

# 12. Phase 2 Experimental Comparison

The main comparison is:

| Parameter               | Continuous PID     | Event-Triggered Controller |
| ----------------------- | ------------------ | -------------------------- |
| Robot                   | Differential-drive | Differential-drive         |
| Environment             | Same Gazebo world  | Same Gazebo world          |
| State input             | Odometry           | Odometry                   |
| Control output          | `cmd_vel`          | `cmd_vel`                  |
| Control strategy        | Continuous PID     | Event-triggered            |
| Error evaluation        | Periodic           | Periodic                   |
| Command publishing      | Continuous         | Only when triggered        |
| Main performance metric | Tracking           | Tracking + communication   |
| Communication metric    | Publication rate   | Reduced publication rate   |

The experiment therefore evaluates two important aspects:

### 1. Control performance

Does the event-triggered controller maintain acceptable tracking compared with continuous PID?

### 2. Communication efficiency

How many fewer velocity commands are actually transmitted?

---

# 13. Expected Phase 2 Evidence

The Phase 2 implementation should produce evidence for the following:

### Tracking

The event-triggered robot should follow the desired motion with acceptable tracking performance.

### Reduced communication

The event-triggered controller should publish fewer `cmd_vel` messages than the continuously publishing PID controller.

### Comparable behavior

The reduction in communication should not cause an unacceptable degradation in tracking performance.

The central result can therefore be expressed as:

> **Event-triggered control can reduce control-message transmissions while maintaining acceptable robotic tracking performance.**

---

# 14. Phase 2 Workflow

The implementation follows this sequence:

```text
1. Launch Gazebo differential-drive demo
                ↓
2. Spawn/use the two robots
                ↓
3. Verify odometry topics
                ↓
4. Verify cmd_vel topics
                ↓
5. Implement continuous PID node
                ↓
6. Implement event-triggered controller
                ↓
7. Run both controllers
                ↓
8. Record controller data
                ↓
9. Measure cmd_vel publication rates
                ↓
10. Plot tracking and control results
                ↓
11. Compare communication savings
```

---

# 15. Main Objective of Phase 2

Phase 2 is intended to bridge the gap between the simplified mathematical demonstration of Phase 1 and a more realistic robotic implementation.

The core progression is:

```text
Phase 1
Mathematical / Simulink demonstration
        ↓
Event-triggered control concept
        ↓
Reduced control updates
        ↓
        Phase 2
ROS2 + Gazebo implementation
        ↓
Real ROS2 topic communication
        ↓
Reduced cmd_vel publications
        ↓
Communication-saving evidence
```

The important contribution of Phase 2 is therefore not the robot model itself.

The focus is on demonstrating that the **event-triggering principle can be transferred from a mathematical simulation to a ROS2-based robotic control architecture**, where reduced controller updates correspond directly to reduced command-message transmissions.

---

## Phase 2 Key Takeaway

> **Phase 1 showed that event-triggered control can reduce control updates while maintaining tracking performance. Phase 2 tests the same principle on a simulated differential-drive robot using ROS2 and Gazebo, where communication savings can be measured directly through the reduction in `cmd_vel` publications.**
