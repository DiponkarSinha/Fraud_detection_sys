#!/usr/bin/env python3
"""
Fraud Detection Dashboard Backend
Flask application to serve the fraud analyst dashboard
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from pathlib import Path

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
        
        # Calculate statistics
        total_transactions = fraud_report.get('total_transactions', len(fraud_transactions) * 10) if fraud_report else 100
        fraud_detected = len(fraud_transactions)
        fraud_rate = (fraud_detected / total_transactions * 100) if total_transactions > 0 else 0
        
        statistics = {
            'totalTransactions': total_transactions,
            'fraudDetected': fraud_detected,
            'fraudRate': round(fraud_rate, 1),
            'lastUpdated': fraud_report.get('timestamp', datetime.now().isoformat()) if fraud_report else datetime.now().isoformat(),
            'highRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'high']),
            'mediumRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'medium']),
            'lowRiskCount': len([t for t in fraud_transactions if t['riskLevel'] == 'low'])
        }
        
        return {
            'transactions': fraud_transactions,
            'statistics': statistics,
            'lastUpdate': datetime.now().isoformat()
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
        'version': '1.0.0'
    })

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