// ============================================================================
// POLÍTICA CEDAR: LISTAGEM DE TAREFAS
// Serviço: AgentCore Policy / AgentCore Gateway
// ============================================================================
//
// Regra de Negócio: Permite que usuários autenticados via JWT consultem a lista
// de tarefas pertencentes à sua identidade (actor_id).

permit(
    principal,
    action == AgentCore::Action::"TaskApi___list_tasks",
    resource == AgentCore::Gateway::"<GATEWAY_ARN>"
);
