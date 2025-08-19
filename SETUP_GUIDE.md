# Fraud Detection System - Complete Setup Guide

## 🚀 System Status

✅ **Local fraud detection**: Working  
✅ **File monitoring**: Working  
✅ **Auto-commit to GitHub**: Working  
✅ **AWS SES email (local)**: Working  
❌ **GitHub Actions email notifications**: Requires secrets configuration  

## 📋 Required GitHub Secrets

To enable email notifications via GitHub Actions, add these secrets in your repository:

**GitHub Repository Settings > Secrets and variables > Actions**

### AWS Configuration
```
AWS_DEFAULT_REGION=us-east-1
AWS_ROLE_TO_ASSUME=arn:aws:iam::YOUR_ACCOUNT:role/GitHubActionsRole
```

### Email Configuration
```
FRAUD_ALERT_EMAIL=your-email@example.com
SES_SENDER_EMAIL=verified-sender@example.com
```

### Kaggle Integration (Optional)
```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

## 🔧 Local Setup

### 1. GitHub Token Configuration

**To configure your GitHub token, add to your shell profile:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export GITHUB_TOKEN='your_github_personal_access_token_here'
```

### 2. Start File Monitor
```bash
cd /path/to/Fraud_detection_sys
export GITHUB_TOKEN='your_github_personal_access_token_here'
python3 tools/file_monitor.py
```

## 🧪 Testing the System

### Test Local Email (Working)
```bash
python3 test_email.py
```

### Test End-to-End Fraud Detection
1. Create a CSV file in `data/raw/` with this format:
```csv
amount,time_hour,day_of_week,is_weekend,previous_failed_attempts,account_age_days,avg_transaction_amount,transaction_frequency,is_fraud
5000.0,2,1,0,0,30,1200.0,5,1
50.0,14,3,0,0,365,800.0,10,0
```

2. The system will automatically:
   - Detect the new CSV file
   - Run fraud detection
   - Generate fraud report
   - Commit to GitHub
   - Trigger GitHub Actions (if secrets are configured)

## 📊 Recent Test Results

**Latest Test**: `github_token_test.csv`
- ✅ File detected and processed
- ✅ Found 2 fraudulent transactions out of 4
- ✅ Auto-committed to GitHub
- ✅ GitHub Actions triggered
- ❌ Email notification failed (missing secrets)

## 🔍 Troubleshooting

### GitHub Actions Failing
1. Check if all required secrets are added to GitHub repository
2. Verify AWS IAM role has SES permissions
3. Ensure sender email is verified in AWS SES

### File Monitor Not Working
1. Ensure GITHUB_TOKEN environment variable is set
2. Check if the monitor is running: `ps aux | grep file_monitor`
3. Restart with: `python3 tools/file_monitor.py`

### Email Not Sending
1. Test local email: `python3 test_email.py`
2. Check AWS credentials: `aws sts get-caller-identity`
3. Verify SES sender email is verified

## 📈 System Architecture

```
CSV File → File Monitor → Fraud Detection → GitHub Commit → GitHub Actions → Email Alert
    ↓           ↓              ↓              ↓              ↓            ↓
  Created    Detected      ML Analysis    Auto-commit    Workflow    SES Email
```

## 🎯 Next Steps

1. **Add GitHub Secrets**: Configure all required secrets in repository settings
2. **Test Email Notifications**: Create a new CSV file to trigger the complete pipeline
3. **Monitor System**: Keep file monitor running for continuous fraud detection

---

**System Status**: Fraud detection is fully operational locally. Email notifications require GitHub secrets configuration.