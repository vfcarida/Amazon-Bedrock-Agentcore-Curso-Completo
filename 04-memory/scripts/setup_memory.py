"""Setup AgentCore Memory for the Aria agent.

Creates a Memory resource with three long-term memory strategies:
- SessionSummarizer: Conversation session summaries
- PreferenceLearner: User preference extraction
- FactExtractor: Semantic fact extraction

Run from notebook or command line:
    python setup_memory.py

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-memory.html
"""

import sys
import os

# Permite importar arquivos da pasta shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError


def create_memory(region: str | None = None) -> dict:
    """Create an AgentCore Memory resource. Idempotent.

    Returns:
        Dict with memory_id, region, and strategies.
    """
    region = region or utils.get_region()
    # Cliente da API de controle do AgentCore — usado para criar e gerenciar recursos.
    client = boto3.client("bedrock-agentcore-control", region_name=region)

    utils.print_banner("Creating AgentCore Memory")
    print()

    # --- Passo 1: Verificar se o recurso de memória já existe na AWS ---
    # Faz uma busca por memórias que comecem com "AriaMemory".
    # Se encontrar uma que já esteja ACTIVE ou READY, reutiliza ela (idempotência).
    try:
        paginator = client.get_paginator("list_memories")
        for page in paginator.paginate():
            for mem in page.get("memories", page.get("items", [])):
                if mem["id"].startswith("AriaMemory"):
                    memory_id = mem["id"]
                    detail = client.get_memory(memoryId=memory_id)
                    memory = detail.get("memory", detail)
                    if memory.get("status") in ("ACTIVE", "READY"):
                        print(f"✅ AriaMemory already exists: {memory_id}")
                        config = {"memory_id": memory_id, "region": region}
                        utils.save_config("memory", config)
                        return config
    except ClientError:
        pass

    # --- Passo 2: Criar uma nova memória com 3 estratégias de LTM (Long-Term Memory) ---
    # Cada estratégia extrai um tipo diferente de informação das conversas:
    print("Creating Memory resource with LTM strategies...")
    try:
        resp = client.create_memory(
            name="AriaMemory",
            description=(
                "Memory for Aria personal assistant - supports conversation "
                "persistence and long-term user knowledge"
            ),
            # eventExpiryDuration: Tempo (em dias) que os eventos brutos de conversa
            # ficam armazenados antes de serem apagados. As memórias extraídas
            # (resumos, preferências, fatos) persistem indefinidamente.
            eventExpiryDuration=90,
            memoryStrategies=[
                {
                    # SessionSummarizer: Ao final de cada sessão, gera um resumo
                    # da conversa. Útil para dar contexto rápido em sessões futuras.
                    # Namespace: /summaries/{actorId}/{sessionId}
                    "summaryMemoryStrategy": {
                        "name": "SessionSummarizer",
                        "description": "Summarizes conversation sessions for quick context retrieval",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"],
                    }
                },
                {
                    # PreferenceLearner: Extrai preferências do usuário mencionadas
                    # durante a conversa (ex: "Eu prefiro Python", "Gosto de café").
                    # Namespace: /preferences/{actorId}
                    "userPreferenceMemoryStrategy": {
                        "name": "PreferenceLearner",
                        "description": "Learns and stores user preferences across sessions",
                        "namespaces": ["/preferences/{actorId}"],
                    }
                },
                {
                    # FactExtractor: Extrai fatos sobre o usuário (ex: "Trabalho na
                    # empresa X", "Moro em São Paulo"). Usa busca semântica para
                    # encontrar fatos relevantes em conversas futuras.
                    # Namespace: /facts/{actorId}
                    "semanticMemoryStrategy": {
                        "name": "FactExtractor",
                        "description": "Extracts and stores factual information from conversations",
                        "namespaces": ["/facts/{actorId}"],
                    }
                },
            ],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("⚠ AriaMemory already exists but wasn't found in listing.")
            print("  This can happen due to eventual consistency.")
            print("  Provide the memory ID manually if needed.")
            raise
        raise

    memory_id = resp["memory"]["id"]
    print(f"Memory ID: {memory_id}")

    # --- Passo 3: Aguardar até que o recurso esteja ativo ---
    # A criação é assíncrona — precisamos ficar verificando o status até chegar em ACTIVE.
    print("Waiting for memory to become ACTIVE...")
    utils.poll_until(
        describe_fn=lambda: client.get_memory(memoryId=memory_id).get("memory", {}),
        target_statuses={"ACTIVE"},
        label="Memory",
        timeout=300,
    )

    # --- Passo 4: Salvar a configuração para os próximos módulos usarem ---
    config = {
        "memory_id": memory_id,
        "region": region,
        "strategies": ["SessionSummarizer", "PreferenceLearner", "FactExtractor"],
    }
    utils.save_config("memory", config)

    print()
    utils.print_banner("Memory Setup Complete")
    print(f"  Memory ID: {memory_id}")
    print()
    print("  Strategies:")
    print("    - SessionSummarizer → /summaries/{actorId}/{sessionId}")
    print("    - PreferenceLearner → /preferences/{actorId}")
    print("    - FactExtractor     → /facts/{actorId}")
    print()
    # Mostra o comando para definir a variável de ambiente manualmente (útil para debug)
    print(f"  export MEMORY_ID={memory_id}")
    print()

    return config


if __name__ == "__main__":
    create_memory()
