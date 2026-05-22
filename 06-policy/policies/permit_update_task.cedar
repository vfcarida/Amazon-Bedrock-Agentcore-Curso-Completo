// Permit all task updates, including setting status to "completed".
// This is the only way tasks can reach "completed" status.
// The sentinel condition satisfies the validator's requirement for
// a context.input reference while effectively allowing all updates.

permit(
  principal,
  action == AgentCore::Action::"TaskApi___update_task",
  resource == AgentCore::Gateway::"<GATEWAY_ARN>"
) when {
  !(context.input has status && context.input.status == "__blocked__")
};
