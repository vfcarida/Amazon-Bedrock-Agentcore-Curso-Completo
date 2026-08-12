// ============================================================================
// POLÍTICA CEDAR: CRIAÇÃO CONTROLADA DE TAREFAS
// Serviço: AgentCore Policy / AgentCore Gateway
// ============================================================================
//
// Regra de Negócio: Permite a criação de tarefas no backend, mas proíbe que
// a tarefa seja criada diretamente com o status "completed".
// As tarefas devem ser iniciadas como "pending" ou "in_progress" e evoluídas
// via atualização (permit_update_task), impedindo desvios no fluxo de auditoria.

permit(
    principal,
    action == AgentCore::Action::"TaskApi___create_task",
    resource == AgentCore::Gateway::"<GATEWAY_ARN>"
) when {
    !(context.input has status && context.input.status == "completed")
};
