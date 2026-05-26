"""Script para adicionar comentários em Português nos notebooks do curso.

Este script processa cada notebook.ipynb do repositório e adiciona
comentários explicativos em português nas células de código.

Uso:
    python add_notebook_comments.py

O script cria backups automáticos antes de modificar cada notebook.
"""

import json
import shutil
import sys
import os
from pathlib import Path

# Corrige problemas de encoding no Windows (console cp1252 vs UTF-8)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Diretório raiz do repositório
REPO_DIR = Path(__file__).resolve().parent

# Mapeamento de comentários em português para cada notebook.
# Cada entrada é: {módulo: {padrão_de_código: comentário_em_português}}
# Os comentários são adicionados ACIMA da linha que contém o padrão.
NOTEBOOK_COMMENTS = {
    "00-prerequisites": {
        # --- Comentários para o notebook de pré-requisitos ---
        "import boto3": "# Importa o SDK da AWS para Python — usado para interagir com todos os serviços da AWS.",
        "get_caller_identity": "# Verifica qual conta e usuário da AWS estão configurados no momento.",
        "describe_stacks": "# Consulta o CloudFormation para verificar se a stack de pré-requisitos foi criada com sucesso.",
        "ensure_ready": "# Função mágica que verifica se todos os pré-requisitos do módulo estão prontos.",
        "print_banner": "# Exibe um banner formatado no terminal para facilitar a visualização.",
        "check_prerequisites": "# Verifica se a stack do CloudFormation foi criada e lista os recursos disponíveis.",
        "from shared": "# Importa as ferramentas compartilhadas do workshop (funções auxiliares).",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "cfn_outputs": "# Recupera as saídas (outputs) do CloudFormation — contêm IDs e ARNs dos recursos criados.",
        "admin_create_user": "# Cria um usuário de teste no Cognito para usar durante o workshop.",
        "admin_set_user_password": "# Define a senha do usuário de teste como permanente (sem necessidade de trocar no primeiro login).",
        "initiate_auth": "# Autentica o usuário de teste e obtém o token JWT (necessário para os módulos 05+).",
        "list_tables": "# Lista as tabelas do DynamoDB para verificar se a tabela de tarefas foi criada.",
    },
    "01-introduction": {
        # --- Comentários para o notebook de introdução ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se todos os pré-requisitos deste módulo estão prontos.",
        "bedrock-agentcore": "# Cliente do AgentCore — usado para gerenciar Runtimes, Gateways, Memória, etc.",
        "list_agent_runtimes": "# Lista todos os Runtimes de agentes criados na sua conta.",
        "list_memories": "# Lista todos os recursos de memória do AgentCore na sua conta.",
        "list_gateways": "# Lista todos os Gateways MCP criados na sua conta.",
        "print_banner": "# Exibe um banner formatado no terminal.",
    },
    "02-runtime": {
        # --- Comentários para o notebook do Runtime ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se todos os pré-requisitos deste módulo estão prontos.",
        "deploy_agent": "# Módulo que empacota o código do agente e faz o deploy no AgentCore Runtime.",
        "deploy(": "# Faz o deploy do agente: empacota o código, sobe pro S3, e cria/atualiza o Runtime.",
        "test_agent": "# Módulo para testar o agente depois do deploy — envia mensagens e mostra respostas.",
        "invoke(": "# Envia uma mensagem para o agente e mostra a resposta em streaming.",
        "agent_dir": "# Caminho para o diretório com o código do agente (main.py + requirements.txt).",
        "stream_async": "# Streaming assíncrono: o agente vai respondendo em tempo real, token por token.",
        "clean_start=True": "# clean_start: Apaga qualquer Runtime antigo antes de criar um novo (evita conflitos).",
    },
    "03-tools": {
        # --- Comentários para o notebook de Ferramentas ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se o Runtime do módulo anterior está rodando (necessário para este módulo).",
        "deploy_agent": "# Módulo de deploy — vai atualizar o Runtime com o novo código que inclui ferramentas.",
        "deploy(": "# Faz o deploy da V2 do agente (agora com Code Interpreter e Browser Tool).",
        "test_agent": "# Módulo para testar o agente com as novas ferramentas.",
        "invoke(": "# Testa o agente enviando prompts que devem acionar as ferramentas.",
        "code_interpreter": "# Interpretador de Código: executa Python em sandbox para cálculos, gráficos e análises.",
        "browser": "# Navegador Web: abre um navegador headless para buscar informações na internet.",
    },
    "04-memory": {
        # --- Comentários para o notebook de Memória ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se o Runtime está rodando (necessário para este módulo).",
        "setup_memory": "# Script que cria o recurso de Memória no AgentCore com 3 estratégias LTM.",
        "create_memory": "# Cria o recurso AriaMemory com as estratégias: SessionSummarizer, PreferenceLearner, FactExtractor.",
        "deploy_agent": "# Módulo de deploy — vai atualizar o Runtime com o código V3 (com memória).",
        "deploy(": "# Faz o deploy da V3 do agente (agora com memória persistente entre sessões).",
        "MEMORY_ID": "# ID do recurso de memória — passado como variável de ambiente para o Runtime.",
        "test_agent": "# Módulo para testar se a memória está funcionando.",
        "invoke(": "# Testa o agente — ele deve lembrar de informações de mensagens anteriores.",
        "session_id": "# ID da sessão — a memória agrupa conversas por sessão e por usuário.",
    },
    "05-gateway-identity": {
        # --- Comentários para o notebook de Gateway e Identidade ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se Runtime e Memória estão prontos (necessários para este módulo).",
        "setup_gateway": "# Script que cria o Gateway MCP e conecta a API de Tarefas como target.",
        "create_gateway": "# Cria o Gateway com autenticação JWT e adiciona a API de Tarefas.",
        "deploy_agent": "# Módulo de deploy — vai atualizar o Runtime com o código V4 (com Gateway).",
        "deploy(": "# Faz o deploy da V4 do agente (agora com conexão ao Gateway e repasse de JWT).",
        "GATEWAY_ENDPOINT": "# URL do Gateway MCP — passada como variável de ambiente para o Runtime.",
        "get_test_token": "# Obtém um token JWT de teste do Cognito para testar a autenticação.",
        "jwt_token": "# Token JWT do usuário — necessário para que o Gateway identifique o usuário.",
        "test_agent": "# Módulo para testar o agente com autenticação JWT.",
        "invoke(": "# Testa o agente com JWT — ele deve conseguir criar/listar tarefas.",
        "discovery_url": "# URL de descoberta OIDC do Cognito — usada pelo Runtime para validar tokens JWT.",
        "client_id": "# ID do app client do Cognito — usado para validar a audiência do JWT.",
    },
    "06-policy": {
        # --- Comentários para o notebook de Políticas ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se Runtime, Memória e Gateway estão prontos.",
        "setup_policy": "# Script que cria o Policy Engine com regras Cedar e anexa ao Gateway.",
        "create_policy_engine": "# Cria o motor de políticas Cedar e define as regras de acesso.",
        "test_agent": "# Módulo para testar se as políticas estão bloqueando ações indevidas.",
        "invoke(": "# Testa o agente — tarefas com status 'completed' devem ser bloqueadas na criação.",
        "cedar": "# Política Cedar: linguagem declarativa de autorização criada pela AWS.",
        "ENFORCE": "# Modo ENFORCE: as políticas são avaliadas E bloqueiam ações não permitidas.",
    },
    "07-observability-evaluations": {
        # --- Comentários para o notebook de Observabilidade ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se Runtime, Memória, Gateway e Política estão prontos.",
        "setup_evaluations": "# Script que cria os avaliadores (LLM-as-a-Judge) e configura avaliação online.",
        "deploy_agent": "# Módulo de deploy — vai atualizar o Runtime com o código V5 (produção).",
        "deploy(": "# Faz o deploy da V5 do agente (versão final com tratamento de erros e tracing).",
        "test_agent": "# Módulo para testar o agente final com todas as funcionalidades.",
        "invoke(": "# Testa o agente V5 — agora com traces visíveis no CloudWatch/X-Ray.",
        "opentelemetry": "# OpenTelemetry: framework de observabilidade que coleta traces automaticamente.",
        "ResponseQuality": "# Avaliador de qualidade: usa um LLM para dar notas (1-5) para as respostas do agente.",
        "ToolUsage": "# Avaliador de ferramentas: verifica se o agente usou as ferramentas certas e de forma eficiente.",
        "sampling": "# Amostragem: apenas uma porcentagem das invocações é avaliada (controla custos).",
        "cloudwatch": "# CloudWatch: serviço da AWS para logs, métricas e dashboards.",
    },
    "08-full-deployment": {
        # --- Comentários para o notebook de Deploy Completo ---
        "from shared": "# Importa as ferramentas compartilhadas do workshop.",
        "sys.path": "# Adiciona o diretório pai ao PATH do Python para permitir imports relativos.",
        "ensure_ready": "# Verifica se TODOS os serviços do AgentCore estão prontos.",
        "cdk": "# AWS CDK (Cloud Development Kit): framework para definir infraestrutura como código.",
        "frontend": "# Código do frontend web (interface do usuário) da Aria.",
        "cloudfront": "# CloudFront: CDN da AWS que serve o frontend com baixa latência globalmente.",
        "npm run build": "# Compila o frontend React/Next.js para produção.",
        "cdk deploy": "# Faz o deploy da infraestrutura do frontend (S3 + CloudFront).",
        "delete-stack": "# Comando para apagar a stack do CloudFormation (limpeza de recursos).",
        "cleanup": "# Limpeza: remove todos os recursos criados durante o workshop para evitar cobranças.",
    },
}


def add_comments_to_notebook(notebook_path: Path, module_name: str) -> bool:
    """Adiciona comentários em português a um notebook.

    Args:
        notebook_path: Caminho para o arquivo .ipynb
        module_name: Nome do módulo (ex: "02-runtime")

    Returns:
        True se o notebook foi modificado, False caso contrário.
    """
    comments = NOTEBOOK_COMMENTS.get(module_name, {})
    if not comments:
        print(f"  ⚠ Nenhum comentário definido para {module_name}")
        return False

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    modified = False

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        source_lines = cell.get("source", [])
        new_source = []

        for line in source_lines:
            line_stripped = line.strip()

            # Verifica se algum padrão de código corresponde a esta linha.
            # Se sim, adiciona o comentário em português ACIMA da linha.
            for pattern, comment in comments.items():
                if pattern in line_stripped:
                    # Verifica se o comentário já não foi adicionado antes.
                    if new_source and new_source[-1].strip() == comment:
                        break
                    # Não adicionar se a própria linha já é um comentário
                    if line_stripped.startswith("#"):
                        break
                    # Detecta a indentação da linha atual para manter a formatação.
                    indent = len(line) - len(line.lstrip())
                    indent_str = " " * indent
                    new_source.append(f"{indent_str}{comment}\n")
                    modified = True
                    break

            new_source.append(line)

        cell["source"] = new_source

    if modified:
        # Cria backup antes de modificar
        backup_path = notebook_path.with_suffix(".ipynb.bak")
        shutil.copy2(notebook_path, backup_path)

        with open(notebook_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
            f.write("\n")

        print(f"  ✅ {module_name}/notebook.ipynb — comentários adicionados (backup: .ipynb.bak)")
    else:
        print(f"  ℹ️  {module_name}/notebook.ipynb — nenhuma alteração necessária")

    return modified


def main():
    """Processa todos os notebooks do repositório."""
    print("=" * 60)
    print("  Adicionando Comentários em Português aos Notebooks")
    print("=" * 60)
    print()

    modules = [
        "00-prerequisites",
        "01-introduction",
        "02-runtime",
        "03-tools",
        "04-memory",
        "05-gateway-identity",
        "06-policy",
        "07-observability-evaluations",
        "08-full-deployment",
    ]

    total_modified = 0
    for module in modules:
        notebook_path = REPO_DIR / module / "notebook.ipynb"
        if notebook_path.exists():
            if add_comments_to_notebook(notebook_path, module):
                total_modified += 1
        else:
            print(f"  ⚠ {module}/notebook.ipynb não encontrado")

    print()
    print(f"Total: {total_modified} notebooks modificados")
    print()
    print("IMPORTANTE: Abra cada notebook no VS Code e verifique se os")
    print("comentários foram adicionados corretamente nas células de código.")
    print()
    print("Para desfazer as alterações em um notebook específico:")
    print("  cp <módulo>/notebook.ipynb.bak <módulo>/notebook.ipynb")


if __name__ == "__main__":
    main()
