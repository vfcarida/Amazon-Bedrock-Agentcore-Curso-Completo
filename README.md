# Amazon Bedrock AgentCore: Complete Course

Build **Aria**, a production-grade AI assistant using all 9 Amazon Bedrock AgentCore services. By the end of this course, you will have a fully deployed assistant with streaming responses, persistent memory, code execution, web browsing, API integrations, policy enforcement, full observability, and automated quality evaluation.

![Aria](images/aria-home.png)

## What you will build

**Aria** is a personal AI assistant where users can:

- **Log in** via Amazon Cognito OAuth and see their own workspace
- **Chat** with streaming AI responses in real-time
- **Execute code** -- ask Aria to run Python for calculations, data analysis, or charting
- **Browse the web** -- ask Aria to look things up online
- **Manage tasks** -- Aria connects to a Task Management API through AgentCore Gateway
- **Remember everything** -- conversations and user preferences persist across sessions via AgentCore Memory

![Architecture](images/full-architecture.drawio.png)

## Modules

Each module builds on the previous one, progressively adding AgentCore capabilities:

| Module | Title | What you will learn |
|--------|-------|---------------------|
| [00](00-prerequisites/) | **Prerequisites** | Deploy foundational AWS infrastructure (Cognito, API Gateway, DynamoDB, IAM) |
| [01](01-introduction/) | **Introduction & AgentCore CLI** | AgentCore architecture, all 9 services, CLI commands |
| [02](02-runtime/) | **AgentCore Runtime** | Deploy your agent to Runtime with streaming and auto-scaling |
| [03](03-tools/) | **AgentCore Tools** | Add Code Interpreter and Browser Tool for code execution and web browsing |
| [04](04-memory/) | **AgentCore Memory** | Add short-term and long-term memory with 3 extraction strategies |
| [05](05-gateway-identity/) | **Gateway & Identity** | Connect to APIs via Gateway, configure JWT auth, understand identity flow |
| [06](06-policy/) | **AgentCore Policy** | Enforce business rules with Cedar policies at the Gateway boundary |
| [07](07-observability-evaluations/) | **Observability & Evaluations** | Traces, metrics, logs, LLM-as-a-Judge quality monitoring |
| [08](08-full-deployment/) | **Full Deployment** | Deploy a web frontend, run integration tests, review the full architecture |

## Agent versions

The agent evolves across modules, deploying to the same Runtime (update in place):

- **V1** (Module 02): Basic chat -- Strands + BedrockModel
- **V2** (Module 03): + Code Interpreter + Browser
- **V3** (Module 04): + Memory (3 LTM strategies)
- **V4** (Module 05): + Gateway MCP client + JWT forwarding
- **V5** (Module 07): + Production error handling

## Prerequisites

### Tools

You need the following installed on your machine:

- **Python 3.12+**
- **Node.js 20+** and **npm**
- **AWS CLI v2** -- configured with credentials for an AWS account
- **AWS CDK** -- `npm install -g aws-cdk`
- **AgentCore CLI** -- `npm install -g @aws/agentcore` (see [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-cli.html))
- **uv** (Python package manager) -- `pip install uv` or [install instructions](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker** -- for building agent deployment packages
- **Jupyter** -- `pip install jupyter ipykernel`

### AWS permissions

Your AWS credentials need broad permissions across these services:
- Amazon Bedrock (model invocation + AgentCore)
- Amazon Cognito
- API Gateway
- DynamoDB
- Lambda
- S3
- IAM (role and policy management)
- CloudFormation
- CloudWatch & X-Ray
- Amazon Verified Permissions
- ECR

> For a detailed IAM policy you can attach to your user/role, see the reference policy used in the managed workshop environment: it covers all required permissions across these services.

### AWS Region

This workshop is designed for **us-east-1**. AgentCore availability may vary by region -- check the [AgentCore documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html) for current region support.

## Getting started

### 1. Deploy the prerequisites CloudFormation stack

The stack in [`infrastructure/prerequisites.yaml`](infrastructure/prerequisites.yaml) creates all foundational resources: Cognito user pool, Task Management API (DynamoDB + Lambda + API Gateway), IAM roles for AgentCore services, S3 buckets, CloudFront distribution, and observability configuration.

```bash
aws cloudformation deploy \
  --template-file infrastructure/prerequisites.yaml \
  --stack-name agentcore-workshop-prerequisites \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

> **X-Ray Transaction Search:** The stack enables [X-Ray Transaction Search](https://docs.aws.amazon.com/xray/latest/devguide/xray-transaction-search.html) by default, which is required for the observability module. Only one Transaction Search configuration is allowed per account per region. If your account already has it enabled, add `--parameter-overrides EnableTransactionSearch=false` to the deploy command above to skip creating it. The prerequisites notebook (`00-prerequisites/notebook.ipynb`) includes a cell that checks whether Transaction Search is already active in your account.

This takes approximately 5-10 minutes. You can monitor progress in the [CloudFormation console](https://console.aws.amazon.com/cloudformation/).

**What the stack creates:**

| Resource | Purpose |
|----------|---------|
| Cognito User Pool + Client | User authentication (OAuth 2.0) |
| DynamoDB table (`aria-tasks`) | Task storage for the Task Management API |
| Lambda + API Gateway | Task Management REST API (CRUD) |
| S3 bucket (`aria-agent-code-*`) | Agent code artifact storage |
| S3 bucket (`aria-frontend-*`) | Frontend static files |
| CloudFront distribution | CDN for the frontend |
| IAM roles | Separate roles for Runtime, Gateway, and Evaluations |
| CloudWatch + X-Ray config | Observability infrastructure |

### 2. Set up your Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install jupyter ipykernel boto3
python -m ipykernel install --user --name workshop --display-name "workshop"
```

### 3. Open the first notebook

Open `00-prerequisites/notebook.ipynb` in your preferred environment:

- **VS Code** -- open the file directly (the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) handles `.ipynb` natively)
- **JetBrains (PyCharm, IntelliJ)** -- open the file directly (built-in Jupyter support)
- **Jupyter in the browser** -- run `jupyter notebook 00-prerequisites/notebook.ipynb`

When prompted, select the **workshop** kernel you created in step 2. Run cells top-to-bottom with `Shift+Enter`.

### 4. Work through modules in order

Follow the notebooks sequentially (00 through 08). Each module:
- Starts with a **catch-up cell** (`ensure_ready`) that checks and creates any missing resources from previous modules
- Contains markdown explanations of the concepts and architecture
- Has code cells that build and deploy each piece
- Ends with a link to the next module

> **Smart catch-up:** You can start at any module. The `ensure_ready()` function at the top of each notebook detects what exists, creates anything missing, and fixes broken resources.

### 5. Clean up

Module 08 includes cleanup instructions. You can also delete all resources by running:

```bash
aws cloudformation delete-stack \
  --stack-name agentcore-workshop-prerequisites \
  --region us-east-1
```

And use the cleanup notebook in `99-admin/` to remove any AgentCore resources (Runtimes, Gateways, Memory stores, etc.) that were created outside of CloudFormation.

## Directory structure

```
.
├── infrastructure/
│   └── prerequisites.yaml           # CloudFormation stack (Cognito, APIs, IAM, S3, etc.)
├── shared/                          # Shared utilities (imported by all notebooks)
│   ├── utils.py                     # AWS helpers, config persistence, polling
│   ├── deploy_agent.py              # Package + deploy agent to Runtime
│   ├── ensure_ready.py              # Smart catch-up (idempotent resource creation)
│   ├── test_agent.py                # Invoke deployed agent + JWT helpers
│   ├── chat.py                      # Chat/conversation utilities
│   └── progress.py                  # Visual progress tracker
├── 00-prerequisites/notebook.ipynb  # Verify environment & infrastructure
├── 01-introduction/notebook.ipynb   # AgentCore architecture & CLI
├── 02-runtime/                      # Deploy first agent
│   ├── notebook.ipynb
│   └── agent/                       # Aria V1 (basic conversational agent)
├── 03-tools/                        # Add code execution & web browsing
│   ├── notebook.ipynb
│   └── agent/                       # Aria V2
├── 04-memory/                       # Add persistent memory
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V3
│   └── scripts/
├── 05-gateway-identity/             # API access & JWT auth
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V4
│   └── scripts/
├── 06-policy/                       # Cedar policy enforcement
│   ├── notebook.ipynb
│   ├── policies/                    # Cedar policy files
│   └── scripts/
├── 07-observability-evaluations/    # Tracing & quality monitoring
│   ├── notebook.ipynb
│   ├── agent/                       # Aria V5 (production-hardened)
│   └── scripts/
├── 08-full-deployment/              # Frontend, integration tests, full review
│   ├── notebook.ipynb
│   ├── cdk/                         # CDK app for frontend infrastructure
│   ├── frontend/                    # Web frontend source
│   └── scripts/
├── 99-admin/                        # Cleanup utilities
└── images/                          # Architecture diagrams
```

## Estimated time

1-2 hours for the complete course.

## Estimated cost

$1-5 depending on usage, dominated by Bedrock model invocation costs. Cleanup instructions are provided in Module 08 and the 99-admin folder.

## Key documentation

- [AgentCore Overview](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-runtime.html)
- [AgentCore Memory](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-memory.html)
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-gateway.html)
- [AgentCore Identity](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-identity.html)
- [AgentCore Policy](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-policy.html)
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-observability.html)
- [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-evaluations.html)
- [Strands Agents SDK](https://strandsagents.com)

## Security

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
