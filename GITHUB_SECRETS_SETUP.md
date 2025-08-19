# GitHub Secrets Manual Setup Guide

This guide will help you manually configure the required GitHub repository secrets for email notifications in the fraud detection system.

## Required Secrets

You need to configure the following secrets in your GitHub repository:

### 1. AWS Configuration
- `AWS_DEFAULT_REGION` - AWS region (e.g., `us-east-1`)
- `AWS_ROLE_TO_ASSUME` - AWS IAM role ARN for OIDC authentication

### 2. Email Configuration
- `FRAUD_ALERT_EMAIL` - Email address to receive fraud alerts
- `SES_SENDER_EMAIL` - Verified SES sender email address

### 3. Kaggle Configuration
- `KAGGLE_USERNAME` - Your Kaggle username
- `KAGGLE_KEY` - Your Kaggle API key

## Step-by-Step Setup Instructions

### Step 1: Access GitHub Repository Settings

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Click on **Settings** tab (top navigation)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Repository Secrets

For each secret, click **New repository secret** and add:

#### AWS_DEFAULT_REGION
- **Name**: `AWS_DEFAULT_REGION`
- **Secret**: `us-east-1` (or your preferred AWS region)

#### AWS_ROLE_TO_ASSUME
- **Name**: `AWS_ROLE_TO_ASSUME`
- **Secret**: `arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ROLE_NAME`
- **Note**: This should be an IAM role configured for GitHub OIDC with SES permissions

#### FRAUD_ALERT_EMAIL
- **Name**: `FRAUD_ALERT_EMAIL`
- **Secret**: `your-email@example.com` (email to receive alerts)

#### SES_SENDER_EMAIL
- **Name**: `SES_SENDER_EMAIL`
- **Secret**: `verified-sender@example.com` (must be verified in AWS SES)

#### KAGGLE_USERNAME
- **Name**: `KAGGLE_USERNAME`
- **Secret**: Your Kaggle username

#### KAGGLE_KEY
- **Name**: `KAGGLE_KEY`
- **Secret**: Your Kaggle API key (from Kaggle Account settings)

## AWS Setup Requirements

### 1. AWS SES Configuration

1. **Verify Sender Email**:
   - Go to AWS SES Console
   - Navigate to "Verified identities"
   - Add and verify your sender email address

2. **Move out of Sandbox** (if needed):
   - Request production access if you want to send to unverified emails
   - Or verify recipient emails in SES

### 2. AWS IAM Role for GitHub OIDC

1. **Create IAM Role**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:YOUR_USERNAME/YOUR_REPO:*"
           }
         }
       }
     ]
   }
   ```

2. **Attach SES Policy**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ses:SendEmail",
           "ses:SendRawEmail"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

## Verification Steps

### 1. Check Secrets Configuration

After adding all secrets, you should see them listed in your repository's Actions secrets:

- ✅ AWS_DEFAULT_REGION
- ✅ AWS_ROLE_TO_ASSUME
- ✅ FRAUD_ALERT_EMAIL
- ✅ SES_SENDER_EMAIL
- ✅ KAGGLE_USERNAME
- ✅ KAGGLE_KEY

### 2. Test the Workflow

1. **Trigger a workflow run**:
   - Push a change to main branch
   - Or manually trigger from Actions tab

2. **Check workflow logs**:
   - Go to Actions tab
   - Click on the latest workflow run
   - Check "Send Fraud Alert Email via SES" step

### 3. Expected Success Output

```
✅ Fraud alert email sent successfully!
📧 MessageId: 0000014a-f896-4c07-b62c-12345678901a-000000
📊 Fraud count: 2, Recipient: your-email@example.com
```

## Troubleshooting

### Common Issues

1. **"Email address not verified"**:
   - Verify sender email in AWS SES Console
   - Ensure SES_SENDER_EMAIL matches verified address

2. **"Access Denied" errors**:
   - Check IAM role permissions
   - Verify OIDC provider configuration
   - Ensure role ARN is correct

3. **"Secrets not found"**:
   - Double-check secret names (case-sensitive)
   - Ensure secrets are added to repository (not organization)

4. **Kaggle errors**:
   - Verify Kaggle credentials
   - Check dataset permissions

### Debug Commands

Add these to your workflow for debugging:

```yaml
- name: Debug Environment
  run: |
    echo "AWS Region: $AWS_REGION"
    echo "Role ARN: $ROLE_ARN"
    echo "Fraud Alert Email: $FRAUD_ALERT_EMAIL"
    echo "SES Sender: $SES_SENDER_EMAIL"
```

## Security Best Practices

1. **Use least privilege**: Only grant necessary SES permissions
2. **Rotate secrets**: Regularly update API keys and credentials
3. **Monitor usage**: Check AWS CloudTrail for SES API calls
4. **Verify emails**: Only use verified sender addresses

## Next Steps

After completing this setup:

1. ✅ All GitHub secrets configured
2. ✅ AWS SES sender email verified
3. ✅ IAM role with proper permissions
4. ✅ Test workflow run successful
5. ✅ Email notifications working

Your fraud detection system will now send automated email alerts when fraudulent transactions are detected!

---

**Need Help?** Check the workflow logs in GitHub Actions for detailed error messages and troubleshooting information.