%% Should be run in the command window after running the simulation

settle_idx = tout > 1.5;   % ignore initial step transient
rmse_pid   = sqrt(mean((ref_log(settle_idx) - y_pid(settle_idx)).^2));
rmse_event = sqrt(mean((ref_log(settle_idx) - y_event(settle_idx)).^2));

num_triggers  = sum(trigger_log);
total_steps   = length(trigger_log);
savings_pct   = (1 - num_triggers/total_steps) * 100;

fprintf('PID RMSE (steady-state): %.4f\n', rmse_pid);
fprintf('Event-Triggered RMSE (steady-state): %.4f\n', rmse_event);
fprintf('Number of triggers: %d out of %d steps\n', num_triggers, total_steps);
fprintf('Update savings: %.1f%%\n', savings_pct);