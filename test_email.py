#!/usr/bin/env python3
"""
Test script to verify AWS SES email functionality
"""

import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_ses_email():
    """Test AWS SES email sending capability"""
    
    # Email configuration
    sender_email = "u4510634023@gmail.com"  # Replace with verified SES email
    recipient_email = "diponkarsinha.cz@gmail.com"
    aws_region = "us-east-1"
    
    try:
        # Initialize SES client
        print("🔧 Initializing AWS SES client...")
        ses_client = boto3.client('ses', region_name=aws_region)
        
        # Test email content
        subject = "🧪 Test: Fraud Detection System Email"
        body = """This is a test email from the Fraud Detection System.
        
If you receive this email, the AWS SES integration is working correctly.
        
Timestamp: 2025-08-19 18:02:11
Test Status: SUCCESS
        
This is an automated test message."""
        
        print(f"📧 Sending test email from {sender_email} to {recipient_email}...")
        
        # Send email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body, 'Charset': 'UTF-8'}}
            }
        )
        
        print(f"✅ Email sent successfully!")
        print(f"📊 MessageId: {response['MessageId']}")
        print(f"📧 Recipient: {recipient_email}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure AWS credentials.")
        print("   Run: aws configure")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS SES Error [{error_code}]: {error_message}")
        
        if error_code == 'MessageRejected':
            print("   💡 Tip: Verify sender email in AWS SES console")
        elif error_code == 'AccessDenied':
            print("   💡 Tip: Check AWS IAM permissions for SES")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing AWS SES Email Functionality")
    print("=" * 40)
    
    success = test_ses_email()
    
    if success:
        print("\n🎉 Email test completed successfully!")
        print("   The fraud detection system should now send email notifications.")
    else:
        print("\n❌ Email test failed.")
        print("   Please check AWS SES configuration and credentials.")