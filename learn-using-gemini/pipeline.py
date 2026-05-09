import os
import yaml
import pandas as pd

# Load and parse the YAML configuration 
config_path = "config.yaml"
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# 2. Extract parameters from the configuration object
source_file = config["data_paths"]["source_file"]
target_dir = config["data_path"]["target_directory"]
category_filter = config["parameters"]["filter_category"]
min_value = config["parameters"]["min_transaction_value"]

print(f"Starting pipeline: {config['pipeline_metadata']['name']} ")
print(f"Reading from: {source_file}")


# 3. Execute data processing using extracted parameters
df = pd.read_csv(source_file)
filtered_df = df[(df["category"] == category_filter) & (df["amount"] >= min_value)]                                   

# 4. Output results to the simulated target directory
os.makedirs(target_dir, exist_ok=True)
output_path = os.path.join(target_dir,"output.csv")
filtered_df.to_csv(output_path, index=False)
print(f"Pipeline complete. Target Written to: {output_path}")
