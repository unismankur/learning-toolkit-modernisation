# Setup Journey — Notes for Future Me

## Lessons learned the hard way

1. **PAT scopes matter.** Default-python template needs `unity-catalog` scope.
   If using Free Edition, generate token with "all-apis" scope.

2. **ARM64 Windows + DAB = pain.** Use WSL2 (Ubuntu) — Terraform binaries
   for ARM64 Windows don't exist for the version Databricks CLI pins.

3. **GitHub push from WSL needs a PAT.** Create at
   github.com/settings/tokens → "Tokens (classic)" → scope: `repo`.
   Use as password when git prompts.

4. **Free Edition serverless** is finicky with Python package installs.
   Use `environment_key` + `environments: client: "2"` with NO dependencies.
   Don't keep `pyproject.toml` unless you actually need a wheel.

5. **default-python template is over-scaffolded** for learning. Strip
   pyproject.toml, tests/, fixtures/, the wheel package, and the DLT pipeline.
   Keep: databricks.yml, resources/<job>.yml, src/<notebook>.ipynb.
