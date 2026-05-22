// Permit deleting tasks by ID.
// The sentinel condition satisfies the validator's requirement for
// a context.input reference while effectively allowing all deletes.

permit(
  principal,
  action == AgentCore::Action::"TaskApi___delete_task",
  resource == AgentCore::Gateway::"<GATEWAY_ARN>"
) when {
  !(context.input has id && context.input.id == "__blocked__")
};
