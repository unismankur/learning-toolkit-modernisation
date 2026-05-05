# Building a DAB Bundle From Scratch — 12-Step Checklist

## Setup (one-time per machine)
1. Install Databricks CLI: `curl -fsSL .../install.sh | sudo sh`
2. Configure: `databricks configure` (host + PAT)
3. Verify: `databricks current-user me`

## Per-bundle (each new project)
4. Create empty repo folder, `cd` into it
5. Run `databricks bundle init default-python`
   - Project name: `<project>`
   - Notebook: yes, ETL: no, Python pkg: no, serverless: yes
   - Default catalog: `workspace`
6. Strip down: delete `pyproject.toml`, `tests/`, `fixtures/`, `src/<pkg>/`,
   `src/<pkg>_etl/`, `resources/<pkg>_etl.pipeline.yml`

## YAML editing
7. In `databricks.yml`:
   - Remove `artifacts:` block
   - Confirm `targets.dev.variables` and `targets.prod.variables` are set
8. In `resources/<job>.job.yml`:
   - Replace with minimal job: one task, notebook_task,
     base_parameters using ${var.x}, environment_key + environments
     block with client: "2"

## Notebook
9. In `src/<notebook>.ipynb`:
   - First cell: dbutils.widgets.text(name, default) for each param
   - Read with dbutils.widgets.get(name)
   - Use values in spark.sql / spark.read / df.write

## Deploy & run
10. `databricks bundle validate` (must say "Validation OK!")
11. `databricks bundle deploy -t dev`
12. `databricks bundle run <job_name> -t dev`

## Verify
- Open Workflows in browser → see "[dev <user>] <job_name>"
- Open Catalog → see new schema/table created
- Logs visible by clicking the run
