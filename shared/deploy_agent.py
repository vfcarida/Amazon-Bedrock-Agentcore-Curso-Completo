"""Deploy or update an agent on AgentCore Runtime.

Used by every module from 02-runtime onward. Handles:
- Packaging agent code into a zip
- Uploading to S3
- Creating a new Runtime OR updating an existing one
- Waiting for READY status

The deploy() function is the main entry point, designed to be called
from Jupyter notebook cells.
"""

import os
import uuid
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from . import utils


def package_agent(agent_dir: str | Path, output_path: str | None = None) -> str:
    """Create a zip package from the agent directory with bundled dependencies.

    Installs requirements.txt into a staging directory using uv, targeting
    the AgentCore Runtime's aarch64 Linux environment, then bundles
    everything into a single zip. This matches the official AgentCore CLI
    packaging approach.

    Args:
        agent_dir: Path to the agent source code directory.
        output_path: Where to write the zip. Defaults to /tmp/<random>.zip.

    Returns:
        Path to the created zip file.
    """
    import subprocess
    import shutil
    import tempfile

    agent_path = Path(agent_dir).resolve()
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent directory not found: {agent_dir}")

    if output_path is None:
        output_path = f"/tmp/aria-agent-{uuid.uuid4().hex[:8]}.zip"

    skip_patterns = {"__pycache__", ".pyc", ".git", ".DS_Store", ".env"}

    # Instala as dependências numa pasta temporária se houver um requirements.txt
    requirements_file = agent_path / "requirements.txt"
    deps_dir = None
    if requirements_file.exists():
        deps_dir = tempfile.mkdtemp(prefix="agentcore-deps-")
        # Tenta encontrar a versão certa da biblioteca de acordo com a arquitetura oficial do AgentCore
        platforms = ["aarch64-manylinux2014", "aarch64-manylinux_2_28", "aarch64-manylinux_2_34"]
        installed = False
        for platform in platforms:
            print(f"📥 Installing dependencies (platform: {platform}) ...")
            result = subprocess.run(
                [
                    "uv", "pip", "install",
                    "--target", deps_dir,
                    "--python-platform", platform,
                    "--python-version", "3.12",
                    "--only-binary", ":all:",
                    "-r", str(requirements_file),
                    "--quiet",
                ],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  Dependencies installed ({platform}).")
                installed = True
                break
            else:
                # Limpa a pasta temporária para tentar novamente, caso falhe
                shutil.rmtree(deps_dir, ignore_errors=True)
                os.makedirs(deps_dir, exist_ok=True)
                print(f"  Platform {platform} failed, trying next...")

        if not installed:
            raise RuntimeError(
                f"Failed to install dependencies for all platform candidates.\n"
                f"Last error: {result.stderr}"
            )

    file_count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Adiciona os arquivos das dependências no zip primeiro (ficam como camada base)
        if deps_dir:
            deps_path = Path(deps_dir)
            for file_path in sorted(deps_path.rglob("*")):
                if not file_path.is_file():
                    continue
                relative = str(file_path.relative_to(deps_path))
                if any(skip in relative for skip in skip_patterns):
                    continue
                zf.write(file_path, file_path.relative_to(deps_path))
                file_count += 1

        # Adiciona os arquivos do próprio agente por cima (para sobrescrever se houver conflitos)
        for file_path in sorted(agent_path.rglob("*")):
            if not file_path.is_file():
                continue
            relative = str(file_path.relative_to(agent_path))
            if any(skip in relative for skip in skip_patterns):
                continue
            zf.write(file_path, file_path.relative_to(agent_path))
            file_count += 1

    # Apaga a pasta temporária de dependências para manter tudo limpo
    if deps_dir:
        shutil.rmtree(deps_dir, ignore_errors=True)

    size = os.path.getsize(output_path)
    print(f"📦 Packaged {file_count} files ({size / 1024 / 1024:.1f} MB) → {output_path}")
    return output_path


def upload_to_s3(zip_path: str, bucket: str, prefix: str = "agentcore-runtimes") -> str:
    """Upload a zip package to S3.

    Returns:
        The S3 key.
    """
    filename = Path(zip_path).name
    s3_key = f"{prefix}/{filename}"

    s3 = boto3.client("s3", region_name=utils.get_region())
    print(f"⬆ Uploading to s3://{bucket}/{s3_key} ...")
    s3.upload_file(zip_path, bucket, s3_key)
    print("  Upload complete.")
    return s3_key


def _find_existing_runtime(control_client, name: str) -> dict | None:
    """Find an existing runtime by name."""
    try:
        paginator = control_client.get_paginator("list_agent_runtimes")
        for page in paginator.paginate():
            for rt in page.get("agentRuntimes", page.get("agentRuntimeSummaries", [])):
                if rt.get("agentRuntimeName") == name:
                    return rt
    except (ClientError, KeyError):
        pass
    return None


def _delete_runtime(control_client, runtime_id: str, timeout: int = 300):
    """Delete a runtime and wait for it to be fully removed."""
    import time

    print(f"🗑 Deleting existing runtime: {runtime_id}")
    try:
        control_client.delete_agent_runtime(agentRuntimeId=runtime_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("  Already deleted.")
            return
        raise

    # Aguarda até que o arquivo seja apagado com sucesso
    start = time.time()
    while time.time() - start < timeout:
        try:
            rt = control_client.get_agent_runtime(agentRuntimeId=runtime_id)
            status = rt.get("status", "")
            if status == "DELETING":
                print(f"  Waiting for deletion... ({int(time.time() - start)}s)")
                time.sleep(10)
            else:
                break
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                break
            raise

    print("  Deleted.")


def deploy(
    agent_dir: str | Path,
    runtime_name: str = "aria_agent",
    role_arn: str | None = None,
    s3_bucket: str | None = None,
    env_vars: dict | None = None,
    discovery_url: str | None = None,
    client_id: str | None = None,
    tracing: bool = True,
    clean_start: bool = False,
    timeout: int = 600,
) -> dict:
    """Package, upload, and deploy (or update) the agent to AgentCore Runtime.

    This is the main entry point for notebook cells. It is idempotent:
    - If no runtime with `runtime_name` exists, it creates one.
    - If a runtime already exists, it updates the code package.

    Args:
        agent_dir: Path to the agent code directory (containing main.py).
        runtime_name: Name for the AgentCore Runtime.
        role_arn: IAM role ARN. Auto-discovered from CFN outputs if None.
        s3_bucket: S3 bucket for uploads. Auto-discovered from CFN outputs if None.
        env_vars: Environment variables for the runtime.
        discovery_url: Cognito OIDC discovery URL for JWT authorizer.
        client_id: Cognito app client ID for JWT authorizer.
        tracing: Enable OpenTelemetry tracing via ADOT SDK. When True, wraps
            the entrypoint with opentelemetry-instrument.
        clean_start: If True, delete any existing runtime before creating
            a new one. Use this for the initial deploy (Module 02) to ensure
            no stale configuration (e.g., JWT auth from a previous run).
        timeout: Max seconds to wait for READY status.

    Returns:
        Dict with runtime_id, runtime_arn, endpoint, and status.
    """
    region = utils.get_region()
    account_id = utils.get_account_id()

    # Descobre automaticamente usando as saídas do CloudFormation outputs if not provided
    cfn = utils.get_all_cfn_outputs()
    if role_arn is None:
        role_arn = cfn.get("AgentRuntimeRoleArn") or cfn.get("RuntimeRoleArn")
        if not role_arn:
            raise ValueError(
                "role_arn not provided and not found in CFN outputs. "
                "Pass it explicitly or ensure the prerequisites stack is deployed."
            )
    if s3_bucket is None:
        s3_bucket = cfn.get("S3BucketName") or cfn.get("ArtifactsBucket") or cfn.get("ArtifactsBucketName")
        if not s3_bucket:
            raise ValueError(
                "s3_bucket not provided and not found in CFN outputs. "
                "Pass it explicitly or ensure the prerequisites stack is deployed."
            )

    env_vars = env_vars or {}

    utils.print_banner("Deploying Agent to AgentCore Runtime")
    print(f"  Account:  {account_id}")
    print(f"  Region:   {region}")
    print(f"  Runtime:  {runtime_name}")
    print(f"  Role:     {role_arn}")
    print(f"  Bucket:   {s3_bucket}")
    print()

    # Passo 1: Empacotar (Criar o zip com o código do agente)
    zip_path = package_agent(agent_dir)

    # Passo 2: Upload pro S3
    s3_key = upload_to_s3(zip_path, s3_bucket)

    # Passo 3: Criar um novo runtime ou atualizar se já existir
    control = boto3.client("bedrock-agentcore-control", region_name=region)
    existing = _find_existing_runtime(control, runtime_name)

    # 'Clean start': apaga qualquer runtime existente para evitar que configurações velhas atrapalhem
    # (Ex: Evitar que configurações antigas de JWT de um lab passado quebrem as coisas agora)
    if clean_start and existing:
        _delete_runtime(control, existing["agentRuntimeId"])
        existing = None

    entrypoint = ["main.py"]
    if tracing:
        entrypoint = ["opentelemetry-instrument", "main.py"]
        print("🔭 Tracing enabled — entrypoint wrapped with opentelemetry-instrument")

    runtime_params = {
        "agentRuntimeArtifact": {
            "codeConfiguration": {
                "code": {"s3": {"bucket": s3_bucket, "prefix": s3_key}},
                "runtime": "PYTHON_3_12",
                "entryPoint": entrypoint,
            }
        },
        "environmentVariables": env_vars,
    }

    # Parâmetros que são usados tanto na criação quanto na atualização
    runtime_params["roleArn"] = role_arn
    runtime_params["networkConfiguration"] = {"networkMode": "PUBLIC"}
    runtime_params["lifecycleConfiguration"] = {
        "idleRuntimeSessionTimeout": 900,   # Mantém a sessão viva por 15 minutos em inatividade
        "maxLifetime": 28800,               # Tempo máximo total da sessão de 8 horas
    }
    if existing:
        runtime_id = existing["agentRuntimeId"]
        print(f"🔄 Updating existing runtime: {runtime_id}")
        runtime_params["agentRuntimeId"] = runtime_id

        # Mantém as configurações atuais do Runtime intactas
        # (para que o deploy de um novo código não zere as configurações de autenticação JWT, por exemplo).
        current = control.get_agent_runtime(agentRuntimeId=runtime_id)
        existing_auth = current.get("authorizerConfiguration")
        if existing_auth:
            runtime_params["authorizerConfiguration"] = existing_auth
            print(f"  Preserving existing auth config: {list(existing_auth.keys())}")
        existing_headers = current.get("requestHeaderConfiguration")
        if existing_headers:
            runtime_params["requestHeaderConfiguration"] = existing_headers
            print(f"  Preserving request header config: {existing_headers}")

        try:
            resp = control.update_agent_runtime(**runtime_params)
        except ClientError as e:
            print(f"  ⚠ Update failed: {e}")
            raise
    else:
        print("🆕 Creating new runtime...")
        runtime_params["agentRuntimeName"] = runtime_name
        runtime_params["protocolConfiguration"] = {"serverProtocol": "HTTP"}
        runtime_params["tags"] = {"Project": utils.PROJECT_TAG}

        # Autorizador via JWT
        if discovery_url and client_id:
            runtime_params["authorizerConfiguration"] = {
                "customJWTAuthorizer": {
                    "discoveryUrl": discovery_url,
                    "allowedAudience": [client_id],
                }
            }
            runtime_params["requestHeaderConfiguration"] = {
                "requestHeaderAllowlist": ["Authorization"],
            }
            print(f"  JWT authorizer: {discovery_url}")

        try:
            resp = control.create_agent_runtime(**runtime_params)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                print("  Runtime already exists (race condition). Finding it...")
                existing = _find_existing_runtime(control, runtime_name)
                if existing:
                    runtime_id = existing["agentRuntimeId"]
                    resp = control.get_agent_runtime(agentRuntimeId=runtime_id)
                else:
                    raise
            else:
                raise

    runtime_id = resp["agentRuntimeId"]
    runtime_arn = resp.get("agentRuntimeArn", "")
    print(f"  Runtime ID:  {runtime_id}")
    print(f"  Runtime ARN: {runtime_arn}")
    print()

    # Passo 4: Fica de olho até o Runtime avisar que está pronto (READY)
    print("⏳ Waiting for runtime to be ready...")
    final = utils.poll_until(
        describe_fn=lambda: control.get_agent_runtime(agentRuntimeId=runtime_id),
        label="Runtime",
        timeout=timeout,
    )

    # Monta a URL completa para fazermos chamadas pro agente
    import urllib.parse
    escaped_arn = urllib.parse.quote(runtime_arn or final.get("agentRuntimeArn", ""), safe="")
    endpoint = (
        f"https://bedrock-agentcore.{region}.amazonaws.com"
        f"/runtimes/{escaped_arn}/invocations"
        f"?qualifier=DEFAULT&accountId={account_id}"
    )

    result = {
        "runtime_id": runtime_id,
        "runtime_arn": runtime_arn or final.get("agentRuntimeArn", ""),
        "runtime_name": runtime_name,
        "endpoint": endpoint,
        "status": final["status"],
        "region": region,
        "account_id": account_id,
    }

    # Salva as configurações num arquivo para os próximos labs lerem
    utils.save_config("runtime", result)

    print()
    utils.print_banner("Runtime Deployed Successfully")
    print(f"  Runtime ID:  {runtime_id}")
    print(f"  Status:      {final['status']}")
    print(f"  Endpoint:    {endpoint[:80]}...")
    print()

    # Apaga o arquivo zip temporário gerado localmente
    try:
        os.remove(zip_path)
    except OSError:
        pass

    return result
