// ============================================================================
// POLÍTICA CEDAR: ATUALIZAÇÃO DE TAREFAS
// Serviço: AgentCore Policy / AgentCore Gateway
// ============================================================================
//
// Regra de Negócio: Permite a atualização do status e conteúdo de tarefas já existentes.

permit(
    principal,
    action == AgentCore::Action::"TaskApi___update_task",
    resource == AgentCore::Gateway::"<GATEWAY_ARN>"
);
