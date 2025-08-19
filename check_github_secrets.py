#!/usr/bin/env python3
"""
GitHub Secrets Configuration Checker
Helps verify which secrets are configured and provides setup guidance.
"""

import os
import json
import subprocess
from datetime import datetime

def get_repo_info():
    """Get current repository information"""
    try:
        # Get remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True, check=True)
        remote_url = result.stdout.strip()
        
        # Extract repo info from URL
        if 'github.com' in remote_url:
            if remote_url.startswith('https://'):
                # https://github.com/username/repo.git
                repo_path = remote_url.replace('https://github.com/', '').replace('.git', '')
            elif remote_url.startswith('git@'):
                # git@github.com:username/repo.git
                repo_path = remote_url.replace('git@github.com:', '').replace('.git', '')
            else:
                repo_path = "unknown/unknown"
        else:
            repo_path = "unknown/unknown"
            
        return repo_path
    except Exception as e:
        return "unknown/unknown"

def check_required_secrets():
    """Check which secrets are required for the fraud detection system"""
    required_secrets = {
        'AWS_DEFAULT_REGION': {
            'description': 'AWS region for SES (e.g., us-east-1)',
            'example': 'us-east-1',
            'required': True
        },
        'AWS_ROLE_TO_ASSUME': {
            'description': 'AWS IAM role ARN for OIDC authentication',
            'example': 'arn:aws:iam::123456789012:role/GitHubActionsRole',
            'required': True
        },
        'FRAUD_ALERT_EMAIL': {
            'description': 'Email address to receive fraud alerts',
            'example': 'alerts@yourcompany.com',
            'required': True
        },
        'SES_SENDER_EMAIL': {
            'description': 'Verified SES sender email address',
            'example': 'noreply@yourcompany.com',
            'required': True
        },
        'KAGGLE_USERNAME': {
            'description': 'Your Kaggle username',
            'example': 'your_kaggle_username',
            'required': True
        },
        'KAGGLE_KEY': {
            'description': 'Your Kaggle API key',
            'example': 'abc123def456...',
            'required': True
        }
    }
    
    return required_secrets

def generate_setup_instructions(repo_path):
    """Generate specific setup instructions for this repository"""
    secrets = check_required_secrets()
    
    print("\n" + "="*60)
    print("🔧 GITHUB SECRETS MANUAL SETUP GUIDE")
    print("="*60)
    
    print(f"\n📍 Repository: {repo_path}")
    print(f"🔗 Settings URL: https://github.com/{repo_path}/settings/secrets/actions")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🚀 QUICK SETUP STEPS:")
    print("1. Go to your GitHub repository")
    print("2. Click Settings → Secrets and variables → Actions")
    print("3. Click 'New repository secret' for each secret below")
    
    print("\n📋 REQUIRED SECRETS TO ADD:")
    print("-" * 50)
    
    for i, (secret_name, info) in enumerate(secrets.items(), 1):
        print(f"\n{i}. {secret_name}")
        print(f"   Description: {info['description']}")
        print(f"   Example: {info['example']}")
        print(f"   Required: {'✅ Yes' if info['required'] else '⚠️ Optional'}")
    
    print("\n" + "="*60)
    print("🔍 VERIFICATION CHECKLIST")
    print("="*60)
    
    print("\nAfter adding secrets, verify:")
    print("□ All 6 secrets are listed in GitHub repository settings")
    print("□ AWS SES sender email is verified in AWS Console")
    print("□ IAM role has SES permissions and OIDC trust policy")
    print("□ Kaggle credentials are valid and active")
    
    print("\n🧪 TEST THE SETUP:")
    print("1. Push a change to trigger the workflow")
    print("2. Check GitHub Actions logs for email sending step")
    print("3. Look for: '✅ Fraud alert email sent successfully!'")
    
    print("\n📧 EXPECTED EMAIL NOTIFICATION:")
    print("Subject: 🚨 FRAUD ALERT: X Fraudulent Transaction(s) Detected")
    print("Or: ✅ Fraud Detection System: No Threats Detected")
    
    print("\n" + "="*60)
    print("🆘 NEED HELP?")
    print("="*60)
    print("• Check GITHUB_SECRETS_SETUP.md for detailed instructions")
    print("• Review GitHub Actions workflow logs for error details")
    print("• Verify AWS SES configuration and email verification")
    print("• Ensure IAM role permissions are correctly configured")
    
    return secrets

def main():
    """Main function to run the secrets checker"""
    print("🔐 GitHub Secrets Configuration Checker")
    print("Fraud Detection System - Email Notifications Setup")
    
    # Get repository information
    repo_path = get_repo_info()
    
    # Generate setup instructions
    secrets = generate_setup_instructions(repo_path)
    
    # Save configuration to file
    config = {
        'repository': repo_path,
        'timestamp': datetime.now().isoformat(),
        'required_secrets': secrets,
        'setup_url': f"https://github.com/{repo_path}/settings/secrets/actions",
        'workflow_url': f"https://github.com/{repo_path}/actions"
    }
    
    with open('github_secrets_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: github_secrets_config.json")
    print(f"\n🎯 Next step: Visit {config['setup_url']} to add secrets")

if __name__ == "__main__":
    main()