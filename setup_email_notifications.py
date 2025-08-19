#!/usr/bin/env python3
"""
Email Notifications Setup Script for Fraud Detection System

This script helps you configure AWS SES email notifications.
Run this script to set up email alerts for fraud detection.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 50)

def run_command(command, description=""):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return result.stdout.strip()
        else:
            print(f"❌ {description} - Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return None

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print_step(1, "Checking AWS Credentials")
    
    result = run_command("aws sts get-caller-identity", "Checking AWS credentials")
    if result:
        identity = json.loads(result)
        print(f"✅ AWS Account ID: {identity.get('Account')}")
        print(f"✅ User ARN: {identity.get('Arn')}")
        return identity.get('Account')
    else:
        print("❌ AWS credentials not configured. Please run 'aws configure' first.")
        return None

def verify_email_address(email, email_type=""):
    """Verify an email address with AWS SES"""
    print(f"\n📧 Verifying {email_type} email: {email}")
    
    # Check if already verified
    result = run_command("aws ses list-verified-email-addresses --region us-east-1", "Checking verified emails")
    if result:
        verified_emails = json.loads(result).get('VerifiedEmailAddresses', [])
        if email in verified_emails:
            print(f"✅ Email {email} is already verified")
            return True
    
    # Verify the email
    cmd = f"aws ses verify-email-identity --email-address {email} --region us-east-1"
    result = run_command(cmd, f"Sending verification email to {email}")
    
    if result is not None:
        print(f"📬 Verification email sent to {email}")
        print(f"⚠️  Please check your inbox (including spam) and click the verification link")
        return True
    return False

def check_ses_permissions():
    """Check SES permissions"""
    print_step(2, "Checking SES Permissions")
    
    result = run_command("aws ses get-send-quota --region us-east-1", "Checking SES quota")
    if result:
        quota = json.loads(result)
        print(f"✅ SES Send Quota: {quota.get('Max24HourSend')} emails/24h")
        print(f"✅ SES Send Rate: {quota.get('MaxSendRate')} emails/second")
        return True
    else:
        print("❌ No SES permissions. Please attach SES policy to your IAM user.")
        return False

def setup_github_secrets_guide(account_id):
    """Provide GitHub secrets setup guide"""
    print_step(3, "GitHub Secrets Configuration")
    
    print("\n📋 Required GitHub Repository Secrets:")
    print("\nGo to: https://github.com/DiponkarSinha/Fraud_detection_sys/settings/secrets/actions")
    print("\nAdd these secrets:")
    
    secrets = [
        ("AWS_ACCESS_KEY_ID", "Your AWS access key ID"),
        ("AWS_SECRET_ACCESS_KEY", "Your AWS secret access key"),
        ("AWS_REGION", "us-east-1"),
        ("AWS_ACCOUNT_ID", account_id or "Your 12-digit AWS account ID"),
        ("FRAUD_ALERT_EMAIL", "your-email@gmail.com (your verified email)"),
        ("SES_SENDER_EMAIL", "fraud-alerts@yourdomain.com (optional verified sender)")
    ]
    
    for name, description in secrets:
        print(f"  • {name:<25} = {description}")
    
    print("\n⚠️  Important: All emails must be verified in AWS SES before use!")

def test_email_sending():
    """Test email sending functionality"""
    print_step(4, "Testing Email Functionality")
    
    sender = input("\nEnter sender email (verified in SES): ").strip()
    recipient = input("Enter recipient email (verified in SES): ").strip()
    
    if not sender or not recipient:
        print("❌ Both sender and recipient emails are required")
        return False
    
    cmd = f'''aws ses send-email \
        --source {sender} \
        --destination ToAddresses={recipient} \
        --message 'Subject={{Data="🚨 Fraud Detection Test Email",Charset=utf8}},Body={{Text={{Data="This is a test email from your fraud detection system. If you receive this, email notifications are working correctly!",Charset=utf8}}}}' \
        --region us-east-1'''
    
    result = run_command(cmd, "Sending test email")
    if result:
        message_data = json.loads(result)
        print(f"✅ Test email sent successfully!")
        print(f"📧 Message ID: {message_data.get('MessageId')}")
        print(f"📬 Check {recipient} for the test email")
        return True
    return False

def main():
    print_header("Fraud Detection Email Notifications Setup")
    
    print("\n🎯 This script will help you configure email notifications for fraud detection.")
    print("\n📋 Prerequisites:")
    print("   • AWS CLI installed and configured")
    print("   • AWS account with SES access")
    print("   • Email addresses that you can verify")
    
    # Step 1: Check AWS credentials
    account_id = check_aws_credentials()
    if not account_id:
        print("\n❌ Setup failed. Please configure AWS credentials first.")
        sys.exit(1)
    
    # Step 2: Check SES permissions
    if not check_ses_permissions():
        print("\n❌ Setup failed. Please configure SES permissions first.")
        print("\n🔧 To fix this, run:")
        print("   aws iam attach-user-policy --user-name YOUR_USERNAME --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess")
        sys.exit(1)
    
    # Step 3: Email verification
    print_step(3, "Email Verification")
    
    print("\n📧 Let's verify your email addresses:")
    
    # Get email addresses from user
    fraud_email = input("\nEnter your email to receive fraud alerts: ").strip()
    sender_email = input("Enter sender email (optional, press Enter to skip): ").strip()
    
    if fraud_email:
        verify_email_address(fraud_email, "recipient")
    
    if sender_email:
        verify_email_address(sender_email, "sender")
    
    # Step 4: GitHub secrets guide
    setup_github_secrets_guide(account_id)
    
    # Step 5: Test email (optional)
    print("\n🧪 Would you like to test email sending now? (y/n): ", end="")
    if input().lower().startswith('y'):
        test_email_sending()
    
    print_header("Setup Complete!")
    print("\n✅ Email notifications setup is complete!")
    print("\n📋 Next steps:")
    print("   1. Check your email inbox for verification emails and click the links")
    print("   2. Add the required secrets to your GitHub repository")
    print("   3. Upload a new CSV file to test the complete pipeline")
    print("\n🎯 Once configured, you'll receive email alerts for fraud detection!")

if __name__ == "__main__":
    main()