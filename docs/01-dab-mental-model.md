┌─────────────────────────────────────────────┐
│  LAYER 3: WHAT TO RUN (the work)            │
│  src/sample_notebook.ipynb                  │
│  → Reads parameters, does the actual work   │
└─────────────────────────────────────────────┘
                    ▲
                    │ "run this notebook with these inputs"
                    │
┌─────────────────────────────────────────────┐
│  LAYER 2: HOW TO RUN IT (the wrapper)       │
│  resources/sample_job.job.yml               │
│  → Defines a Job: which notebook, what      │
│    parameters, what compute, on failure...  │
└─────────────────────────────────────────────┘
                    ▲
                    │ "deploy this job to my workspace"
                    │
┌─────────────────────────────────────────────┐
│  LAYER 1: WHERE TO RUN IT (the context)     │
│  databricks.yml                             │
│  → Defines: which workspace, which envs     │
│    (dev/prod), what variables in each       │
└─────────────────────────────────────────────┘
