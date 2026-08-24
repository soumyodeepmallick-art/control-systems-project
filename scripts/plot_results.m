%% Should be run in the command window after running the simulation

%% Plot 1 — Tracking performance comparison
figure('Name','Controller Comparison');
subplot(3,1,1);
plot(tout, ref_log, 'k--', 'LineWidth', 1.2); hold on;
plot(tout, y_pid, 'b-', 'LineWidth', 1.2);
plot(tout, y_event, 'r-.', 'LineWidth', 1.2);
legend('Reference','Continuous PID','Event-Triggered PID','Location','SouthEast');
xlabel('Time (s)'); ylabel('Output (y)');
title('System Tracking Performance Comparison');
grid on;

%% Plot 2 — Control effort comparison
subplot(3,1,2);
plot(tout, u_pid, 'b-', 'LineWidth', 1); hold on;
plot(tout, u_event, 'r-.', 'LineWidth', 1);
legend('u_{PID}','u_{Event}');
xlabel('Time (s)'); ylabel('Control Signal (u)');
title('Control Effort Comparison');
grid on;

%% Plot 3 — Trigger events over time (this is your "savings" visual)
subplot(3,1,3);
stem(tout, trigger_log, 'r', 'Marker', 'none');
xlabel('Time (s)'); ylabel('Trigger (1/0)');
title(sprintf('Event Trigger Instances (%.1f%% fewer updates than PID)', savings_pct));
ylim([-0.2 1.2]);
grid on;