#!/usr/bin/env python3
"""
Manage Databricks Jobs via CLI
Creates or updates Databricks job definitions for ML pipelines
"""

import os
import sys
import json
import subprocess
import argparse


def run_command(cmd, capture_output=True):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def load_job_config(config_path):
    """Load job configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✓ Loaded job configuration from {config_path}")
        return config
    except FileNotFoundError:
        print(f"Job config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config file: {e}")
        sys.exit(1)


def get_existing_job_id(job_name):
    """Check if job with given name already exists"""
    try:
        result = run_command("databricks jobs list --output JSON")
        jobs = json.loads(result) if result else {"jobs": []}
        
        for job in jobs.get("jobs", []):
            if job.get("settings", {}).get("name") == job_name:
                return job.get("job_id")
        
        return None
    except Exception as e:
        print(f"Warning: Could not check existing jobs: {e}")
        return None


def create_job(config_path):
    """Create a new Databricks job"""
    print(f"Creating new Databricks job...")
    
    cmd = f'databricks jobs create --json-file "{config_path}"'
    output = run_command(cmd)
    
    try:
        result = json.loads(output)
        job_id = result.get("job_id")
        print(f"Job created successfully! Job ID: {job_id}")
        return job_id
    except json.JSONDecodeError:
        print(f"Job created successfully!")
        return None


def update_job(job_id, config):
    """Update existing Databricks job"""
    print(f"Updating existing Databricks job (ID: {job_id})...")
    
    # Create temporary config file for update
    temp_file = "temp_job_config.json"
    with open(temp_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        cmd = f'databricks jobs reset --job-id {job_id} --json-file "{temp_file}"'
        run_command(cmd, capture_output=False)
        print(f"Job updated successfully! Job ID: {job_id}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return job_id


def manage_job(config_path, force_update=False):
    """Create or update Databricks job based on configuration"""
    
    # Load configuration
    config = load_job_config(config_path)
    job_name = config.get("name")
    
    if not job_name:
        print("Job name not found in configuration")
        sys.exit(1)
    
    print(f"Managing job: {job_name}")
    
    # Check if job exists
    existing_job_id = get_existing_job_id(job_name)
    
    if existing_job_id:
        print(f" Job already exists with ID: {existing_job_id}")
        
        if force_update:
            job_id = update_job(existing_job_id, config)
        else:
            print(" Skipping update (use --force-update to update existing job)")
            job_id = existing_job_id
    else:
        print("Job does not exist, creating new job")
        job_id = create_job(config_path)
    
    return job_id


def get_job_url(job_id):
    """Construct Databricks job URL"""
    databricks_host = os.environ.get("DATABRICKS_HOST", "")
    if databricks_host and job_id:
        # Remove trailing slash if present
        host = databricks_host.rstrip("/")
        return f"{host}/#job/{job_id}"
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks jobs via CLI"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to job configuration JSON file"
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Force update if job already exists"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Trigger job run after creation/update"
    )
    
    args = parser.parse_args()
    
    # Verify Databricks credentials
    if not os.environ.get("DATABRICKS_HOST") or not os.environ.get("DATABRICKS_TOKEN"):
        print(" DATABRICKS_HOST and DATABRICKS_TOKEN environment variables must be set")
        sys.exit(1)
    
    # Configure Jobs API 2.1
    print("Configuring Databricks CLI to use Jobs API 2.1...")
    try:
        run_command("databricks jobs configure --version=2.1", capture_output=False)
        print("✓ Jobs API 2.1 configured")
    except:
        print("Warning: Could not configure Jobs API version, continuing anyway...")
    
    print("=" * 60)
    print("Databricks Job Management")
    print("=" * 60)
    
    # Manage job (create or update)
    job_id = manage_job(args.config, args.force_update)
    
    # Display job URL
    job_url = get_job_url(job_id)
    if job_url:
        print(f"\n Job URL: {job_url}")
    
    # Optionally trigger job run
    if args.run and job_id:
        print(f"\n Triggering job run...")
        cmd = f"databricks jobs run-now --job-id {job_id}"
        output = run_command(cmd)
        
        try:
            result = json.loads(output)
            run_id = result.get("run_id")
            print(f" Job run triggered! Run ID: {run_id}")
            
            if job_url:
                print(f"Run URL: {job_url}/runs/{run_id}")
        except json.JSONDecodeError:
            print(f" Job run triggered!")
    
    print("\n" + "=" * 60)
    print("Job management completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()