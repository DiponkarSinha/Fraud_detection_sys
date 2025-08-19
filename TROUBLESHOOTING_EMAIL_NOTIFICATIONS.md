# 🚨 Email Notifications Troubleshooting Guide

## Problem: Not Receiving Fraud Detection Emails

If you're not receiving fraud detection email notifications despite GitHub Actions showing successful fraud detection, follow this comprehensive troubleshooting guide.

## 🔍 Root Cause Analysis

The main issues preventing email notifications are:

1. **AWS SES Permissions**: IAM user lacks necessary SES permissions
2. **Email Verification**: Sender/recipient emails not verified in AWS SES
3. **GitHub Secrets**: Missing or incorrect AWS credentials in GitHub repository
4. **Lambda Function**: AWS Lambda function not deployed or misconfigured

## 🛠️ Step-by-Step Solutions

### Step 1: Fix AWS IAM Permissions

#### 1.1 Apply IAM Policy
```bash
# Navigate to your project directory
cd /path/to/Fraud_detection_sys

# Apply the IAM policy (replace YOUR_USERNAME with your AWS IAM username)
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# Or create a custom policy with minimal permissions
aws iam create-policy \
  --policy-name FraudDetectionSESPolicy \
  --policy-document file://deploy/aws/iam_policy_fraud_detection.json

# Attach the custom policy
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/FraudDetectionSESPolicy
```

#### 1.2 Verify IAM User Permissions
```bash
# Check attached policies
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Test SES access
aws ses get-send-quota --region us-east-1
```

### Step 2: Configure AWS SES Email Verification

#### 2.1 Verify Sender Email
```bash
# Verify the sender email address
aws ses verify-email-identity \
  --email-address fraud-alerts@yourdomain.com \
  --region us-east-1
```

#### 2.2 Verify Recipient Email (Your Gmail)
```bash
# Verify your Gmail address
aws ses verify-email-identity \
  --email-address your-email@gmail.com \
  --region us-east-1
```

#### 2.3 Check Email Verification Status
```bash
# List verified email addresses
aws ses list-verified-email-addresses --region us-east-1
```

**Important**: Check your email inbox (including spam folder) for verification emails from AWS and click the verification links.

### Step 3: Configure GitHub Repository Secrets

Go to your GitHub repository: `https://github.com/DiponkarSinha/Fraud_detection_sys/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | IAM user secret key |
| `AWS_REGION` | `us-east-1` | AWS region for SES |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID | AWS account identifier |
| `FRAUD_ALERT_EMAIL` | `your-email@gmail.com` | Your verified email address |
| `SES_SENDER_EMAIL` | `fraud-alerts@yourdomain.com` | Verified sender email (optional) |

### Step 4: Deploy AWS Lambda Function

#### 4.1 Run Setup Script
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_ACCOUNT_ID="your_account_id"
export FRAUD_ALERT_EMAIL="your-email@gmail.com"

# Run the setup script
python3 deploy/setup_integrations.py
```

#### 4.2 Manual Lambda Deployment (if setup script fails)
```bash
# Create Lambda execution role
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document '{
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
  }'

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach SES policy to Lambda role
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# Create deployment package
cd deploy/aws
zip fraud-email-lambda.zip lambda_fraud_email.py

# Deploy Lambda function
aws lambda create-function \
  --function-name fraud-detection-email-alert \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_fraud_email.lambda_handler \
  --zip-file fileb://fraud-email-lambda.zip \
  --description "Send fraud detection email alerts via SES" \
  --timeout 30 \
  --environment Variables='{"SES_SENDER_EMAIL":"fraud-alerts@yourdomain.com","FRAUD_ALERT_EMAIL":"your-email@gmail.com"}'
```

### Step 5: Test the Complete Pipeline

#### 5.1 Test Email Sending Manually
```bash
# Test AWS SES directly
aws ses send-email \
  --source fraud-alerts@yourdomain.com \
  --destination ToAddresses=your-email@gmail.com \
  --message Subject={Data="Test Email",Charset=utf8},Body={Text={Data="This is a test email from AWS SES",Charset=utf8}} \
  --region us-east-1
```

#### 5.2 Test Lambda Function
```bash
# Test Lambda function invocation
aws lambda invoke \
  --function-name fraud-detection-email-alert \
  --payload '{
    "fraud_count": 1,
    "timestamp": "2025-01-19T10:00:00Z",
    "repository": "DiponkarSinha/Fraud_detection_sys",
    "commit_sha": "test123",
    "email_recipient": "your-email@gmail.com"
  }' \
  response.json

# Check response
cat response.json
```

#### 5.3 Test End-to-End Pipeline
```bash
# Create a new test CSV to trigger the pipeline
cp data/raw/test_transactions.csv data/raw/final_email_test.csv

# Monitor GitHub Actions
echo "Check GitHub Actions at: https://github.com/DiponkarSinha/Fraud_detection_sys/actions"
```

## 🔧 Verification Commands

### Check AWS Configuration
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check SES quota and statistics
aws ses get-send-quota --region us-east-1
aws ses get-send-statistics --region us-east-1

# List verified emails
aws ses list-verified-email-addresses --region us-east-1

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `fraud`)]'
```

### Check GitHub Actions Logs
1. Go to: `https://github.com/DiponkarSinha/Fraud_detection_sys/actions`
2. Click on the latest workflow run
3. Check the "Trigger AWS Lambda for Email Notification" step
4. Look for any error messages

## 🚨 Common Issues and Solutions

### Issue 1: "AccessDenied" Error
**Solution**: Apply the IAM policy from Step 1

### Issue 2: "Email address not verified"
**Solution**: Complete email verification in Step 2

### Issue 3: "Lambda function not found"
**Solution**: Deploy Lambda function using Step 4

### Issue 4: "GitHub secrets not found"
**Solution**: Add all required secrets in Step 3

### Issue 5: "SES sending limit exceeded"
**Solution**: Request production access in AWS SES console

## 📧 Expected Email Format

Once configured correctly, you should receive emails with:
- **Subject**: 🚨 FRAUD ALERT: X Fraudulent Transaction(s) Detected
- **Content**: HTML-formatted email with fraud details
- **Links**: Direct links to GitHub Actions and fraud reports

## 🆘 Still Not Working?

If you're still not receiving emails after following all steps:

1. **Check spam folder** in your Gmail
2. **Verify AWS SES is in production mode** (not sandbox)
3. **Check CloudWatch logs** for Lambda function errors
4. **Ensure GitHub secrets are correctly set** (no extra spaces)
5. **Verify your AWS account has SES enabled** in us-east-1 region

## 📞 Support

For additional support:
- Check AWS SES console: https://console.aws.amazon.com/ses/
- Review CloudWatch logs: https://console.aws.amazon.com/cloudwatch/
- Monitor GitHub Actions: https://github.com/DiponkarSinha/Fraud_detection_sys/actions

---

**Note**: This troubleshooting guide addresses the specific issue where GitHub Actions shows successful fraud detection but email notifications are not being received.