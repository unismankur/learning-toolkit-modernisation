# Learning Toolkit — Data Pipeline Modernisation

A reusable template for parameter-driven data pipeline migrations using
Databricks Declarative Automation Bundles (formerly Asset Bundles), demonstrated
on the public Lending Club loans dataset.

## Why This Exists
Migrating data pipelines between platforms is repetitive and error-prone. This
toolkit demonstrates a YAML-parameterised approach where the same notebook code
runs against different environments and table targets without modification.

## Pattern
- `databricks.yml` — bundle root, environment targets, variable definitions
- `resources/jobs/*.yml` — job specs decoupled from code
- `src/notebooks/*` — pure transformation logic, parameter-driven
- `conf/*.yml` — environment-specific overrides

## Stack
Databricks Free Edition · Python · PySpark · Declarative Automation Bundles

## Status
Work in progress — built as a personal learning artefact.