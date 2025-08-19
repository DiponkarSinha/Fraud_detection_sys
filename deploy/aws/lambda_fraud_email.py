import json
import boto3
from datetime import datetime
import os

def lambda_handler(event, context):
    """
    AWS Lambda function to send fraud detection email alerts
    Triggered by GitHub Actions when fraud is detected
    """
    
    # Initialize SES client
    ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    try:
        # Extract data from event
        fraud_count = event.get('fraud_count', 0)
        timestamp = event.get('timestamp', datetime.utcnow().isoformat())
        repository = event.get('repository', 'Unknown')
        commit_sha = event.get('commit_sha', 'Unknown')
        recipient_email = event.get('email_recipient', os.environ.get('FRAUD_ALERT_EMAIL'))
        
        # Email configuration
        sender_email = os.environ.get('SES_SENDER_EMAIL', 'fraud-alerts@yourdomain.com')
        
        # Create email content based on fraud detection results
        if fraud_count > 0:
            subject = f"🚨 FRAUD ALERT: {fraud_count} Fraudulent Transaction(s) Detected"
            priority = "HIGH"
            alert_type = "FRAUD DETECTED"
            message_color = "#ff4444"
        else:
            subject = "✅ Fraud Detection System: No Threats Detected"
            priority = "NORMAL"
            alert_type = "SYSTEM HEALTHY"
            message_color = "#44ff44"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background-color: {message_color}; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-box {{ background-color: #f8f9fa; border-left: 4px solid {message_color}; padding: 15px; margin: 20px 0; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; color: #666; }}
                .button {{ display: inline-block; background-color: {message_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Fraud Detection System</h1>
                    <h2>{alert_type}</h2>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h3>Alert Summary</h3>
                        <p><strong>Fraud Transactions Detected:</strong> {fraud_count}</p>
                        <p><strong>Priority Level:</strong> {priority}</p>
                        <p><strong>Detection Time:</strong> {timestamp}</p>
                    </div>
                    
                    <div class="details">
                        <h3>Technical Details</h3>
                        <p><strong>Repository:</strong> {repository}</p>
                        <p><strong>Commit SHA:</strong> {commit_sha[:8]}...</p>
                        <p><strong>AWS Region:</strong> {os.environ.get('AWS_REGION', 'us-east-1')}</p>
                    </div>
                    
                    {f'<p style="color: {message_color}; font-weight: bold; font-size: 18px;">⚠️ IMMEDIATE ACTION REQUIRED: Review and investigate the detected fraudulent transactions.</p>' if fraud_count > 0 else '<p style="color: #44ff44; font-weight: bold; font-size: 18px;">✅ All transactions appear legitimate. System is operating normally.</p>'}
                    
                    <a href="https://github.com/{repository}/actions" class="button">View GitHub Actions</a>
                    <a href="https://github.com/{repository}/blob/main/outputs/fraud_report.json" class="button">View Fraud Report</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from the Fraud Detection System.</p>
                    <p>Powered by AWS Lambda + GitHub Actions + Machine Learning</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        FRAUD DETECTION SYSTEM ALERT
        ============================
        
        Alert Type: {alert_type}
        Fraud Count: {fraud_count}
        Priority: {priority}
        Timestamp: {timestamp}
        
        Technical Details:
        - Repository: {repository}
        - Commit: {commit_sha[:8]}...
        - AWS Region: {os.environ.get('AWS_REGION', 'us-east-1')}
        
        {'⚠️ IMMEDIATE ACTION REQUIRED: Review detected fraudulent transactions.' if fraud_count > 0 else '✅ No fraud detected. System operating normally.'}
        
        View details: https://github.com/{repository}/actions
        
        This is an automated message from the Fraud Detection System.
        """
        
        # Send email via SES
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
                        'Data': text_body,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        # Log success
        print(f"Email sent successfully! MessageId: {response['MessageId']}")
        print(f"Fraud count: {fraud_count}, Recipient: {recipient_email}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Fraud alert email sent successfully',
                'messageId': response['MessageId'],
                'fraudCount': fraud_count,
                'recipient': recipient_email,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error sending fraud alert email: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to send fraud alert email',
                'details': str(e)
            })
        }