// Permit creating tasks, but NOT with status "completed".
//
// Business rule: Tasks must start as "pending" or "in_progress".
// They can only reach "completed" via an update (permit_update_task).
// This prevents the agent from creating pre-completed tasks that
// would bypass workflow tracking.

permit(
  principal,
  action == AgentCore::Action::"TaskApi___create_task",
  resource == AgentCore::Gateway::"<GATEWAY_ARN>"
) when {
  !(context.input has status && context.input.status == "completed")
};
