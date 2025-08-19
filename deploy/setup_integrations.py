#!/usr/bin/env python3
"""
Setup script for fraud detection integrations
Configures AWS Lambda, SES, and Kaggle dataset
"""

import boto3
import json
import os
import zipfile
from pathlib import Path
import subprocess
import sys

def setup_aws_lambda():
    """Deploy AWS Lambda function for email notifications"""
    print("🚀 Setting up AWS Lambda function...")
    
    # Create Lambda deployment package
    lambda_dir = Path('deploy/aws')
    zip_path = lambda_dir / 'fraud-email-lambda.zip'
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(lambda_dir / 'lambda_fraud_email.py', 'lambda_function.py')
    
    # Deploy to AWS
    lambda_client = boto3.client('lambda')
    
    try:
        # Create or update Lambda function
        with open(zip_path, 'rb') as zip_file:
            response = lambda_client.create_function(
                FunctionName='fraud-detection-email-alert',
                Runtime='python3.9',
                Role=f"arn:aws:iam::{os.environ['AWS_ACCOUNT_ID']}:role/lambda-execution-role",
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_file.read()},
                Description='Send fraud detection email alerts via SES',
                Timeout=30,
                Environment={
                    'Variables': {
                        'SES_SENDER_EMAIL': os.environ.get('SES_SENDER_EMAIL', 'fraud-alerts@yourdomain.com'),
                        'FRAUD_ALERT_EMAIL': os.environ.get('FRAUD_ALERT_EMAIL', 'your-email@gmail.com')
                    }
                }
            )
        print(f"✅ Lambda function created: {response['FunctionArn']}")
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        with open(zip_path, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName='fraud-detection-email-alert',
                ZipFile=zip_file.read()
            )
        print("✅ Lambda function updated successfully")
    
    # Clean up
    zip_path.unlink()

def setup_ses_email():
    """Configure AWS SES for email sending"""
    print("📧 Setting up AWS SES...")
    
    ses_client = boto3.client('ses')
    
    # Verify email addresses
    sender_email = os.environ.get('SES_SENDER_EMAIL', 'fraud-alerts@yourdomain.com')
    recipient_email = os.environ.get('FRAUD_ALERT_EMAIL', 'your-email@gmail.com')
    
    try:
        # Verify sender email
        ses_client.verify_email_identity(EmailAddress=sender_email)
        print(f"✅ Sender email verification initiated: {sender_email}")
        
        # Verify recipient email
        ses_client.verify_email_identity(EmailAddress=recipient_email)
        print(f"✅ Recipient email verification initiated: {recipient_email}")
        
        print("📬 Check your email and click verification links!")
        
    except Exception as e:
        print(f"⚠️ SES setup warning: {e}")

def setup_kaggle_dataset():
    """Initialize Kaggle dataset"""
    print("📊 Setting up Kaggle dataset...")
    
    try:
        # Install kaggle if not present
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle'], check=True)
        
        # Create kaggle config directory
        kaggle_dir = Path.home() / '.kaggle'
        kaggle_dir.mkdir(exist_ok=True)
        
        # Create kaggle.json if credentials are provided
        if 'KAGGLE_USERNAME' in os.environ and 'KAGGLE_KEY' in os.environ:
            kaggle_config = {
                'username': os.environ['KAGGLE_USERNAME'],
                'key': os.environ['KAGGLE_KEY']
            }
            
            with open(kaggle_dir / 'kaggle.json', 'w') as f:
                json.dump(kaggle_config, f)
            
            # Set proper permissions
            os.chmod(kaggle_dir / 'kaggle.json', 0o600)
            
            print("✅ Kaggle credentials configured")
            
            # Copy dataset metadata
            metadata_src = Path('deploy/kaggle/dataset-metadata.json')
            metadata_dst = Path('data/dataset-metadata.json')
            
            if metadata_src.exists():
                import shutil
                shutil.copy2(metadata_src, metadata_dst)
                print("✅ Kaggle dataset metadata configured")
            
        else:
            print("⚠️ Kaggle credentials not found in environment variables")
            print("   Set KAGGLE_USERNAME and KAGGLE_KEY to enable Kaggle integration")
            
    except Exception as e:
        print(f"❌ Kaggle setup failed: {e}")

def create_github_secrets_template():
    """Create template for GitHub secrets"""
    print("🔐 Creating GitHub secrets template...")
    
    secrets_template = {
        "Required GitHub Secrets": {
            "AWS_ACCESS_KEY_ID": "Your AWS access key ID",
            "AWS_SECRET_ACCESS_KEY": "Your AWS secret access key",
            "AWS_REGION": "us-east-1",
            "AWS_ACCOUNT_ID": os.environ.get('AWS_ACCOUNT_ID', 'YOUR_AWS_ACCOUNT_ID'),
            "KAGGLE_USERNAME": "Your Kaggle username",
            "KAGGLE_KEY": "Your Kaggle API key",
            "FRAUD_ALERT_EMAIL": "your-email@gmail.com",
            "SES_SENDER_EMAIL": "fraud-alerts@yourdomain.com"
        },
        "Setup Instructions": [
            "1. Go to your GitHub repository settings",
            "2. Navigate to Secrets and Variables > Actions",
            "3. Add each secret listed above",
            "4. Ensure AWS IAM user has Lambda, SES, and CloudWatch permissions",
            "5. Verify email addresses in AWS SES console",
            "6. Create Kaggle API token from kaggle.com/account"
        ]
    }
    
    with open('deploy/github-secrets-template.json', 'w') as f:
        json.dump(secrets_template, f, indent=2)
    
    print("✅ GitHub secrets template created: deploy/github-secrets-template.json")

def test_integrations():
    """Test all integrations"""
    print("🧪 Testing integrations...")
    
    # Test AWS connectivity
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS connection successful: {identity['Account']}")
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
    
    # Test SES
    try:
        ses = boto3.client('ses')
        quota = ses.get_send_quota()
        print(f"✅ SES connection successful: {quota['Max24HourSend']} emails/day limit")
    except Exception as e:
        print(f"❌ SES connection failed: {e}")
    
    # Test Lambda
    try:
        lambda_client = boto3.client('lambda')
        functions = lambda_client.list_functions()
        fraud_functions = [f for f in functions['Functions'] if 'fraud' in f['FunctionName'].lower()]
        print(f"✅ Lambda connection successful: {len(fraud_functions)} fraud-related functions found")
    except Exception as e:
        print(f"❌ Lambda connection failed: {e}")

def main():
    """Main setup function"""
    print("🔧 Starting fraud detection integrations setup...")
    print("=" * 50)
    
    # Check AWS credentials
    if not all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']):
        print("❌ AWS credentials not found in environment variables")
        print("   Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return
    
    try:
        # Setup components
        setup_aws_lambda()
        setup_ses_email()
        setup_kaggle_dataset()
        create_github_secrets_template()
        
        print("\n" + "=" * 50)
        print("🎯 Integration setup completed!")
        print("\n📋 Next steps:")
        print("1. Check your email for SES verification links")
        print("2. Add GitHub secrets using the template in deploy/github-secrets-template.json")
        print("3. Test the pipeline by adding a new CSV file to data/raw/")
        print("4. Monitor GitHub Actions for automated execution")
        
        # Run tests
        print("\n🧪 Running integration tests...")
        test_integrations()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())