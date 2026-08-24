# Theory Notes: Event-Triggered vs Continuous PID Control (Simulink Model)

## 1. Why a Plant Model at All?

A "plant" in control terms is the physical system being controlled — here, a motor driving a robot wheel. We can't test a controller in isolation; we need something for it to act on and something that reacts realistically (with inertia, delay, etc.), otherwise any controller looks perfect. Simulink lets us represent the plant as a mathematical model (a transfer function) instead of needing real hardware for every test.

**DC Motor Plant (Phase 1):**
A DC motor's speed response to voltage input is commonly approximated as a first-order transfer function:

```
G(s) = K / (τs + 1)
```

Where:
- `K` = motor gain (steady-state speed per volt)
- `τ` = time constant (how fast the motor responds — larger τ = sluggish motor)

This is realistic enough to show meaningful controller behavior (rise time, overshoot, settling time) without needing motor electrical dynamics (inductance, back-EMF), which would be Phase 2/3 territory and unnecessary complexity for this comparison.

**Differential-Drive Kinematics (Phase 2, optional):**
For the full robot model, the plant becomes:
```
ẋ = v·cos(θ)
ẏ = v·sin(θ)
θ̇ = ω
```
Where `v` = linear velocity, `ω` = angular velocity, and `(x, y, θ)` is robot pose. This is nonlinear (note the trig terms), so it's built using Integrator blocks + trigonometric function blocks rather than a single transfer function — there's no single "G(s)" for a nonlinear system.

---

## 2. PID Controller (Baseline)

PID computes the control signal as:
```
u(t) = Kp·e(t) + Ki·∫e(t)dt + Kd·(de(t)/dt)
```
Where `e(t) = reference − actual`.

- **Proportional (Kp):** reacts to current error — bigger error, bigger correction
- **Integral (Ki):** eliminates steady-state error by accumulating past error over time
- **Derivative (Kd):** dampens overshoot by reacting to the *rate* of error change

**Why this is your baseline, not your novelty:** PID is 80+ years old and about as "prior art" as control theory gets. Its role here is purely as the fair comparison point — every claim about your event-triggered controller's savings is measured *relative to* this running continuously.

In Simulink, the built-in **PID Controller** block (Continuous library) implements this exact equation and updates its output every simulation timestep — i.e., continuously, which is exactly the behavior you're trying to reduce.

---

## 3. Event-Triggered Control (Your Novel Contribution)

**Core idea:** Instead of recomputing/sending a new control signal at every timestep, only do so when the tracking error has changed "enough" since the last update. Between triggers, the system just holds the last computed control value (Zero-Order Hold behavior).

**Triggering condition used in this model:**
```
if |e(t) − e_last_triggered| ≥ threshold:
    → recompute u using PID law, send it, update e_last_triggered
else:
    → hold previous u (do nothing)
```

This is a simplified version of the classic Tabuada-style relative-threshold event-triggering condition from event-triggered control literature. The full literature version often scales the threshold by the state magnitude (`σ·|x(t)|`); we use a fixed threshold here for simplicity, which is a reasonable simplification for a course-level project and still defensible as "adaptive" if the threshold itself is tuned/adjusted based on operating conditions (worth mentioning in your report if you want the "adaptive" framing to hold up).

**Why this saves computation/communication:** In a real networked/wireless robot, every control update means a computation cycle and (if networked) a radio transmission — both cost power and bandwidth. If the error barely changes for 200ms, sending 200 identical control updates is wasted work. Event-triggering only "spends" an update when it's actually needed.

**Why performance doesn't collapse:** As long as the threshold is small relative to the acceptable error tolerance, the system stays within an acceptable error band between triggers — it's a controlled trade-off (slightly worse tracking) for a large gain (far fewer updates), not a free lunch, and that trade-off curve is exactly what your results section should show.

**Implementation choice — MATLAB Function block instead of pure block diagram:**
Event-triggering logic involves conditional branching (if/else) and needs to "remember" the last-sent error value between timesteps (a persistent/memory variable). This is awkward to build from raw Simulink blocks (would need Memory blocks, Relational Operator blocks, Switch blocks, and Enabled Subsystems wired together) but trivial to write as a few lines of MATLAB code inside a single **MATLAB Function** block. This is a legitimate, standard Simulink practice, not a shortcut that undermines the project — MathWorks explicitly provides MATLAB Function blocks for exactly this kind of stateful logic.

---

## 4. Key Blocks and What They Do

| Block | Library | Role in this model |
|---|---|---|
| **Step / Signal Builder** | Sources | Generates the reference signal (desired speed/trajectory) both controllers try to track |
| **Sum** | Math Operations | Computes error = reference − actual output |
| **PID Controller** | Continuous | Baseline controller; recalculates output every timestep |
| **Transfer Fcn** | Continuous | Represents the DC motor plant (Phase 1) |
| **MATLAB Function** | User-Defined Functions | Houses the event-triggered controller logic (threshold check + PID math + memory of last state) |
| **Zero-Order Hold** | Discrete | Ensures the event-triggered branch's control signal stays constant between trigger events, rather than snapping/interpolating |
| **Scope** | Sinks | Real-time visual comparison while tuning |
| **To Workspace** | Sinks | Exports logged signals (error, control signal, trigger flag) to the MATLAB workspace as arrays, so you can compute RMSE, count triggers, and generate comparison plots after the sim runs |
| **Step (disturbance)** | Sources | Injects a mid-simulation disturbance to test robustness of both controllers |

---

## 5. What the Comparison Actually Proves

| Metric | What it demonstrates |
|---|---|
| RMSE (both branches, close in value) | Event-triggered control doesn't meaningfully sacrifice tracking accuracy |
| Number of triggers vs. total timesteps | The actual computation/communication savings — your headline number |
| Control effort (∫\|u\|dt) | Event-triggered controller isn't "cheating" by just applying less control effort overall |
| Recovery time after disturbance | Both controllers remain robust, not just efficient under ideal conditions |

This is the evidence base for your patent-style claims section — each claim should map to one of these logged, quantifiable results rather than a qualitative statement.