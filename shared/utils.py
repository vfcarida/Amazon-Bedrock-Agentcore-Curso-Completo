"""Common utilities for the AgentCore workshop notebooks.

Provides helper functions used across multiple modules for AWS account
discovery, CloudFormation output retrieval, and configuration management.
"""

import codecs
import json
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSHOP_DIR = Path(__file__).resolve().parent.parent  # workshop-code/
CONFIG_DIR = WORKSHOP_DIR / "shared" / ".config"
REGION = os.environ.get("AWS_REGION", "us-east-1")
PROJECT_TAG = "aria-agentcore-workshop"


# ---------------------------------------------------------------------------
# AWS helpers
# ---------------------------------------------------------------------------


def get_region() -> str:
    """Return the active AWS region."""
    return REGION


def get_account_id() -> str:
    """Return the current AWS account ID."""
    sts = boto3.client("sts", region_name=REGION)
    return sts.get_caller_identity()["Account"]


def get_cfn_outputs(stack_name: str = "cfn-template") -> dict:
    """Retrieve CloudFormation stack outputs as a dict.

    Args:
        stack_name: Name of the CloudFormation stack.

    Returns:
        Dict mapping output keys to output values.
    """
    cfn = boto3.client("cloudformation", region_name=REGION)
    try:
        resp = cfn.describe_stacks(StackName=stack_name)
        outputs = resp["Stacks"][0].get("Outputs", [])
        return {o["OutputKey"]: o["OutputValue"] for o in outputs}
    except ClientError as e:
        print(f"⚠ Could not read stack '{stack_name}': {e}")
        return {}


def get_all_cfn_outputs() -> dict:
    """Retrieve outputs from the workshop CloudFormation stack.

    Looks for the workshop prerequisites stack first. Falls back to
    scanning all stacks only if the workshop stack is not found.
    """
    # Try the workshop stack directly first
    workshop_outputs = get_cfn_outputs("cfn-template")
    if workshop_outputs:
        return workshop_outputs

    # Fallback: scan all stacks (for non-standard stack names)
    cfn = boto3.client("cloudformation", region_name=REGION)
    all_outputs = {}
    try:
        paginator = cfn.get_paginator("list_stacks")
        for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]):
            for stack_summary in page["StackSummaries"]:
                stack_name = stack_summary["StackName"]
                try:
                    resp = cfn.describe_stacks(StackName=stack_name)
                    for output in resp["Stacks"][0].get("Outputs", []):
                        all_outputs[output["OutputKey"]] = output["OutputValue"]
                except ClientError:
                    pass
    except ClientError:
        pass
    return all_outputs


# ---------------------------------------------------------------------------
# Configuration persistence
# ---------------------------------------------------------------------------


def save_config(name: str, data: dict) -> Path:
    """Save a JSON config file to the shared config directory.

    Args:
        name: Config name (without .json extension).
        data: Dict to persist.

    Returns:
        Path to the saved file.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path = CONFIG_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def load_config(name: str) -> dict | None:
    """Load a JSON config file from the shared config directory.

    Returns None if the file does not exist.
    """
    path = CONFIG_DIR / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ---------------------------------------------------------------------------
# Gateway config helper
# ---------------------------------------------------------------------------


def get_gateway_config(control_client=None) -> dict:
    """Load gateway config, discovering it from the API if necessary.

    Returns a dict with gateway_id, gateway_arn, gateway_url, and region.
    Saves/updates the config file for downstream use.

    Args:
        control_client: Optional pre-built bedrock-agentcore-control client.
    """
    gw_config = load_config("gateway")
    gateway_id = gw_config.get("gateway_id") if gw_config else None
    gateway_arn = gw_config.get("gateway_arn", "") if gw_config else ""

    if not gateway_id:
        print("Gateway config not found -- searching for existing gateway...")
        if control_client is None:
            control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
        paginator = control_client.get_paginator("list_gateways")
        for page in paginator.paginate():
            for gw in page.get("items", []):
                if "aria" in gw.get("name", "").lower():
                    gateway_id = gw["gatewayId"]
                    break
            if gateway_id:
                break
        if not gateway_id:
            raise RuntimeError("No gateway found. Run the Module 05 catch-up first.")

    if not gateway_arn:
        if control_client is None:
            control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
        gw_detail = control_client.get_gateway(gatewayIdentifier=gateway_id)
        gateway_arn = gw_detail["gatewayArn"]
        gateway_url = gw_detail.get("gatewayUrl", "")
    else:
        gateway_url = gw_config.get("gateway_url", "") if gw_config else ""

    config = {
        "gateway_id": gateway_id,
        "gateway_arn": gateway_arn,
        "gateway_url": gateway_url,
        "region": REGION,
    }
    save_config("gateway", config)
    return config


# ---------------------------------------------------------------------------
# Polling helper
# ---------------------------------------------------------------------------


def poll_until(
    describe_fn,
    status_path: str = "status",
    target_statuses: set[str] = {"READY", "ACTIVE"},
    failure_statuses: set[str] = {"CREATE_FAILED", "FAILED", "DELETE_FAILED"},
    timeout: int = 600,
    interval: int = 10,
    label: str = "resource",
) -> dict:
    """Poll a describe function until the resource reaches a target status.

    Args:
        describe_fn: Callable that returns a dict with a status field.
        status_path: Dot-separated path to the status field in the response.
        target_statuses: Set of statuses that indicate success.
        failure_statuses: Set of statuses that indicate failure.
        timeout: Maximum seconds to wait.
        interval: Seconds between polls.
        label: Human-readable label for log messages.

    Returns:
        The final describe response dict.

    Raises:
        RuntimeError: If the resource enters a failure state.
        TimeoutError: If the timeout is exceeded.
    """
    start = time.time()
    last_status = None

    while time.time() - start < timeout:
        response = describe_fn()

        # Navigate the status path
        status = response
        for key in status_path.split("."):
            status = status[key] if isinstance(status, dict) else status

        if status != last_status:
            elapsed = int(time.time() - start)
            print(f"  [{elapsed:>4}s] {label}: {status}")
            last_status = status

        if status in target_statuses:
            return response

        if status in failure_statuses:
            raise RuntimeError(
                f"{label} entered failure state: {status}\n"
                f"Response: {json.dumps(response, indent=2, default=str)}"
            )

        time.sleep(interval)

    raise TimeoutError(
        f"{label} did not reach {target_statuses} within {timeout}s. Last: {last_status}"
    )


# ---------------------------------------------------------------------------
# SSE response parsing
# ---------------------------------------------------------------------------


def stream_sse_response(stream) -> str:
    """Stream an AgentCore Runtime SSE response, printing text as it arrives.

    Args:
        stream: The botocore StreamingBody from response["response"].

    Returns:
        The full accumulated response text.
    """
    full_text = ""
    buffer = ""
    decoder = codecs.getincrementaldecoder("utf-8")("replace")

    for chunk in stream.iter_chunks(chunk_size=1024):
        buffer += decoder.decode(chunk, final=False)
        # Process complete lines from the buffer
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line.startswith("data: "):
                continue
            try:
                event = json.loads(line[6:])
                if not isinstance(event, dict):
                    continue
                if event.get("error"):
                    error_type = event.get("error_type", "Error")
                    err = f"\n❌ {error_type}: {event['error']}\n"
                    print(err, end="", flush=True)
                    full_text += err
                    continue
                if event.get("force_stop") and event.get("force_stop_reason"):
                    msg = f"\n⚠ Agent stopped: {event['force_stop_reason']}\n"
                    print(msg, end="", flush=True)
                    full_text += msg
                    continue
                delta = (event.get("event", {})
                             .get("contentBlockDelta", {})
                             .get("delta", {})
                             .get("text", ""))
                if not delta:
                    delta = (event.get("contentBlockDelta", {})
                                 .get("delta", {})
                                 .get("text", ""))
                if delta:
                    print(delta, end="", flush=True)
                    full_text += delta
            except (json.JSONDecodeError, AttributeError):
                pass

    # Flush any trailing bytes from the incremental decoder
    buffer += decoder.decode(b"", final=True)

    # Process any remaining data in the buffer
    if buffer.strip().startswith("data: "):
        try:
            event = json.loads(buffer.strip()[6:])
            if isinstance(event, dict):
                delta = (event.get("event", {})
                             .get("contentBlockDelta", {})
                             .get("delta", {})
                             .get("text", ""))
                if not delta:
                    delta = (event.get("contentBlockDelta", {})
                                 .get("delta", {})
                                 .get("text", ""))
                if delta:
                    print(delta, end="", flush=True)
                    full_text += delta
        except (json.JSONDecodeError, AttributeError):
            pass

    print()  # trailing newline
    return full_text


def parse_sse_text(raw: str) -> str:
    """Extract agent text from a raw AgentCore Runtime SSE response.

    Handles multiple event formats:
    - Standard:  data: {"event": {"contentBlockDelta": {"delta": {"text": "..."}}}}
    - Flat:      data: {"contentBlockDelta": {"delta": {"text": "..."}}}
    - Error:     data: {"error": "...", "error_type": "..."}
    - Force stop: data: {"force_stop": true, "force_stop_reason": "..."}
    """
    text = ""
    for line in raw.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        try:
            event = json.loads(line[6:])
            if not isinstance(event, dict):
                continue
            # Check for error events first
            if event.get("error"):
                error_type = event.get("error_type", "Error")
                error_msg = event["error"]
                text += f"\n❌ {error_type}: {error_msg}\n"
                continue
            if event.get("force_stop") and event.get("force_stop_reason"):
                text += f"\n⚠ Agent stopped: {event['force_stop_reason']}\n"
                continue
            # Extract text from content deltas
            delta = (event.get("event", {})
                         .get("contentBlockDelta", {})
                         .get("delta", {})
                         .get("text", ""))
            if not delta:
                delta = (event.get("contentBlockDelta", {})
                             .get("delta", {})
                             .get("text", ""))
            if delta:
                text += delta
        except (json.JSONDecodeError, AttributeError):
            pass
    return text


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def print_banner(title: str, width: int = 64) -> None:
    """Print a formatted banner."""
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_config(label: str, data: dict) -> None:
    """Print key-value pairs in a formatted block."""
    max_key = max(len(k) for k in data) if data else 0
    for key, value in data.items():
        print(f"  {key:<{max_key + 2}}: {value}")


