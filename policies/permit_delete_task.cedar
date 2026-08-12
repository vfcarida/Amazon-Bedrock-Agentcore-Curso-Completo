// ============================================================================
// POLÍTICA CEDAR: EXCLUSÃO DE TAREFAS
// Serviço: AgentCore Policy / AgentCore Gateway
// ============================================================================
//
// Regra de Negócio: Permite a exclusão de tarefas pelo proprietário.

permit(
    principal,
    action == AgentCore::Action::"TaskApi___delete_task",
    resource == AgentCore::Gateway::"<GATEWAY_ARN>"
);
