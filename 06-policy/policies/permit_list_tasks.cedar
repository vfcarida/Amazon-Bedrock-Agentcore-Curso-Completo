// Permit listing tasks.
// Blocks listing only completed tasks (optional status filter).
//
// The condition references the optional 'status' query parameter
// from the list_tasks tool schema.

permit(
  principal,
  action == AgentCore::Action::"TaskApi___list_tasks",
  resource == AgentCore::Gateway::"<GATEWAY_ARN>"
) when {
  !(context.input has status && context.input.status == "completed")
};
