# Databricks Job Automation Guide

## Overview

This guide explains how to automate Databricks job creation and management using GitHub Actions CI/CD. Jobs are automatically created/updated whenever you push code to your repository.

---

## Table of Contents

1. [What Gets Automated](#what-gets-automated)
2. [Job Configuration Files](#job-configuration-files)
3. [How It Works](#how-it-works)
4. [Customizing Your Jobs](#customizing-your-jobs)
5. [Common Use Cases](#common-use-cases)
6. [Testing Job Creation](#testing-job-creation)
7. [Syncing Changes Back from Databricks UI](#syncing-changes-back-from-databricks-ui)
8. [FAQ & Best Practices](#faq--best-practices)
9. [Troubleshooting](#troubleshooting)

---

## What Gets Automated

When you push code to GitHub, the CI/CD pipeline automatically:

**Creates new Databricks jobs** if they don't exist  
**Updates existing jobs** with new configuration  
**Manages separate dev and prod jobs** based on branch  
**Sets up job schedules** (for production)  
**Syncs notebooks** to Databricks workspace (with JUPYTER format)  
**Configures training pipelines** with MULTI_TASK format  
**Updates only when config changes** (efficient, no unnecessary updates)  

### Job Types Created

| Branch | Job Name | Notebook Path | Schedule | Format |
|--------|----------|---------------|----------|--------|
| `dev` | `ML_Regression_Training` | `/ml-regression-model-dev/notebooks/train.ipynb` | None (manual) | MULTI_TASK |
| `main` | `ML_Regression_Training_Prod` | `/ml-regression-model-prod/notebooks/train.ipynb` | Daily 2am UTC (paused) | MULTI_TASK |

---

## Job Configuration Files

### Development Job: `config/databricks_job_config.json`

```json
{Training",
  "tasks": [
    {
      "task_key": "ml_training_task",
      "notebook_task": {
        "notebook_path": "/ml-regression-model-dev/notebooks/train.ipynb",
        "base_parameters": {},
        "source": "WORKSPACE"
      },
      "timeout_seconds": 3600
    }
  ],
  "email_notifications": {
    "no_alert_for_skipped_runs": false
  },
  "format": "MULTI_TASK",
  "max_concurrent_runs": 1
}
```

**Used for:** `dev` branch deployments  
**Purpose:** Testing and development  
**Schedule:** None (manual trigger)  
**Task Type:** MULTI_TASK format (single training task)  
**Notebook Source:** WORKSPACE (notebooks in Databricks workspace)  
**Timeout:** 1 hour (3600 seconds)  
**Cluster:** Uses existing cluster from Databricks workspace
2. Inference - Runs prediTraining_Prod",
  "tasks": [
    {
      "task_key": "ml_training_task",
      "notebook_task": {
        "notebook_path": "/ml-regression-model-prod/notebooks/train.ipynb",
        "base_parameters": {},
        "source": "WORKSPACE"
      },
      "timeout_seconds": 3600
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC",
    "pause_status": "PAUSED"
  },
  "email_notifications": {
    "no_alert_for_skipped_runs": false
  },
  "format": "MULTI_TASK",
  "max_concurrent_runs": 1
}
```

**Used for:** `main` branch deployments  
**Purpose:** Production workloads  
**Schedule:** Daily at 2am UTC (starts paused for safety)  
**Task Type:** MULTI_TASK format (single training task)  
**Notebook Source:** WORKSPACE (notebooks in Databricks workspace)  
**Timeout:** 1 hour (3600 seconds)  
**Cluster:** Uses existing cluster from Databricks workspace  

⚠️ **Note:** Schedule starts PAUSED. Enable it manually in Databricks UI when ready for automated runs.
**Purpose:** Production workloads  
**Schedule:** Daily at 2am UTC (starts paused for safety)  
**Cluster:** Two workers (better performance)  
**Tasks:**
1. Train model - Trains regression model (2 retries)
2. Inference - Runs predictions (depends on train_model)  

---

## How It Works

### Workflow Process

```
Push to GitHub
    ↓
Run Unit Tests
    ↓
Sync Files to Databricks
    ↓
    Create/Update Databricks Job
    ├─ Check if job exists by name
    ├─ If exists → Update configuration
    └─ If not exists → Create new job
    ↓
Display Job URL
    Done
```

### Script Behavior

The `manage_databricks_job.py` script:

1. **Loads configuration** from JSON file
2. **Checks for existing job** with same name
3. **Creates new job** if it doesn't exist
4. **Updates existing job** with `--force-update` flag
5. **Outputs job URL** for easy access

---

## Jupyter Notebook Syncing

CI/CD pipeline automatically syncs Jupyter notebooks (.ipynb files) to Databricks with proper formatting.

### How Notebooks Are Synced

**Before sync:**
```
notebooks/
├── train.ipynb
└── inference.ipynb
```

**After sync (in Databricks workspace):**
```
/ml-regression-model-dev/
└── notebooks/
    ├── train.ipynb     ✓ Imported with JUPYTER format
    └── inference.ipynb ✓ Imported with JUPYTER format
```

### Key Features

**JUPYTER Format Import** - Uses `--format JUPYTER` for proper rendering  
**Cell Structure Preserved** - All cells, outputs, and formatting maintained  
**Executable in Databricks** - Can run directly in workspace  
**Integration with Jobs** - Jobs reference these synced notebooks  
**Automatic Updates** - Modifications to .ipynb files sync on next push  

### Notebook Execution in Jobs

When your job runs, it executes the synced notebook:

```json
{
  "notebook_task": {
    "notebook_path": "/ml-regression-model-dev/notebooks/train.ipynb",
    "source": "WORKSPACE"
  }
}
```

Databricks:
1. Locates notebook at specified path
2. Executes all cells in order
3. Captures outputs and metrics
4. Returns results and logs

### Python Code in Notebooks

Notebooks can include:

**Python code** - Executed as PySpark  
**SQL queries** - Via `%sql` magic  
**Shell commands** - Via `%sh` magic  
**Markdown cells** - For documentation  
**Visualizations** - Charts, plots, tables  
**Databricks utilities** - `dbutils` for file operations  

Example notebook cell:

```python
# In Databricks notebook
import pandas as pd
from sklearn.linear_model import LinearRegression

# Load data
data = pd.read_csv("/path/to/data.csv")

# Train model
model = LinearRegression()
model.fit(X, y)

# Log metrics
print(f"R² Score: {model.score(X, y)}")
dbutils.notebook.run("/path/to/other_notebook", 60)
```

### Syncing Your Own Notebooks

1. **Create or modify** `.ipynb` file locally
2. **Commit to Git**
   ```bash
   git add notebooks/my_notebook.ipynb
   git commit -m "feat: add new analysis notebook"
   ```
3. **Push to GitHub**
   ```bash
   git push origin dev
   ```
4. **Workflow syncs automatically** to Databricks
5. **Use in jobs** by referencing the path

### Notebook Best Practices

**Clear naming** - `data_prep.ipynb`, `train_model.ipynb`  
**Add markdown cells** - Explain what each section does  
**Modular structure** - One notebook per task  
**Parameterize** - Use widgets for dynamic inputs  
**Error handling** - Catch and handle exceptions  
**Logging** - Print progress and metrics  

Example parameterized notebook:

```python
# Create widgets for parameters
dbutils.widgets.text("model_type", "linear_regression")
dbutils.widgets.text("test_size", "0.2")

# Get parameter values
model_type = dbutils.widgets.get("model_type")
test_size = float(dbutils.widgets.get("test_size"))

# Use in code
if model_type == "linear_regression":
    model = LinearRegression()
elif model_type == "random_forest":
    model = RandomForestRegressor()
```

Then pass parameters in job config:

```json
"notebook_task": {
  "notebook_path": "/ml-regression-model-dev/notebooks/train",
  "base_parameters": {
    "model_type": "random_forest",
    "test_size": "0.3"
  }
}
```

---

### Script Behavior

The `manage_databricks_job.py` script:

1. **Loads configuration** from JSON file
2. **Checks for existing job** with same name
3. **Creates new job** if it doesn't exist
4. **Updates existing job** with `--force-update` flag
5. **Outputs job URL** for easy access

### Idempotency

Jobs are **idempotent** - running the pipeline multiple times:
- Won't create duplicate jobs
- Will update existing jobs with new config
- Safe to run repeatedly

---

## Customizing Your Jobs

### 1. Change Job Name

Edit the job config file:

```json
{
  "name": "Your_Custom_Job_Name"
}
```

⚠️ **Important:** Changing the name creates a NEW job (old job remains)

### 2. Add Multiple Tasks

```json
{
  "name": "Multi_Task_Pipeline",
  "tasks": [
    {
      "task_key": "data_prep",
      "notebook_task": {
        "notebook_path": "/ml-regression-model-dev/notebooks/prep_data"
      },
      "new_cluster": { "num_workers": 1 }
    },
    {
      "task_key": "train_model",
      "depends_on": [{"task_key": "data_prep"}],
      "notebook_task": {
        "notebook_path": "/ml-regression-model-dev/notebooks/train"
      },
      "new_cluster": { "num_workers": 2 }
    },
    {
      "task_key": "evaluate_model",
      "depends_on": [{"task_key": "train_model"}],
      "notebook_task": {
        "notebook_path": "/ml-regression-model-dev/notebooks/evaluate"
      },
      "new_cluster": { "num_workers": 1 }
    }
  ]
}
```

### 3. Change Cluster Configuration

**Cluster Size:**
```json
"new_cluster": {
  "num_workers": 4  // Increase for larger datasets
}
```

**Node Type (AWS):**
```json
"node_type_id": "i3.xlarge"  // AWS instance type
```

**Node Type (Azure):**
```json
"node_type_id": "Standard_DS4_v2"  // Azure VM size
```

**Autoscaling:**
```json
"new_cluster": {
  "autoscale": {
    "min_workers": 1,
    "max_workers": 5
  }
}
```

### 4. Set Up Job Schedule

**Daily at specific time:**
```json
"schedule": {
  "quartz_cron_expression": "0 0 2 * * ?",  // 2am UTC daily
  "timezone_id": "America/New_York",
  "pause_status": "UNPAUSED"
}
```

**Weekly on Mondays:**
```json
"schedule": {
  "quartz_cron_expression": "0 0 2 ? * MON",  // Mondays 2am
  "timezone_id": "UTC"
}
```

**Hourly:**
```json
"schedule": {
  "quartz_cron_expression": "0 0 * * * ?",  // Every hour
  "timezone_id": "UTC"
}
```

### 5. Add Email Notifications

```json
"email_notifications": {
  "on_success": ["team@company.com"],
  "on_failure": ["oncall@company.com", "manager@company.com"],
  "no_alert_for_skipped_runs": true
}
```

### 6. Pass Parameters to Notebooks

```json
"notebook_task": {
  "notebook_path": "/ml-regression-model-dev/notebooks/train",
  "base_parameters": {
    "model_type": "linear_regression",
    "max_iterations": "100",
    "test_size": "0.2"
  }
}
```

Access parameters in notebook:
```python
# In Databricks notebook
dbutils.widgets.text("model_type", "linear_regression")
dbutils.widgets.text("max_iterations", "100")

model_type = dbutils.widgets.get("model_type")
max_iter = int(dbutils.widgets.get("max_iterations"))
```

### 7. Use Existing Cluster

Instead of creating new cluster:

```json
"existing_cluster_id": "0123-456789-abc123"
```

---

## Common Use Cases

### Use Case 1: Multi-Stage ML Pipeline

```json
{
  "name": "Full_ML_Pipeline",
  "tasks": [
    {
      "task_key": "ingest_data",
      "notebook_task": {
        "notebook_path": "/ml-pipeline/01_ingest"
      }
    },
    {
      "task_key": "clean_data",
      "depends_on": [{"task_key": "ingest_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/02_clean"
      }
    },
    {
      "task_key": "feature_engineering",
      "depends_on": [{"task_key": "clean_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/03_features"
      }
    },
    {
      "task_key": "train_model",
      "depends_on": [{"task_key": "feature_engineering"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/04_train"
      }
    },
    {
      "task_key": "evaluate",
      "depends_on": [{"task_key": "train_model"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/05_evaluate"
      }
    }
  ]
}
```

### Use Case 2: A/B Test Multiple Models

```json
{
  "name": "Model_Comparison_Pipeline",
  "tasks": [
    {
      "task_key": "prep_data",
      "notebook_task": {
        "notebook_path": "/ml-pipeline/prep"
      }
    },
    {
      "task_key": "train_linear",
      "depends_on": [{"task_key": "prep_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/train",
        "base_parameters": {"model": "linear"}
      }
    },
    {
      "task_key": "train_rf",
      "depends_on": [{"task_key": "prep_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/train",
        "base_parameters": {"model": "random_forest"}
      }
    },
    {
      "task_key": "train_xgboost",
      "depends_on": [{"task_key": "prep_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/train",
        "base_parameters": {"model": "xgboost"}
      }
    },
    {
      "task_key": "compare_models",
      "depends_on": [
        {"task_key": "train_linear"},
        {"task_key": "train_rf"},
        {"task_key": "train_xgboost"}
      ],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/compare"
      }
    }
  ]
}
```

### Use Case 3: Scheduled Retraining

```json
{
  "name": "Weekly_Model_Retrain",
  "tasks": [
    {
      "task_key": "fetch_new_data",
      "notebook_task": {
        "notebook_path": "/ml-pipeline/fetch_data"
      }
    },
    {
      "task_key": "retrain_model",
      "depends_on": [{"task_key": "fetch_new_data"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/retrain"
      }
    },
    {
      "task_key": "validate_model",
      "depends_on": [{"task_key": "retrain_model"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/validate"
      }
    },
    {
      "task_key": "deploy_if_better",
      "depends_on": [{"task_key": "validate_model"}],
      "notebook_task": {
        "notebook_path": "/ml-pipeline/deploy"
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 3 ? * SUN",  // Sundays 3am
    "timezone_id": "UTC"
  }
}
```

---

## Testing Job Creation

You can test job creation without pushing to GitHub:

### Prerequisites

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token-here"
```

### Test Job Creation

```bash
# Create/update dev job
python .github/scripts/manage_databricks_job.py \
  --config databricks_job_config.json \
  --force-update

# Create/update prod job
python .github/scripts/manage_databricks_job.py \
  --config databricks_job_config_prod.json \
  --force-update
```

### Create and Immediately Run

```bash
python .github/scripts/manage_databricks_job.py \
  --config databricks_job_config.json \
  --force-update \
  --run
```

---

## Syncing Changes Back from Databricks UI

You can modify Databricks jobs in the UI, export their configuration, and sync changes back to Git.

### Workflow

```
1. Edit job in Databricks UI
   ↓
2. Export job configuration as JSON
   ↓
3. Copy JSON to Git repo (config/databricks_job_config.json)
   ↓
4. Commit and push to GitHub
   ↓
5. Next workflow run uses updated config
   ↓
6. Job stays in sync with Git
```

### Step-by-Step: Export Job from Databricks

#### Method A: Using Databricks CLI (Recommended)

```bash
# Get job ID
databricks jobs list --output JSON | grep "ML_Regression_Training"

# Export job configuration
databricks jobs get --job-id <JOB_ID> > job_export.json

# Pretty-print to review
cat job_export.json | python -m json.tool
```

#### Method B: Using Databricks UI

1. Open your job in Databricks
2. Click **Workflows** → Find your job
3. Right-click and select **Export** or take note of job ID
4. Use CLI method above

### Clean Up Exported JSON

The export includes extra fields. Extract only the `settings` object:

```bash
# Using Python
python3 << 'EOF'
import json
with open('job_export.json', 'r') as f:
    data = json.load(f)
settings = data.get('settings', data)
with open('config/databricks_job_config.json', 'w') as f:
    json.dump(settings, f, indent=2)
print("✓ Extracted settings")
EOF
```

Or using `jq`:
```bash
jq '.settings' job_export.json > config/databricks_job_config.json
```

### Update Git and Commit

```bash
# Verify JSON is valid
python -m json.tool < config/databricks_job_config.json > /dev/null

# Commit changes
git add config/databricks_job_config.json
git commit -m "chore: sync Databricks job config from UI"
git push origin dev  # or main for prod job
```

### Result

Next workflow run will:
1. Detect config change
2. Update Databricks job with new configuration
3. Keep everything in sync ✓

---

## FAQ & Best Practices

### Q1: Will jobs update every workflow run?

**A:** No, only when config changes. The workflow checks:
```yaml
git diff HEAD~1 HEAD config/databricks_job_config.json
```

**If no change** → Skip job update  
**If change detected** → Update job

This is efficient and prevents unnecessary API calls.

### Q2: Can I edit jobs in the Databricks UI?

**A:** **Yes!** Then export the config back to Git:

1. Edit job in Databricks UI
2. Test it manually
3. Export config to JSON
4. Commit to Git
5. Workflow keeps everything in sync

### Q3: What if my cluster doesn't support new_cluster config?

**A:** Use `existing_cluster_id` instead:

```json
{
  "name": "ML_Regression_Training",
  "tasks": [...],
  "existing_cluster_id": "0123-456789-abc123"
}
```

### Q4: Can I have multiple jobs?

**A:** Yes! Create multiple config files:

```
config/
├── databricks_job_config.json           # Dev training job
├── databricks_job_config_prod.json      # Prod training job
├── data_prep_job_config.json            # Data prep job
└── evaluation_job_config.json           # Model evaluation job
```

Then create a workflow step for each:

```yaml
- name: Create/Update Training Job
  run: python manage_databricks_job.py --config config/databricks_job_config.json
  
- name: Create/Update Data Prep Job
  run: python manage_databricks_job.py --config config/data_prep_job_config.json
```

### Q5: How do I enable/disable the production schedule?

**A:** Change `pause_status` in `databricks_job_config_prod.json`:

```json
"schedule": {
  "quartz_cron_expression": "0 0 2 * * ?",
  "timezone_id": "UTC",
  "pause_status": "UNPAUSED"  // Set to UNPAUSED to enable
}
```

Or in Databricks UI:
1. Open job → Click **Schedule**
2. Toggle **Pause job** on/off
3. Export config to Git

### Q6: What's the difference between single and multi-task jobs?

**Single-task (simpler, what we use):**
```json
{
  "name": "job_name",
  "notebook_task": {...},
  "format": "MULTI_TASK"  // Even single task uses MULTI_TASK
}
```

**Multi-task (with dependencies):**
```json
{
  "name": "pipeline",
  "tasks": [
    {"task_key": "step1", ...},
    {"task_key": "step2", "depends_on": [{"task_key": "step1"}], ...}
  ],
  "format": "MULTI_TASK"
}
```

---

## Best Practices

### 1. Always Review Changes
```bash
git diff config/databricks_job_config.json
python -m json.tool < config/databricks_job_config.json
```

### 2. Keep Git as Source of Truth
- Edit in Databricks UI for testing
- Export to Git for versioning
- Let workflow apply updates

### 3. Use Meaningful Names
✅ `train_model`, `validate_data`, `deploy_model`  
❌ `task1`, `step2`, `process`

### 4. Test in Dev First
- Make changes in dev job config
- Verify workflow updates job correctly
- Then update production job

### 5. Document Important Changes
```bash
git commit -m "feat: add data validation step to training pipeline"
git commit -m "chore: increase cluster workers from 1 to 4"
git commit -m "fix: update notebook path for training job"
```

### 6. Conditional Updates (Already Implemented)
Your workflow automatically:
- Creates new jobs only once
- Updates only when config changes
- Skips unnecessary API calls

---

## Troubleshooting

### Issue: Job not created

**Check:**
1. Databricks credentials are correct
2. Job config JSON is valid
3. Notebook paths exist in workspace
4. Cluster configuration is valid for your workspace

**View logs:**
- GitHub Actions → Click workflow run → Expand "Create/Update Databricks Job" step

### Issue: Job created but won't run

**Common causes:**
- Notebook path incorrect
- Cluster size too large for workspace limits
- Missing notebook dependencies
- Invalid parameters

**Fix:**
1. Go to Databricks UI
2. Navigate to Workflows → Jobs
3. Find your job
4. Click "Run now"
5. Check error messages in run logs

### Issue: Job exists but not updating

**Solution:**
The workflow uses `--force-update` flag by default. If updates aren't applying:

1. Delete the job manually in Databricks UI
2. Push code again to recreate it

Or check job name matches exactly in config file.

### Issue: Wrong cluster type

**Error:** `Invalid node_type_id`

**Fix:** Node types differ by cloud provider:

**AWS:**
```json
"node_type_id": "i3.xlarge"
```

**Azure:**
```json
"node_type_id": "Standard_DS3_v2"
```

**GCP:**
```json
"node_type_id": "n1-standard-4"
```

Check available node types:
```bash
databricks clusters list-node-types
```

### Issue: Schedule not working

**Check:**
1. Cron expression is valid (use [crontab.guru](https://crontab.guru/))
2. `pause_status` is set to `"UNPAUSED"`
3. Timezone is correct

**Enable schedule:**
```json
"schedule": {
  "quartz_cron_expression": "0 0 2 * * ?",
  "timezone_id": "UTC",
  "pause_status": "UNPAUSED"  // ← Change from PAUSED
}
```

---

## Additional Resources

- [Databricks Jobs API Documentation](https://docs.databricks.com/dev-tools/api/latest/jobs.html)
- [Databricks CLI Reference](https://docs.databricks.com/dev-tools/cli/index.html)
- [Quartz Cron Expressions](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html)
- [Cluster Configuration Guide](https://docs.databricks.com/clusters/configure.html)

---

## Next Steps

1. Review `databricks_job_config.json` and `databricks_job_config_prod.json`
2. Customize job names, schedules, and cluster sizes
3. Push code to `dev` branch to test job creation
4. Verify job appears in Databricks UI (Workflows → Jobs)
5. Run job manually to test
---

## Technical Details: File Sync Implementation

### sync_to_databricks.py Script

The script intelligently handles different file types:

**File Processing Flow:**

```
File discovered in git
    ↓
Is it binary/compiled? → YES → Skip (don't upload)
    ↓ NO
Is it a Jupyter notebook (.ipynb)? → YES → import_notebook()
    ↓ NO
Is it source code? → upload_file()
```

### Jupyter Notebook Handling

When a `.ipynb` file is detected:

```python
def import_notebook(source_path, databricks_path):
    # Create directory if needed
    databricks workspace mkdirs <target_dir>
    
    # Import with JUPYTER format (critical!)
    databricks workspace import \
      <source_path> \
      <target_path> \
      --language PYTHON \
      --format JUPYTER \           # ← Preserves notebook structure
      --overwrite
```

**Key aspects:**
- `--format JUPYTER` - Tells Databricks to treat as notebook, not raw code
- `--language PYTHON` - Default language (can be changed per notebook)
- `--overwrite` - Updates existing notebooks on push
- Directory creation - Ensures target paths exist before import

### Source Code Handling

For `.py`, `.yaml`, and other code files:

```python
def upload_file(source_path, target_path, databricks_path):
    # Detect language from extension
    language = get_language_for_file(source_path)
    # .py → PYTHON, .scala → SCALA, etc.
    
    # Upload as source code
    databricks workspace import \
      <source_path> \
      <target_path> \
      --language <DETECTED> \
      --overwrite
```

**Language Detection:**
| Extension | Language |
|-----------|----------|
| `.py` | PYTHON |
| `.scala` | SCALA |
| `.sql` | SQL |
| `.r` | R |
| `.yaml`, `.md`, `.json`, etc. | PYTHON (default) |

### File Filtering

**Excluded (not synced):**
- `.git`, `.github`, `.gitignore`
- `__pycache__`, `.pytest_cache`
- `*.pyc`, `*.pyo` (compiled Python)
- `.DS_Store` (macOS metadata)
- Binary/executable files

**Included (synced):**
- Source code (`.py`, `.scala`, `.sql`, `.r`)
- Jupyter notebooks (`.ipynb`)
- Configuration (`.yaml`, `.json`)
- Documentation (`.md`, `.txt`)

### Sync Summary Output

```
50 matches (more results are available)
Starting sync from . to /ml-regression-model-dev
Branch: dev
Total files to sync: 28

✓ Uploaded: /ml-regression-model-dev/src/utils.py
✓ Uploaded: /ml-regression-model-dev/config/model_config.yaml
✓ Uploaded notebook: /ml-regression-model-dev/notebooks/train.ipynb
✓ Uploaded notebook: /ml-regression-model-dev/notebooks/inference.ipynb
⊘ Skipped: .gitignore (excluded pattern)
...

==================================================
Sync Summary:
  Successful: 25
  Failed: 0
  Skipped: 3
  Total processed: 25
==================================================
```

### Error Handling

If sync fails for a file:

```
✗ Failed to upload: /ml-regression-model-dev/src/utils.py
  Error: <error message from CLI>
  Output: <any additional output>
```

**Common failures:**
- Path too long (Databricks limitation)
- Invalid characters in filename
- Permission issues
- Network timeout

**Solution:** Check error message, fix locally, and re-push to retry

---

6. Push to `main` for production job creation
7. Enable schedule in prod job when ready

---