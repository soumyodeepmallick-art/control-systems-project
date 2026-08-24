# Event-Triggered PID Control: Key Issues & Solutions

---

## Key Issues Encountered & Resolved

### 1. Simulink Output Port Mismatch
* **Error:** `Unable to register number of outputs`
* **Cause:** Modifying the function header to `function [u, trigger] = ...` created a desynchronization in the MATLAB Function block's symbol manager, which retained an unassigned output symbol (`data`) assigned to Port 3.
* **Resolution:** Deleted the orphaned `data` output entry from the Symbols Pane / Symbol Manager to realign the internal symbol table with the function header.

### 2. Sample Time & Continuous Syntax Error
* **Error:** Persistent variable allocation or discrete sample rate warnings.
* **Cause:** MATLAB Function blocks default to inherited/continuous sample time (`-1`), which prohibits using digital state memory constructs like `persistent` variables.
* **Resolution:** Configured an explicit discrete sample time (`0.001` s) in the block properties and placed a Zero-Order Hold (ZOH) block on the error input path.

### 3. Data Access & Type Conversion Failures
* **Error:** `Unable to resolve the name 'y_pid.Data'` or `Conversion to double from timeseries is not possible`
* **Cause:** Workspace outputs were exported either wrapped inside an `out` simulation object, saved as flat double matrices, or kept as intact `timeseries` objects that couldn't be directly cast with `double()`.
* **Resolution:** Implemented conditional extraction (`if exist('out', 'var')`) to extract the raw `.Data` and `.Time` arrays prior to casting them into 1D double column vectors.

---

## Baseline Simulation Enhancements

* **Realistic Baseline Setup:** Placed a **Zero-Order Hold (ZOH)** block ($T_s = 0.02\text{ s}$) on the conventional PID path to limit updates to a realistic **50 Hz** digital controller rate rather than evaluating at every raw solver time step.
* **Disturbance Rejection Testing:** Introduced a step disturbance at $t = 10\text{ s}$ to evaluate dynamic trigger bursts and transient recovery under active load changes.
* **Steady-State Evaluation Window:** Filtered out the initial step transient phase ($t < 1.5\text{ s}$) when computing Root Mean Square Error (RMSE) to accurately reflect true steady-state tracking performance.