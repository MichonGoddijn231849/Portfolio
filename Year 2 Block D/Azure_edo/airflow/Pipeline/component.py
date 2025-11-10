# component.py

from azure.ai.ml import command, Input, Output

# ─────────────────────────────────────────────────────────────────────
# 0️⃣  Champion lookup
# ─────────────────────────────────────────────────────────────────────
get_best_model_comp = command(
    name="get_core_emotion_champion",
    version="15",
    display_name="Get Current Champion (folder + F1)",
    inputs={
        "model_name": Input(type="string"),
    },
    outputs={
        "best_model_dir": Output(type="uri_folder", mode="upload"),
        "best_f1": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command="""
python get_best_model_comp.py \
  --model_name=${{inputs.model_name}} \
  --best_model_dir=${{outputs.best_model_dir}} \
  --best_f1=${{outputs.best_f1}}
""",
    environment_variables={
        "AZURE_TENANT_ID": "0a33589b-0036-4fe8-a829-3ed0926af886",
        "AZURE_CLIENT_ID": "a2230f31-0fda-428d-8c5c-ec79e91a49f5",
        "AZURE_CLIENT_SECRET": "AWA8Q~14jhEuWoP5K4FNnRfsRc_Qcbhx8PeLRaXw",
    },
)

# ─────────────────────────────────────────────────────────────────────
# 1️⃣  Preprocess raw CSV
# ─────────────────────────────────────────────────────────────────────
preprocess_comp = command(
    name="preprocess_data",
    version="8",
    display_name="Pre-process raw CSV",
    inputs={
        "raw_df": Input(type="uri_file", mode="download"),
    },
    outputs={
        "train_texts": Output(type="uri_file", mode="upload"),
        "train_labels": Output(type="uri_file", mode="upload"),
        "test_texts": Output(type="uri_file", mode="upload"),
        "test_labels": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command="""
python preprocessing.py \
  --input_path=${{inputs.raw_df}} \
  --train_texts_out=${{outputs.train_texts}} \
  --train_labels_out=${{outputs.train_labels}} \
  --test_texts_out=${{outputs.test_texts}} \
  --test_labels_out=${{outputs.test_labels}}
""",
)

# ─────────────────────────────────────────────────────────────────────
# 2️⃣  Train (warm-start capable)
# ─────────────────────────────────────────────────────────────────────
train_comp = command(
    name="train_core_emotion",
    version="24",
    display_name="Train core-emotion BERT (warm-start)",
    inputs={
        "train_texts": Input(type="uri_file", mode="download"),
        "train_labels": Input(type="uri_file", mode="download"),
        "base_model_dir": Input(type="uri_folder", mode="download", optional=True),
    },
    outputs={
        "model_dir": Output(type="uri_folder", mode="upload"),
        "log_history": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command=r"""
python train.py \
  --train_texts=${{inputs.train_texts}} \
  --train_labels=${{inputs.train_labels}} \
  --output_dir=${{outputs.model_dir}} \
  --log_history=${{outputs.log_history}} \
  $[[ --base_model_dir=${{inputs.base_model_dir}} ]]
""",
    resources={"instance_type": "gpu"},
)

# ─────────────────────────────────────────────────────────────────────
# 3️⃣  Evaluate
# ─────────────────────────────────────────────────────────────────────
evaluate_comp = command(
    name="evaluate_core_emotion",
    version="20",
    display_name="Evaluate core-emotion model",
    inputs={
        "model_dir": Input(type="uri_folder", mode="download"),
        "test_texts": Input(type="uri_file", mode="download"),
        "test_labels": Input(type="uri_file", mode="download"),
    },
    outputs={
        "metrics_json": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command="""
python evaluate.py \
  --model_dir=${{inputs.model_dir}} \
  --test_texts=${{inputs.test_texts}} \
  --test_labels=${{inputs.test_labels}} \
  --output_metrics=${{outputs.metrics_json}}
""",
    resources={"instance_type": "gpu"},
)

# ─────────────────────────────────────────────────────────────────────
# 4️⃣  Visualize loss curve
# ─────────────────────────────────────────────────────────────────────
visualize_comp = command(
    name="visualize_loss",
    version="20",
    display_name="Plot Train-vs-Val Loss",
    inputs={
        "log_history": Input(type="uri_file", mode="download"),
    },
    outputs={
        "loss_curve_png": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command="""
python visualize.py \
  --log_history_path=${{inputs.log_history}} \
  --output_plot_path=${{outputs.loss_curve_png}}
""",
)

# ─────────────────────────────────────────────────────────────────────
# 5️⃣  Register if F1 improves
# ─────────────────────────────────────────────────────────────────────
register_comp = command(
    name="register_core_emotion_model",
    version="37",
    display_name="Register if F1 improves",
    inputs={
        "model_dir": Input(type="uri_folder", mode="download"),
        "model_name": Input(type="string"),
        "metrics_json": Input(type="uri_file", mode="download"),
    },
    outputs={
        "registered_model": Output(type="uri_file", mode="upload"),
    },
    environment="azureml:huggingface-transformers-env:35",
    code=".",
    command="""
python register_model.py \
  --model_dir=${{inputs.model_dir}} \
  --model_name=${{inputs.model_name}} \
  --metrics_json=${{inputs.metrics_json}} \
  --registered_model=${{outputs.registered_model}}
""",
    environment_variables={
        "AZURE_TENANT_ID": "0a33589b-0036-4fe8-a829-3ed0926af886",
        "AZURE_CLIENT_ID": "a2230f31-0fda-428d-8c5c-ec79e91a49f5",
        "AZURE_CLIENT_SECRET": "AWA8Q~14jhEuWoP5K4FNnRfsRc_Qcbhx8PeLRaXw",
    },
)

# ─────────────────────────────────────────────────────────────────────
# 6️⃣  Deploy the chosen model
# ─────────────────────────────────────────────────────────────────────
deploy_comp = command(
    name="deploy_core_emotion_model",
    version="24",
    display_name="Deploy Core-Emotion Model",
    inputs={
        "model_id_file": Input(type="uri_file", mode="download"),
    },
    code=".",
    command="""
python deploy_model.py \
  --model_id_file=${{inputs.model_id_file}} \
  --endpoint_name=edoardo-fastapi-endpoint \
  --deployment_name=green \
  --code_dir=./src \
  --scoring_script=score.py \
  --instance_type=gpu \
  --instance_count=1
""",
    environment="azureml:huggingface-transformers-env:35",
    environment_variables={
        "AZURE_TENANT_ID": "0a33589b-0036-4fe8-a829-3ed0926af886",
        "AZURE_CLIENT_ID": "a2230f31-0fda-428d-8c5c-ec79e91a49f5",
        "AZURE_CLIENT_SECRET": "AWA8Q~14jhEuWoP5K4FNnRfsRc_Qcbhx8PeLRaXw",
    },
)
