// ============================================================================
// POLÍTICA CEDAR CANÔNICA: DEFAULT DENY (ACESSO ZERO-TRUST)
// Serviço: AgentCore Policy / AgentCore Gateway
// Avaliação Matemática: O(n) estático sem dependência de loops ou estado externo
// ============================================================================
//
// FINALIDADE E BLINDAGEM CONTRA ALUCINAÇÕES DE LLM:
// Modelos de Linguagem de Grande Porte (LLMs) podem sofrer alucinações de ferramentas,
// tentando invocar endpoints não cadastrados, alterar recursos de terceiros ou forjar
// parâmetros de chamadas de API.
//
// A semântica "Default Deny" (Negação por Padrão) estabelece que qualquer requisição
// que não seja EXPLICITAMENTE PERMITIDA por uma regra "permit" será IMEDIATAMENTE
// REJEITADA com HTTP 403 Forbidden antes que o AgentCore Gateway repasse a chamada ao backend.
//
// AVALIAÇÃO DE TRÍPLA DIMENSÃO:
// 1. Principal: Identidade autenticada via JWT (sub / actor_id).
// 2. Action: Operação solicitada no gateway (ex: TaskApi___create_task).
// 3. Resource: O recurso alvo encapsulado pelo AgentCore Gateway.

forbidden(
    principal,
    action,
    resource
) unless {
    action in [
        AgentCore::Action::"TaskApi___list_tasks",
        AgentCore::Action::"TaskApi___create_task",
        AgentCore::Action::"TaskApi___update_task",
        AgentCore::Action::"TaskApi___delete_task"
    ]
};
