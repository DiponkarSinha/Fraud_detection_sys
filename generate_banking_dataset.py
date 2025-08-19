#!/usr/bin/env python3

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import json

class BankingDatasetGenerator:
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        self.fake = Faker()
        Faker.seed(seed)
        
        # Banking-specific parameters
        self.merchant_categories = [
            'grocery', 'gas_station', 'restaurant', 'pharmacy', 'retail',
            'online_shopping', 'atm_withdrawal', 'bank_transfer', 'bill_payment',
            'entertainment', 'travel', 'healthcare', 'education', 'insurance'
        ]
        
        self.locations = [
            'New_York', 'Los_Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San_Antonio', 'San_Diego', 'Dallas', 'San_Jose',
            'Austin', 'Jacksonville', 'Fort_Worth', 'Columbus', 'Charlotte',
            'Seattle', 'Denver', 'Boston', 'Nashville', 'Baltimore'
        ]
        
    def generate_normal_transaction(self, user_id, transaction_id):
        """Generate a normal banking transaction"""
        category = np.random.choice(self.merchant_categories)
        
        # Amount based on category (realistic banking amounts)
        if category == 'grocery':
            amount = np.random.normal(85, 30)
        elif category == 'gas_station':
            amount = np.random.normal(45, 15)
        elif category == 'restaurant':
            amount = np.random.normal(35, 20)
        elif category == 'atm_withdrawal':
            amount = np.random.choice([20, 40, 60, 80, 100, 200])
        elif category == 'bill_payment':
            amount = np.random.normal(150, 50)
        elif category == 'online_shopping':
            amount = np.random.normal(75, 40)
        else:
            amount = np.random.normal(60, 25)
            
        amount = max(5, round(amount, 2))  # Minimum $5
        
        # Time patterns (normal banking hours)
        hour = np.random.choice(range(6, 23), p=[
            0.02, 0.03, 0.05, 0.08, 0.12, 0.15, 0.12, 0.10,
            0.08, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02, 0.02, 0.01
        ])
        
        day_of_week = np.random.randint(1, 8)
        is_weekend = 1 if day_of_week in [6, 7] else 0
        
        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'amount': amount,
            'merchant_category': category,
            'location': np.random.choice(self.locations),
            'time_hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'previous_failed_attempts': 0,
            'account_age_days': np.random.randint(30, 3650),
            'avg_transaction_amount': np.random.normal(75, 25),
            'transaction_frequency': np.random.randint(5, 50),
            'is_fraud': 0
        }
    
    def generate_fraud_transaction(self, user_id, transaction_id):
        """Generate a fraudulent banking transaction"""
        # Fraud patterns
        fraud_patterns = [
            'high_amount',
            'unusual_time',
            'unusual_location',
            'multiple_attempts',
            'new_account'
        ]
        
        pattern = np.random.choice(fraud_patterns)
        
        if pattern == 'high_amount':
            amount = np.random.uniform(5000, 50000)  # Unusually high amounts
            category = np.random.choice(['online_shopping', 'retail', 'atm_withdrawal'])
            hour = np.random.randint(0, 24)
            failed_attempts = np.random.randint(3, 10)
            
        elif pattern == 'unusual_time':
            amount = np.random.uniform(200, 2000)
            category = np.random.choice(self.merchant_categories)
            hour = np.random.choice([0, 1, 2, 3, 4, 5, 23])  # Very late/early hours
            failed_attempts = np.random.randint(1, 5)
            
        elif pattern == 'unusual_location':
            amount = np.random.uniform(100, 1000)
            category = np.random.choice(self.merchant_categories)
            hour = np.random.randint(6, 22)
            failed_attempts = np.random.randint(0, 3)
            
        elif pattern == 'multiple_attempts':
            amount = np.random.uniform(50, 500)
            category = np.random.choice(self.merchant_categories)
            hour = np.random.randint(0, 24)
            failed_attempts = np.random.randint(5, 15)  # Many failed attempts
            
        else:  # new_account
            amount = np.random.uniform(1000, 10000)
            category = np.random.choice(['online_shopping', 'bank_transfer'])
            hour = np.random.randint(0, 24)
            failed_attempts = np.random.randint(2, 8)
        
        day_of_week = np.random.randint(1, 8)
        is_weekend = 1 if day_of_week in [6, 7] else 0
        
        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'amount': round(amount, 2),
            'merchant_category': category,
            'location': np.random.choice(self.locations + ['Unknown', 'Foreign']),
            'time_hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'previous_failed_attempts': failed_attempts,
            'account_age_days': np.random.randint(1, 365) if pattern == 'new_account' else np.random.randint(30, 3650),
            'avg_transaction_amount': np.random.normal(75, 25),
            'transaction_frequency': np.random.randint(1, 30),
            'is_fraud': 1
        }
    
    def generate_dataset(self, n_samples=10000, fraud_rate=0.02):
        """Generate complete banking dataset"""
        n_fraud = int(n_samples * fraud_rate)
        n_normal = n_samples - n_fraud
        
        transactions = []
        
        # Generate normal transactions
        for i in range(n_normal):
            user_id = f"USER_{i+1:06d}"
            transaction_id = f"TXN_{i+1:08d}"
            transactions.append(self.generate_normal_transaction(user_id, transaction_id))
        
        # Generate fraud transactions
        for i in range(n_fraud):
            user_id = f"USER_{n_normal+i+1:06d}"
            transaction_id = f"TXN_{n_normal+i+1:08d}"
            transactions.append(self.generate_fraud_transaction(user_id, transaction_id))
        
        # Shuffle the dataset
        random.shuffle(transactions)
        
        # Create DataFrame
        df = pd.DataFrame(transactions)
        
        # Ensure proper data types
        df['amount'] = df['amount'].round(2)
        df['avg_transaction_amount'] = df['avg_transaction_amount'].round(2)
        
        return df

if __name__ == "__main__":
    print("🏦 Generating realistic banking dataset...")
    
    generator = BankingDatasetGenerator()
    
    # Generate training dataset (10,000 samples with 2% fraud rate)
    train_df = generator.generate_dataset(n_samples=10000, fraud_rate=0.02)
    
    # Save training dataset
    train_path = "data/raw/banking_transactions_train.csv"
    train_df.to_csv(train_path, index=False)
    
    print(f"✅ Training dataset saved: {train_path}")
    print(f"📊 Dataset shape: {train_df.shape}")
    print(f"🚨 Fraud transactions: {train_df['is_fraud'].sum()}")
    print(f"✅ Normal transactions: {(train_df['is_fraud'] == 0).sum()}")
    print(f"📈 Fraud rate: {train_df['is_fraud'].mean():.2%}")
    
    # Display sample data
    print("\n📋 Sample transactions:")
    print(train_df.head(10))
    
    print("\n🎯 Dataset generation completed!")