#!/usr/bin/env python3
"""
Manual Lambda deployment script
Deploys the fraud detection email Lambda function using AWS CLI
"""

import subprocess
import json
import os
import zipfile
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        return None
    
    return result.stdout.strip()

def get_aws_account_id():
    """Get AWS account ID"""
    result = run_command("aws sts get-caller-identity --query Account --output text")
    return result

def create_lambda_execution_role():
    """Create IAM role for Lambda execution"""
    print("🔐 Creating Lambda execution role...")
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Create role
    cmd = f"aws iam create-role --role-name lambda-fraud-email-role --assume-role-policy-document '{json.dumps(trust_policy)}'"
    result = run_command(cmd, check=False)
    
    if result is None:
        print("⚠️ Role might already exist, continuing...")
    
    # Attach basic Lambda execution policy
    run_command("aws iam attach-role-policy --role-name lambda-fraud-email-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", check=False)
    
    # Attach SES policy
    run_command("aws iam attach-role-policy --role-name lambda-fraud-email-role --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess", check=False)
    
    print("✅ Lambda execution role configured")

def create_lambda_package():
    """Create Lambda deployment package"""
    print("📦 Creating Lambda deployment package...")
    
    lambda_dir = Path('deploy/aws')
    zip_path = Path('fraud-email-lambda.zip')
    
    # Remove existing zip if it exists
    if zip_path.exists():
        zip_path.unlink()
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(lambda_dir / 'lambda_fraud_email.py', 'lambda_function.py')
    
    print(f"✅ Lambda package created: {zip_path}")
    return zip_path

def deploy_lambda_function(account_id, zip_path):
    """Deploy Lambda function"""
    print("🚀 Deploying Lambda function...")
    
    role_arn = f"arn:aws:iam::{account_id}:role/lambda-fraud-email-role"
    
    # Try to create the function
    cmd = f"""aws lambda create-function \
        --function-name fraud-detection-email-alert \
        --runtime python3.9 \
        --role {role_arn} \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://{zip_path} \
        --description "Send fraud detection email alerts via SES" \
        --timeout 30 \
        --region us-east-1"""
    
    result = run_command(cmd, check=False)
    
    if result is None:
        print("⚠️ Function might already exist, trying to update...")
        # Update existing function
        update_cmd = f"aws lambda update-function-code --function-name fraud-detection-email-alert --zip-file fileb://{zip_path} --region us-east-1"
        result = run_command(update_cmd)
        
        if result:
            print("✅ Lambda function updated successfully")
        else:
            print("❌ Failed to update Lambda function")
            return False
    else:
        print("✅ Lambda function created successfully")
    
    return True

def test_lambda_deployment():
    """Test if Lambda function is accessible"""
    print("🧪 Testing Lambda function deployment...")
    
    cmd = "aws lambda get-function --function-name fraud-detection-email-alert --region us-east-1"
    result = run_command(cmd, check=False)
    
    if result:
        print("✅ Lambda function is accessible")
        return True
    else:
        print("❌ Lambda function is not accessible")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting manual Lambda deployment...")
    print("="*50)
    
    try:
        # Get AWS account ID
        account_id = get_aws_account_id()
        if not account_id:
            print("❌ Failed to get AWS account ID")
            return False
        
        print(f"📋 AWS Account ID: {account_id}")
        
        # Create IAM role
        create_lambda_execution_role()
        
        # Wait a bit for IAM role to propagate
        print("⏳ Waiting for IAM role to propagate...")
        import time
        time.sleep(10)
        
        # Create Lambda package
        zip_path = create_lambda_package()
        
        # Deploy Lambda function
        success = deploy_lambda_function(account_id, zip_path)
        
        if success:
            # Test deployment
            if test_lambda_deployment():
                print("\n🎉 Lambda function deployed successfully!")
                print("📧 You can now test email notifications")
                
                # Clean up
                zip_path.unlink()
                return True
            else:
                print("\n❌ Lambda deployment verification failed")
                return False
        else:
            print("\n❌ Lambda deployment failed")
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Manual Lambda deployment completed successfully!")
    else:
        print("\n💥 Manual Lambda deployment failed!")