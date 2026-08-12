"""Funções auxiliares para leitura de stacks CloudFormation e metadados da conta AWS."""

import os
import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_region() -> str:
    """Retorna a região ativa da AWS."""
    return REGION


def get_account_id() -> str:
    """Retorna o ID da conta AWS atual via STS."""
    sts = boto3.client("sts", region_name=REGION)
    return sts.get_caller_identity()["Account"]


def get_cfn_outputs(stack_name: str = "cfn-template") -> dict:
    """Recupera as saídas (Outputs) de uma stack CloudFormation como dicionário.

    Args:
        stack_name: Nome da stack no CloudFormation.

    Returns:
        Dicionário mapeando chave -> valor das saídas.
    """
    cfn = boto3.client("cloudformation", region_name=REGION)
    try:
        resp = cfn.describe_stacks(StackName=stack_name)
        outputs = resp["Stacks"][0].get("Outputs", [])
        return {o["OutputKey"]: o["OutputValue"] for o in outputs}
    except ClientError:
        return {}


def get_all_cfn_outputs() -> dict:
    """Busca os outputs da stack do workshop com fallback para todas as stacks."""
    workshop_outputs = get_cfn_outputs("cfn-template")
    if workshop_outputs:
        return workshop_outputs

    cfn = boto3.client("cloudformation", region_name=REGION)
    all_outputs = {}
    try:
        paginator = cfn.get_paginator("list_stacks")
        for page in paginator.paginate(
            StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]
        ):
            for stack_summary in page["StackSummaries"]:
                stack_name = stack_summary["StackName"]
                try:
                    resp = cfn.describe_stacks(StackName=stack_name)
                    for output in resp["Stacks"][0].get("Outputs", []):
                        all_outputs[output["OutputKey"]] = output[
                            "OutputValue"
                        ]
                except ClientError:
                    pass
    except ClientError:
        pass
    return all_outputs
