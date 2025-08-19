#!/usr/bin/env python3
"""
Fraud Detection System
Processes transaction CSV files and detects fraudulent transactions
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import glob

class FraudDetector:
    def __init__(self):
        self.model = None
        self.feature_columns = ['amount']  # Will be dynamically set based on available columns
    
    def load_data(self, csv_path):
        """Load transaction data from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df)} transactions from {csv_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def preprocess_data(self, df):
        """Preprocess the data for model training/prediction"""
        # Create features from available columns
        features_df = pd.DataFrame()
        
        # Amount feature (always available)
        if 'amount' in df.columns:
            features_df['amount'] = df['amount']
        
        # Extract time features if timestamp is available
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            features_df['time_hour'] = df['timestamp'].dt.hour
            features_df['day_of_week'] = df['timestamp'].dt.dayofweek
            features_df['is_weekend'] = (df['timestamp'].dt.dayofweek >= 5).astype(int)
        
        # Risk level encoding if available
        if 'risk_level' in df.columns:
            risk_mapping = {'low': 1, 'medium': 2, 'high': 3}
            features_df['risk_score'] = df['risk_level'].map(risk_mapping).fillna(1)
        
        # Transaction type encoding if available
        if 'transaction_type' in df.columns:
            features_df['is_online'] = (df['transaction_type'] == 'online').astype(int)
        
        # If we have very few features, add some derived ones
        if len(features_df.columns) < 3:
            features_df['amount_log'] = np.log1p(features_df['amount']) if 'amount' in features_df.columns else 0
            features_df['amount_squared'] = features_df['amount'] ** 2 if 'amount' in features_df.columns else 0
        
        # Handle missing values
        features_df = features_df.fillna(features_df.mean())
        
        # Update feature columns for future use
        self.feature_columns = list(features_df.columns)
        
        # Get target variable if available
        y = df['is_fraud'] if 'is_fraud' in df.columns else None
        
        return features_df, y
    
    def train_model(self, X, y):
        """Train the fraud detection model"""
        print("🔄 Training fraud detection model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"📊 Accuracy: {accuracy:.2%}")
        print("\n📈 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def predict_fraud(self, X):
        """Predict fraud for new transactions"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]  # Probability of fraud
        
        return predictions, probabilities
    
    def save_model(self, model_path):
        """Save the trained model"""
        if self.model is not None:
            joblib.dump(self.model, model_path)
            print(f"💾 Model saved to {model_path}")
    
    def load_model(self, model_path):
        """Load a pre-trained model"""
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"📂 Model loaded from {model_path}")
        else:
            print(f"❌ Model file not found: {model_path}")
    
    def generate_report(self, df, predictions, probabilities, output_path):
        """Generate fraud detection report"""
        # Add predictions to dataframe
        df_report = df.copy()
        df_report['predicted_fraud'] = predictions
        df_report['fraud_probability'] = probabilities
        df_report['risk_level'] = pd.cut(
            probabilities, 
            bins=[0, 0.3, 0.7, 1.0], 
            labels=['Low', 'Medium', 'High']
        )
        
        # Generate summary statistics
        total_transactions = len(df_report)
        fraud_detected = sum(predictions)
        fraud_rate = fraud_detected / total_transactions * 100
        
        # Create summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_transactions': total_transactions,
            'fraud_detected': int(fraud_detected),
            'fraud_rate_percent': round(fraud_rate, 2),
            'high_risk_transactions': len(df_report[df_report['risk_level'] == 'High']),
            'medium_risk_transactions': len(df_report[df_report['risk_level'] == 'Medium']),
            'low_risk_transactions': len(df_report[df_report['risk_level'] == 'Low'])
        }
        
        # Save detailed report
        report_csv = output_path.replace('.json', '_detailed.csv')
        df_report.to_csv(report_csv, index=False)
        
        # Save summary report
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📋 FRAUD DETECTION REPORT")
        print(f"=========================")
        print(f"Total Transactions: {total_transactions}")
        print(f"Fraud Detected: {fraud_detected}")
        print(f"Fraud Rate: {fraud_rate:.2f}%")
        print(f"High Risk: {summary['high_risk_transactions']}")
        print(f"Medium Risk: {summary['medium_risk_transactions']}")
        print(f"Low Risk: {summary['low_risk_transactions']}")
        print(f"\n📄 Detailed report saved: {report_csv}")
        print(f"📄 Summary report saved: {output_path}")
        
        return summary

def main():
    """Main function to run fraud detection"""
    import sys
    
    # Get data path from command line argument or find latest CSV
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        # Find the latest CSV file in data/raw directory
        csv_files = glob.glob('data/raw/*.csv')
        if csv_files:
            # Sort by modification time, get the latest
            data_path = max(csv_files, key=os.path.getmtime)
            print(f"📁 Auto-detected latest CSV: {data_path}")
        else:
            data_path = 'data/raw/banking_dataset.csv'
    
    print(f"🔍 Starting fraud detection analysis on: {data_path}")
    
    # Initialize detector
    detector = FraudDetector()
    
    # Paths
    model_path = 'models/fraud_model.joblib'
    report_path = 'outputs/fraud_report.json'
    root_report_path = 'fraud_report.json'  # For dashboard compatibility
    
    # Create directories if they don't exist
    os.makedirs('models', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Load data
    df = detector.load_data(data_path)
    if df is None:
        return
    
    # Preprocess data
    X, y = detector.preprocess_data(df)
    
    # Train model if we have labels
    if y is not None:
        accuracy = detector.train_model(X, y)
        detector.save_model(model_path)
    else:
        # Load pre-trained model
        detector.load_model(model_path)
    
    # Make predictions
    predictions, probabilities = detector.predict_fraud(X)
    
    # Generate report
    summary = detector.generate_report(df, predictions, probabilities, report_path)
    
    # Also save report to root directory for dashboard
    import shutil
    if os.path.exists(report_path):
        shutil.copy2(report_path, root_report_path)
        print(f"📋 Report copied to {root_report_path} for dashboard")
    
    # Alert if fraud detected
    if summary['fraud_detected'] > 0:
        print(f"\n🚨 FRAUD ALERT: {summary['fraud_detected']} fraudulent transactions detected!")
        print(f"📧 Triggering notification system...")
    else:
        print(f"\n✅ No fraudulent transactions detected.")
    
    print(f"\n🎯 Fraud detection completed successfully!")
    return summary

if __name__ == "__main__":
    main()