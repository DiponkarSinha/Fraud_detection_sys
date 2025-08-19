#!/usr/bin/env python3

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_test_transactions():
    """Generate exactly 10 test transactions with 2 fraud cases"""
    
    transactions = []
    
    # Generate 8 normal transactions
    for i in range(8):
        transaction = {
            'transaction_id': f'TEST_{i+1:04d}',
            'user_id': f'USER_{random.randint(1000, 9999)}',
            'amount': round(random.uniform(10, 500), 2),  # Normal amounts
            'merchant_category': random.choice(['grocery', 'gas_station', 'restaurant', 'retail', 'pharmacy']),
            'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'time_hour': random.randint(8, 22),  # Normal business hours
            'day_of_week': random.randint(0, 6),
            'is_weekend': random.choice([0, 1]),
            'previous_failed_attempts': random.randint(0, 2),  # Low failed attempts
            'account_age_days': random.randint(365, 2000),  # Established accounts
            'avg_transaction_amount': round(random.uniform(50, 300), 2),
            'transaction_frequency': random.randint(20, 50),  # Regular users
            'is_fraud': 0
        }
        transactions.append(transaction)
    
    # Generate 2 fraud transactions with suspicious patterns
    
    # Fraud case 1: High amount + unusual time + multiple failed attempts
    fraud_1 = {
        'transaction_id': 'TEST_FRAUD_001',
        'user_id': 'USER_FRAUD_001',
        'amount': 2500.00,  # Very high amount
        'merchant_category': 'online',
        'location': 'Unknown',  # Unusual location
        'time_hour': 3,  # Very early morning (suspicious)
        'day_of_week': 2,
        'is_weekend': 0,
        'previous_failed_attempts': 8,  # Many failed attempts
        'account_age_days': 15,  # Very new account
        'avg_transaction_amount': 45.50,  # Much higher than average
        'transaction_frequency': 2,  # Very low frequency
        'is_fraud': 1
    }
    
    # Fraud case 2: Multiple suspicious indicators
    fraud_2 = {
        'transaction_id': 'TEST_FRAUD_002',
        'user_id': 'USER_FRAUD_002',
        'amount': 1800.00,  # High amount
        'merchant_category': 'atm',
        'location': 'Foreign',  # Unusual location
        'time_hour': 23,  # Late night
        'day_of_week': 6,
        'is_weekend': 1,
        'previous_failed_attempts': 5,  # Multiple failed attempts
        'account_age_days': 7,  # Very new account
        'avg_transaction_amount': 75.00,  # Much higher than average
        'transaction_frequency': 1,  # Very low frequency
        'is_fraud': 1
    }
    
    transactions.append(fraud_1)
    transactions.append(fraud_2)
    
    # Shuffle to mix normal and fraud transactions
    random.shuffle(transactions)
    
    return pd.DataFrame(transactions)

def main():
    print("🧪 Generating test CSV with 10 rows (2 fraud cases)...")
    
    # Generate test data
    test_df = generate_test_transactions()
    
    # Verify we have exactly 10 rows and 2 fraud cases
    assert len(test_df) == 10, f"Expected 10 rows, got {len(test_df)}"
    fraud_count = test_df['is_fraud'].sum()
    assert fraud_count == 2, f"Expected 2 fraud cases, got {fraud_count}"
    
    # Save to CSV
    output_path = 'data/raw/test_transactions.csv'
    test_df.to_csv(output_path, index=False)
    
    print(f"✅ Test CSV saved: {output_path}")
    print(f"📊 Total transactions: {len(test_df)}")
    print(f"🚨 Fraud transactions: {fraud_count}")
    print(f"✅ Normal transactions: {len(test_df) - fraud_count}")
    print(f"📈 Fraud rate: {fraud_count/len(test_df)*100:.1f}%")
    
    print("\n📋 Test transactions preview:")
    print(test_df[['transaction_id', 'user_id', 'amount', 'merchant_category', 'time_hour', 'previous_failed_attempts', 'is_fraud']].to_string(index=False))
    
    print("\n🎯 Fraud cases details:")
    fraud_cases = test_df[test_df['is_fraud'] == 1]
    for idx, row in fraud_cases.iterrows():
        print(f"  🚨 {row['transaction_id']}: ${row['amount']:.2f} at {row['time_hour']}:00, {row['previous_failed_attempts']} failed attempts")
    
    print("\n🧪 Test CSV generation completed!")

if __name__ == "__main__":
    main()