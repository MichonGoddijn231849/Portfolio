#!/usr/bin/env python3
"""
deploy_model.py — blue/green rollout using your prebuilt y2bd-k8s-env:4
"""

import argparse
import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    KubernetesOnlineDeployment,
    CodeConfiguration,
)
from azure.core.exceptions import ResourceNotFoundError


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--model_id_file",
        required=True,
        help="Text file containing name:version of the model",
    )
    p.add_argument("--endpoint_name", required=True)
    p.add_argument("--deployment_name", default="green")
    p.add_argument("--code_dir", default="./src")
    p.add_argument("--scoring_script", default="score.py")
    p.add_argument("--instance_type", default="gpu")
    p.add_argument("--instance_count", type=int, default=1)
    p.add_argument(
        "--subscription_id",
        default=os.getenv("AZURE_SUB_ID", "0a94de80-6d3b-49f2-b3e9-ec5818862801"),
    )
    p.add_argument(
        "--resource_group",
        default=os.getenv("AZURE_RG", "buas-y2"),
    )
    p.add_argument(
        "--workspace_name",
        default=os.getenv("AZURE_WS", "NLP1-2025"),
    )
    return p.parse_args()


def main():
    args = parse_args()

    # Authenticate
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=args.subscription_id,
        resource_group_name=args.resource_group,
        workspace_name=args.workspace_name,
    )

    # Read the registered model name and version
    name, version = open(args.model_id_file).read().strip().split(":")
    print(f"▶️  Deploying model {name}:{version}")
    model = ml_client.models.get(name=name, version=version)

    # Grab your prebuilt K8S environment
    built_env = ml_client.environments.get(name="y2bd-k8s-env", version="4")

    # Ensure the endpoint exists (or create it)
    try:
        endpoint = ml_client.online_endpoints.get(args.endpoint_name)
        print(f"ℹ️  Endpoint '{args.endpoint_name}' found")
    except ResourceNotFoundError:
        print(f"ℹ️  Creating endpoint '{args.endpoint_name}'")
        endpoint = ManagedOnlineEndpoint(name=args.endpoint_name, auth_mode="key")
        ml_client.begin_create_or_update(endpoint).result()

    # Delete any prior 'green' deployment
    try:
        ml_client.online_deployments.begin_delete(
            name=args.deployment_name,
            endpoint_name=args.endpoint_name,
        ).result()
        print(f"⚠️  Removed old deployment '{args.deployment_name}'")
    except ResourceNotFoundError:
        # nothing to delete if it's not there
        pass

    # Create the new Kubernetes deployment
    dep = KubernetesOnlineDeployment(
        name=args.deployment_name,
        endpoint_name=args.endpoint_name,
        model=model,
        environment=built_env,
        code_configuration=CodeConfiguration(
            code=args.code_dir,
            scoring_script=args.scoring_script,
        ),
        instance_type=args.instance_type,
        instance_count=args.instance_count,
    )
    ml_client.online_deployments.begin_create_or_update(dep).result()
    print(f"✅ Deployed '{args.deployment_name}' with {version}")

    # Flip traffic: 100% to the new green deployment
    endpoint.traffic = {args.deployment_name: 100}
    ml_client.begin_create_or_update(endpoint).result()
    print(f"✅ Traffic routed: 100% → '{args.deployment_name}'")


if __name__ == "__main__":
    main()
