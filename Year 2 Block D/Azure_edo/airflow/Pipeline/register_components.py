# register_components.py  ── SDK-only, YAML round-trip

import tempfile
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import component  # ← your component.py with factories

SUB_ID = "0a94de80-6d3b-49f2-b3e9-ec5818862801"
RGROUP = "buas-y2"
WS_NAME = "NLP1-2025"

ml = MLClient(
    DefaultAzureCredential(),
    subscription_id=SUB_ID,
    resource_group_name=RGROUP,
    workspace_name=WS_NAME,
)

factories = [
    component.get_best_model_comp,
    component.preprocess_comp,
    component.train_comp,
    component.evaluate_comp,
    component.visualize_comp,
    component.register_comp,
    component.deploy_comp,
]

tmpdir = Path(tempfile.mkdtemp(prefix="comp_yaml_"))
print(f"✍️  Exporting YAMLs to {tmpdir}")

for fac in factories:
    yaml_path = tmpdir / f"{fac.name}_v{fac.version}.yaml"
    fac.save(str(yaml_path))  # ① write YAML
    created = ml.components.create_or_update(str(yaml_path))  # ② register
    print(f"✔ Registered {created.name}:{created.version}")

print("🏁 All components registered successfully.")
