import json
import os

mod00_translations = {
    "# Module 0: Prerequisites & Environment Setup": "# Módulo 0: Pré-requisitos & Configuração do Ambiente",
    "## Welcome to the Amazon Bedrock AgentCore Workshop!": "## Bem-vindo ao Laboratório Prático do Amazon Bedrock AgentCore!",
    "In this workshop, you will build **Aria** -- a production-grade AI assistant powered by **Amazon Bedrock AgentCore**. Over the course of 9 modules, you will go from zero to a fully deployed, secure, observable AI agent.": "Neste curso prático, você vai construir a **Aria** -- uma assistente de inteligência artificial pronta para produção usando o **Amazon Bedrock AgentCore**. Ao longo de 9 módulos, você vai do zero até ter uma IA totalmente no ar, segura e com métricas de observabilidade.",
    "### What you will build": "### O que você vai construir",
    "Aria is not a toy demo. By the end of this workshop, your assistant will:": "A Aria não é apenas um projetinho de teste. Até o final deste curso, sua assistente vai:",
    "- **Run in AgentCore Runtime** -- deployed as a managed, scalable agent endpoint": "- **Rodar no AgentCore Runtime** -- hospedada como um endpoint gerenciado e escalável",
    "- **Use Code Interpreter & Browser tools** -- to execute code and browse the web on behalf of users": "- **Usar o Interpretador de Código e o Navegador Web** -- para rodar código Python e navegar na internet por conta própria",
    "- **Remember conversations** -- with AgentCore Memory for persistent, cross-session context": "- **Lembrar das conversas** -- usando o AgentCore Memory para manter o contexto mesmo depois de fechar a sessão",
    "- **Expose a secure API** -- through AgentCore Gateway with Identity-based authentication": "- **Ter uma API segura** -- acessível pelo AgentCore Gateway com autenticação baseada em identidade (JWT)",
    "- **Enforce fine-grained policies** -- using Cedar policies via AgentCore Policy": "- **Respeitar regras de negócio** -- aplicando bloqueios rígidos usando políticas Cedar",
    "- **Emit traces and metrics** -- through AgentCore Observability": "- **Gerar traces e métricas** -- acompanhando tudo pelo AgentCore Observabilidade",
    "- **Pass quality checks** -- validated by AgentCore Evaluations": "- **Passar por avaliações automáticas** -- sendo testada por outras IAs usando o AgentCore Avaliações",
    "### Workshop modules": "### Módulos do Curso",
    "| Module | Topic |": "| Módulo | Tópico |",
    "|--------|-------|": "|--------|-------|",
    "| **00** | Prerequisites & Environment Setup (this module) |": "| **00** | Pré-requisitos & Configuração do Ambiente (este módulo) |",
    "| **01** | Introduction to Amazon Bedrock AgentCore |": "| **01** | Introdução ao Amazon Bedrock AgentCore |",
    "| **02** | Deploy Your First Agent to Runtime |": "| **02** | Fazendo o Deploy do seu Primeiro Agente |",
    "| **03** | Add Code Interpreter & Browser Tools |": "| **03** | Adicionando Ferramentas: Código e Navegador |",
    "| **04** | Add Persistent Memory |": "| **04** | Dando Memória Persistente para o Agente |",
    "| **05** | Connect Gateway & Identity |": "| **05** | Conectando o Gateway & Autenticação |",
    "| **06** | Enforce Cedar Policies |": "| **06** | Bloqueios e Regras com Políticas Cedar |",
    "| **07** | Observability & Evaluations |": "| **07** | Observabilidade e Avaliações de Qualidade |",
    "| **08** | Full Production Deployment |": "| **08** | Subindo Tudo em Produção (Frontend) |",
    "Let's start by verifying that your environment is ready.": "Vamos começar checando se o seu ambiente está pronto.",
    "## 1. Environment Verification": "## 1. Verificando o Ambiente",
    "We need to confirm that the required tools are installed and that your AWS credentials are configured correctly.": "Precisamos confirmar se as ferramentas estão instaladas e se o seu acesso na AWS está configurado certinho.",
    "### 1.1 Python version": "### 1.1 Versão do Python",
    "This workshop requires **Python 3.12**.": "Este curso exige o **Python 3.12**.",
    "### 1.2 AWS CLI": "### 1.2 AWS CLI",
    "The AWS CLI is used for various operations throughout the workshop.": "A linha de comando da AWS (CLI) é usada para vários comandos durante o laboratório.",
    "### 1.3 AWS CDK": "### 1.3 AWS CDK",
    "The AWS CDK is used in the deployment modules.": "O AWS CDK vai ser usado nos módulos de deploy.",
    "### 1.4 AWS Credentials": "### 1.4 Credenciais da AWS",
    "Verify that your AWS credentials are valid and that you can make API calls.": "Verifique se suas credenciais da AWS estão válidas e se consegue bater na API.",
    "## 1.5 X-Ray Transaction Search Check": "## 1.5 Checando o X-Ray",
    "The prerequisites CloudFormation stack enables **X-Ray Transaction Search** by default. This is an account-level setting (only one configuration is allowed per account per region), and it is required for the observability module later in the workshop.": "A pilha de pré-requisitos habilita o **X-Ray Transaction Search** por padrão. Essa configuração só pode ser ativada uma vez por conta na mesma região, e vamos precisar disso mais pra frente no módulo de métricas.",
    "If your account already has Transaction Search enabled, the stack deployment will fail unless you set the `EnableTransactionSearch` parameter to `false`. Run the cell below to check your account's current status **before deploying the stack**.": "Se a sua conta da AWS já tem isso ligado, o CloudFormation pode dar erro. Rode a célula abaixo para conferir o status da sua conta **antes de rodar o deploy**.",
    "## 2. CloudFormation Stack Verification": "## 2. Verificando o CloudFormation",
    "If you followed the README instructions, you deployed the prerequisites CloudFormation stack using `aws cloudformation deploy`. Let's verify that the stack completed successfully and that all required outputs are available.": "Se você seguiu o README, já rodou o deploy do CloudFormation. Vamos verificar se tudo terminou bem e se as saídas (outputs) estão prontas.",
    "## 3. What Was Provisioned": "## 3. O Que Foi Criado?",
    "The CloudFormation stack created the following resources that Aria will use throughout the workshop:": "O CloudFormation acabou de criar os seguintes recursos na AWS para a Aria usar no curso:",
    "### Authentication & Identity": "### Autenticação & Identidade",
    "- **Amazon Cognito User Pool** -- Manages user accounts for Aria's end users": "- **Amazon Cognito User Pool** -- Gerencia as contas de quem usar a Aria",
    "- **Cognito App Client** -- Allows Aria's frontend to authenticate users": "- **Cognito App Client** -- Deixa o frontend da Aria fazer o login da galera",
    "- **Cognito Domain** -- Provides hosted UI endpoints for sign-in flows": "- **Cognito Domain** -- Cria as telas prontas de login e senha",
    "### Data & APIs": "### Dados & APIs",
    "- **Amazon DynamoDB Table** -- Stores tasks that Aria can create, read, update, and delete": "- **Amazon DynamoDB Table** -- Banco de dados onde a Aria vai ler, criar e apagar tarefas",
    "- **AWS Lambda Function** -- Implements the Task API business logic": "- **AWS Lambda Function** -- Onde fica o código da API de Tarefas",
    "- **Amazon API Gateway REST API** -- Exposes the Task API as a secure HTTP endpoint": "- **Amazon API Gateway REST API** -- Cria um endpoint seguro na web para a API de Tarefas",
    "### Storage": "### Armazenamento",
    "- **Amazon S3 Bucket** -- Stores artifacts, logs, and other files generated during the workshop": "- **Amazon S3 Bucket** -- Guarda nossos arquivos, logs e o frontend do curso",
    "### IAM Roles": "### Permissões IAM",
    "- **Runtime Execution Role** -- Grants Aria's agent the permissions it needs when running in AgentCore Runtime": "- **Runtime Execution Role** -- Dá as permissões pro Agente rodar no AgentCore Runtime",
    "- **Gateway Execution Role** -- Grants AgentCore Gateway the permissions to invoke and manage agent endpoints": "- **Gateway Execution Role** -- Dá permissão pro Gateway acessar nosso agente",
    "### Observability": "### Observabilidade",
    "- **X-Ray Transaction Search** -- Enables distributed trace indexing so you can search and analyze agent traces in the observability module. This is an account-level setting that indexes 100% of traces and takes approximately 10 minutes to become active. If your account already had Transaction Search enabled, this resource was skipped (controlled by the `EnableTransactionSearch` stack parameter).": "- **X-Ray Transaction Search** -- Habilita a indexação de logs pra gente poder investigar depois. Isso demora uns 10 minutinhos pra ficar ativo.",
    "- **CloudWatch Logs Resource Policy** -- Grants X-Ray permission to write trace spans to CloudWatch Logs (`aws/spans` log group)": "- **CloudWatch Logs Resource Policy** -- Dá permissão pro X-Ray salvar os rastros lá no CloudWatch.",
    "These resources form the backbone of Aria's environment. In the modules ahead, you will connect Aria to each of them.": "Isso tudo forma a espinha dorsal do ambiente da Aria. Mais pra frente, vamos conectar a Aria em tudo isso.",
    "## 4. Mark Module Complete": "## 4. Marcar o Módulo como Concluído",
    "Everything checks out! Let's record your progress.": "Tudo certo! Vamos salvar o seu progresso.",
    "**Next up: [Module 1 -- Introduction to Amazon Bedrock AgentCore](../01-introduction/notebook.ipynb)**": "**Próximo Passo: [Módulo 1 -- Introdução ao Amazon Bedrock AgentCore](../01-introduction/notebook.ipynb)**"
}

def translate_notebook_00():
    nb_path = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo\00-prerequisites\notebook.ipynb"
    
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb_data = json.load(f)
        
    # Translate markdown cells
    for cell in nb_data.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            new_source = []
            for line in cell.get('source', []):
                new_line = line
                # Simple string replacement for each key
                for en_text, pt_text in mod00_translations.items():
                    if en_text in new_line:
                        new_line = new_line.replace(en_text, pt_text)
                new_source.append(new_line)
            cell['source'] = new_source
            
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb_data, f, indent=2, ensure_ascii=False)
        
    print("Module 00 translated.")

if __name__ == '__main__':
    translate_notebook_00()
