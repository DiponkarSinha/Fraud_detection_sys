#!/usr/bin/env python3
"""
Test SES Email Functionality
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_ses_email():
    # Initialize SES client
    ses_client = boto3.client('ses', region_name='us-east-1')
    
    # Email configuration
    sender_email = "u4510634023@gmail.com"
    recipient_email = "diponkarsinha.cz@gmail.com"
    subject = "🚨 Fraud Detection Test Email"
    body_text = "This is a test email from your fraud detection system. If you receive this, email notifications are working correctly!"
    
    try:
        # Send email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print("✅ Email sent successfully!")
        print(f"📧 Message ID: {response['MessageId']}")
        print(f"📤 From: {sender_email}")
        print(f"📥 To: {recipient_email}")
        print(f"📋 Subject: {subject}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print(f"❌ Failed to send email")
        print(f"🔴 Error Code: {error_code}")
        print(f"🔴 Error Message: {error_message}")
        
        if error_code == 'MessageRejected':
            print("\n💡 Possible solutions:")
            print("   • Verify both sender and recipient emails in AWS SES")
            print("   • Check if you're in SES sandbox mode")
            print("   • Ensure proper IAM permissions for SES")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing SES Email Functionality...")
    print("=" * 50)
    
    success = test_ses_email()
    
    if success:
        print("\n🎉 SES email test completed successfully!")
        print("📬 Check your inbox for the test email.")
    else:
        print("\n🚨 SES email test failed.")
        print("📋 Please check the error messages above and fix the issues.")