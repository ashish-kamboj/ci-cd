# ML Regression Model - GitHub Actions CI/CD Pipeline

A complete, production-ready CI/CD pipeline for ML projects using GitHub Actions and Databricks. Automatically syncs code, runs tests, and manages deployments across development and production environments.

## Quick Summary

- **What it does**: Automatically tests and deploys ML code from GitHub to Databricks
- **When it works**: Every time you push code to `dev` or `main` branch
- **Where it goes**: `/ml-regression-model-dev` (dev) or `/ml-regression-model-prod` (prod)

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Setup Instructions](#setup-instructions)
5. [How It Works](#how-it-works)
6. [File Reference](#file-reference)
7. [Common Commands](#common-commands)
8. [Troubleshooting](#troubleshooting)
9. [Architecture](#architecture)

---

## Features

### CI/CD Pipeline
- **Automated testing** - Unit tests run before deployment
- **Dual environments** - Separate dev (`/ml-regression-model-dev`) and prod (`/ml-regression-model-prod`)
- **File sync** - Automatically uploads new and modified files
- **Cleanup** - Removes deleted files from Databricks
- **Branch-aware** - Different paths based on `dev` or `main` branch
- **Approval gates** - Mandatory review & approval required before production deployment
- **Job automation** - Automatically creates/updates Databricks jobs (ML pipelines)

### ML Model
- **Modular code** - Config, utils, notebook, tests
- **YAML configuration** - Change parameters without code changes
- **Linear regression** - Boston Housing dataset example
- **Comprehensive tests** - 12 unit tests for all functionality
- **Metrics tracking** - Automatic MSE, RMSE, MAE, R² reporting

---

## Project Structure

```
.
├── .github/
│   ├── workflows/
│   │   └── databricks-sync.yml          # Main CI/CD workflow
│   └── scripts/
│       ├── sync_to_databricks.py        # File upload script
│       ├── cleanup_deleted_files.py     # Deletion handler
│       └── manage_databricks_job.py     # Job creation/update script
│
├── config/
│   ├── model_config.yaml                # Model parameters (edit this)
│   ├── databricks_job_config.json       # Dev job configuration
│   └── databricks_job_config_prod.json  # Prod job configuration
│
├── src/
│   ├── __init__.py                      # Package marker
│   └── utils.py                         # Utility functions
│
├── notebooks/
│   ├── train.ipynb                      # Training notebook
│   └── inference.ipynb                  # Inference notebook
│
├── tests/
│   └── test_model.py                    # 12 unit tests
│
├── requirements.txt                     # Python dependencies
├── .gitignore                          # Git ignore patterns
├── README.md                           # This file (project overview)
├── QUICK_START.md                      # 5-min setup guide
└── DATABRICKS_JOBS_GUIDE.md            # Job automation & configuration
```

---

## Quick Start

### Step 1: Get Databricks Credentials

1. Log in to Databricks → Click profile icon → **Settings**
2. Go to **Developer** → **Access tokens** → **Generate new token**
3. Set expiration (90 days) and **copy the token**
4. Note your workspace URL: `https://<region>.cloud.databricks.com`

### Step 2: Add GitHub Secrets

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add `DATABRICKS_HOST` = your workspace URL
4. Add `DATABRICKS_TOKEN` = your token

### Step 3: Test the Pipeline

1. Make a small change to any file
2. Commit and push to `dev` branch
3. Go to **Actions** tab in GitHub
4. Watch the workflow run
5. Check Databricks for files at `/ml-regression-model-dev`

**Done!** CI/CD pipeline is live.

---

## Setup Instructions

### Prerequisites

- GitHub repository with `dev` and `main` branches
- Databricks workspace (any plan)
- GitHub Actions enabled (default)

### Detailed Setup

#### 1. Generate Databricks Token

```
Databricks → Profile Icon → Settings → Developer → Access Tokens
→ Generate New Token (copy the token)
```

Get workspace URL from your Databricks URL bar:
- Format: `https://<region>.cloud.databricks.com`
- Example: `https://eastus2.cloud.databricks.com`

#### 2. Create GitHub Secrets

| Secret | Value |
|--------|-------|
| `DATABRICKS_HOST` | Your workspace URL |
| `DATABRICKS_TOKEN` | Your access token |

Steps:
1. GitHub → Settings → Secrets and variables → Actions
2. Select **Repository secrets**
3. New repository secret → Enter name and value
4. Click **Add secret**

#### 3. Create GitHub Environments (Optional but Recommended)

To enable **approval gates** for production deployments:

**For development (auto-deploy):**
1. Go to GitHub repo → **Settings** → **Environments**
2. Click **New environment**
3. Name: `databricks-dev`
4. Click **Configure environment** (keep defaults, no protection rules)
5. Click **Save**

**For production (requires approval):**
1. Click **New environment** again
2. Name: `databricks-prod`
3. Under **Deployment branches and tags**:
   - Select **Selected branches**
   - Add branch: `main`
4. Under **Required reviewers**:
   - ✓ Check the box
   - Add yourself or team members who should approve prod deployments
5. Click **Save protection rules**

**Result:**
- `dev` branch → `databricks-dev` (deploys automatically)
- `main` branch → `databricks-prod` (pauses for approval)

#### 4. Customize Databricks Jobs (Optional)

The pipeline automatically creates/updates Databricks jobs for ML pipelines:

**Job Configuration Files:**
- `databricks_job_config.json` - Development job (dev branch)
- `databricks_job_config_prod.json` - Production job (main branch)

**What gets automated:**
- Job creation if doesn't exist
- Job updates when config changes
- Cluster configuration
- Notebook linking
- Schedules (prod only, starts paused)

**To customize:** Edit the JSON files to change:
- Job names
- Cluster sizes
- Schedules
- Email notifications
- Multi-task workflows

**Complete guide:** See [DATABRICKS_JOBS_GUIDE.md](DATABRICKS_JOBS_GUIDE.md) for detailed instructions.

#### 5. Verify Setup

1. Make a small change (e.g., update `config/model_config.yaml`)
2. Commit: `git commit -m "test: verify pipeline"`
3. Push to dev: `git push origin dev`
4. Check GitHub Actions tab
5. Verify files appear in Databricks

---

## How It Works

### Automatic Workflow

#### Development Branch (auto-deploy)
```
Push to dev
    ↓
Run Tests
    ↓
   PASS? ──→ NO ──→ Stop
    ↓
   YES
    ↓
Sync to Databricks (/ml-regression-model-dev)
    ↓
Create/Update Databricks Job (ML_Regression_Pipeline)
    ↓
Clean up deleted files
    Done
```

#### Production Branch (requires approval)
```
Push to main
    ↓
Run Tests
    ↓
   PASS? ──→ NO ──→ Stop
    ↓
   YES
    ↓
⏸️  AWAIT APPROVAL
    (GitHub pauses workflow)
    (Reviewers notified)
    ↓
Reviewer clicks "Approve"?
    ↓
   YES ──→ Sync to Databricks (/ml-regression-model-prod)
    ↓
Create/Update Databricks Job (ML_Regression_Pipeline_Prod)
    ↓
   NO ──→ Stop (deployment blocked)
    ↓
Clean up deleted files
    Done
```
    ↓
Clean up deleted files
    Done
```

### Branch Behavior

| Branch | Sync Path | Purpose |
|--------|-----------|---------|
| `dev` | `/ml-regression-model-dev` | Development & testing |
| `main` | `/ml-regression-model-prod` | Production (stable) |

### What Gets Synced

✅ **Included**: `.py`, `.yaml`, `.ipynb` (Jupyter notebooks), `.txt`, `.md` files
- Python files: Synced as SOURCE code (auto-detected)
- YAML config: Synced as PYTHON code
- **Jupyter notebooks**: Synced with JUPYTER format for proper rendering
- Markdown & text: Synced as documentation
  
❌ **Excluded**: `.git`, `__pycache__`, `.pyc`, `.DS_Store`, binary files  

### What Happens on Delete

When you delete a file locally and push:
1. Workflow detects deletion via `git diff`
2. File is automatically removed from Databricks
3. Workspace stays clean and in sync

---

## File Reference

### Workflow Files (`.github/`)

**`databricks-sync.yml`**
- Main GitHub Actions workflow
- 3 jobs: test, sync, cleanup
- Triggers on push to dev/main branches
- Uses secrets for authentication

**`sync_to_databricks.py`**
- Uploads files to Databricks workspace
- Smart language detection for code files
- Special handling for Jupyter notebooks (.ipynb files)
  - Uses `--format JUPYTER` for proper notebook import
  - Preserves notebook structure and cell formatting
- Excludes binary and cache files
- Error reporting with diagnostics

**`cleanup_deleted_files.py`**
- Detects deleted files via git diff
- Removes them from Databricks workspace
- Prevents workspace clutter

---

## Approval Process (Production Safety)

### How Approval Gates Work

When you push to the `main` branch (production), the workflow **pauses automatically** and waits for approval before deploying:

1. **Tests Run** - Unit tests execute first
2. **Workflow Pauses** - If tests pass, workflow waits for approval
3. **Notification** - Configured reviewers are notified
4. **Review** - Reviewers examine the changes in GitHub
5. **Decision** - Reviewer clicks "Approve" or "Reject"
6. **Deploy or Block** - Approved → sync to Databricks, Rejected → stop

### Approval Workflow in GitHub Actions

**Step-by-step:**

1. You push code to `main` branch
2. Tests run automatically
3. GitHub Actions shows workflow status → **Awaiting approval**
4. Go to **Actions** tab → Click the workflow
5. You'll see button: **Review deployments**
6. Select required reviewers and click **Approve**
7. Workflow resumes and syncs to Databricks

### Environment Configuration

| Environment | Branch | Auto-Deploy? | Requires Approval? |
|-------------|--------|--------------|-------------------|
| `databricks-dev` | `dev` | Yes | No |
| `databricks-prod` | `main` | No | Yes |

### Why This Matters

- **Safety**: Prevents accidental production deployments
- **Control**: Team lead/senior engineer must review changes
- **Audit Trail**: GitHub records who approved what and when
- **Rollback Ready**: Time to prepare rollback if needed

---

### ML Code (`src/`, `config/`, `notebooks/`)

**`config/model_config.yaml`**
- Model parameters and configuration
- Features, train/test split, model settings
- Edit this to change model behavior (no code changes needed)

**`src/utils.py`**
- `load_config()` - Load YAML configuration
- `prepare_features()` - Extract feature arrays
- `evaluate_model()` - Calculate metrics
- `validate_input()` - Data validation
- `save_metrics()` - Export results

**`notebooks/train.ipynb`**
- Self-contained training notebook
- Runs in Databricks
- Loads config, trains model, evaluates metrics
- Saves results to JSON

### Tests (`tests/`)

**`test_model.py`** - 12 unit tests
- `TestConfigLoading` - Configuration loading (2 tests)
- `TestMetricsHandling` - Metric calculation (3 tests)
- `TestFeaturePreparation` - Feature extraction (2 tests)
- `TestInputValidation` - Data validation (3 tests)

Run locally: `pytest tests/ -v`

---

## Common Commands

### Running Tests Locally

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_model.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=src
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature
git checkout dev
git pull origin dev

# Make changes and commit
git add .
git commit -m "description of changes"

# Push to dev branch
git push origin dev

# Merge to main (production)
git checkout main
git pull origin main
git merge dev
git push origin main
```

### Manual Databricks Operations

```bash
# Configure Databricks CLI
databricks configure --token

# List workspace files
databricks workspace ls /ml-regression-model-dev

# Upload file
databricks workspace import --language PYTHON src/utils.py /ml-regression-model-dev/src/utils

# Delete file
databricks workspace rm /ml-regression-model-dev/src/utils

# Download file
databricks workspace export /ml-regression-model-dev/src/utils.py utils.py
```

---

## Troubleshooting

### "Tests fail before sync"

**Problem**: GitHub Actions shows red X, files not uploaded  
**Solution**:
1. Check Actions tab for error message
2. Run tests locally: `pytest tests/ -v`
3. Fix failing tests
4. Commit and push again

### "Files don't appear in Databricks"

**Problem**: Workflow completes but no files in workspace  
**Checks**:
1. Verify secrets are set correctly:
   - `DATABRICKS_HOST` = full workspace URL
   - `DATABRICKS_TOKEN` = valid token (not expired)
2. Check Actions logs for errors
3. Verify branch is `dev` or `main` (others are ignored)
4. Check Databricks workspace permissions

**Manual test**:
```bash
python .github/scripts/sync_to_databricks.py \
  --source-dir . \
  --target-path /ml-regression-model-dev \
  --branch dev
```

### "Workflow never runs"

**Problem**: No workflow in Actions tab after push  
**Checks**:
1. Workflow file exists: `.github/workflows/databricks-sync.yml`
2. Filename ends in `.yml` (not `.yaml`)
3. Pushed to `dev` or `main` branch (other branches ignored)
4. Wait 1-2 minutes for workflow to appear

### "Workflow runs but gets stuck"

**Problem**: Workflow runs for 10+ minutes and hangs  
**Solution**:
1. Cancel workflow (Actions tab → workflow → Cancel)
2. Check Actions logs for last line of output
3. Usually: authentication issue or network timeout
4. Verify credentials and try again

### "Can't import src module in tests"

**Problem**: Import error: `No module named 'src'`  
**Solution**:
1. Ensure `src/__init__.py` exists (creates package)
2. Run with: `PYTHONPATH=. pytest tests/`
3. Or set in VS Code settings

---

## Architecture

### System Components

```
┌───────────────────────┐
│  GitHub Repository    │
│  (dev + main branches)│
└──────────┬────────────┘
           │
           │ (push event)
           v
┌───────────────────────────────────────┐
│     GitHub Actions (CI/CD)            │
│                                       │
│  Job 1: Test (pytest)                 │
│  Job 2: Sync (databricks CLI)         │
│  Job 3: Cleanup (deleted files)       │
└──────────┬────────────────────────────┘
           │
           v
┌───────────────────────────────────────┐
│    Databricks Workspace               │
│                                       │
│  /ml-regression-model-dev     (dev)   │
│  /ml-regression-model-prod    (prod)  │
└───────────────────────────────────────┘
```

### Data Flow

1. **Developer** → Makes changes locally
2. **Git** → Commits and pushes to GitHub
3. **GitHub Actions** → Detects push event
4. **Test Job** → Runs `pytest tests/`
   - If fails: ❌ Stop, don't deploy
   - If passes: ✅ Continue to sync
5. **Sync Job** → Uploads files via Databricks CLI
   - Determines path (dev or prod)
   - Creates workspace directories
   - Imports all files with language detection
6. **Cleanup Job** → Removes deleted files
   - Git diff finds deleted files
   - Databricks CLI removes them
7. **Databricks** → Stores synced files
   - Ready to run training notebooks
   - Notebooks use imported utils and config

### Configuration Files

**`requirements.txt`** - Python dependencies
```
pyyaml>=6.0
pandas>=1.3.0
scikit-learn>=1.0.0
numpy>=1.21.0
pytest>=6.2.0
pytest-cov
databricks-cli
```

**`.gitignore`** - Files to exclude from git
- `.git`, `__pycache__`, `.pyc`, `.DS_Store`, `.databrickscfg`

**`setup.sh` / `setup.bat`** - Environment setup scripts

---

## Best Practices

1. **Test before pushing**
   ```bash
   pytest tests/ -v
   ```

2. **Use meaningful commit messages**
   ```bash
   git commit -m "feat: add new feature" # not "fix"
   ```

3. **Keep config in YAML**
   - Modify `config/model_config.yaml` for model changes
   - Don't hardcode parameters in code

4. **Check workflow status**
   - GitHub Actions tab after every push
   - Fix any failures immediately

5. **Use dev branch for experiments**
   - Test new features on `dev`
   - Only merge stable code to `main`

6. **Document your changes**
   - Update README if adding features
   - Comment complex code

---

## Security

- Never commit secrets to repository
- Rotate Databricks tokens regularly (90+ days)
- Use repository secrets (not organization-level)
- Restrict Databricks token permissions if possible
- Review workflow logs for sensitive information

---

## External Resources

- **Databricks Docs**: https://docs.databricks.com
- **GitHub Actions**: https://docs.github.com/en/actions
- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Databricks CLI**: https://docs.databricks.com/dev-tools/cli/

---

## Support & Debugging

### Check Logs
1. GitHub Actions tab → Select workflow
2. Click failed job for detailed logs
3. Look for error messages and stack traces

### Manual Testing
```bash
# Test locally
pytest tests/ -v

# Test databricks connection
databricks workspace ls /

# Verify config loads
python -c "from src.utils import load_config; print(load_config('config/model_config.yaml'))"
```

### Common Issues
- **Auth errors**: Check secrets are set correctly
- **Import errors**: Ensure `src/__init__.py` exists
- **Path errors**: Verify workspace path is correct
- **Timeout errors**: Check network connectivity

---

## Model Configuration

Edit `config/model_config.yaml` to change:

```yaml
model_config:
  name: "ML Regression"
  version: "1.0"
  features:
    numerical_features: ["RM", "LSTAT", "AGE"]
  target: "MEDV"
  train_test_split: 0.2
```

Access in code:
```python
from src.utils import load_config
config = load_config('config/model_config.yaml')
features = config['model_config']['features']['numerical_features']
```

---

## All Set!

CI/CD pipeline is ready to use. Next steps:

1. Verify secrets are added
2. Make a test push to `dev`
3. Check Actions tab
4. Confirm files in Databricks
5. Run training notebook
6. Review metrics and results

For quick setup reference, see [QUICK_START.md](QUICK_START.md).

---