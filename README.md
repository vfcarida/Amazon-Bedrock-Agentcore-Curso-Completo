# Curso Prático: Amazon Bedrock AgentCore

Neste laboratório, você vai construir a **Aria**, uma assistente virtual com inteligência artificial pronta para o mundo real, usando os 9 serviços do **Amazon Bedrock AgentCore**. No final deste curso, você terá criado do zero uma assistente hospedada na nuvem que responde em tempo real (streaming), lembra das conversas passadas, executa códigos em Python, navega na web, e se conecta com APIs. Tudo isso enquanto respeita regras rígidas de segurança, gera métricas e é avaliada automaticamente!

![Aria](images/aria-home.png)

## O Que Você Vai Construir

**Aria** é uma assistente de IA pessoal onde os usuários podem:

- **Fazer Login:** Acesso seguro via Amazon Cognito.
- **Conversar:** Respostas fluidas e rápidas geradas em tempo real.
- **Rodar Códigos:** Pedir para a Aria executar scripts em Python para fazer cálculos matemáticos, análise de dados ou gerar gráficos.
- **Navegar na Internet:** A Aria consegue acessar a web e buscar informações recentes para te responder.
- **Gerenciar Tarefas:** Através do Gateway do AgentCore, a Aria se conecta com a sua API de Gestão de Tarefas.
- **Lembrar de Tudo:** Graças à Memória do AgentCore, a Aria não esquece das suas preferências e do contexto das conversas passadas.

![Architecture](images/full-architecture.drawio.png)

## Módulos do Curso

O curso é totalmente prático e incremental. Cada módulo adiciona novas funcionalidades ao seu agente:

| Módulo | Título | O Que Você Vai Aprender |
|--------|-------|---------------------|
| [00](00-prerequisites/) | **Pré-requisitos** | Como subir a infraestrutura base na AWS (Cognito, API Gateway, DynamoDB). |
| [01](01-introduction/) | **AgentCore CLI & Introdução** | Entendendo a arquitetura do AgentCore e conhecendo a linha de comando. |
| [02](02-runtime/) | **AgentCore Runtime** | Colocando o seu agente para rodar na nuvem com auto-scaling e streaming. |
| [03](03-tools/) | **AgentCore Tools** | Adicionando as ferramentas de Interpretador de Código (Python) e Navegador Web. |
| [04](04-memory/) | **AgentCore Memory** | Dando memória de curto e longo prazo para a Aria. |
| [05](05-gateway-identity/) | **Gateway & Identity** | Conectando sua IA com APIs externas e protegendo tudo com autenticação JWT. |
| [06](06-policy/) | **AgentCore Policy** | Bloqueando acessos indevidos e aplicando regras de negócio usando o Cedar Policy. |
| [07](07-observability-evaluations/) | **Observabilidade & Avaliações** | Criando painéis de métricas, traces e usando LLMs para dar "notas" de qualidade para o seu agente. |
| [08](08-full-deployment/) | **Full Deployment** | Subindo a interface Web (Frontend) e vendo o projeto inteiro funcionando junto! |

## Versões do Agente

Ao longo dos módulos, nosso agente vai evoluindo na nuvem:

- **V1** (Módulo 02): Chat básico -- Só conversa simples usando modelos do Bedrock.
- **V2** (Módulo 03): V1 + Interpretador de Código + Navegador Web.
- **V3** (Módulo 04): V2 + Memória persistente.
- **V4** (Módulo 05): V3 + Conexão com Gateway + Repasse de token JWT.
- **V5** (Módulo 07): V4 + Tratamento de erros avançado para produção.

## Pré-requisitos

### Ferramentas Necessárias
Para rodar esse laboratório na sua máquina, você vai precisar ter instalado:
- **Python 3.12+**
- **Node.js 20+** e **npm**
- **AWS CLI v2** -- Configurado com a sua conta da AWS.
- **AWS CDK** -- Instale rodando `npm install -g aws-cdk`
- **AgentCore CLI** -- Instale rodando `npm install -g @aws/agentcore`
- **uv** (Gerenciador de pacotes Python super rápido) -- Instale com `pip install uv`
- **Docker** -- Essencial para montar as imagens de deploy.
- **Jupyter** -- Instale com `pip install jupyter ipykernel` (vamos usar notebooks para o passo-a-passo).

### Permissões da AWS
A sua conta da AWS vai precisar de permissões para criar recursos nesses serviços:
- Amazon Bedrock
- Amazon Cognito
- API Gateway
- DynamoDB
- AWS Lambda
- Amazon S3
- AWS IAM
- AWS CloudFormation
- Amazon CloudWatch & AWS X-Ray
- Amazon Verified Permissions
- Amazon ECR

### Região da AWS
Para evitar problemas, faça este laboratório usando a região **us-east-1**. 

## Como Começar

### 1. Crie a Infraestrutura Base (CloudFormation)
O arquivo `infrastructure/prerequisites.yaml` já tem tudo pronto para criar a base do projeto (usuários, tabelas, APIs). É só rodar no terminal:

```bash
aws cloudformation deploy \
  --template-file infrastructure/prerequisites.yaml \
  --stack-name agentcore-workshop-prerequisites \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

> **Atenção sobre o X-Ray:** O script acima já habilita o X-Ray Transaction Search por padrão. A AWS só permite um desses por conta/região. Se a sua conta já tem isso habilitado, adicione o parâmetro `--parameter-overrides EnableTransactionSearch=false` no comando acima para não dar erro.

Esse passo demora cerca de 5 a 10 minutos. Você pode acompanhar pelo console do CloudFormation na sua conta da AWS.

### 2. Prepare seu Ambiente Python
Crie um ambiente virtual e instale o Jupyter:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install jupyter ipykernel boto3
python -m ipykernel install --user --name workshop --display-name "workshop"
```

### 3. Abra o Primeiro Notebook
Abra o arquivo `00-prerequisites/notebook.ipynb` na sua ferramenta favorita (VS Code, Jupyter no navegador, PyCharm). Quando pedir para escolher o kernel, selecione o `workshop` que acabamos de criar. Rode as células apertando `Shift+Enter`.

### 4. Siga os Módulos na Ordem
Cada notebook foi pensado para ser rodado passo a passo (do 00 ao 08). Eles começam fazendo uma checagem mágica (`ensure_ready`) para garantir que você não esqueceu de rodar o módulo anterior e explicam tudo direitinho de forma bem didática.

### 5. Limpando Tudo no Final
Para não gastar dinheiro na AWS depois que terminar o curso, lembre-se de limpar os recursos. O Módulo 08 mostra como fazer isso, e você pode rodar esse comando para apagar a infra base:

```bash
aws cloudformation delete-stack \
  --stack-name agentcore-workshop-prerequisites \
  --region us-east-1
```

## Estimativa de Tempo e Custo
- **Tempo:** Você deve levar entre 1 e 2 horas para terminar todos os passos.
- **Custo:** Você deve gastar cerca de $1 a $5 USD na sua conta da AWS, a maior parte sendo apenas do uso do modelo (LLM) no Amazon Bedrock.

---

> [!IMPORTANT]
> **Atribuição de Autoria e Compliance Institucional**
> 
> Todo o escopo, código base e arquitetura de infraestrutura gerada neste material de ensino derivam integralmente das fontes originais criadas pelo engenheiro de infraestrutura e autor da AWS, **Mike G. Chambers** (referência no GitHub: **mikegc-aws**). 
> 
> Este repositório é uma adaptação intensiva, traduzida e estruturada em formato de laboratório focado exclusivamente em ensino (hands-on) para o mercado brasileiro. Todos os direitos e créditos da arquitetura original pertencem e originam-se de seu trabalho. A finalidade deste repositório adaptado é educacional.
