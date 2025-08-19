#!/usr/bin/env python3
"""
Test script for AWS Lambda email notification
Mimics the GitHub Actions workflow approach
"""

import boto3
import json
import os
from datetime import datetime

def test_lambda_email():
    """Test the Lambda function with proper payload encoding"""
    print("🧪 Testing AWS Lambda email notification...")
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create payload exactly like GitHub Actions does
    payload = {
        "fraud_count": 2,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "repository": "DiponkarSinha/Fraud_detection_sys",
        "commit_sha": "test-manual-invocation-123456",
        "email_recipient": os.environ.get('FRAUD_ALERT_EMAIL', 'your-email@gmail.com')
    }
    
    print(f"📧 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Invoke Lambda function with proper encoding (like GitHub Actions)
        response = lambda_client.invoke(
            FunctionName="fraud-detection-email-alert",
            InvocationType="RequestResponse",  # Synchronous for testing
            Payload=json.dumps(payload).encode()  # This is the key fix!
        )
        
        print(f"✅ Lambda invocation successful!")
        print(f"📊 Status Code: {response.get('StatusCode')}")
        
        # Read response payload
        if 'Payload' in response:
            response_payload = json.loads(response['Payload'].read())
            print(f"📋 Response: {json.dumps(response_payload, indent=2)}")
            
            if response_payload.get('statusCode') == 200:
                print("🎉 Email sent successfully!")
                return True
            else:
                print(f"❌ Lambda function returned error: {response_payload}")
                return False
        
    except Exception as e:
        print(f"❌ Error invoking Lambda function: {str(e)}")
        return False

def check_aws_setup():
    """Check AWS configuration and Lambda function existence"""
    print("🔍 Checking AWS setup...")
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS Identity: {identity.get('Arn')}")
        
        # Check Lambda function exists
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        function_info = lambda_client.get_function(FunctionName="fraud-detection-email-alert")
        print(f"✅ Lambda function found: {function_info['Configuration']['FunctionName']}")
        print(f"📝 Runtime: {function_info['Configuration']['Runtime']}")
        print(f"🕒 Last Modified: {function_info['Configuration']['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS setup issue: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Lambda email notification test...\n")
    
    # Check AWS setup first
    if check_aws_setup():
        print("\n" + "="*50)
        # Test Lambda function
        success = test_lambda_email()
        
        if success:
            print("\n🎯 Test completed successfully! Check your email inbox.")
        else:
            print("\n💥 Test failed. Check the error messages above.")
    else:
        print("\n💥 AWS setup verification failed. Please check your configuration.")