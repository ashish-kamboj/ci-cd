# Quick Start - 5 Minute Setup

Get your CI/CD pipeline running in 5 minutes.

## 1️. Get Databricks Token (2 min)

**In Databricks:**
1. Click your profile icon (top-right)
2. **Settings** → **Developer** → **Access tokens**
3. **Generate new token**
4. Set expiration: 90 days
5. **Copy the token** (save it securely)

**Get workspace URL:**
- Look at your browser URL bar
- Copy the base: `https://<region>.cloud.databricks.com`
- Example: `https://eastus2.cloud.databricks.com`

## 2️. Add GitHub Secrets (2 min)

**In GitHub:**
1. Go to your repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** (green button)

**Add Secret #1:**
- Name: `DATABRICKS_HOST`
- Value: `https://eastus2.cloud.databricks.com` ← your URL
- Click **Add secret**

**Add Secret #2:**
- Name: `DATABRICKS_TOKEN`
- Value: ← paste your token from Databricks
- Click **Add secret**

## 3️. Test It (1 min)

1. Make a small change to a file (any file)
2. Commit and push to `dev` branch:
   ```bash
   git add .
   git commit -m "test: verify pipeline"
   git push origin dev
   ```
3. Go to GitHub **Actions** tab
4. Watch the workflow run (takes ~2 min)
5. Check Databricks workspace for files at `/ml-regression-model-dev`

## Done! 

Pipeline is live and working.

---

## Next Steps

- Read [README.md](README.md) for complete documentation
- Run local tests: `pytest tests/ -v`
- Modify `config/model_config.yaml` to change model parameters
- Push to `main` branch when ready for production
- Merge branches when code is tested and working

---

## Troubleshooting

**Workflow not running?**
- Pushed to `dev` or `main` branch?
- Wait 1-2 minutes for workflow to appear

**Files not in Databricks?**
- Check GitHub Actions logs for errors
- Verify `DATABRICKS_HOST` and `DATABRICKS_TOKEN` secrets exist
- Token hasn't expired?

**Tests failing?**
- Run locally: `pytest tests/ -v`
- Fix errors, commit, and push again

**More help?**
- See Troubleshooting section in [README.md](README.md)

