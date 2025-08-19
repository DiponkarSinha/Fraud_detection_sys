#!/usr/bin/env python3
"""
GitHub Secrets Setup Helper
This script helps you set up the required GitHub secrets for the fraud detection pipeline.
"""

import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    print("🔐 GitHub Secrets Setup Helper")
    print("=" * 50)
    print("\nTo set up GitHub secrets for your fraud detection pipeline,")
    print("go to your GitHub repository settings and add these secrets:")
    print("\n📍 Repository URL: https://github.com/DiponkarSinha/Fraud_detection_sys/settings/secrets/actions")
    
    secrets = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": os.getenv("AWS_REGION"),
        "AWS_ACCOUNT_ID": os.getenv("AWS_ACCOUNT_ID"),
        "KAGGLE_USERNAME": os.getenv("KAGGLE_USERNAME"),
        "KAGGLE_KEY": os.getenv("KAGGLE_KEY"),
        "FRAUD_ALERT_EMAIL": os.getenv("RECIPIENT_EMAIL")
    }
    
    print("\n🔑 Required GitHub Secrets:")
    print("-" * 30)
    
    for secret_name, secret_value in secrets.items():
        if secret_value:
            # Mask sensitive values
            if "KEY" in secret_name or "PASSWORD" in secret_name:
                masked_value = secret_value[:4] + "*" * (len(secret_value) - 8) + secret_value[-4:] if len(secret_value) > 8 else "*" * len(secret_value)
                print(f"✅ {secret_name}: {masked_value}")
            else:
                print(f"✅ {secret_name}: {secret_value}")
        else:
            print(f"❌ {secret_name}: NOT FOUND")
    
    print("\n📋 Manual Setup Instructions:")
    print("1. Go to your GitHub repository")
    print("2. Click Settings > Secrets and variables > Actions")
    print("3. Click 'New repository secret'")
    print("4. Add each secret with the exact name and value shown above")
    
    print("\n🚀 After setting up secrets, you can:")
    print("• Push changes to trigger the workflow automatically")
    print("• Go to Actions tab to manually run the workflow")
    print("• Check workflow runs at: https://github.com/DiponkarSinha/Fraud_detection_sys/actions")
    
    print("\n🔍 Current Workflow Status:")
    print("Visit: https://github.com/DiponkarSinha/Fraud_detection_sys/actions/workflows/fraud-detection.yml")

if __name__ == "__main__":
    main()