# deploy.py
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AciWebservice, Model, Environment, InferenceConfig
import logging

logger = logging.getLogger(__name__)


def deploy_model(
    subscription_id,
    resource_group,
    workspace_name,
    model_name,
    model_version,
    endpoint_name="emotion-endpoint",
):
    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group, workspace_name
    )

    # Define inference environment & config
    env = Environment(
        name="bert-inference-env",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        conda_file="environment.yml",
    )
    inference_config = InferenceConfig(
        entry_script="score.py", environment=env  # you’d write a scoring script here
    )
    deployment_config = AciWebservice(cpu_cores=1, memory_gb=2, auth_enabled=True)
    deployment = ml_client.online_endpoints.begin_deploy(
        endpoint_name=endpoint_name,
        model=Model(name=model_name, version=model_version),
        deployment_config=deployment_config,
        inference_config=inference_config,
    ).result()
    logger.info(f"Deployed endpoint {endpoint_name}")
    return deployment
