#!/usr/bin/env python3
"""
Fraud Detection Dashboard Backend
Flask application to serve the fraud analyst dashboard
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           static_folder='.',
           template_folder='.')
CORS(app)

# Configuration
CONFIG = {
    'FRAUD_REPORT_PATH': '../fraud_report.json',
    'DATA_RAW_PATH': '../data/raw',
    'REFRESH_INTERVAL': 30  # seconds
}

class FraudDataManager:
    """Manages fraud detection data and analytics"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.fraud_report_path = self.base_path / 'fraud_report.json'
        self.data_raw_path = self.base_path / 'data' / 'raw'
        self.cache = {
            'last_update': None,
            'fraud_data': [],
            'statistics': {}
        }
    
    def load_fraud_report(self):
        """Load the latest fraud report"""
        try:
            if self.fraud_report_path.exists():
                with open(self.fraud_report_path, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded fraud report: {data.get('fraud_detected', 0)} frauds detected")
                    return data
        except Exception as e:
            logger.error(f"Error loading fraud report: {e}")
        return None
    
    def load_banking_dataset(self):
        """Load banking dataset to get accurate transaction counts"""
        try:
            banking_path = self.data_raw_path / 'banking_transactions_train.csv'
            if banking_path.exists():
                df = pd.read_csv(banking_path)
                total_transactions = len(df)
                fraud_transactions = len(df[df['is_fraud'] == 1])
                legitimate_transactions = len(df[df['is_fraud'] == 0])
                fraud_rate = (fraud_transactions / total_transactions) * 100 if total_transactions > 0 else 0
                
                return {
                    'total_transactions': total_transactions,
                    'fraud_detected': fraud_transactions,
                    'legitimate_transactions': legitimate_transactions,
                    'fraud_rate_percent': round(fraud_rate, 2),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error loading banking dataset: {e}")
        return None
    
    def get_latest_csv_files(self, limit=5):
        """Get the latest CSV files from data/raw directory"""
        try:
            if not self.data_raw_path.exists():
                return []
            
            csv_files = list(self.data_raw_path.glob('*.csv'))
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return csv_files[:limit]
        except Exception as e:
            logger.error(f"Error getting CSV files: {e}")
            return []
    
    def analyze_csv_file(self, csv_path):
        """Analyze a CSV file for fraud patterns"""
        try:
            df = pd.read_csv(csv_path)
            
            # Identify fraud transactions (assuming 'is_fraud' column)
            if 'is_fraud' in df.columns:
                fraud_transactions = df[df['is_fraud'] == 1]
            else:
                # Fallback: use heuristics to identify potential fraud
                fraud_transactions = df[
                    (df.get('amount', 0) > 5000) |
                    (df.get('merchant', '').str.contains('unknown|suspicious', case=False, na=False))
                ]
            
            return self.process_fraud_transactions(fraud_transactions)
        except Exception as e:
            logger.error(f"Error analyzing CSV file {csv_path}: {e}")
            return []
    
    def process_fraud_transactions(self, fraud_df):
        """Process fraud transactions into dashboard format"""
        transactions = []
        
        for idx, row in fraud_df.iterrows():
            # Calculate risk score based on amount and other factors
            amount = float(row.get('amount', 0))
            risk_score = min(95, 50 + (amount / 1000) * 5)
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = 'high'
            elif risk_score >= 60:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            transaction = {
                'id': row.get('transaction_id', f'TXN{idx:03d}'),
                'amount': amount,
                'merchant': row.get('merchant', 'Unknown Merchant'),
                'location': row.get('location', 'Unknown Location'),
                'riskScore': round(risk_score, 1),
                'riskLevel': risk_level,
                'timestamp': row.get('timestamp', datetime.now().isoformat()),
                'cardNumber': self.mask_card_number(row.get('card_number', '1234567890123456')),
                'customerName': row.get('customer_name', f'Customer {idx + 1}'),
                'transactionType': row.get('transaction_type', 'Unknown'),
                'ipAddress': row.get('ip_address', 'Unknown'),
                'deviceFingerprint': row.get('device_fingerprint', 'Unknown Device')
            }
            transactions.append(transaction)
        
        return transactions
    
    def mask_card_number(self, card_number):
        """Mask card number for security"""
        card_str = str(card_number)
        if len(card_str) >= 4:
            return f"**** **** **** {card_str[-4:]}"
        return "**** **** **** ****"
    
    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        # Load banking dataset for accurate statistics
        banking_stats = self.load_banking_dataset()
        
        # Load fraud report
        fraud_report = self.load_fraud_report()
        
        # Get fraud transactions
        fraud_transactions = []
        
        if fraud_report:
            # Use report data to generate sample transactions
            fraud_count = fraud_report.get('fraud_detected', 0)
            for i in range(fraud_count):
                fraud_transactions.append(self.generate_sample_transaction(i))
        else:
            # Analyze latest CSV files
            csv_files = self.get_latest_csv_files()
            for csv_file in csv_files:
                transactions = self.analyze_csv_file(csv_file)
                fraud_transactions.extend(transactions)
        
        # Use banking dataset statistics if available, otherwise calculate from transactions
        if banking_stats:
            total_transactions = banking_stats['total_transactions']
            fraud_detected = banking_stats['fraud_detected']
            fraud_rate = banking_stats['fraud_rate_percent']
            last_updated = banking_stats['timestamp']
        else:
            # Fallback to existing calculation
            total_transactions = fraud_report.get('total_transactions', len(fraud_transactions) * 10) if fraud_report else 100
            fraud_detected = len(fraud_transactions)
            fraud_rate = (fraud_detected / total_transactions * 100) if total_transactions > 0 else 0
            last_updated = fraud_report.get('timestamp', datetime.now().isoformat()) if fraud_report else datetime.now().isoformat()
        
        statistics = {
            'totalTransactions': total_transactions,
            'fraudDetected': fraud_detected,
            'fraudRate': round(fraud_rate, 1),
            'lastUpdated': last_updated,
            'highRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'high']),
            'mediumRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'medium']),
            'lowRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'low'])
        }
        
        return {
            'transactions': fraud_transactions,
            'statistics': statistics,
            'lastUpdate': datetime.now().isoformat(),
            'banking_dataset_info': banking_stats
        }
    
    def generate_sample_transaction(self, index):
        """Generate a sample fraud transaction"""
        import random
        
        merchants = ['Unknown Online Store', 'Suspicious Vendor', 'Fake Electronics', 'Fraudulent Marketplace']
        locations = ['Lagos, Nigeria', 'Moscow, Russia', 'Unknown Location', 'Suspicious Area']
        amounts = [5000, 8500, 12000, 15000, 20000]
        
        amount = amounts[index % len(amounts)] + random.uniform(-1000, 2000)
        risk_score = 70 + random.uniform(0, 25)
        
        return {
            'id': f'TXN{index + 1:03d}',
            'amount': round(amount, 2),
            'merchant': merchants[index % len(merchants)],
            'location': locations[index % len(locations)],
            'riskScore': round(risk_score, 1),
            'riskLevel': 'high' if risk_score >= 80 else 'medium' if risk_score >= 60 else 'low',
            'timestamp': (datetime.now() - timedelta(hours=index)).isoformat(),
            'cardNumber': f"**** **** **** {random.randint(1000, 9999)}",
            'customerName': f'Customer {index + 1}',
            'transactionType': 'Online Purchase',
            'ipAddress': f'192.168.1.{random.randint(100, 255)}',
            'deviceFingerprint': 'Unknown Device'
        }

# Initialize data manager
data_manager = FraudDataManager()

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return send_from_directory('.', 'index.html')

@app.route('/api/fraud-data')
def get_fraud_data():
    """API endpoint to get fraud detection data"""
    try:
        data = data_manager.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error getting fraud data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get fraud statistics"""
    try:
        data = data_manager.get_dashboard_data()
        return jsonify({
            'success': True,
            'statistics': data['statistics']
        })
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transactions')
def get_transactions():
    """API endpoint to get fraud transactions"""
    try:
        data = data_manager.get_dashboard_data()
        return jsonify({
            'success': True,
            'transactions': data['transactions']
        })
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transaction/<transaction_id>')
def get_transaction_details(transaction_id):
    """API endpoint to get specific transaction details"""
    try:
        data = data_manager.get_dashboard_data()
        transaction = next((t for t in data['transactions'] if t['id'] == transaction_id), None)
        
        if transaction:
            return jsonify({
                'success': True,
                'transaction': transaction
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Fraud Detection Dashboard'
    })

@app.route('/api/send-dashboard-link', methods=['POST'])
def send_dashboard_link():
    """Send dashboard link via email"""
    try:
        data = request.get_json()
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({
                'success': False,
                'error': 'Email address is required'
            }), 400
        
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        dashboard_url = f"http://{local_ip}:5000"
        
        # Get current statistics
        dashboard_data = data_manager.get_dashboard_data()
        stats = dashboard_data['statistics']
        
        # Create email content
        subject = "🚨 Fraud Detection Dashboard - Access Link"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fraud Detection Dashboard</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="max-width: 650px; margin: 0 auto; padding: 40px 20px;">
                <!-- Header Section -->
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 30px; border-radius: 20px 20px 0 0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🛡️ Fraud Detection Dashboard</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Real-time Security Monitoring System</p>
                </div>
                
                <!-- Main Content -->
                <div style="background: white; padding: 0; border-radius: 0 0 20px 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden;">
                    
                    <!-- Dashboard Access Section -->
                    <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); padding: 25px; color: white;">
                        <h2 style="margin: 0 0 15px 0; font-size: 20px; display: flex; align-items: center;">🔗 Dashboard Access Links</h2>
                        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 14px;"><strong>🌐 Network URL:</strong></p>
                            <a href="{dashboard_url}" style="color: #ffeaa7; text-decoration: none; font-weight: 600; word-break: break-all;">{dashboard_url}</a>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 14px;"><strong>🏠 Local URL:</strong></p>
                            <a href="http://localhost:5000" style="color: #ffeaa7; text-decoration: none; font-weight: 600;">http://localhost:5000</a>
                        </div>
                    </div>
                    
                    <!-- Statistics Section -->
                    <div style="padding: 25px; background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); color: white;">
                        <h2 style="margin: 0 0 20px 0; font-size: 20px; display: flex; align-items: center;">📊 Live Statistics</h2>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; text-align: center; backdrop-filter: blur(10px);">
                                <div style="font-size: 24px; font-weight: 700; margin-bottom: 5px;">{stats.get('totalTransactions', 'N/A'):,}</div>
                                <div style="font-size: 12px; opacity: 0.9;">📈 Total Transactions</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; text-align: center; backdrop-filter: blur(10px);">
                                <div style="font-size: 24px; font-weight: 700; margin-bottom: 5px; color: #ff7675;">{stats.get('fraudDetected', 'N/A'):,}</div>
                                <div style="font-size: 12px; opacity: 0.9;">🚨 Fraud Detected</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; text-align: center; backdrop-filter: blur(10px);">
                                <div style="font-size: 24px; font-weight: 700; margin-bottom: 5px; color: #fdcb6e;">{stats.get('fraudRate', 'N/A')}%</div>
                                <div style="font-size: 12px; opacity: 0.9;">📊 Fraud Rate</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; text-align: center; backdrop-filter: blur(10px);">
                                <div style="font-size: 11px; font-weight: 600; margin-bottom: 5px;">🕒 Updated</div>
                                <div style="font-size: 10px; opacity: 0.9;">{stats.get('lastUpdated', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Features Section -->
                    <div style="padding: 25px; background: linear-gradient(135deg, #00cec9 0%, #00b894 100%); color: white;">
                        <h2 style="margin: 0 0 20px 0; font-size: 20px;">🔍 Advanced Features</h2>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
                            <div style="display: flex; align-items: center; padding: 8px;">⚡ Real-time Monitoring</div>
                            <div style="display: flex; align-items: center; padding: 8px;">📈 Interactive Analytics</div>
                            <div style="display: flex; align-items: center; padding: 8px;">🔍 Investigation Tools</div>
                            <div style="display: flex; align-items: center; padding: 8px;">🎯 Risk Assessment</div>
                            <div style="display: flex; align-items: center; padding: 8px;">📋 Export Reports</div>
                            <div style="display: flex; align-items: center; padding: 8px;">📱 Mobile Responsive</div>
                        </div>
                    </div>
                    
                    <!-- CTA Section -->
                    <div style="padding: 30px; text-align: center; background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);">
                        <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #ff7675 0%, #e17055 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px;">🚀 Launch Dashboard</a>
                        <p style="margin: 15px 0 0 0; color: rgba(255,255,255,0.8); font-size: 14px;">Click to access your fraud detection system</p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="padding: 20px; background: #2d3436; color: #b2bec3; text-align: center; font-size: 12px;">
                        <p style="margin: 0 0 5px 0;">🛡️ Fraud Detection System - Powered by AI</p>
                        <p style="margin: 0; opacity: 0.7;">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        🚨 FRAUD DETECTION DASHBOARD - ACCESS LINK
        
        Dashboard URL: {dashboard_url}
        Local Access: http://localhost:5000
        
        📊 CURRENT STATISTICS:
        - Total Transactions: {stats.get('totalTransactions', 'N/A'):,}
        - Fraud Detected: {stats.get('fraudDetected', 'N/A'):,}
        - Fraud Rate: {stats.get('fraudRate', 'N/A')}%
        - Last Updated: {stats.get('lastUpdated', 'N/A')}
        
        🔍 DASHBOARD FEATURES:
        - Real-time fraud transaction monitoring
        - Interactive charts and analytics
        - Transaction investigation tools
        - Risk assessment visualization
        - Export capabilities for reporting
        - Mobile-responsive design
        
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = 'fraud-detection@system.local'
        msg['To'] = recipient_email
        
        # Attach both text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # For demo purposes, we'll return the email content instead of actually sending
        # In a real implementation, you would configure SMTP settings
        
        return jsonify({
            'success': True,
            'message': f'Dashboard link prepared for {recipient_email}',
            'dashboard_url': dashboard_url,
            'local_url': 'http://localhost:5000',
            'email_content': {
                'subject': subject,
                'html_body': html_body,
                'text_body': text_body
            },
            'statistics': stats,
            'note': 'Email content generated successfully. In production, configure SMTP to actually send emails.'
        })
        
    except Exception as e:
        logger.error(f"Error sending dashboard link: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Static file serving
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    logger.info("Starting Fraud Detection Dashboard...")
    logger.info(f"Dashboard will be available at: http://localhost:5000")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )