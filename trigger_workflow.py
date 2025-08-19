#!/usr/bin/env python3
import os
import requests
import json

# GitHub token from environment
github_token = os.environ.get('GITHUB_TOKEN')
if not github_token:
    print("Error: GITHUB_TOKEN environment variable not set")
    exit(1)

# Repository information
repo_owner = "diponkarsinha"
repo_name = "Fraud_detection_sys"
workflow_id = "fraud-detection.yml"

# API endpoint
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
payload = {"ref": "main"}

# Trigger workflow
print(f"Triggering workflow: {workflow_id}")
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check response
if response.status_code == 204:
    print("✅ Success! Workflow triggered.")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)