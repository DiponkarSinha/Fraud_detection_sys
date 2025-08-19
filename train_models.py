#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FraudModelTrainer:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
    def load_and_preprocess_data(self, data_path):
        """Load and preprocess the banking dataset"""
        print(f"📊 Loading data from {data_path}...")
        df = pd.read_csv(data_path)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Fraud rate: {df['is_fraud'].mean():.2%}")
        
        # Encode categorical variables
        le_category = LabelEncoder()
        le_location = LabelEncoder()
        
        df['merchant_category_encoded'] = le_category.fit_transform(df['merchant_category'])
        df['location_encoded'] = le_location.fit_transform(df['location'])
        
        # Store encoders
        self.encoders['merchant_category'] = le_category
        self.encoders['location'] = le_location
        
        # Feature engineering
        df['amount_log'] = np.log1p(df['amount'])
        df['avg_amount_ratio'] = df['amount'] / (df['avg_transaction_amount'] + 1)
        df['failed_attempts_ratio'] = df['previous_failed_attempts'] / (df['transaction_frequency'] + 1)
        
        # Select features for modeling
        feature_columns = [
            'amount', 'amount_log', 'merchant_category_encoded', 'location_encoded',
            'time_hour', 'day_of_week', 'is_weekend', 'previous_failed_attempts',
            'account_age_days', 'avg_transaction_amount', 'transaction_frequency',
            'avg_amount_ratio', 'failed_attempts_ratio'
        ]
        
        X = df[feature_columns]
        y = df['is_fraud']
        
        return X, y, df
    
    def train_supervised_models(self, X_train, X_test, y_train, y_test):
        """Train supervised learning models"""
        print("\n🤖 Training Supervised Models...")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['supervised'] = scaler
        
        # 1. Random Forest Classifier
        print("\n🌲 Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate Random Forest
        rf_pred = rf_model.predict(X_test_scaled)
        rf_prob = rf_model.predict_proba(X_test_scaled)[:, 1]
        
        print("Random Forest Results:")
        print(classification_report(y_test, rf_pred))
        print(f"AUC Score: {roc_auc_score(y_test, rf_prob):.4f}")
        
        self.models['random_forest'] = rf_model
        
        # 2. Logistic Regression
        print("\n📈 Training Logistic Regression...")
        lr_model = LogisticRegression(
            random_state=42,
            class_weight='balanced',
            max_iter=1000
        )
        lr_model.fit(X_train_scaled, y_train)
        
        # Evaluate Logistic Regression
        lr_pred = lr_model.predict(X_test_scaled)
        lr_prob = lr_model.predict_proba(X_test_scaled)[:, 1]
        
        print("Logistic Regression Results:")
        print(classification_report(y_test, lr_pred))
        print(f"AUC Score: {roc_auc_score(y_test, lr_prob):.4f}")
        
        self.models['logistic_regression'] = lr_model
        
        return X_train_scaled, X_test_scaled
    
    def train_unsupervised_models(self, X_train, X_test, y_test):
        """Train unsupervised learning models"""
        print("\n🔍 Training Unsupervised Models...")
        
        # Use only normal transactions for unsupervised training
        X_normal = X_train[y_test.iloc[:len(X_train)] == 0] if len(X_train) < len(y_test) else X_train
        
        # Scale features for unsupervised models
        scaler_unsup = StandardScaler()
        X_normal_scaled = scaler_unsup.fit_transform(X_normal)
        X_test_scaled = scaler_unsup.transform(X_test)
        self.scalers['unsupervised'] = scaler_unsup
        
        # 1. Isolation Forest
        print("\n🌳 Training Isolation Forest...")
        iso_model = IsolationForest(
            contamination=0.02,  # Expected fraud rate
            random_state=42,
            n_estimators=100
        )
        iso_model.fit(X_normal_scaled)
        
        # Evaluate Isolation Forest
        iso_pred = iso_model.predict(X_test_scaled)
        iso_pred_binary = (iso_pred == -1).astype(int)  # -1 for anomaly, 1 for normal
        
        print("Isolation Forest Results:")
        print(classification_report(y_test, iso_pred_binary))
        
        self.models['isolation_forest'] = iso_model
        
        # 2. One-Class SVM
        print("\n🎯 Training One-Class SVM...")
        svm_model = OneClassSVM(
            kernel='rbf',
            gamma='scale',
            nu=0.02  # Expected fraud rate
        )
        svm_model.fit(X_normal_scaled)
        
        # Evaluate One-Class SVM
        svm_pred = svm_model.predict(X_test_scaled)
        svm_pred_binary = (svm_pred == -1).astype(int)  # -1 for anomaly, 1 for normal
        
        print("One-Class SVM Results:")
        print(classification_report(y_test, svm_pred_binary))
        
        self.models['oneclass_svm'] = svm_model
    
    def save_models(self):
        """Save all trained models and preprocessors"""
        print("\n💾 Saving models...")
        
        # Create models directory if it doesn't exist
        os.makedirs('models/artifacts', exist_ok=True)
        
        # Save each model
        for model_name, model in self.models.items():
            model_path = f'models/artifacts/{model_name}_model.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"✅ Saved: {model_path}")
        
        # Save scalers
        for scaler_name, scaler in self.scalers.items():
            scaler_path = f'models/artifacts/{scaler_name}_scaler.pkl'
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            print(f"✅ Saved: {scaler_path}")
        
        # Save encoders
        for encoder_name, encoder in self.encoders.items():
            encoder_path = f'models/artifacts/{encoder_name}_encoder.pkl'
            with open(encoder_path, 'wb') as f:
                pickle.dump(encoder, f)
            print(f"✅ Saved: {encoder_path}")
        
        # Save model metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'models': list(self.models.keys()),
            'scalers': list(self.scalers.keys()),
            'encoders': list(self.encoders.keys()),
            'feature_columns': [
                'amount', 'amount_log', 'merchant_category_encoded', 'location_encoded',
                'time_hour', 'day_of_week', 'is_weekend', 'previous_failed_attempts',
                'account_age_days', 'avg_transaction_amount', 'transaction_frequency',
                'avg_amount_ratio', 'failed_attempts_ratio'
            ]
        }
        
        with open('models/artifacts/model_metadata.pkl', 'wb') as f:
            pickle.dump(metadata, f)
        print("✅ Saved: models/artifacts/model_metadata.pkl")
    
    def train_all_models(self, data_path):
        """Complete training pipeline"""
        print("🚀 Starting ML Model Training Pipeline...")
        
        # Load and preprocess data
        X, y, df = self.load_and_preprocess_data(data_path)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📊 Data Split:")
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Training fraud rate: {y_train.mean():.2%}")
        print(f"Test fraud rate: {y_test.mean():.2%}")
        
        # Train supervised models
        X_train_scaled, X_test_scaled = self.train_supervised_models(X_train, X_test, y_train, y_test)
        
        # Train unsupervised models
        self.train_unsupervised_models(X_train_scaled, X_test_scaled, y_test)
        
        # Save all models
        self.save_models()
        
        print("\n🎉 Model training completed successfully!")
        print(f"📁 Models saved in: models/artifacts/")
        
        return self.models

if __name__ == "__main__":
    trainer = FraudModelTrainer()
    models = trainer.train_all_models('data/raw/banking_transactions_train.csv')
    
    print("\n🏆 Trained Models:")
    for model_name in models.keys():
        print(f"  ✅ {model_name}")