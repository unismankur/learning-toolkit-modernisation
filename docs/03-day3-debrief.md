# Day 3 Debrief

## What worked
- Serverless env config: `environment_key` on task + `environments` block with `client: "2"` (no dependencies)
- Parameter passing: `base_parameters` in YAML → `dbutils.widgets` in notebook
- Source: `samples.tpch.customer` (built-in, no upload needed)
- Target: `workspace.${var.schema}.bronze_customer`

## Pattern locked in
Same notebook code runs against any target — schema is injected via YAML variable.
Adding a `staging` target = add 4 lines to `databricks.yml`. No notebook changes.

## NAB translation
- `samples.tpch.customer` → silver layer table via CDDS persona
- `workspace.dev` → squad's dev schema in TINA
- Same `base_parameters` pattern Faye's pipelines use

## Next session
- Add a second target (`staging`) to demonstrate env switching
- Add silver transform notebook
