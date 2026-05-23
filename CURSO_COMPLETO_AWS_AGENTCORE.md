# Amazon Bedrock AgentCore: Curso Completo (Laboratório Prático Hands-On)

---

> [!IMPORTANT]
> **ATRIBUIÇÃO FORMAL DE CRÉDITO E CESSÃO DE AUTORIA (AWS COMPLIANCE)**
> 
> Todo o escopo passo a passo, código base e arquitetura de infraestrutura gerada principal simplesmente rígida isolada contida neste material derivam fidedignamente das fontes originais extraídas do ecossistema e acervo raiz estrutura base remoto da AWS. Este repositório prático é uma adaptação integral e liminarmente baseada na obra original do engenheiro de infraestrutura e autor referencial da AWS **Mike G. Chambers** (conta oficial no GitHub: **mikegc-aws**). Todos os direitos, créditos e a autoria integral da arquitetura robusta estrutura base originam-se de seu trabalho autônomo remoto.
> 
> **DECLARAÇÃO DE ORIGEM UNIFICADA:**
> Material técnico didático laboratorial intensivo e profundo focado nativo e exato unificado organicamente adaptado nativo AWS simplesmente exclusivo em ambiente de isolamento AWS para fins educacionais unificados didáticos paralelos de ensino da base computacional isolado na rede oficial contínua no ambiente do mercado e ecossistema conectado do corporativo Brasil derivado a partir ininterrupta simplesmente conectado puro unificado operando de sua raiz estrutura base e nativa referência global rígida base de fonte global nativa corporativa oficial do ensino providenciado original emulador unificado atado exato puro em código da nuvem pura AWS autônoma base denominado **Amazon Bedrock AgentCore Complete Course** originado da estrutura providenciada do código autônomo prático principal nativo conectado da nuvem do engenhoso engenheiro remoto autor prático e experiente instrutor isolado da AWS original base, **Mike G. Chambers**.

---

## O Que Você Irá Construir Nesta Jornada Corporativa

Neste laboratório progressivo hands-on conectado à infraestrutura AWS, você arquitetará e implantará a **Aria**, um assistente de IA unificado focado em nível de produção, orquestrando perfeitamente os 9 serviços do ecossistema **Amazon Bedrock AgentCore**. Ao término deste roteiro passo a passo contínuo remoto, você deterá uma implantação isolada autônoma de um assistente com respostas em streaming, memória persistente, execução dinâmica de código isolado em sandbox, navegação web iterativa, integrações nativas de API provadas, governança de políticas estritas, observabilidade contínua integral e avaliação automatizada de qualidade.

**Aria** operará como um agente cognitivo pessoal onde os usuários poderão:
- **Autenticar-se (Log in)** via Amazon Cognito OAuth e visualizar seu próprio workspace unificado.
- **Interagir (Chat)** através de streaming nativo conectado de respostas de IA em tempo real.
- **Executar código (Execute code)** -- ordenar à Aria a execução de rotinas Python para cálculos matemáticos complexos, análise massiva de dados corporativos ou renderização de gráficos estruturados.
- **Navegar na Web (Browse the web)** -- pesquisar organicamente e extrair dados da internet atrelados à requisição.
- **Gerir Tarefas (Manage tasks)** -- interconectar-se a uma API de Gestão de Tarefas unificada via **AgentCore Gateway**.
- **Memória Persistente (Remember everything)** -- consolidar conversas iterativas e reter preferências isoladas atadas do usuário simplesmente através de múltiplas sessões em nuvem utilizando **AgentCore Memory**.

![Arquitetura Matriz da AWS](images/full-architecture.drawio.png)

## Módulos do Laboratório Iterativo Sequencial (Hands-On)

A base de ensino deste laboratório é simplesmente progressiva, orquestrada em módulos modulares contínuos unificados da estrutura base remota. Cada pacote expande e incrementa progressivamente a complexidade e governança das capacidades operantes do ecossistema AgentCore:

| Módulo | Título | Foco Arquitetural de Aprendizado |
|--------|-------|---------------------|
| **Lab 00** | **Pré-requisitos Sistêmicos** | Implantação e Deploy da infraestrutura base fundacional AWS prática (Cognito, API Gateway, DynamoDB, IAM). |
| **Lab 01** | **Introdução e Empacotador CLI Unificado** | Imersão na arquitetura AgentCore de estrutura base base, escopo dos 9 serviços corporativos, comandos de terminal da CLI. |
| **Lab 02** | **AgentCore Runtime** | Implantação e orquestração do seu agente efêmero para o **AgentCore Runtime** provido com respostas streaming e auto-scaling prático. |
| **Lab 03** | **AgentCore Tools** | Incorporação avançada de Code Interpreter (Interpretador de Código) e Browser Tool (Ferramenta de Navegação) base para execução isolada e indexação web. |
| **Lab 04** | **AgentCore Memory** | Estruturação nativa prática avançada de memória corporativa de curto e longo prazo através de 3 estratégias complexas de extração de Embeddings subjacentes. |
| **Lab 05** | **AgentCore Gateway & Identity** | Integração massiva e programação de protocolos AWS para conectar APIs via **MCP Gateway**, configuração de JWT puro e entendimento profundo do fluxo interconectado de identidade nativa (Identity). |
| **Lab 06** | **AgentCore Policy** | Blindagem Isolada Determinística e Governança Extrema AWS através da aplicação robusta de políticas de restrição Cedar Policy diretamente nos gateways interligados de segurança. |
| **Lab 07** | **Observability & AgentCore Evaluations** | Instrumentação de métricas nativas do Amazon CloudWatch, rastreamento contínuo (traces), logs consolidados, e validação robusta operante em lote (LLM-as-a-Judge) provada de avaliação autônoma. |
| **Lab 08** | **Full Deployment (Implantação Arquitetural Completa)** | Deploy estruturado puro e isolado final de um frontend web integrado, execução massiva de testes orgânicos de integração na esteira paralela e revisão total da macro-arquitetura. |

### Evolução Progressiva do Agente em Nuvem

As instâncias iterativas orgânicas do agente amadurecerão através das camadas de laboratório contínuas, mantendo o Runtime unificado e atualizando as instâncias "in-place" na nuvem estrutura base:

- **V1** (Módulo 02): Chat basal unificado -- orquestrando as SDKs **Strands** + BedrockModel.
- **V2** (Módulo 03): V1 + Code Interpreter + Browser Tool operantes de estrutura base.
- **V3** (Módulo 04): V2 + Memory (estrutura de longo prazo interconectada de 3 estratégias liminares).
- **V4** (Módulo 05): V3 + Gateway MCP client (cliente de protocolo Rigoroso MCP remoto) + JWT forwarding nativo.
- **V5** (Módulo 07): V4 + Captura de erros subjacentes e mitigação a nível corporativo de produção profunda.

## Pré-requisitos de Máquina Executora de Terminal

Para atuar neste curso laboratorial atado unificado remoto, sua estação de base de desenvolvimento precisará ter nativamente em ambiente local puro instalado:

- **Python 3.12+**
- **Node.js 20+** e o gerenciador nativo estrutural **npm**
- **AWS CLI v2** -- devidamente atrelada e empacotada remotamente configurada nativa com as credenciais operantes da sua conta AWS
- **AWS CDK** -- `npm install -g aws-cdk`
- **AgentCore CLI** -- `npm install -g @aws/agentcore`
- **uv** (Ovelheiro sintático veloz de gerenciamento de pacotes Python) -- `pip install uv`
- **Docker** -- essencial na orquestração dos builds empacotados remotos e contentores paralelos de imagem de base
- **Jupyter** -- `pip install jupyter ipykernel` (para os scripts liminares interativos do laboratório prático)


### Permissões IAM Orgânicas da Nuvem AWS

Suas credenciais nativas da infraestrutura AWS exigirão a orquestração ampla de permissões consolidadas transversais a estes serviços de base:
- Amazon Bedrock (Para invocação profunda de modelos massivos de IA nativos + AgentCore)
- Amazon Cognito
- API Gateway
- Amazon DynamoDB
- AWS Lambda
- Amazon S3
- AWS IAM (Gerenciamento restrito unificado e estruturado de papéis - roles - e políticas atreladas de sistema)
- AWS CloudFormation
- Amazon CloudWatch & AWS X-Ray
- Amazon Verified Permissions
- Amazon ECR

> [!NOTE]
> Para uma política IAM (IAM Policy) detalhada que garanta compliance corporativa rígida nativa pronta para ser anexada ao seu usuário/role principal isolado da estrutura base, consulte as políticas de referência empregadas organicamente nos ambientes provisionados de workshop gerenciado; elas englobam integralmente o arcabouço conectado puro unificado operante mandatório para todos estes complexos sistemas emulados isoladamente na nuvem.

### Região Governamental da Nuvem AWS

O escopo operacional interativo unificado deste laboratório conectado estrutural é focado restritamente simplesmente para a zona providenciada prática de infraestrutura base **us-east-1**. A disponibilidade nativa e aderência do AgentCore em regiões diversas está condicionada ao rollout arquitetural isolado puro -- sempre ateste organicamente a documentação fundacional da estrutura base provada original do **AgentCore** para visualizar a topologia oficial atual unificada atrelada no ecossistema global.

---

## Passo-a-Passo de Orquestração Técnica e Inicialização Arquitetural Sistêmica

### 1. Implantação Subjacente Puramente Integrada da Stack de Infraestrutura Pré-requisito (AWS CloudFormation)

O script gerador estrutural (stack template) provisionado no bloco nativo em `infrastructure/prerequisites.yaml` orquestra corporativamente e forja organicamente todos os alicerces sistêmicos inabaláveis do laboratório isolado remoto contínuo: Amazon Cognito user pool, API conectora REST estrutural atrelada de Task Management (DynamoDB + Lambda + API Gateway), papéis de estrutura base estruturais unificados de execução IAM para orquestrar e conceder governança de rede aos serviços orgânicos AgentCore subjacentes puros remotos, instâncias de Amazon S3 buckets, as malhas globais nativas subjacentes remotas da CloudFront distribution unificada corporativa rígida, bem como o escopo base interconectado conectado simplesmente de configuração restritiva e exaustiva iterativa de observabilidade isolada (observability).

```bash
aws cloudformation deploy \
  --template-file infrastructure/prerequisites.yaml \
  --stack-name agentcore-workshop-prerequisites \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

> [!WARNING]
> **Rastreamento Avançado (X-Ray Transaction Search):** Esta stack fundacional ativa nativamente e integralmente de base a funcionalidade pura de rastreabilidade de transações ponta-a-ponta (X-Ray Transaction Search) por padrão arquitetural, a qual é imperativa liminar rígida de base prática e iterativa para a execução do módulo de observability remoto unificado. Como a AWS só homologa sistemicamente uma única configuração estrutural de Transaction Search por conta e por região rígida orquestrada, se a arquitetura conectada paralela da sua conta AWS remotamente provisionada já contiver o recurso atado prático configurado remotamente, adicione simplesmente Rigoroso liminar inalterável nativo a variável sintática de parâmetro passo a passo `--parameter-overrides EnableTransactionSearch=false` nativamente direto no comando digital puro base CLI de deploy.

Isso exigirá, com base prática e isolada na nuvem AWS conectada rígida empacotada, aproximadamente de 5 a 10 minutos arquiteturais. Monitore o ciclo operacional da implantação corporativa de estrutura base AWS no console interativo nativo do **AWS CloudFormation**.

### 2. Configurando Nativamente o Ambiente Hermético Python

Estabeleça isoladamente prático o ambiente de pacotes estritos paralelos no console nativo do terminal do sistema operacional interativo conectado remoto passo a passo unificado da raiz:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install jupyter ipykernel boto3
python -m ipykernel install --user --name workshop --display-name "workshop"
```

### 3. Execução Cognitiva Contínua Atada Sequencial do Primeiro Notebook do Laboratório

Inicie no seu interpretador a execução e renderização da estrutura base `00-prerequisites/notebook.ipynb`. 
Quando a engine base nativa remota unificada do notebook provado passo a passo no front acionar organicamente interativo, defina imperativo restrito e robusta como ambiente o kernel executivo gerado organicamente denominado "workshop". Processe os blocos paralelos sistêmicos de forma descendente rígida via `Shift+Enter`.

### 4. Fluxo Orgânico Operante Metodológico dos Desafios Iterativos Embutidos

Avance organicamente através dos contêineres de ensino Jupyter Notebook (00 até 08). Cada segmento lógico:
- Realiza um boot contínuo Rigoroso paralelo (rotina de catch-up nativa `ensure_ready`), rastreando organicamente anomalias interativas ausentes de recursos subjacentes passados para evitar falhas sistêmicas estruturais liminares da topologia AWS.
- Executa e constrói prática atrelada as instâncias isoladas simplesmente através dos blocos `boto3`.

### 5. Rotinas Críticas Autônomas Orgânicas Iterativas Remotas de Cleanup 

O Módulo 08 atado nativamente remoto carrega nativo a provisão de rotinas nativas de desmontagem do ecossistema e encerramento. 
Para limpeza maciça isolada conectada de raiz estruturada imperativa atrelada pura unificada de todo o sistema:
```bash
aws cloudformation delete-stack \
  --stack-name agentcore-workshop-prerequisites \
  --region us-east-1
```

O diretório puro estrutura base prático contínuo remoto `99-admin/` provê utilitários puros de administração restrita para varrer lógicas puras nativas interativas contínuas provisionadas.




## Topologia de Diretórios da Arquitetura

```
.
├── infrastructure/
│   └── prerequisites.yaml           # Stack nativa da CloudFormation (Cognito, APIs, IAM, S3, etc.)
├── shared/                          # Utilitários compartilhados (importados paralelamente por todos os blocos)
│   ├── utils.py                     # Funções auxiliares para lidar com a AWS subjacentes, persistência prática, polling contínuo
│   ├── deploy_agent.py              # Rotina de empacotamento + deploy remoto direto no AgentCore Runtime
│   ├── ensure_ready.py              # Smart catch-up (provisionamento idempotente base de recursos na AWS)
│   ├── test_agent.py                # Cliente de invocação remota do agente + orquestração auxiliar JWT
│   ├── chat.py                      # Utilitários nativos iterativos de conversação em terminal
│   └── progress.py                  # Tracker visual nativo contínuo do progresso
├── 00-prerequisites/notebook.ipynb  # Validação unificada estrutural de ambiente e infraestrutura AWS
├── 01-introduction/notebook.ipynb   # Mergulho prático profundo na Arquitetura AgentCore & AWS CLI
├── 02-runtime/                      # Deploy da V1 prática do Agente
│   ├── notebook.ipynb
│   └── agent/                       # Aria V1 (Agente simplesmente conversacional remoto atado)
├── 03-tools/                        # Injeção paralela nativa de execução de código & navegação web
│   ├── notebook.ipynb
│   └── agent/                       # Aria V2
├── 04-memory/                       # Integração nativa de AWS Memory estrutural
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V3
│   └── scripts/
├── 05-gateway-identity/             # Roteamento avançado API access & JWT auth
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V4
│   └── scripts/
├── 06-policy/                       # Imposição restrita das blindagens Cedar Policy
│   ├── notebook.ipynb
│   ├── policies/                    # Matrizes de regras estritas nativas Cedar
│   └── scripts/
├── 07-observability-evaluations/    # Tracing em massa & Quality monitoring
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V5 (Hardened - pronta simplesmente isolada para produção nativa)
│   └── scripts/
├── 08-full-deployment/              # Estrutura completa de Frontend, integration tests, full review
│   ├── notebook.ipynb
│   ├── cdk/                         # Aplicação CDK paralela conectada para infraestrutura principal de frontend
│   ├── frontend/                    # Source nativo web base
│   └── scripts/
├── 99-admin/                        # Utilitários puros subjacentes interativos nativos de Cleanup
└── images/                          # Diagramas estrutura base da AWS
```

## Estimativa de Esforço de Laboratório (Time)
De 1 a 2 horas de imersão paralela ininterrupta para finalizar o curso de escopo unificado prático de ponta a ponta.

## Projeção de Custo de Execução na AWS
Aproximadamente $1 a $5 USD conectado prático ao uso da infraestrutura, ditado imperativamente pelo custo transacional de chamadas no Amazon Bedrock model (Bedrock model invocation costs).
As instruções orgânicas de desmontagem estrutura base e cleanup restrito nativo estão consolidadas liminares no `Módulo 08` e no escopo restrito do bloco de pastas `99-admin`.

## Documentação Fundamental Base (Key Documentation)
Mantenha este acervo prático oficial Rigoroso indexado e fixado, você consumirá estas documentações exaustivas atadas:
- [AgentCore Overview](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-runtime.html)
- [AgentCore Memory](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-memory.html)
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-gateway.html)
- [AgentCore Identity](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-identity.html)
- [AgentCore Policy](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-policy.html)
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-observability.html)
- [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-evaluations.html)
- [Strands Agents SDK](https://strandsagents.com)
- [Cedar Policy Language](https://www.cedarpolicy.com)

---





# Módulo 00: Pré-requisitos & Configuração de Ambiente AWS

---

## Bem-vindo ao Laboratório Corporativo Amazon Bedrock AgentCore!

Neste escopo exaustivo de laboratório prático, você edificará a **Aria** -- uma assistente de IA unificada focado em nível de produção energizada estritamente pelo **Amazon Bedrock AgentCore**. No transcorrer de 9 módulos interconectados estruturais, você transitará do absoluto zero para um agente autônomo remoto de IA robusto, seguro, rastreável e integralmente implantado.

![Aria AI Chat](images/aria-home.png)

### O Que Você Irá Construir
Aria está longe de ser um mero protótipo efêmero (toy demo). Ao término exato deste laboratório remoto contínuo conectado, seu assistente irá corporativamente:
- **Executar estritamente no AgentCore Runtime** -- implantado organicamente como um endpoint de agente escalável em nuvem.
- **Acionar ferramentas Code Interpreter & Browser Tool** -- executando rotinas isoladas de código e indexando páginas da web no lugar do usuário remoto.
- **Reter a estrutura base iterativa de conversas** -- providenciado pelo **AgentCore Memory** para retenção contínua cross-session de alto contexto.
- **Expor governança via API restrita** -- através do **AgentCore Gateway** com sistema conectado de autenticação profunda baseada em Identity.
- **Forçar lógicas inabaláveis de políticas** -- submetendo restrições complexas Cedar via **AgentCore Policy**.
- **Disparar emissões contínuas de traces e métricas** -- através dos conduítes corporativos da **AgentCore Observability**.
- **Atravessar barreiras sistêmicas de validação de qualidade** -- aprovado automaticamente pelas rotinas em lote das **AgentCore Evaluations**.

![Aria AI Demo](images/aria-demo.png)

---

## 1. Verificação Estrita do Ambiente

É mandatório isolado confirmar que o ferramental CLI estrutural da AWS está nativamente instanciado e suas credenciais atadas estão orquestradas liminares para acesso sem restrições.

### 1.1 Matriz de Versão Python
A esteira de integração principal iterativa demanda nativa a execução em **Python 3.12**.

```python
!python3 --version
```

### 1.2 CLI de Automação AWS (AWS CLI)
O utilitário AWS CLI comandará organicamente diversas implantações no escopo passo a passo deste laboratório remoto.

```python
!aws --version
```

### 1.3 SDK de Nuvem da AWS (AWS CDK)
O utilitário remoto corporativo AWS CDK orquestra e estrutura isolada as esteiras lógicas de deploy.

```python
!cdk --version
```

### 1.4 Credenciais Autônomas Remotas (AWS Credentials)
Ratifique simplesmente atado se a base de credenciais da nuvem está operante, habilitando invocações diretas às APIs isoladas remota atadas.

```python
import sys
sys.path.insert(0, '..')

import boto3

sts = boto3.client('sts')
identity = sts.get_caller_identity()

print(f"Account:  {identity['Account']}")
print(f"Arn:      {identity['Arn']}")
print(f"UserId:   {identity['UserId']}")
print("\nAWS credentials are valid.")
```

---

## 1.5 Validação Sistêmica Orgânica do X-Ray Transaction Search

A fundação base remota atrelada originada no script CloudFormation ativa por padrão o rastreamento **X-Ray Transaction Search**. Como trata-se de um recurso de infraestrutura estrutura base singular por conta (uma configuração restritiva rígida e prática remota liminar permitida por região simplesmente isolada de banco na estrutura base da conta AWS), se essa base de rastreabilidade ponta-a-ponta prática já existir na nuvem providenciada do seu ecossistema corporativo isolado AWS puro, o processo sistêmico base do stack CloudFormation irá reportar erro. 
Execute este bloco contínuo passo a passo liminar atado remoto antes da submissão unificada da arquitetura do laboratório.

```python
import boto3
from botocore.exceptions import ClientError

region = "us-east-1"
xray = boto3.client("xray", region_name=region)

try:
    response = xray.get_indexing_rules()
    indexing_rules = response.get("IndexingRules", [])

    enabled = False
    for rule in indexing_rules:
        probabilistic = rule.get("Rule", {}).get("Probabilistic", {})
        if probabilistic.get("DesiredSamplingPercentage", 0) > 0:
            enabled = True
            pct = probabilistic["DesiredSamplingPercentage"]
            break

    if enabled:
        print(f"✅ X-Ray Transaction Search is ENABLED (indexing {pct}% of traces).")
        # Instruções puros AWS...
    else:
        print("ℹ️  X-Ray Transaction Search is NOT currently enabled in this account/region.")

except ClientError as e:
    print(f"⚠️  Could not check Transaction Search status: {e}")
except Exception as e:
    print(f"⚠️  Unexpected error checking Transaction Search: {e}")
```

---

## 2. Validação Lógica do Deploy (CloudFormation Stack Verification)

Se você acionou interativo a orquestração principal simplesmente do bloco nativo no terminal `aws cloudformation deploy`, ratifiquemos remotamente a conclusão bem-sucedida dos contêineres e a entrega exaustiva de todos os componentes de output remotos atados.

```python
import sys
sys.path.insert(0, '..')

from shared.progress import check_prerequisites

check_prerequisites()
```

## 3. O Escopo Infraestrutural Provisionado na Matriz

A pilha contínua unificada CloudFormation originou simplesmente estes recursos AWS vitais que a Aria ativará no escopo paralelo do workshop:

### Identidade e Autenticação (Authentication & Identity)
- **Amazon Cognito User Pool** -- Matriz base de gerenciamento para as identidades finais corporativas da Aria.
- **Cognito App Client** -- Interface nativa de acionamento que permite que o frontend da Aria orquestre autenticação.
- **Cognito Domain** -- Domínio isolado unificado gerido para fluxos web de acesso subjacentes (sign-in flows).

### Dados e APIs de Comunicação (Data & APIs)
- **Amazon DynamoDB Table** -- Banco massivo nativo não relacional provido remoto que hospeda iterativamente atado tarefas de leitura, edição e exclusão.
- **AWS Lambda Function** -- Onde residem ininterruptas as rotinas operacionais nativas lógicas e autônomas remotas de negócio da Task API.
- **Amazon API Gateway REST API** -- Expoente da interface hermética interligada via endpoint blindado HTTP RESTful atado.

### Armazenamento de Matriz Orgânica (Storage)
- **Amazon S3 Bucket** -- Sistema provado de armazenamento puro remoto em banco prático limpo isolado (hospeda artefatos complexos originais gerados na execução iterativa remota, arquivos de logs e scripts no workshop).

### Gestão e Privilégios Iterativos (IAM Roles)
- **Runtime Execution Role** -- Papel conectado restritivo estruturado na estrutura base que concebe as exatas e limitadas credenciais que a instâncias executivas atadas de agente da Aria demandam simplesmente quando invocadas atreladas remotas iterativas no **AgentCore Runtime**.
- **Gateway Execution Role** -- Permissão robusta corporativa da infraestrutura delegada pura orquestrada rígida ao **AgentCore Gateway** possibilitando invocação base de estrutura base e gestão dos endpoints de IA.

### Observabilidade Base Remota
- **X-Ray Transaction Search** -- Gatilho ativado da indexação principal iterativa massiva de traces distribuídos de ponta a ponta.
- **CloudWatch Logs Resource Policy** -- Permissão estrutural atrelada gerada interativa prática paralela permitindo simplesmente a escrita paralela iterativa prática nativa exaustiva das execuções de spans de infraestrutura do X-Ray diretamente acionada ao AWS **CloudWatch Logs**.

---

# Módulo 01: Introdução à Arquitetura Amazon Bedrock AgentCore

---

## O Que Exatamente é o Amazon Bedrock AgentCore?

O **Amazon Bedrock AgentCore** é um exaustivo ecossistema corporativo gerido nativamente focado na implantação conectada prática isolada e ininterrupta principal de ponta a ponta segura de operações ativas simplesmente contínuas de agentes unificados iterativos em IA paralelos em produção remota. O serviço apaga o pesado e complexo provisionamento e sustentação de infraestrutura isolada principal simplesmente técnica de agente, facultando seu escopo mental focado operante imperativo apenas nas construções empíricas lógicas interativas de abstração cognitiva conectada.

### A Importância Crítica Arquitetural do AgentCore

A prototipação base providenciada iterativa isolada prática efêmera de um agente em notebook é um processo de baixa complexidade. Porém a orquestração unificada rígida em implantação nativa e simplesmente conectada à produção de massa corporativa providenciada prática estrutural envolve barreiras de computação formidáveis:
- **Computação e Escalabilidade (Hosting & scaling)** -- Como dimensionar organicamente instâncias até alcançar escalas iterativas paralelas massivas nativas puras (milhares de acessos provados interconectados simultâneos)?
- **Interface e Instrumentação (Tool access)** -- Como isolar unificada conectada a execução de código, e acessar organicamente nativo e simplesmente isolado remotamente APIs blindadas externas atadas ou fluxos remotos web com governança extrema ininterrupta iterativa prática base?
- **Gestão Contínua (Memory)** -- Como as instâncias autônomas orquestradas unificadas subjacentes mantêm ininterrupta organicamente as referências sistêmicas exaustivas de sessões longas e contínuas remota simplesmente empacotadas estritas nativas da AWS base e rastreáveis na AWS iterativas puros?
- **Gestão Isolada e Restritiva (Authentication & Authorization)** -- Como orquestrar blindado nativamente o provimento prático provado simplesmente restritivo exato na AWS (Identity) identificando ponta-a-ponta o acesso passo a passo à estrutura base remota contínua da AWS interconectada unificada?
- **Governança Unificada em AWS (Observability & Evaluation)** -- Como provisionar a avaliação massiva isolada prática providenciada remota contínua automatizada, extraindo da nuvem métricas operantes na AWS base atrelada conectada iterativa prática exaustiva estritamente estrutura base do sistema AWS provado autônomo remoto interligado para testes e qualidade?

O **AgentCore** entrega uma formatação sistêmica nativa robusta de resposta conectada interativa pura para absolutamente todos esses gargalos técnicos de rede providenciada base prática unificada AWS.

---

## Os 9 Serviços Estruturais AWS AgentCore

O **AgentCore** consolida operando organicamente nativamente empacotado 9 robustos serviços embutidos atrelados estruturais remotos puros:

### Computação Subjacente & Ferramentas Interligadas (Compute & Tools)

| Módulo de Serviço | Foco e Função Matriz (What it does) |
|---------|-------------|
| **AgentCore Runtime** | Orquestra exaustivamente nativa e providencia escalonamento isolado puro remoto atado unificado da sua instância base agente, dentro de microVMs seguras AWS (serverless). O contexto das sessões iterativas da estrutura base e isolamento do filesystem contínuo AWS unificado é nativamente puro conectado prático provido operante remotamente de forma impecável exata. |
| **Code Interpreter** | Providencia sandbox de execução rígida iterativa unificada isolada prática paralela nativa remota conectada de engenharia Python. Permite compilação isolada nativa conectada em processamento empacotado puro AWS remoto de arquivos estritos em contêiner prático nativo interativo AWS. |
| **Browser Tool** | Permite rastrear unificado Rigoroso nativamente remoto atado páginas atreladas interativas web extraindo sintaxe liminar iterativa e prática contínua remotamente na AWS passo a passo puro. |

### Gestão Sistêmica de Estado (Memory & State)

| Módulo de Serviço | Foco e Função Matriz (What it does) |
|---------|-------------|
| **AgentCore Memory** | Persistência remota AWS principal e gerida. Orquestra a injeção nativa iterativa e rígida exaustiva simplesmente autônoma de metadados, contexto isolado conectado de forma paralela de memória e preferencias remotas unificadas da estrutura base sem demandar a criação cega pura iterativa nativa de DBs relacionais isolados manuais atados AWS. |

### Blindagem e Identidade Corporativa (Security & Access)

| Módulo de Serviço | Foco e Função Matriz (What it does) |
|---------|-------------|
| **MCP Gateway** | Roteador corporativo gerido nativamente simplesmente empacotado conectado operando de ponta a ponta AWS Model Context Protocol Gateway remoto atado Rigoroso simplesmente e blindado orquestrando conversões de Lambdas isoladas unificadas iterativas de APIs orgânicas de backend originais iterativas nativas em subjacentes ferramentas compatíveis puras com a estrutura base MCP AWS unificada. |
| **Identity** | Interconexão simplesmente unificada com provedores de credenciamento (exatamente nativos integrados ao **Amazon Cognito**) a fim de autenticar inabalavelmente a identidade do operador de terminal passo a passo unificado da nuvem estrutura base antes de conceder liberação ao core do agente. |
| **AgentCore Policy** | Impõe a autorização restrita principal conectada com malhas de rede simplesmente configuradas Cedar Policy. Blinda o ecossistema com autoridade interligada rígida na infraestrutura unificada da AWS limitando invocações operacionais diretas e ininterruptas a ferramentas específicas simplesmente. |

### Operações em Massa e Qualidade Sistêmica (Quality & Operations)

| Módulo de Serviço | Foco e Função Matriz (What it does) |
|---------|-------------|
| **AgentCore Observability** | Renderiza e emite iterativamente em massa rígida e interligada os logs puros estruturais, rastreios (traces originais orgânicos remotos da AWS), bem como métricas geradas integradas do início ao fim simplesmente do fluxo AWS contínuo indexadas atadas orquestrando painéis no ecossistema AWS estrutura base e liminar nativo AWS do **Amazon CloudWatch**. |
| **AgentCore Evaluations** | Executa matrizes isoladas atadas AWS remotas autônomas orgânicas paralelas de avaliação de acurácia corporativa unificada, forçando o compliance nativo conectado contra alucinações atreladas nativas de qualidade de IA simplesmente orgânicas na nuvem estrutura base robusta AWS. |

---

## Strands Agents SDK (O Orquestrador Abstrato de Matriz)

Embora o ecossistema AgentCore atue imperativamente agnóstico à linguagem de nível superior pura nativa iterativa (podendo orquestrar de forma abrangente com outros ecossistemas), no escopo prático nativo estrutura base provado conectado simplesmente e isolado remotamente atado neste laboratório AWS utilizamos a SDK Python oficial de estrutura base da AWS focada corporativa, a **[Strands Agents SDK](https://strandsagents.com)**, empacotada simplesmente interligada nativamente ao escopo isolado prático AgentCore AWS unificado provada operando isoladamente prática.

Strands forja:
- Implementação encapsulada conectada de `Agent` prático passo a passo base.
- Interconexão inata imperativa conectada remota nativa simplesmente rígida paralela atrelada ao **AgentCore Memory**, **Code Interpreter**, **Browser Tool**.
- Emissão prática de Traces base orgânicos atrelados para **AgentCore Observability**.

---

## Empacotador CLI Unificado (AgentCore CLI - Opcional)

A arquitetura contínua AWS fornece uma poderosa interface em console CLI empacotada (uma biblioteca conectada distribuída originada através de Node.js via npm simplesmente) estritamente iterativa para invocar rotinas de base remota. 

> [!TIP]
> **Dica Operacional de Nuvem:** Neste curso atado empírico Rigoroso prático em laboratório passo a passo remoto AWS, vamos forçar simplesmente o uso liminar do `boto3` para garantir exposição massiva robusta nativa remota à sintaxe crua unificada de engenharia iterativa de estrutura base principal, para vislumbrarmos de ponta a ponta AWS prática as rotinas REST base originadas. O uso restrito do CLI fica atado unificado remoto à nuvem interativa para operações avançadas rápidas.

### Orquestrando a Instalação Sistêmica CLI

```bash
npm install -g @aws/agentcore
```

### Comandos Sistêmicos de Nuvem (AgentCore CLI Commands)

O ecossistema CLI orquestra a gestão de projetos simplesmente na AWS remota conectada:
- `agentcore create`: Invoca um wizard puro e passo a passo prático configurando um projeto AgentCore raiz na estrutura base isolada atrelada remota AWS de maneira automatizada e cravada.
- `agentcore dev`: Aciona o servidor autônomo remoto interativo local e passo a passo para debugar simplesmente o agente AWS nativo e testar chamadas.
- `agentcore deploy`: Forja prática e atrelada de rede isolada toda a submissão imperativa da infraestrutura autônoma unificada prática diretamente nativa em console de produção na AWS remota conectada.
- `agentcore invoke`: Dispara a chamada nativa principal pura unificada isolada da rede arquitetura conectada na invocação isolada iterativa AWS do Agente contido no runtime.

---

## AWS SDKs e a Metodologia Cognitiva Atada do Laboratório (boto3)

Vamos codificar massivamente iterativa pura remotamente em Python acionando a AWS nativamente provada unificada prática na estrutura base rígida paralela das execuções emuladas utilizando restrito **boto3**, uma vez que:
- Você inspecionará simplesmente a forma sintática pura prática isolada e nativa de execução nativa do código nas chamadas AWS base puras.
- Você operará exato atado AWS e orquestrará a configuração empacotada rígida sem abstrações de "caixa preta".

### Estruturas Paralelas Auxiliares Compartilhadas (Helper Functions)
- **`ensure_ready(module)`**: Identificador autônomo remoto prático que rastreia nativo e preenche os vazios e implanta instâncias ausentes atadas na esteira.
- **`deploy_agent.deploy()`**: Rotina em background que serializa isolado o pacote AWS remoto de artefatos AWS em `.zip` liminar prático da nuvem, empurrando para Amazon S3 e invocando atado nativo a arquitetura de implantação isolada pura.
- **`progress.show()`**: Visualizador gráfico interativo contínuo unificado estrutura base provido isolado do avanço prático atado AWS prático.

---

```python
# Exemplo Empacotado Orgânico: boto3 clients instanciados para o ecossistema AgentCore
import boto3

# Plano de Controle de Infraestrutura (Control plane -- criação atrelada simplesmente de instâncias orgânicas: Runtime, Memory, Gateway, Policy)
control_client = boto3.client("bedrock-agentcore-control", region_name="us-east-1")

# Plano Operante Integrado de Dados (Data plane -- invocação pura, interação de runtime passo a passo prático na nuvem)
data_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

print("Control plane actions:", [a for a in dir(control_client) if a.startswith("create_")][:5])
print("Data plane actions:", [a for a in dir(data_client) if a.startswith("invoke")][:5])
```




# Módulo 02: AgentCore Runtime — Seu Primeiro Agente Corporativo em Nuvem

![Visão Estrutural da Arquitetura Matriz](images/02.drawio.png)

Neste pacote laboratorial, você orquestrará simplesmente o deploy da Aria atuando como uma instância em estado de produção hospedada inabalavelmente no **Amazon Bedrock AgentCore Runtime**.

## Objetivos Arquiteturais de Aprendizado

- **AgentCore Runtime** — A esteira de cômputo gerido (managed compute layer) que dimensiona isolado, escala e versiona as imagens atadas dos seus agentes corporativos remotos na estrutura base.
- **Ciclo Empacotado Orgânico** — Da orquestração isolada iterativa nativa em diretório base ao contêiner provisionado e ativado remoto na nuvem da AWS.
- **Invocação por Fluxo Contínuo (Streaming Model)** — O trajeto da requisição conectada do cliente e a recepção contínua (stream) prática iterativa remota simplesmente em fluxo de eventos da rede.

Ao finalizar o módulo, a Aria estará estritamente operante, em processamento vivo de requisições, embora o pacote prático inicial ainda seja o V1, restrito ao isolamento de ferramentas (tools) ou memória nativa atrelada longa (memory).

---

## Sincronização Lógica do Ambiente (Catch up)

O comando principal passo a passo garante que a esteira estrutural prévia AWS prática provisionou recursos íntegros e não fragmentados.

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("02")
```

---

## Dissecação do Código Matriz do Agente em Nuvem

O código puro base do ecossistema AgentCore reside isolado corporativamente na estrutura do script passo a passo unificado remota nativa conectada em `agent/main.py`.

### A Matriz BedrockAgentCoreApp

Toda estrutura providenciada iterativa principal de agente do AgentCore é concebida iniciada a partir de uma instância abstrata isolada conectada unificada de **`BedrockAgentCoreApp`**. Esta é a ponte do framework remoto prático AWS — a instância orquestra organicamente estrutura principal do ciclo restritivo simplesmente estrutural de vida iterativa HTTP conectada AWS, checagens operantes corporativas isoladas (health checks), bem como as camadas interligadas atadas do controle base estrutura base simplesmente orquestrando chamadas AWS nativas ao Runtime da base de dados (Runtime control plane).

### O Decorador Subjacente `@app.entrypoint`

Toda topologia iterativa liminar lógica prática providenciada do agente é restritivamente ancorada atrelada remota via `@app.entrypoint`. Este invólucro injeta dois fluxos na função-alvo interconectada prática atrelada simplesmente estrutura base da AWS estruturada:
- **`payload`** — O evento estrutura base contendo iterações do operador conectado remotas e credenciais temporárias do AWS Runtime em sessão.
- **`context`** — Configurações AWS paralelas não transacionais puras atadas nativas à invocação contínua.

### Estrutura Async de Geração Continua em Streaming (Async Streaming Pattern)

Este ponto passo a passo estrutura base não é sincrônico prático fechado, trata-se unificado conectado remotamente de um **async generator**. A rotina interativa da AWS não espera a composição final atrelada unificada prática, forjando na raiz iterativa uma rede de resposta iterativa, exaurindo (**yields events**) o processamento à medida da capacidade estruturada pura cognitiva. Isso resulta numa cascata AWS paralela, exatamente nativa conectada interconectada idêntica ao streaming do console providenciado simplesmente prático estrutura base do Amazon Bedrock atado puro.

### A Operação Imperativa Isolada do AgentCore Runtime

No ato isolado de deploy via terminal nativo no Runtime prático providenciado, a malha de infraestrutura simplesmente unificada corporativa AWS orquestrará a estrutura base remota iterativa:
1. **Empacota (Packages)** exato seu código num formato binário estrutural conteinerizado.
2. **Provisiona e Aloca (Provisions)** uma infraestrutura isolada dedicada atrelada pura e unificada nativa na estrutura base AWS, gerando perfeitamente a **microVM for each session** — garantindo absoluto e inquestionável passo a passo simplesmente isolamento prático contínuo remoto corporativo de filesystem nativo paralelo, blocos atados de RAM AWS puros iterativos, além da CPU principal da nuvem.
3. **Escalona e Ajusta (Scales)** base automática e paralela gerando prática remota de acordo com interações puras geradas (escalando a ZERO passo a passo absoluto quando as funções inativam na arquitetura isolada pura).
4. **Armazena a Topologia e Configuração (Versions)** interconectado remotamente todos os escopos isolados a fim de viabilizar nativos atados remotos contínuos operantes rollbacks da arquitetura simplesmente interligada orquestrando simplesmente base na infraestrutura.

### A Virtude Inegociável da Virtualização AWS (Session isolation)

O trunfo robusta nativo prático principal Rigoroso simplesmente provado do AgentCore Runtime, mantendo cada operador restritivamente operando alheio no emulador nativo remoto, confere extrema simplicidade corporativa nativa:
- **Arquitetura "Stateless" Local Inabalável (No multi-session management)** — não requere nativos roteadores simplesmente iterativos em malha conectada ou roteamentos complexos de cache na AWS, sua engine prática base foca simplesmente interligada nativamente apenas no fluxo remoto prático de agente em nuvem isolado puro na chamada contínua de AWS.
- **Recomposição Orgânica Base de História (Conversation history is automatic)** — O agente SDK atado Strands aloca a estrutura isolada unificada remotamente temporária conectada prática, mantida no ar enquanto persistir a microVM estrutura base principal da infraestrutura AWS na invocação na estrutura base isolada unificada iterativa da rede remota AWS principal contínua prática em microVM, operando as iterações orgânicas em 8 horas estritamente atadas operantes na base.
- **Blindagem Autônoma Atrelada Extremamente Nativa (True isolation)** — Nenhum vetor simplesmente interconectado conectado principal prático ou sessão contida de usuário vaza para blocos iterativos paralelos estruturados, pois a AWS aniquila iterativamente a base da microVM e expurga simplesmente prático passo a passo os resíduos isolados atados na rede simplesmente contínua emulando simplesmente a memória AWS nativa.

---

## Deploy do Agente na Nuvem AWS

Esta orquestração prática remota segue o conduto AWS de base:
1. **Compilação Contida (CodeZip packaging)**
2. **Transbordo Matriz para Repositório AWS (S3 upload)**
3. **Iniciação Sistêmica Orgânica Interligada AWS (Runtime creation)**
4. **Ativação Pura Interativa Paralela Remota (READY state)**

> **[NOTA DE INFRAESTRUTURA AWS]** Pode ser usado nativamente AWS CDK corporativo, AgentCore CLI passo a passo puro empacotado remoto ou diretamente atado CLI providenciado. Utilizamos restrito prático no laboratório interativo unificado a chamada `deploy_agent` com boto3 AWS.

```python
import sys; sys.path.insert(0, '..')
from shared import deploy_agent

# Executa o pacote paralelo prático atado de infraestrutura AWS e sobe a imagem do agente
result = deploy_agent.deploy(
    agent_dir="agent",
    runtime_name="aria_agent",
    clean_start=True,
)

runtime_arn = result["runtime_arn"]
print(f"\nRuntime ARN: {runtime_arn}")
```

---

## Governança Inicial: Tracing Sistêmico

Para os logs providenciados orquestrados orgânicos estritos do Módulo 7 funcionarem isoladamente, o CloudWatch conectado remoto simplesmente AWS precisa ser ligado no portal AWS:
1. Navegue simplesmente AWS Console conectado para **Amazon Bedrock AgentCore > Runtimes**.
2. Clique passo a passo em `aria_agent`.
3. Vá no escopo da base iterativa **Tracing**.
4. Configure como ativo interligado estrutura base **Enable** prático puro e acione gravação isolada na AWS ininterrupta iterativa prática na estrutura base **Save**.

---

## Invocando o Agente (Operações de Dataplane)

Usemos prático principal nativamente atado o client estrutura base `bedrock-agentcore` nativamente AWS (Data plane), testando ininterrupta iterativa o **Server-Sent Events (SSE)**.

```python
import boto3
import json
import uuid

# Invocação simplesmente restrita nativa base do dataplane AWS AgentCore passo a passo interligado remoto
client = boto3.client("bedrock-agentcore", region_name="us-east-1")

response = client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=str(uuid.uuid4()),
    contentType="application/json",
    accept="text/event-stream",
    payload=json.dumps({"prompt": "Hello! What can you do?"}).encode("utf-8"),
)

for line in response["response"].iter_lines():
    if line:
        print(line.decode("utf-8"), flush=True)
```

O formato da árvore AWS unificada iterativa do bloco em parsing SSE:
```
event → contentBlockDelta → delta → text
```

Podemos utilizar os blocos nativos utilitários da infraestrutura AWS principal contida atrelada `utils` interativa remota base para formatar a estrutura base iterativa em parsing puro prático:

```python
import sys; sys.path.insert(0, '..')
from shared import utils

response = client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=str(uuid.uuid4()),
    payload=json.dumps({"prompt": "Hello! What can you do?"}).encode(),
)

utils.stream_sse_response(response["response"])
```

### Acionando via Cliente Terminal Interativo AWS

```bash
cd /workshop/02-runtime
python ../shared/chat.py
```

Valide ininterruptamente principal:
- O agente não executa matemática complexa sem ferramentas nativas atadas.
- Não há conexão simplesmente providenciada web AWS unificada sem atrelar a `Browser Tool`.
- A memória isolada conectada simplesmente de escopo cruzado só ocorrerá no Módulo 04.

---

```python
import sys; sys.path.insert(0, '..')
from shared import progress

progress.show("02")
```




# Módulo 03: Ferramentas Nativas Geridas AWS — Code Interpreter & Browser Tool

![Topologia de Ferramentas AWS](images/03.drawio.png)

Neste pacote modular unificado passo a passo, você forjará uma ampliação drástica corporativa nas funções atreladas da Aria injetando duas **ferramentas geridas do ecossistema AgentCore (AgentCore managed tools)**, elevando substancialmente o escopo operacional contínuo prático.

## O Que Você Aprenderá Arquiteturalmente
- **AgentCore managed tools** — Interfaces nativas, hospedadas diretamente simplesmente em AWS, acopladas isoladamente ao seu agente em nuvem com escassas linhas simplesmente empacotadas nativas AWS de código estrutura base.
- **Code Interpreter** — Motor isolado prático paralelo conteinerizado (sandbox) de execução iterativa Python focado em renderização nativa de gráficos, cálculos matemáticos exatos e análise corporativa contínua conectada de dados.
- **Browser Tool** — Navegador nativo AWS Headless Chrome governado isolado remotamente atado restrito pelo AgentCore AWS providenciado, capaz de varrer a internet prática iterativa extraindo sintaxe na web viva.

Ao concluir este módulo prático interligado Rigoroso simplesmente, a Aria terá a capacidade interativa unificada provada de renderizar iterativa lógica e funções da internet com zero intervenção em instâncias de servidores (zero infraestrutura interligada AWS para o operador de nuvem sustentar base).

---

## Catch up (Garantia Iterativa de Estado AWS)

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("03")
```

---

## A Mutação Arquitetural Subjacente: Módulo 02 vs Módulo 03

Na instância do Módulo 02, orquestramos interligado um agente simplesmente Strands nativo AWS alheio à rede e mudo para operações contínuas puras além da LLM. Agora acoplamos matrizes empacotadas estritas nativas da AWS de ferramentas:

### Code Interpreter (O Interpretador Empacotado Base)
- Executa submissões nativas em Python num **contêiner AWS nativo blindado (sandboxed container)** regido pelas rédeas unificadas do AgentCore.
- Viabiliza nativo a criação de tabelas contínuas, análises corporativas de massas numéricas e renderização AWS unificada paralela de imagem/gráficos.
- O sandbox passo a passo Rigoroso remoto possui **isolamento total de internet (no internet access)** — blinda-se contra fetch em URLs abertas estritas nativas atadas.
- Fundamental e prático AWS puro unificado para iterações do tipo "calcule iterativa a massa de juros orgânicos sobre esse volume" corporativo remoto estrutura base.

### Browser Tool (A Sonda Web da AWS)
- Instância unificada conectada de **Headless Chrome** nativamente mantida pura e orquestrada pelo AgentCore na rede.
- Sonda interativa de rede, vasculhando estrutura base principal, navegando simplesmente e lendo formulários com capturas orgânicas exatas.
- Concede simplesmente conectado ao agente visão prática em tempo real e interativa AWS na web global contínua.
- Essencial para rotinas orgânicas AWS de extração: "consulte atrelada e busque estrutura base conectada a bolsa na cotação de mercado atual paralela prática remota."

### Ferramentas Nativas Geridas AWS (Managed Services)
Nestas matrizes da rede prática conectada iterativas, você não providencia clusters atados ou binários do navegador ou patches remotos de segurança sistêmica isolada conectada do sandbox remoto interativo isolado; a AWS, pelo AgentCore prático base unificado conectado, entrega o provisionamento isoladamente unificado AWS.

---

## Deploy Corporativo do Agente Expandido

Acionaremos o empacotador remoto passo a passo simplesmente base AWS (deploy) atualizando in-place a imagem da instanciada atrelada prática AWS estrutura base. A governança unificada AgentCore orquestrará a substituição versionada simplesmente conectada sem interrupções.

```python
import sys; sys.path.insert(0, '..')
from shared import deploy_agent

result = deploy_agent.deploy(
    agent_dir="agent",
    runtime_name="aria_agent",
)

runtime_arn = result["runtime_arn"]
print(f"\nRuntime ARN: {runtime_arn}")
```

---

## Rastreamento Interligado (Enable Tracing for Code Interpreter & Browser Tool)

Providencie organicamente no console simplesmente AWS remoto nativo passo a passo o Tracing estruturado principal conectado destas instâncias AWS para indexar seus logs de execução atrelados orgânicos no AgentCore Observability.

### Code Interpreter (Passo-a-passo)
1. Navegue simplesmente AWS Console conectado para **Amazon Bedrock AgentCore > Built-in tools > Code Interpreter**.
2. No escopo passo a passo base da estrutura base **Tracing**, defina em `Edit`.
3. Configure como ativo interligado estrutura base **Enable** prático puro e salve (Save).

### Browser Tool (Passo-a-passo)
1. Avance simplesmente em **Built-in tools > Browser**.
2. Vá até a seção **Tracing**, edite.
3. Fixe ativo **Enable** e ative simplesmente prático estrutura base remoto.

---

## Construção do Client Base de Invocação Unificada

O acionador de chamadas Rigoroso nativo AWS boto3 (boto3 client) provisionará uma arquitetura conectada envelopada prática paralela nativa na execução para garantir a invocação principal iterativa liminar pura remota conectada AWS `invoke_agent_runtime`.

```python
import boto3, json, uuid
import sys; sys.path.insert(0, '..')
from shared import utils

client = boto3.client("bedrock-agentcore", region_name="us-east-1")

def invoke(prompt):
    """
    Envelopamento simples e nativo remoto para iterar o stream contínuo AWS.
    A cada submissão, uma sessão estrutura base paralela nova (fresh session) é gerada
    para atestar estabilidade iterativa prática remota.
    """
    session_id = str(uuid.uuid4())
    response = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": prompt}).encode(),
    )
    return utils.stream_sse_response(response["response"])
```

---

## Orquestrando o Sandbox: Teste Code Interpreter

Se antes a Aria dependia unicamente das camadas congeladas da rede neural da LLM base, neste exato momento principal interativo contínuo unificado estrutura base AWS ela compila de modo autônomo e invoca remotamente nativo execução isolada **Python** em nuvem estrutura principal.

```python
# Code Interpreter: processamento corporativo isolado em sandbox remota Python
invoke("Calcule matematicamente os juros corporativos sobre R$ 10.000 a 7% de juros orgânicos anuais no prazo massivo de 30 anos")
```

---

## Orquestrando a Malha Web: Teste Browser Tool

A orquestração remota do componente unificado Browser Tool provê à Aria um fluxo contínuo exaustivo web isolado interligado na rede AWS de busca estrutura base interativa atrelada pura web.

```python
# Browser Tool: acionamento nativo Headless Chrome governado pelo AgentCore AWS providenciado
invoke("Qual é o principal destaque noticiário corporativo no Hacker News hoje?")
```

---

```python
import sys; sys.path.insert(0, '..')
from shared import progress

progress.show("03")
```




# Módulo 04: AgentCore Memory -- Persistência Estrutural de Contexto

![Topologia Estrutural Matriz de AgentCore Memory](images/04.drawio.png)

Neste pacote corporativo providenciado, dotaremos a Aria iterativa de **memória persistente estrutural (memory)** para permitir reconhecimento principal simplesmente interligado passo a passo através de conversas remotas (cross-conversations).

---

## Objetivos Arquiteturais de Aprendizado

| Tópico AWS | Aprofundamento Corporativo |
|---|---|
| **AgentCore Memory service** | A fundação gerida na AWS de retenção principal simplesmente paralela e persistente empacotada no ecossistema AWS Bedrock AgentCore nativo estrutura base. |
| **Short-term (STM) vs. Long-term (LTM)** | Diferenciação prática da orquestração interligada entre o buffer conversacional prático imediato e estrutura base iterativa do conhecimento extraído em nuvem longa duração. |
| **Estratégias iterativas de LTM (LTM extraction strategies)** | Interconexões estrutura base simplesmente atadas de resumos estruturados (Session summaries), aprendizado conectado base (user preferences) e dados semânticos factuais isolados (semantic facts). |
| **Strands integration (Matriz iterativa)** | Fluxo em que o módulo isolado estrutura base simplesmente conectado remota **`AgentCoreMemorySessionManager`** é acoplado estrutural no agente. |

## Sincronização Lógica do Ambiente (Catch-up)

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("04")
```

---

## Engenharia Interna Estrutural do AgentCore Memory

O ecossistema **AgentCore Memory** faculta organicamente ao agente em nuvem a arquitetura de reter e buscar simplesmente contínuo informações (remember) estritamente iterativas transpassando sessões (cross sessions). Funciona ininterruptamente gerando em 2 matrizes orgânicas:

### Memória Volátil Interligada de Curto Prazo (Short-term memory - STM)
Quando a malha do agente transmite simplesmente eventos conversacionais para o **AgentCore Memory**, a infraestrutura AWS os indexa restritivamente na estrutura principal iterativa prática na forma isolada nativa de eventos (**events**). Essa esteira gerando atrelada iterativamente captura as transações da invocação contínua. Seu agente reidrata organicamente e interligado a história simplesmente através da invocação de leitura — base iterativa conectada unificada para restaurar um ambiente após interrupções (resume). A orquestração estrutura base destes disparos de eventos na AWS prática também aciona o gatilho das iterações autônomas remota da LTM (detalhado puro abaixo).

### Extração Remota Persistente de Longo Prazo (Long-term memory - LTM)
É o arcabouço cognitivo extraído isolado que persiste (persists across sessions). Conforme o stream providenciado simplesmente envia os turnos para a rede, o ecossistema AgentCore dispara de forma corporativa principal a esteira paralela e autônoma na AWS de instâncias operantes (extraction strategies) destilando as invocações estrutura base simplesmente numa inteligência durável AWS. É a inteligência isolada de ponta a ponta AWS provada.

Estratégias AWS do AgentCore Memory acopláveis iterativas remotas (LTM):

| Estratégia AWS | Instância Python | Namespace (Estrutura de Malha) | O Que Faz (Purpose) |
|---|---|---|---|
| **Resumidor (Session Summarizer)** | `summaryMemoryStrategy` | `/summaries/{actorId}/{sessionId}` | Sintetiza iterativamente as invocações simplesmente base de sessões longas atadas permitindo resgatar remotamente o resumo. |
| **Aprendizado Atado (Preference Learner)** | `userPreferenceMemoryStrategy` | `/preferences/{actorId}` | Detecta e consolida restritamente os gostos unificados de estrutura base do ator (ex: "Programo unificado prático passo a passo em Python invés de Java"). |
| **Extrator Liminar de Fatos (Fact Extractor)** | `semanticMemoryStrategy` | `/facts/{actorId}` | Subtrai principal simplesmente e hospeda os axiomas orgânicos nativos remotos ("Eu componho o quadro corporativo AWS estrutura base da Empresa Corp"). |

> **Documentação Fundamental da Matriz:** [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)

---

### Instanciando o Recurso Base (Create the Memory resource)

A API estrutural AWS simplesmente conectada via boto3 `create_memory` cria e provisiona o espaço estrutura base estrutural do banco AWS de alocação de eventos.

```python
import boto3
from botocore.exceptions import ClientError

region = "us-east-1"
client = boto3.client("bedrock-agentcore-control", region_name=region)

try:
    response = client.create_memory(
        name="AriaMemory",
        description="Memory for Aria personal assistant — conversation persistence and long-term user knowledge",
        eventExpiryDuration=90,  # Dias contínuos atados AWS simplesmente até expurgo autônomo remoto
        memoryStrategies=[
            {
                "summaryMemoryStrategy": {
                    "name": "SessionSummarizer",
                    "description": "Summarizes conversation sessions for quick context retrieval",
                    "namespaces": ["/summaries/{actorId}/{sessionId}"],
                }
            },
            {
                "userPreferenceMemoryStrategy": {
                    "name": "PreferenceLearner",
                    "description": "Learns and stores user preferences across sessions",
                    "namespaces": ["/preferences/{actorId}"],
                }
            },
            {
                "semanticMemoryStrategy": {
                    "name": "FactExtractor",
                    "description": "Extracts and stores factual information from conversations",
                    "namespaces": ["/facts/{actorId}"],
                }
            },
        ],
    )
    memory_id = response["memory"]["id"]
    print(f"Memory created: {memory_id}")
    print(f"   Status: {response['memory'].get('status', 'CREATING')}")

except ClientError as e:
    if "already exists" in str(e):
        print("AriaMemory already exists -- looking it up...")
        # Polling remoto atado simplesmente AWS
        paginator = client.get_paginator("list_memories")
        for page in paginator.paginate():
            for mem in page.get("memories", []):
                if mem["id"].startswith("AriaMemory"):
                    memory_id = mem["id"]
                    print(f"Found existing memory: {memory_id}")
                    break
    else:
        raise
```

### Orquestração Autônoma de Validação (Wait for ACTIVE)

```python
import time

print(f"Waiting for memory {memory_id} to become ACTIVE...")
for i in range(30):
    resp = client.get_memory(memoryId=memory_id)
    memory = resp.get("memory", resp)
    status = memory.get("status", "UNKNOWN")
    print(f"  [{i*10}s] Status: {status}")
    if status == "ACTIVE":
        print("Memory is ACTIVE!")
        break
    if status in ("FAILED", "DELETE_FAILED"):
        print(f"Memory creation failed: {status}")
        break
    time.sleep(10)
```

### Salvando a Credencial de Nuvem

```python
import sys; sys.path.insert(0, '..')
from shared import utils

utils.save_config("memory", {"memory_id": memory_id, "region": region})
print(f"Saved memory_id={memory_id}")
```

---

## Rastreamento Interligado (Enable Tracing for Memory)

Ative ininterrupta e remotamente a rastreabilidade simplesmente AWS Tracing da base de Memory simplesmente conectada AWS no ecossistema:
1. Console AWS > **Amazon Bedrock AgentCore > Memory**.
2. Restrito selecione **AriaMemory**.
3. Na seção iterativa estrutura base **Tracing**, defina em `Edit`.
4. Fixe atado em **Enable** e interconecte (Save).

---

## Implantação Operante (Deploy with Memory)

Transbordaremos a atualização prática iterativa remota simplesmente AWS usando a variável robusta de ambiente `MEMORY_ID`.

```python
import sys; sys.path.insert(0, '..')
from shared.deploy_agent import deploy

result = deploy(
    agent_dir="agent",
    env_vars={"MEMORY_ID": memory_id},
)
runtime_arn = result["runtime_arn"]
```

---

## Invocação de Massa: Teste de Conversação Isolada Atada (Conversation 1)

### Interação Cognitiva (STM recall)

```python
import boto3, json, uuid
import sys; sys.path.insert(0, '..')
from shared import utils

data_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

# Session 1: Insere contexto isolado passo a passo
session_1 = str(uuid.uuid4())
print(f"Session 1: {session_1[:16]}...")

response = data_client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_1,
    payload=json.dumps({
        "prompt": "My name is Alex and I'm a software engineer. I prefer Python over Java.",
        "session_id": session_1,
    }).encode(),
)
utils.stream_sse_response(response["response"])

# Chamada paralela conectada nativamente imediata no mesmo container de sessão AWS base interativa (STM recall)
response = data_client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_1,
    payload=json.dumps({
        "prompt": "What's my name and what language do I prefer?",
        "session_id": session_1,
    }).encode(),
)
utils.stream_sse_response(response["response"])
```

### Nova Sessão Puramente Inabalável: Teste Isolado Remoto (LTM recall)

Criamos uma nova sessão infraestrutura (brand-new session).

```python
# NOVA sessão iterativa prática remota: LTM recall (cross-session)
session_2 = str(uuid.uuid4())
print(f"Session 2 (new): {session_2[:16]}...")

response = data_client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_2,
    payload=json.dumps({
        "prompt": "What do you remember about me?",
        "session_id": session_2,
    }).encode(),
)
utils.stream_sse_response(response["response"])
```

## Dissecação Corporativa Arquitetural AWS do Fluxo (How it works)

- AgentCoreMemorySessionManager injeta e consulta simplesmente AWS a malha.
- **Preferences** usam corte probabilístico Rigoroso (relevance_score=0.7) pois preferência imperativamente orquestra viés autônomo remoto.
- **Facts** usam cortes amplos paralelos na AWS base simplesmente conectada (relevance_score=0.3, top_k=10).
- **Summaries** repousam num delta interativo estrutura base (relevance_score=0.5).

---

```python
import sys; sys.path.insert(0, '..')
from shared.progress import show
show("04")
```




# Módulo 05: AgentCore Gateway & Identity -- Roteamento Avançado de APIs Externas

![Estrutura Gateway & Identity](images/05.drawio.png)

Nesta iteração corporativa atrelada AWS, você provisionará a capacidade estrutura base na Aria de **orquestrar gestão e roteamento de tarefas (manage tasks)**. Conectando a instância base nativa a uma API REST externa via **AgentCore Gateway**, a estrutura base isolada usará tokens de identidade restritivos JWT (Identity), garantindo passo a passo simplesmente o isolamento da privacidade massiva interligada de dados principal por usuário remoto.

---

## Objetivos Arquiteturais de Aprendizado

| Tópico AWS | Aprofundamento Corporativo |
|---|---|
| **AgentCore Gateway** | Ponto de interconexão e roteamento de rede MCP nativo gerenciado na AWS (MCP endpoint) simplesmente atado e operante para conduzir as rotinas das ferramentas de IA isolado para as APIs backend corporativas. |
| **Protocolo de Rede (MCP protocol)** | Mecânica prática AWS onde o Gateway detecta autônomo as interfaces da rede (auto-discovers) e renderiza atado o modelo base das APIs como ferramentas remotas do MCP interligadas. |
| **Identidade de Base e Fluxo (Identity & JWT auth)** | Governança unificada onde o modelo `CUSTOM_JWT` valida e audita a base de tokens de acesso interativos de usuários simplesmente contra a malha AWS do Amazon Cognito nativo. |
| **Rastreamento Identitário Integrado (End-to-end identity flow)** | O conduíte base de rastreio prático contínuo em que o JWT de identidade viaja da Runtime na AWS fluindo pelo Gateway atado simplesmente AWS remoto na API de base. |

## Sincronização Lógica do Ambiente (Catch-up)

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("05")
```

---

## Engenharia Interna Estrutural do AgentCore Gateway

O AgentCore Gateway opera corporativo conectado na função de **managed MCP endpoint**, ancorado em rede simplesmente isolada entre seu agente AWS e o backend sistêmico (APIs). Em contraste com a programação crua estrutura base conectada prática em nuvem simplesmente contínua manual da ferramenta, você espelha a infraestrutura no Gateway e o subsistema AWS:
1. **Auto-descobre (Auto-discovers)** a morfologia e arquitetura REST (métodos iterativos e paths).
2. **Gera simplesmente (Generates MCP tools)** instâncias encapsuladas na AWS de ferramentas que o seu código aciona (ex: `list_tasks`).
3. **Controla Autenticação Subjacente (Handles authentication)** no gap entre a instância paralela de agente base estrutura base e a rede corporativa conectada alvo prática da API (Target API).
4. **Aciona Requisições Interligadas (Routes requests)** no alvo prático remoto embutindo as credenciais simplesmente operantes do papel IAM de rede e execução isolada (Gateway's execution role).

### Topologia AWS Atada dos Alvos (Target types)

O Gateway engloba organicamente e suporta o acoplamento a 5 topologias sistêmicas corporativas unificadas remotas da AWS (backend targets):

| Instância do Alvo Remoto | Finalidade e Descrição AWS |
|---|---|
| **AWS Lambda** | Invoca iterativamente interativa prática unificada a rotina de execução restrita autônoma `Lambda function` atrelada diretamente. |
| **Amazon API Gateway** | Extrai a estrutura base estrutural isolada de uma rede `REST API` paralela da rede (Modelo usado ininterrupto prático neste laboratório corporativo remoto passo a passo). |
| **OpenAPI** | Aloca a submissão de arquivo manifesto de contrato `OpenAPI spec` simplesmente passo a passo. |
| **Smithy** | Recepciona isolado definição sintática e estrutura principal do `Smithy model`. |
| **MCP server** | Ponte transparente de empacotamento simplesmente ligada para acionamento remoto de um ecossistema nativo simplesmente atado remoto (MCP-compatible server). |

### Malhas de Gestão de Autenticação Matriz

| Matriz de Autorização (Auth Mode) | Uso Iterativo de Rede (Use Case) |
|---|---|
| `NONE` | Para requisições em malha pública aberta não-governadas simplesmente AWS isoladas. |
| `CUSTOM_JWT` | Malhas transacionais atadas do cliente onde cada roteamento insere estrutura base isolada principal remota de identidade `JWT`. |
| `AWS_IAM` | Roteamento em camada AWS interligada de ponta a ponta AWS paralela AWS (service-to-service). |

O escopo passo a passo deste curso laboratorial emprega o modelo prático estrutura base `CUSTOM_JWT` conectado no **Amazon Cognito**.

> **[NOTA DE INFRAESTRUTURA AWS]** O agente migrará estritamente neste escopo da submissão unificada IAM (SigV4) nativa paralela de rotinas simplesmente atrelada conectada AWS para validar tokens orgânicos na nuvem via JWT remotos de sessão isolado para permitir o controle de autorização extrema e isolamento de estrutura base `Cedar policy`.

> **Documentação Fundamental da Matriz:** [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)

---

## Engenharia Integrada de Matriz de Identidade (Identity)

No modelo `CUSTOM_JWT`, a esteira flui da seguinte forma AWS iterativa atrelada pura unificada nativa na rede:
1. O usuário se valida (User authenticates) na estrutura base base nativa **Amazon Cognito**, extraindo o Id Token (JWT).
2. A esteira prática providenciada do AgentCore Runtime carrega simplesmente nativo no header AWS `Authorization` o JWT.
3. O script da orquestração paralela do agente envia (forwards) restritamente no ambiente do gateway unificado o token.
4. O AgentCore Gateway verifica iterativamente base a procedência simplesmente na URL `OIDC discovery endpoint` associada no Cognito AWS conectado prático puro.
5. O AgentCore Gateway orquestra o envio do pacote simplesmente isolado para o fluxo da API remota usando o `IAM role credentials` prático.

---

### Instanciando o MCP Gateway (Create the Gateway)

Acionaremos no plano de infraestrutura nativo o endpoint providenciado.

```python
import sys; sys.path.insert(0, '..')
import boto3
from botocore.exceptions import ClientError
from shared import utils

region = utils.get_region()
cfn = utils.get_all_cfn_outputs()

gateway_role_arn = cfn.get("GatewayRoleArn") or cfn.get("GatewayServiceRoleArn")
rest_api_id = cfn.get("ApiGatewayRestApiId") or cfn.get("TaskApiRestApiId")
user_pool_id = cfn.get("UserPoolId") or cfn.get("CognitoUserPoolId")
cognito_client_id = cfn.get("UserPoolClientId") or cfn.get("CognitoClientId")

oidc_discovery_url = (
    f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
    f"/.well-known/openid-configuration"
) if user_pool_id else None

control = boto3.client("bedrock-agentcore-control", region_name=region)

try:
    resp = control.create_gateway(
        name="aria-gateway",
        description="AgentCore Gateway for Aria — routes MCP tool requests to backend APIs",
        roleArn=gateway_role_arn,
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration={
            "customJWTAuthorizer": {
                "discoveryUrl": oidc_discovery_url,
                "allowedAudience": [cognito_client_id],
            }
        },
    )
    gateway_id = resp["gatewayId"]
    print(f"Gateway created: {gateway_id}")

except ClientError as e:
    # Verificação de existência paralela estrutura base simplesmente de colisão AWS...
    pass
```

*(Uma rotina de polling remoto estruturado atado AWS aguardará no pipeline até que o ambiente unificado passo a passo principal mude simplesmente para estado READY).*

---

### Injeção Sistêmica do Alvo da API (Add the Task API target)

Injetaremos Rigoroso o `target` API Gateway.
- `apiGateway`: Comando interativo do autodescobrimento estrutura base paralelo.
- `toolOverrides`: Mascaramento principal conectado de interfaces com descritores semânticos orgânicos.
- `toolFilters`: Defesa em profundidade rígida de rotas providenciadas nativas em nuvem atadas paralela simplesmente interativas (defense in depth).
- `GATEWAY_IAM_ROLE`: Outbound passo a passo autenticado simplesmente prático AWS contínuo restrito passo a passo na estrutura base com IAM role.

```python
try:
    target_resp = control.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name="TaskApi",
        description="Task Management REST API — CRUD operations for user tasks",
        targetConfiguration={
            "mcp": {
                "apiGateway": {
                    "restApiId": rest_api_id,
                    "stage": "prod",
                    "apiGatewayToolConfiguration": {
                        "toolOverrides": [
                            {"path": "/tasks", "method": "GET", "name": "list_tasks",
                             "description": "List all tasks for the current user"},
                            # ... demarcação de outras rotinas AWS base interativas (POST, PUT, DELETE)
                        ],
                        "toolFilters": [
                            {"filterPath": "/tasks", "methods": ["GET", "POST"]},
                            {"filterPath": "/tasks/{id}", "methods": ["PUT", "DELETE"]},
                        ],
                    },
                }
            }
        },
        credentialProviderConfigurations=[
            {"credentialProviderType": "GATEWAY_IAM_ROLE"}
        ],
    )
    target_id = target_resp["targetId"]
except ClientError as e:
    pass
```

---

## Rastreamento Interligado (Enable Tracing for Gateway)

1. Console AWS > **Amazon Bedrock AgentCore > Gateways**.
2. Restrito selecione **aria-gateway**.
3. Na seção iterativa estrutura base **Tracing**, defina em `Edit` > **Enable** > `Save`.

---

## Implantação e Deploy com Gateway

Agora inserimos passo a passo no `env_vars` prático a nova topologia `GATEWAY_ENDPOINT`.

```python
import sys; sys.path.insert(0, '..')
from shared.deploy_agent import deploy
from shared.utils import load_config

memory_cfg = load_config("memory")

env_vars = {}
if memory_cfg:
    env_vars["MEMORY_ID"] = memory_cfg["memory_id"]
env_vars["GATEWAY_ENDPOINT"] = gateway_url

result = deploy(
    agent_dir="agent",
    env_vars=env_vars,
)
```

---

## Invocação Iterativa Puramente Nativa: Autenticação JWT Interligada

Extraímos o JWT do Cognito simplesmente nativo e testamos o escopo de inserção e processamento de fluxo corporativo:

```python
import sys; sys.path.insert(0, '..')
from shared import test_agent

jwt_token = test_agent.get_test_token()

# Invocação 1: Operação de escrita conectada na API
result = test_agent.invoke(
    "Create a task: Learn about AgentCore Gateway",
    jwt_token=jwt_token,
)

# Invocação 2: Orquestração de resgate prático e listagem mantendo sessão AWS (memory)
result = test_agent.invoke(
    "List all my tasks",
    session_id=result["session_id"],
    jwt_token=jwt_token,
)

# Invocação 3: Atualização de campo corporativo
result = test_agent.invoke(
    "Mark the AgentCore Gateway task as completed",
    session_id=result["session_id"],
    jwt_token=jwt_token,
)
```

---

```python
import sys; sys.path.insert(0, '..')
from shared.progress import show
show("05")
```




# Módulo 06: AgentCore Policy -- Blindagem Determinística e Cedar Policies

![Arquitetura AgentCore Policy](images/06.drawio.png)

Neste pacote laboratorial unificado, você orquestrará simplesmente a injeção ininterrupta iterativa corporativa de **Cedar policies** ao longo do conduíte Gateway da Aria, orquestrando via o serviço nativo AWS de governança **AgentCore Policy**.

Distanciando-se simplesmente estrutura base AWS de guardrails efêmeros orgânicos atrelados gerados via engenharia de prompt restritos à interpretação e falha probabilística isolada paralela nativa da LLM (alucinação), a linguagem principal simplesmente Cedar Policy impõe restrição **determinística** absoluta — avalia e restringe implacavelmente estrutura base conectada direto na fronteira unificada AWS do Gateway, num perímetro principal puro paralelo passo a passo exterior à lógica atrelada do agente, ostentando Rigoroso 100% de precisão e rastreabilidade na AWS simplesmente operante.

Não há, nesta estrutura base paralela interativa conectada, alterações em pacotes de agentes. A Aria restritamente opera isolada pura unificada a engine V4 base do Módulo 05. Nosso escopo unificado AWS foca estritamente em **Security & Access Policy**.

---

## Objetivos Arquiteturais de Aprendizado

- **AgentCore Policy**: O processo de forjar simplesmente interligada nativa a `Policy Engine` AWS e orquestrá-la na engrenagem isolada do Gateway.
- **Sintaxe de Matriz Cedar (Cedar language)**: A estrutura corporativa restritiva `permit(principal, action, resource) when { conditions }`.
- **Governança Inabalável (Deterministic guardrails)**: O trunfo arquitetural nativo de forçar restrições em perímetro Gateway invés de regras fluidas subjacentes.
- **Restrição Empírica de Negócio (Business rules)**: Restringir a criação imperativa pura nativa iterativa de tarefas que já iniciam "completadas" (completed).
- **Roteamentos de Tráfego (ENFORCE vs LOG_ONLY)**: Escolha estrutural exata prática interligada do modo operacional base estrutura base.

## Sincronização Lógica do Ambiente (Catch-up)

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("06")
```

---

## A Necessidade Arquitetural Determinística

A diferença unificada paralela de ponta a ponta AWS na regra corporativa *"um usuário jamais pode orquestrar isolado AWS nativo passo a passo uma tarefa já com o status completada"*:

| Estratégia de Bloqueio | Processo Orgânico Matriz (How it works) | Governança e Rastreabilidade (Reliability) |
|---|---|---|
| **Engenharia de Prompt (Prompt-based)** | Injeção no system prompt base nativo. | *Probabilístico*: A malha generativa frequentemente obedece, mas pode ser suplantada ou abstrair (jailbroken). |
| **Política AWS Cedar (Cedar policy)** | `permit(...) unless { action is create_task and status is completed }` | *Determinístico*: O Gateway executa a malha lógica simplesmente externa conectada **antes** de rotear. 100% blindado. |

A avaliação paralela Cedar opera exata e robusta no **Gateway boundary** (Fronteira AWS Gateway) isolada unificada iterativa do agente prático atado nativo AWS estrutura base e fora da alçada LLM. A requisição iterativa morre antes, não atingindo sequer o ambiente simplesmente conectado estrutura base da Target API. 
*(Obs: Cedar é a exata topologia de rede em linguística de estrutura base autorizada simplesmente iterativa operante no [Amazon Verified Permissions](https://aws.amazon.com/verified-permissions/))*

> **Documentação Fundamental da Matriz:** [AgentCore Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html)

---

## Modelagem e Engenharia Base Cedar (Understanding Cedar)

Cedar opera simplesmente unificado estrutura base no modelo passo a passo corporativo atado **principal / action / resource** anexado de escopos condicionais simplesmente restritivos:

```cedar
permit(
  principal,                                                // Quem atado estrutura base invoca (Who)
  action == AgentCore::Action::"TaskApi___create_task",     // Qual rotina operada remota (What)
  resource == AgentCore::Gateway::"<gateway-arn>"           // Ambiente e infraestrutura isolada (Where)
) when {
  !(context.input has status && context.input.status == "completed")
};
```

### Fundamentos Corporativos (Key concepts)
- **Bloqueio Liminar Orgânico AWS (Default deny)** — A esteira iterativa Cedar bloqueia nativo tudo que não é concedido e mapeado `permit`. Toda ação da `tool` interligada necessita de submissão `permit`.
- **Invocação Ação (Actions)** — Nomeada iterativa paralela no escopo e formato `<target-name>___<tool-name>`, que deve coincidir puro e exato ao `toolOverrides` do Gateway. (Ex: `TaskApi___list_tasks`).
- **Escopo e Limite (Resource)** — ARN da infraestrutura do Gateway provado AWS: `AgentCore::Gateway::"<ARN>"`.
- **Malhas de Condição AWS (Conditions)** — Usa restritamente estrutura base `context.input` para inspecionar simplesmente nativo AWS passo a passo a requisição (payload de entrada). Toda restrição nativa conectada precisa de um invólucro restrito passo a passo condicional `when`. O validador rejeita organicamente aprovações universais sem contexto nativo.
- **Roteamento Vazio Permissivo (Sentinel conditions)** — Se a intenção é conceder passagem irrestrita conectada estrutura base iterativa em AWS pura, envie um condicional passo a passo conectado nativo sempre inatingível: `!(context.input has field && context.input.field == "__blocked__")`.

---

### Conexão do Plano Restritivo AWS

```python
import boto3, time
from botocore.exceptions import ClientError
import sys; sys.path.insert(0, '..')
from shared import utils

region = utils.get_region()
control = boto3.client("bedrock-agentcore-control", region_name=region)

gw_config = utils.get_gateway_config(control)
gateway_id = gw_config["gateway_id"]
gateway_arn = gw_config["gateway_arn"]

print(f"Gateway ID:  {gateway_id}")
print(f"Gateway ARN: {gateway_arn}")
```

### Criação Estrutural da Policy Engine

Criamos e instanciamos a máquina restritiva simplesmente (Policy Engine), o escopo que reterá iterativa as políticas.

```python
# Passo 1: Instanciando organicamente AWS Policy Engine
try:
    resp = control.create_policy_engine(
        name="aria_policy_engine",
        description="Policy engine for Aria -- Cedar policy enforcement on Gateway tools",
    )
    engine_id = resp["policyEngineId"]
    engine_arn = resp["policyEngineArn"]
    print(f"Policy Engine created: {engine_id}")

except ClientError as e:
    pass # Lógica de colisão iterativa de poling base AWS
```

### Inserção Iterativa de Malha Cedar (Create Cedar policies)

Como a topologia conectada é `Default Deny`, aprovaremos iterativa simplesmente restritivo quatro instâncias AWS atadas de `tool`.

```python
# Orquestra as 4 Cedar policies interligadas atadas AWS remotas
policies = [
    {
        "name": "permit_list_tasks",
        "description": "Permit listing tasks. Blocks listing only completed tasks.",
        "cedar": (
            f'permit(\n'
            f'  principal,\n'
            f'  action == AgentCore::Action::"TaskApi___list_tasks",\n'
            f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
            f') when {{\n'
            f'  !(context.input has status && context.input.status == "completed")\n'
            f'}};\n'
        ),
    },
    {
        "name": "permit_create_task",
        "description": "Permit creating tasks, but NOT with status completed.",
        "cedar": (
            f'permit(\n'
            f'  principal,\n'
            f'  action == AgentCore::Action::"TaskApi___create_task",\n'
            f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
            f') when {{\n'
            f'  !(context.input has status && context.input.status == "completed")\n'
            f'}};\n'
        ),
    },
    {
        "name": "permit_update_task",
        "description": "Permit all task updates including setting status to completed.",
        "cedar": (
            f'permit(\n'
            f'  principal,\n'
            f'  action == AgentCore::Action::"TaskApi___update_task",\n'
            f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
            f') when {{\n'
            f'  !(context.input has status && context.input.status == "__blocked__")\n'
            f'}};\n'
        ),
    },
    {
        "name": "permit_delete_task",
        "description": "Permit deleting tasks.",
        "cedar": (
            f'permit(\n'
            f'  principal,\n'
            f'  action == AgentCore::Action::"TaskApi___delete_task",\n'
            f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
            f') when {{\n'
            f'  !(context.input has id && context.input.id == "__blocked__")\n'
            f'}};\n'
        ),
    },
]

# Create each policy
for p in policies:
    try:
        resp = control.create_policy(
            policyEngineId=engine_id,
            name=p["name"],
            description=p["description"],
            definition={"cedar": {"statement": p["cedar"]}},
        )
    except ClientError as e:
        pass
```

### O Acelerador NL2Cedar

Você também pode utilizar o motor inteligente corporativo passo a passo AWS de tradução NL2Cedar, enviando linguagem pura abstrata para ele criar nativamente as lógicas orgânicas iterativas AWS do Cedar (Language to Cedar).

```python
control.start_policy_generation(
    policyEngineId=engine_id,
    name="gen_refund_limit",
    resource={"arn": gateway_arn},
    content={"rawText": "Allow customer service agents to process refunds up to 500 dollars"},
)
```

### Interconectando a Policy Engine no Gateway (Attach)

Nós acoplaremos simplesmente conectada estrutura base iterativa o `policy engine` diretamente no Gateway prático usando o parâmetro inflexível de estrutura base operante rígida `ENFORCE`.

```python
import time
time.sleep(5)  # Tempo de espalhamento passo a passo conectado remoto de policy (allow policies to propagate)

# Modo restritivo ENFORCE de bloqueio nativo passo a passo AWS
gw = control.get_gateway(gatewayIdentifier=gateway_id)
update_params = {
    "gatewayIdentifier": gateway_id,
    "name": gw["name"],
    "roleArn": gw["roleArn"],
    "protocolType": gw["protocolType"],
    "authorizerType": gw["authorizerType"],
    "policyEngineConfiguration": {
        "arn": engine_arn,
        "mode": "ENFORCE",
    },
}
if "authorizerConfiguration" in gw:
    update_params["authorizerConfiguration"] = gw["authorizerConfiguration"]

control.update_gateway(**update_params)
print("Policy engine attached to Gateway in ENFORCE mode")
```

---

## Testando a Política Determinística (Test Cedar policy enforcement)

### Teste de Bloqueio (DENIED)
```python
import sys; sys.path.insert(0, '..')
from shared import test_agent

jwt_token = test_agent.get_test_token()

# Será restritivamente obliterado na fronteira estrutura base do Cedar policy (DENIED)
result = test_agent.invoke(
    "Create a task with status completed: Test policy bypass",
    jwt_token=jwt_token,
)
```

### Teste de Liberação Padrão (SUCCEED)
```python
# Liberação estrutura base operante (SUCCEED)
result = test_agent.invoke(
    "Create a task: Test policy enforcement",
    jwt_token=jwt_token,
)
```

## ENFORCE vs LOG_ONLY

| Modalidade de Tráfego | Roteamento Sistêmico | Aplicação Corporativa (Use case) |
|---|---|---|
| **ENFORCE** | Aplica veto (denies). O payload é barrado restritamente e agente acusa falha. | Produção nativa pura — cumprimento inexorável passo a passo simplesmente de blindagem |
| **LOG_ONLY** | Audita restritamente, rastreia unificado na infraestrutura nativa e emite na AWS estrutura base o log, todavia permite acesso estrutura base e rota do tráfego prático AWS de base robusta rígida. | Testes em nuvem (Testing) — depuração paralela iterativa prática na estrutura base antes da transição simplesmente iterativa de restrição final. |

---

```python
import sys; sys.path.insert(0, '..')
from shared.progress import show
show("06")
```




# Módulo 07: Observability & Evaluations -- Telemetria e Monitoramento em Produção

![Arquitetura de Observabilidade e Avaliação](images/07.drawio.png)

Até o escopo corporativo providenciado no momento, iteramos em rotinas nativas AWS base subjacentes (Tracing) de cada infraestrutura AgentCore. A estrutura base Runtime exportou rastros (OpenTelemetry traces) desde o Módulo 02, enquanto as sessões AWS nativas de Memory e Gateway orquestram tracing nativo passo a passo providenciado puro paralelo estrutura base no Módulo 04 e 05, respectivamente.

Nesta arquitetura base nativa AWS isolada iterativa final atrelada, você mergulhará nesse oceano providenciado simplesmente de dados logados orgânicos, transbordando o deploy blindado de produção V5 da Aria e instanciando avaliadores de qualidade (custom evaluators) orquestrando passo a passo pontuação cognitiva prática contínua corporativa em malha da AWS.

---

## Objetivos Arquiteturais de Aprendizado

- **Exploração Estrutural de Malhas Roteadas (Exploring traces)**: Orquestração no dashboard corporativo AWS do *CloudWatch GenAI Observability* monitorando iterações nativas de ferramentas (Gateway e Memory).
- **Entendimento da Esteira Matriz (Trace pipeline)**: Mecânica interligada do `ADOT instrumentation` acoplada restritamente ao `X-Ray Transaction Search`.
- **Avaliadores Orgânicos Interligados (Custom evaluators)**: Implementação conectada remota nativa simplesmente do *LLM-as-judge* pontuando com nota a qualidade estruturada AWS base interligada paralela da orquestração de resposta (response quality) e gestão isolada provada da ferramenta (tool usage).
- **Matriz Ativa Avaliativa (Online evaluations)**: Interligado monitoramento autônomo AWS corporativo contínuo via submissão conectada base pura amostral (sampling rates).

## Sincronização Lógica do Ambiente (Catch-up)

```python
import sys; sys.path.insert(0, '..')
from shared.ensure_ready import ensure_ready

config = ensure_ready("07")
```

---

## Engenharia Interna da Malha Base de Observabilidade AWS

Sua orquestração prática nativa em nuvem instanciou principal métricas ocultas simplesmente atadas de tracing:

### Tracing de Matriz do Agente em Nuvem
A cada comando executivo corporativo do deploy, o emulador injetou isoladamente:
1. `aws-opentelemetry-distro` englobado diretamente ao script da Aria.
2. Involucro corporativo AWS de `opentelemetry-instrument` interligando autoinstrumentação de API calls (HTTP iterativas) puro e isolado conectado prático.
3. Fixou providenciado `tracingConfiguration={"enabled": True}` ininterrupto no AWS Runtime nativo.

### Tracing Atado Nativo de Ferramentas (Resource-level tracing)
Ao editar as abas e instanciar `Tracing > Enable` nas topologias de AWS Memory e AWS Gateway simplesmente atrelada.

### Métricas Automáticas Nativas Matriz (Service-vended metrics)
Métricas brutas (Invocations, latência iterativa paralela base nativa remota unificada, CPU e RAM prática AWS conectada remota em malha, erros) exportadas com zero acoplamento na camada paralela simplesmente interativa `Bedrock-AgentCore` do CloudWatch nativo.

> **Documentação Fundamental da Matriz:** [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)

---

## Instanciando a Imagem Blindada Interativa de Produção (V5)

```python
import sys; sys.path.insert(0, '..')
from shared import utils, deploy_agent

# Compila as chaves transacionais estrutura base providenciada iterativa AWS (Environment variables)
env_vars = {}

memory_config = utils.load_config("memory")
if memory_config:
    env_vars["MEMORY_ID"] = memory_config["memory_id"]

gateway_config = utils.load_config("gateway")
if gateway_config:
    env_vars["GATEWAY_ENDPOINT"] = gateway_config.get("gateway_url", "")

# Deploy passo a passo restritivo unificado puro
runtime_config = deploy_agent.deploy(
    agent_dir="agent",
    env_vars=env_vars,
)
```

---

## Executando as Submissões Autônomas AWS de Telemetria (Exploração)

Geraremos instâncias iterativas simplesmente atreladas arquitetura conectada na AWS e rastrearemos no portal nativo.

```python
import sys; sys.path.insert(0, '..')
from shared import test_agent
jwt_token = test_agent.get_test_token()

# Trace 1: Matemática exata (Força iterativa de renderização estrutura base no sandbox Code Interpreter)
result = test_agent.invoke("Qual a raiz quadrada robusta de 144?", jwt_token=jwt_token)

# Trace 2: Orquestração interligada (Aplica principal Gateway + Cedar policy simplesmente restritiva)
result = test_agent.invoke(
    "Crie uma task corporativa restrita estrutura base conectada interativa iterativa remota AWS na nuvem: Avaliar a estrutura base",
    jwt_token=jwt_token,
)

# Trace 3: Escrita persistente estruturada conectada remota (Força iterativa Memory LTM)
result = test_agent.invoke(
    "Guarde restritamente prático e robusta que prefiro dark mode nas matrizes corporativas",
    jwt_token=jwt_token,
)

# Trace 4: Recuperação prática da rede externa
result = test_agent.invoke("Exiba simplesmente base todas as minhas tarefas corporativas", jwt_token=jwt_token)
```

---

## Roteiro AWS: Matriz Estrutural no CloudWatch

Acesse no painel interligado: **CloudWatch Console > Application Signals > GenAI Observability > Bedrock AgentCore**.

1. **Aba Agents**: Matriz (Root span), Invocação Cognitiva Base (LLM spans), Execução conectada AWS de ferramentas (Tool spans).
2. **Aba Memory**: Logs orgânicos extraídos isolados da AWS de `CreateEvent`, e da engrenagem prática paralela estrutura principal (Consolidation processing).
3. **Aba Built-in Tools**: CPU, processamento RAM passo a passo prático atado de Sandbox Code Interpreter.
4. **Aba Gateways**: Disparo no conduíte e veto simplesmente isolado nativamente AWS gerado pela **Cedar Policy** (policy evaluation results infraestrutura interativa).

---

## Avaliadores Autônomos Remotos AWS (Custom Evaluators)

A observabilidade nativa dita *o que* a máquina orquestrou; a estrutura base paralela de **Avaliação** audita unificada iterativa AWS em *qual excelência e qualidade (how well)*.
Você utiliza simplesmente um **LLM-as-judge** (Juiz IA), definindo: Escala Base (Rating scale), Instruções de auditoria prática, e o nível (TRACE para ações precisas; SESSION para contexto massivo atado).

> **Documentação AWS Matriz Base:** [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)

### Criando o Juiz 1: ResponseQuality (SESSION level)

Este avaliador lê a sessão longa conectada na AWS e atribui nota 1 a 5 simplesmente gerando prático interativo estrutura base.

```python
import boto3
from botocore.exceptions import ClientError
import sys; sys.path.insert(0, '..')
from shared import utils

region = utils.get_region()
control = boto3.client("bedrock-agentcore-control", region_name=region)

# A rubrica (instructions) conectada possui formatação robusta restrita para extrair a carga (placeholders) nativa AWS:
response_quality_instructions = """Você avalia corporativamente a excelência principal da Aria.
Contexto:
{context}
Ferramentas nativas atadas providenciadas estrutura base AWS disponíveis base:
{available_tools}
Trajetória restrita iterativa estruturada interligada:
{actual_tool_trajectory}

Escala (Rating):
5 - Excelente: Resposta simplesmente cirúrgica prática conectada corporativa.
4 - Boa... [omitido para concisão]"""

try:
    resp = control.create_evaluator(
        evaluatorName="ResponseQuality",
        description="Evaluates helpfulness, accuracy, and completeness of responses",
        level="SESSION",
        evaluatorConfig={
            "llmAsAJudge": {
                "instructions": response_quality_instructions,
                "ratingScale": {
                    "numerical": [
                        {"value": 1, "label": "Unacceptable", "definition": "Wrong"},
                        {"value": 5, "label": "Excellent", "definition": "Fully addresses request"},
                    ],
                },
                "modelConfig": {
                    "bedrockEvaluatorModelConfig": {
                        "modelId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    }
                },
            }
        },
    )
    response_quality_id = resp["evaluatorId"]
except ClientError as e:
    pass
```

### Criando o Juiz 2: ToolUsage (TRACE level)

Auditor focado iterativamente em avaliar se as *tools* providenciadas nativas em rede AWS simplesmente iterativas subjacentes remotas orgânicas da AWS base matrizes iterativas foram invocadas na malha nativa conectada.

```python
tool_usage_instructions = """Você é um auditor robusta focado restritamente na exata orquestração remota conectada de ferramentas estrutura base simplesmente base nativa AWS iterativa... {context}, {assistant_turn}..."""

try:
    resp = control.create_evaluator(
        evaluatorName="ToolUsage",
        description="Evaluates tool selection and usage efficiency",
        level="TRACE",
        evaluatorConfig={
            "llmAsAJudge": {
                "instructions": tool_usage_instructions,
                "ratingScale": { # Configuração de notas base nativa prática remota AWS
                    "numerical": [
                        {"value": 1, "label": "Critical failure", "definition": "Severe misuse"},
                        {"value": 5, "label": "Optimal", "definition": "Exactly the right tools"},
                    ],
                },
                "modelConfig": {
                    "bedrockEvaluatorModelConfig": {
                        "modelId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    }
                },
            }
        },
    )
    tool_usage_id = resp["evaluatorId"]
except ClientError as e:
    pass
```

---

## Ativação Interativa Puramente Remota Online (Online evaluation)

Acoplamento ininterrupto prático conectado (sampling rate) lendo logs nativos simplesmente de rastreio corporativos interligados na AWS atados e gerando telemetria em tempo real prática no CloudWatch (100% sampling para o laboratório).
Utiliza a configuração `create_online_evaluation_config` e avaliadores corporativos construídos inativos nativos AWS (`Builtin.Helpfulness`).

```python
runtime_config = utils.load_config("runtime")
runtime_id = runtime_config["runtime_id"]
runtime_name = runtime_config["runtime_name"]

log_group = f"/aws/bedrock-agentcore/runtimes/{runtime_id}-DEFAULT"
service_name = f"{runtime_name}.DEFAULT"

cfn_outputs = utils.get_all_cfn_outputs()
eval_role_arn = cfn_outputs["EvaluationRoleArn"]

try:
    config = control.create_online_evaluation_config(
        onlineEvaluationConfigName="aria_quality_monitor",
        description="Monitor Aria response quality — 100% sampling for workshop",
        rule={"samplingConfig": {"samplingPercentage": 100.0}},
        dataSourceConfig={
            "cloudWatchLogs": {
                "logGroupNames": [log_group],
                "serviceNames": [service_name],
            },
        },
        evaluators=[
            {"evaluatorId": "Builtin.GoalSuccessRate"},
            {"evaluatorId": "Builtin.Helpfulness"},
        ],
        evaluationExecutionRoleArn=eval_role_arn,
        enableOnCreate=True,
    )
except ClientError as e:
    pass

# Salva topologia de Juiz corporativo
eval_config = {
    "custom_evaluators": {
        "ResponseQuality": response_quality_id if "response_quality_id" in dir() else "existing",
        "ToolUsage": tool_usage_id if "tool_usage_id" in dir() else "existing",
    },
    "builtin_evaluators": ["Builtin.GoalSuccessRate", "Builtin.Helpfulness"],
}
utils.save_config("evaluations", eval_config)
```

---

## Teste Isolado Exato Atado On-demand de Juiz IA (On-demand evaluation)

O teste gerando prático on-demand (Manual e sob demanda nativa conectada AWS corporativa remota interativa) orquestra o `evaluate()` num sub-espaço simplesmente rastreado passo a passo paralelo nativo restrito do log `CloudWatch Logs Insights`.

```python
import sys; sys.path.insert(0, '..')
from shared import test_agent

jwt_token = test_agent.get_test_token()

# Invoca a Aria
result = test_agent.invoke(
    "Calcule corporativo juros compostos de R$ 5.000 a 6% para 10 anos, crie a task base nativa AWS conectada de rever carteira interativa prática na estrutura base...",
    jwt_token=jwt_token,
)
eval_session_id = result["session_id"]
```

Extraindo o log do CloudWatch `get_session_spans(eval_session_id)` e enviando para o AgentCore corporativo atado:

```python
data_client = boto3.client("bedrock-agentcore", region_name=region)
# Omitindo rotina repetitiva Python e injetando:
response = data_client.evaluate(
    evaluatorId=rq_id,
    evaluationInput={"sessionSpans": session_spans},
)
# A LLM estrutura base provada emitirá a pontuação (Score, Tokens, Explanation inabaláveis remotos)
```

---

```python
import sys; sys.path.insert(0, '..')
from shared.progress import show
show("07")
```




# Módulo 08: Full Deployment -- Orquestração Corporativa Absoluta

![Topologia Global Matriz](images/08.drawio.png)

**Nível Máximo Alcançado! (Congratulations!)**
Você forjou do absoluto zero a **Aria**, uma base de Inteligência Artificial simplesmente prática em status unificado e robusta de produção isolada, sendo operada remotamente por todos os 9 ecossistemas estruturais unificados da AWS no Amazon Bedrock AgentCore. Este marco passo a passo atado e remoto interligado orquestra a revisão profunda, atesta simplesmente estrutura base a funcionalidade iterativa liminar das integrações isoladas simplesmente atreladas AWS.

---

## Retrospectiva Arquitetural da Matriz AWS (Architecture review)

| # | Serviço AgentCore | Módulo Nativo | Função Estrutural AWS na Malha (Role) |
|---|---|---|---|
| 1 | **Runtime** | 02 | Hospeda corporativo o framework base Strands nativo AWS remoto de ponta a ponta AWS iterativa unificada. |
| 2 | **Code Interpreter** | 03 | Sandbox conectado estrutura base restrito passo a passo Python (matemática). |
| 3 | **Browser Tool** | 03 | Conduíte web AWS puro prático e gerando nativamente atado estrutura base (Web browsing). |
| 4 | **Memory** | 04 | Interação AWS LTM/STM (fatos atados, preferências, resumos de sessão provados interligados). |
| 5 | **Gateway** | 05 | Ponte de rede MCP protocolo isolado conectando APIs de backend matrizes puras iterativas AWS. |
| 6 | **Identity** | 05 | AWS JWT gerando estrutura base `CUSTOM_JWT` (segregação corporativa isolada estrutura base base nativa iterativa). |
| 7 | **Policy** | 06 | Blindagem **determinística** implacável via restrições estrutura base operantes Cedar (Cedar policy enforcement). |
| 8 | **Observability** | 07 | ADOT SDK simplesmente unificado injetando logs no CloudWatch (OpenTelemetry tracing). |
| 9 | **Evaluations** | 07 | Auditoria estrutura base LLM-as-judge na nuvem prática conectada corporativa AWS interligada. |
| -- | **Frontend** | 08 | Aplicação Web rígida prática conectada gerando (Streaming nativo passo a passo AWS puro e interativo Cognito estrutura base auth). |

## Sincronização Lógica do Ambiente

```python
import sys; sys.path.insert(0, '..')
import boto3, json, uuid
from shared import utils

region = utils.get_region()
control = boto3.client("bedrock-agentcore-control", region_name=region)
data_client = boto3.client("bedrock-agentcore", region_name=region)

print(f"Region:  {region}")
print(f"Account: {utils.get_account_id()}")
```

---

## Atestando a Integridade Sistêmica AWS (Verify all services)

As submissões base iterativas via *boto3* provam a integridade e atestam que todos os módulos foram gerados atados e a rede AWS simplesmente interativa responde simplesmente conectada sem falhas.

### 1. Auditoria Runtime
```python
# Verify Runtime prático AWS
runtime_config = utils.load_config("runtime")
if runtime_config:
    runtime_id = runtime_config["runtime_id"]
    rt = control.get_agent_runtime(agentRuntimeId=runtime_id)
    print(f"Runtime Status: {rt.get('status', 'UNKNOWN')}")
```

### 2. Auditoria Memory
```python
# Verify Memory gerando prático passo a passo
memory_config = utils.load_config("memory")
if memory_config:
    memory_id = memory_config["memory_id"]
    mem = control.get_memory(memoryId=memory_id)
    mem_data = mem.get("memory", mem)
    print(f"Memory Status: {mem_data.get('status', 'UNKNOWN')}")
```

### 3. Auditoria Gateway
```python
# Verify Gateway corporativo atado
gateway_config = utils.load_config("gateway")
if gateway_config:
    gateway_id = gateway_config["gateway_id"]
    gw = control.get_gateway(gatewayIdentifier=gateway_id)
    print(f"Gateway Status: {gw.get('status', 'UNKNOWN')} - Protocol: {gw.get('protocolType')}")
```

### 4. Auditoria Policy Engine
```python
# Verify Policy Engine restritivo nativo AWS
policy_config = utils.load_config("policy")
if policy_config:
    engine_id = policy_config["policy_engine_id"]
    engine = control.get_policy_engine(policyEngineId=engine_id)
    print(f"Policy Engine Status: {engine.get('status', 'UNKNOWN')} | Mode: {policy_config.get('enforcement_mode')}")
```

### 5. Auditoria Evaluations
```python
# Verify Evaluations robusta atado remota
evals_config = utils.load_config("evaluations")
if evals_config:
    custom_evals = evals_config.get("custom_evaluators", {})
    print(f"Custom evaluators active: {len(custom_evals)}")
```

---

## Implantação e Transbordo de Frontend Interativo AWS (Deploy the frontend web application)

Provisionaremos iterativa simplesmente prático a casca e malha web base nativa AWS isolada para interagir simplesmente estrutura base AWS com Aria via navegador corporativo AWS restrito interativo puro atado remoto.
A infraestrutura (S3, CloudFront, Lambda, API Gateway) instanciada pelo CloudFormation será injetada para conectar-se ininterrupta ao AgentCore nativo estrutura base:
1. **Ativa o OAuth AWS no Runtime** para invocações orgânicas AWS estrutura base HTTPS restritas diretas via Cognito JWT remoto.
2. Injeta as rotas `POST /chat`.
3. Injeta o passo a passo estrutura base isolada unificada simplesmente AWS puro Memory ID.
4. Faz a estrutura base base gerando de upload passo a passo interligado de `config.js` via Amazon S3 prático puro.
5. Invalida cache de distribuição passo a passo simplesmente nativo no **CloudFront cache**.

```python
import sys; sys.path.insert(0, 'scripts')
from deploy_frontend import deploy

# Executa emulação providenciada prática de infraestrutura corporativa
frontend_config = deploy()
```

---

## Interação AWS Viva Matriz na Plataforma Web

Sua esteira AWS conectada Web nativa está na nuvem (Live).

```python
frontend_config = utils.load_config("frontend")
if frontend_config:
    url = frontend_config.get("cloudfront_url", "")
    print(f"Aria Web Application URL: {url}")
    print("Username: workshop@example.com")
    print("Password: WorkshopPass123!")
```

Teste a malha iterativa simplesmente base nativa AWS e os escopos corporativos unificados em uma única conversa isolada remota:
1. *"Grave simplesmente na nuvem que o Python prático estrutura base gerando iterativa atado é vital para mim."* (Testa Memory LTM).
2. *"Aja na nuvem gerando calculando a renderização paralela iterativa dos 20 números Fibonacci."* (Testa Code Interpreter).
3. *"Crie a tarefa prática estrutura base conectada: Aprender AgentCore passo a passo AWS."* (Testa Gateway nativamente remoto e Cedar Policy interligada).
4. *"Use orquestração paralela estrutura base para acessar AWS atado restrito e buscar iterações atadas notícias do re:Invent."* (Testa Browser Tool AWS pura unificada robusta providenciada).

---

## Governança Absoluta: Arquitetura Final de AgentCore

O insight unificado estrutural da AWS simplesmente base:
> "Aria prática simplesmente operante conectada permaneceu corporativa e simples (Um agent Strands padrão passo a passo estrutura base prático em nuvem). Toda a esteira massiva prática de produção robusta (Tokens OAuth, Políticas Cedar, Avaliadores ADOT AWS nativos iterativos remotos) e segurança isolada repousa unificada iterativa organicamente injetada conectada AWS simplesmente **na plataforma de base do AgentCore**, sem poluir o núcleo simplesmente limpo prático passo a passo base da Aria."

---

## Procedimentos Puramente Restritos de Cleanup

Para destruição de estrutura base nativa AWS unificada corporativa e cessar custeios após a sessão interligada prática:

```python
# Destrói os motores provisionados pelo curso
import sys; sys.path.insert(0, '..'); sys.path.insert(0, 'scripts')
from cleanup import cleanup

# Descomente principal simplesmente para limpar a malha do laboratório estrutura base:
# cleanup(auto_confirm=True)
```

*(Obs: Os stacks base de recursos paralelos CloudFormation `cfn-template` devem ser suprimidos remotamente no portal de console da nuvem prática iterativa).*

---

```python
import sys; sys.path.insert(0, '..')
from shared.progress import show
show("08")
```


