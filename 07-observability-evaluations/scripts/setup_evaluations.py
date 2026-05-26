"""Setup AgentCore Evaluations for the Aria agent.

Creates custom evaluators (ResponseQuality, ToolUsage) and online
evaluation configurations for continuous monitoring.

Run from notebook or command line:
    python setup_evaluations.py

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-evaluations.html
"""

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Modelo usado como "juiz" para avaliar as respostas do agente.
# O LLM-as-a-Judge é um padrão onde um modelo de IA avalia a qualidade
# das respostas de outro modelo, seguindo critérios definidos em um prompt.
EVALUATOR_MODEL_ID = os.environ.get(
    "EVALUATOR_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)

# Porcentagem de invocações que serão avaliadas automaticamente.
# 10% é um bom equilíbrio entre cobertura e custo (cada avaliação gera
# uma chamada extra ao modelo juiz).
SAMPLING_RATE = int(os.environ.get("SAMPLING_RATE", "10"))


def get_evaluator_definitions() -> list[dict]:
    """Return the evaluator definitions for the Aria agent.

    Each definition uses the create_evaluator API shape:
    - evaluatorName: unique name
    - description: what it evaluates
    - level: SESSION or TRACE
    - evaluatorConfig.llmAsAJudge: judge model config with instructions & rating scale
    """
    return [
        {
            # ResponseQuality: Avalia a qualidade geral das respostas da Aria.
            # Nível SESSION: analisa a conversa inteira (todas as mensagens da sessão).
            # Critérios: Precisão, completude, relevância, clareza e fundamentação.
            "evaluatorName": "ResponseQuality",
            "description": (
                "Evaluates helpfulness, accuracy, and completeness of agent "
                "responses across a conversation session."
            ),
            "level": "SESSION",
            "evaluatorConfig": {
                "llmAsAJudge": {
                    # Instruções para o modelo juiz: definem os critérios de avaliação
                    # e a escala de notas (1 a 5). O juiz lê toda a conversa,
                    # incluindo chamadas de ferramentas, e dá uma nota.
                    "instructions": """You are evaluating the quality of an AI assistant named Aria.

Examine the full conversation session including:
- The user's original request and any follow-up messages
- All tool calls the agent made (inputs and outputs)
- The agent's final response to the user

Score on this scale:
5 - Excellent: Fully addresses request with accurate, complete, well-structured information.
4 - Good: Mostly addresses request with minor gaps. All information accurate.
3 - Adequate: Partially addresses request with noticeable gaps.
2 - Poor: Fails to adequately address request. May contain inaccuracies.
1 - Unacceptable: Fundamentally wrong, hallucinated, or harmful.

Weigh: Accuracy, Completeness, Relevance, Clarity, Groundedness.
Provide brief justification before the numeric rating.""",
                    # Escala de notas numéricas com rótulos descritivos.
                    "ratingScale": {
                        "numerical": [
                            {"value": 1, "label": "Unacceptable", "definition": "Hallucinations or harmful content"},
                            {"value": 2, "label": "Poor", "definition": "Fails to address request"},
                            {"value": 3, "label": "Adequate", "definition": "Partially addresses with gaps"},
                            {"value": 4, "label": "Good", "definition": "Mostly complete and accurate"},
                            {"value": 5, "label": "Excellent", "definition": "Fully addresses with high quality"},
                        ],
                    },
                    "modelConfig": {
                        "bedrockEvaluatorModelConfig": {
                            "modelId": EVALUATOR_MODEL_ID,
                        }
                    },
                }
            },
        },
        {
            # ToolUsage: Avalia se o agente usou as ferramentas corretas e de forma eficiente.
            # Nível TRACE: analisa cada invocação individual (cada chamada ao agente).
            # Critérios: Seleção de ferramenta, qualidade dos inputs, eficiência,
            # completude e tratamento de erros.
            "evaluatorName": "ToolUsage",
            "description": (
                "Evaluates whether the agent selected and used appropriate tools "
                "efficiently for the given request."
            ),
            "level": "TRACE",
            "evaluatorConfig": {
                "llmAsAJudge": {
                    "instructions": """You are evaluating how well an AI assistant named Aria used its tools.

Available tools: code_interpreter, browser, memory, task_api (via Gateway).

Score on this scale:
5 - Optimal: Exactly the right tools, well-formed inputs, no unnecessary calls.
4 - Good: Correct tools with minor inefficiencies.
3 - Acceptable: Suboptimal but functional tool usage.
2 - Poor: Wrong tool selected or many unnecessary calls.
1 - Critical failure: Essential tools not used or severe misuse.

Weigh: Tool selection, Input quality, Efficiency, Completeness, Error handling.
Provide brief justification before the numeric rating.""",
                    "ratingScale": {
                        "numerical": [
                            {"value": 1, "label": "Critical failure", "definition": "Essential tools not used"},
                            {"value": 2, "label": "Poor", "definition": "Wrong tool or many unnecessary calls"},
                            {"value": 3, "label": "Acceptable", "definition": "Suboptimal but functional"},
                            {"value": 4, "label": "Good", "definition": "Correct tools with minor issues"},
                            {"value": 5, "label": "Optimal", "definition": "Exactly the right tools used efficiently"},
                        ],
                    },
                    "modelConfig": {
                        "bedrockEvaluatorModelConfig": {
                            "modelId": EVALUATOR_MODEL_ID,
                        }
                    },
                }
            },
        },
    ]


def setup_evaluations(
    agent_name: str = "aria_agent",
    sampling_rate: int | None = None,
) -> dict:
    """Create evaluators and online evaluation configs. Idempotent.

    Args:
        agent_name: Name of the agent in AgentCore Runtime.
        sampling_rate: Percentage of invocations to evaluate (default: 10).

    Returns:
        Dict with evaluator IDs and online eval names.
    """
    sampling_rate = sampling_rate or SAMPLING_RATE
    region = utils.get_region()
    cfn = utils.get_all_cfn_outputs()
    # Role IAM que o serviço de avaliação usa para acessar os logs do CloudWatch
    # e invocar o modelo juiz.
    evaluation_role_arn = cfn.get("EvaluationRoleArn")
    client = boto3.client("bedrock-agentcore-control", region_name=region)

    utils.print_banner("AgentCore Evaluations Setup")
    print(f"  Agent:         {agent_name}")
    print(f"  Judge model:   {EVALUATOR_MODEL_ID}")
    print(f"  Sampling rate: {sampling_rate}%")
    print()

    # --- Fase 1: Criar os avaliadores (Evaluators) ---
    # Avaliadores são definições reutilizáveis que dizem ao sistema COMO avaliar.
    # Cada um tem um prompt de instruções e uma escala de notas.
    print("Phase 1: Creating custom evaluators")
    evaluator_ids = {}

    for eval_def in get_evaluator_definitions():
        name = eval_def["evaluatorName"]

        # Verifica se já existe um avaliador com este nome (idempotência).
        existing_id = None
        try:
            resp = client.list_evaluators()
            for ev in resp.get("evaluators", []):
                if ev.get("evaluatorName") == name:
                    existing_id = ev["evaluatorId"]
                    break
        except ClientError:
            pass

        if existing_id:
            print(f"  ✅ {name} already exists: {existing_id}")
            evaluator_ids[name] = existing_id
            continue

        try:
            resp = client.create_evaluator(**eval_def)
            evaluator_ids[name] = resp["evaluatorId"]
            print(f"  ✅ Created {name}: {resp['evaluatorId']}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                print(f"  ✅ {name} already exists (conflict)")
            else:
                print(f"  ❌ Failed to create {name}: {e}")
                raise

    # --- Fase 2: Configurações de Avaliação Online ---
    # As avaliações online rodam automaticamente em produção:
    # - Pegam uma amostra das invocações do agente (sampling)
    # - Leem os traces do CloudWatch
    # - Enviam para o modelo juiz avaliar
    # - Armazenam os resultados para análise posterior
    print()
    print("Phase 2: Creating online evaluation configurations")

    # Grupo de logs do CloudWatch onde ficam os traces do AgentCore Runtime.
    log_group = f"/aws/bedrock-agentcore/runtimes/{agent_name}"

    online_evals = [
        {
            "name": "QualityMonitor",
            "evaluator_name": "ResponseQuality",
            "sampling_pct": sampling_rate,  # 10% das invocações
        },
        {
            "name": "ToolMonitor",
            "evaluator_name": "ToolUsage",
            "sampling_pct": max(sampling_rate // 2, 1),  # 5% (metade do sampling)
        },
    ]

    for oe in online_evals:
        name = oe["name"]

        # Verifica se já existe uma configuração com este nome.
        try:
            resp = client.list_online_evaluation_configs()
            existing = any(
                e.get("onlineEvaluationConfigName") == name
                for e in resp.get("onlineEvaluationConfigs", [])
            )
            if existing:
                print(f"  ✅ {name} already exists")
                continue
        except ClientError:
            pass

        evaluator_id = evaluator_ids.get(oe["evaluator_name"])
        if not evaluator_id:
            print(f"  ⚠ Skipping {name}: evaluator {oe['evaluator_name']} not found")
            continue

        try:
            client.create_online_evaluation_config(
                onlineEvaluationConfigName=name,
                description=f"Online evaluation for {oe['evaluator_name']}",
                rule={
                    # samplingConfig: Define a porcentagem de invocações que serão avaliadas.
                    # Um valor baixo (5-10%) mantém o custo sob controle enquanto
                    # fornece dados estatisticamente relevantes.
                    "samplingConfig": {
                        "samplingPercentage": float(oe["sampling_pct"]),
                    },
                },
                dataSourceConfig={
                    # CloudWatch Logs: Os traces do AgentCore Runtime são armazenados
                    # automaticamente neste grupo de logs. O avaliador lê esses traces
                    # para entender o que o agente fez durante cada invocação.
                    "cloudWatchLogs": {
                        "logGroupNames": [log_group],
                        "serviceNames": ["bedrock-agentcore"],
                    },
                },
                evaluators=[{"evaluatorId": evaluator_id}],
                evaluationExecutionRoleArn=evaluation_role_arn,
                # enableOnCreate: Ativa a avaliação imediatamente após a criação.
                enableOnCreate=True,
            )
            print(f"  ✅ Created {name} ({oe['sampling_pct']}% sampling)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                print(f"  ✅ {name} already exists (conflict)")
            else:
                print(f"  ❌ Failed to create {name}: {e}")

    # Salva as configurações para referência.
    config = {
        "evaluator_ids": evaluator_ids,
        "agent_name": agent_name,
        "sampling_rate": sampling_rate,
        "region": region,
    }
    utils.save_config("evaluations", config)

    print()
    utils.print_banner("Evaluations Setup Complete")
    print("  Evaluators:")
    for name, eid in evaluator_ids.items():
        print(f"    {name} → {eid}")
    print()
    print("  Online evaluations:")
    for oe in online_evals:
        print(f"    {oe['name']} ({oe['evaluator_name']}, {oe['sampling_pct']}%)")
    print()

    return config


if __name__ == "__main__":
    setup_evaluations()
