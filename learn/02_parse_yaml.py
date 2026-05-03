import yaml
from pathlib import Path

config_path = Path("learn/01_yaml_basics.yml")
with config_path.open("r") as f:
    config = yaml.safe_load(f)

# YAML loads as a Python dict — that's the whole magic
print(f"Project: {config['project_name']}")
print(f"Environments: {config['environments']}")
print(f"First pipeline: {config['pipelines'][0]['name']}")
print(f"Bronze job timeout: {config['jobs']['bronze_job']['timeout_seconds']}")
print(f"Silver job timeout: {config['jobs']['silver_job']['timeout_seconds']}")