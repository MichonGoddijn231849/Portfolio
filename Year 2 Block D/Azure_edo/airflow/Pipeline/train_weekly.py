from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, Input  # ← import Input here
from pipeline import emotion_pipeline  # import the @pipeline fn

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="0a94de80-6d3b-49f2-b3e9-ec5818862801",
    resource_group_name="buas-y2",
    workspace_name="NLP1-2025",
)

# build the job exactly the way you want weekly
weekly_job = emotion_pipeline(
    input_data=Input(
        type="uri_file",
        path="azureml:data_pipeline:2",  # or "azureml:data_pipeline:latest"
        mode="download",
    ),
    sub_id="0a94de80-6d3b-49f2-b3e9-ec5818862801",
    rg_name="buas-y2",
    ws_name="NLP1-2025",
)

# register the job definition so a schedule can point to it
registered_job = ml_client.jobs.create_or_update(
    weekly_job, create_job=True  # tell Azure ML to keep this pipeline definition around
)
print("Registered pipeline job:", registered_job.name)
