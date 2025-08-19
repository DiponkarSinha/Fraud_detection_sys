#!/usr/bin/env python3

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(456)  # Different seed for variety
np.random.seed(456)
random.seed(456)

def generate_15_transactions():
    """Generate exactly 15 test transactions with 3 fraud cases"""
    
    transactions = []
    
    # Generate 12 normal transactions
    for i in range(12):
        transaction = {
            'transaction_id': f'SET3_{i+1:04d}',
            'user_id': f'USER_{random.randint(2000, 7999)}',
            'amount': round(random.uniform(12, 450), 2),  # Normal amounts
            'merchant_category': random.choice(['grocery', 'gas_station', 'restaurant', 'retail', 'pharmacy', 'entertainment', 'utilities', 'clothing', 'books']),
            'location': random.choice(['San Francisco', 'Austin', 'Nashville', 'Orlando', 'Salt Lake City', 'Richmond', 'Buffalo']),
            'time_hour': random.randint(6, 22),  # Normal hours
            'day_of_week': random.randint(0, 6),
            'is_weekend': random.choice([0, 1]),
            'previous_failed_attempts': random.randint(0, 2),  # Low failed attempts
            'account_age_days': random.randint(300, 1500),  # Established accounts
            'avg_transaction_amount': round(random.uniform(45, 280), 2),
            'transaction_frequency': random.randint(18, 45),  # Regular users
            'is_fraud': 0
        }
        transactions.append(transaction)
    
    # Generate 3 fraud transactions with distinct suspicious patterns
    
    # Fraud case 1: High amount + very early morning + new account
    fraud_1 = {
        'transaction_id': 'FRAUD_SET3_001',
        'user_id': 'USER_FRAUD_SET3_001',
        'amount': 3500.00,  # Very high amount
        'merchant_category': 'luxury_goods',
        'location': 'Unverified_Location',
        'time_hour': 4,  # Very early morning
        'day_of_week': 4,
        'is_weekend': 0,
        'previous_failed_attempts': 22,  # Very high failed attempts
        'account_age_days': 2,  # Brand new account
        'avg_transaction_amount': 28.50,  # Much lower than current
        'transaction_frequency': 1,  # Very low frequency
        'is_fraud': 1
    }
    
    # Fraud case 2: Weekend late night + suspicious merchant + multiple flags
    fraud_2 = {
        'transaction_id': 'FRAUD_SET3_002',
        'user_id': 'USER_FRAUD_SET3_002',
        'amount': 2200.00,  # High amount
        'merchant_category': 'wire_transfer',
        'location': 'Cross_Border',
        'time_hour': 23,  # Late night
        'day_of_week': 6,
        'is_weekend': 1,
        'previous_failed_attempts': 16,  # High failed attempts
        'account_age_days': 4,  # Very new account
        'avg_transaction_amount': 42.00,  # Much lower than current
        'transaction_frequency': 2,  # Very low frequency
        'is_fraud': 1
    }
    
    # Fraud case 3: Just under threshold + suspicious category + timing
    fraud_3 = {
        'transaction_id': 'FRAUD_SET3_003',
        'user_id': 'USER_FRAUD_SET3_003',
        'amount': 1499.99,  # Just under $1500
        'merchant_category': 'prepaid_cards',
        'location': 'Anonymous_Vendor',
        'time_hour': 2,  # Very late night
        'day_of_week': 0,
        'is_weekend': 1,
        'previous_failed_attempts': 11,  # High failed attempts
        'account_age_days': 6,  # Very new account
        'avg_transaction_amount': 31.25,  # Much lower than current
        'transaction_frequency': 3,  # Very low frequency
        'is_fraud': 1
    }
    
    # Add all fraud cases
    transactions.extend([fraud_1, fraud_2, fraud_3])
    
    # Shuffle to mix normal and fraud transactions
    random.shuffle(transactions)
    
    return pd.DataFrame(transactions)

def main():
    print("🧪 Generating CSV with 15 rows (3 fraud cases)...")
    
    # Generate test data
    test_df = generate_15_transactions()
    
    # Verify we have exactly 15 rows and 3 fraud cases
    assert len(test_df) == 15, f"Expected 15 rows, got {len(test_df)}"
    fraud_count = test_df['is_fraud'].sum()
    assert fraud_count == 3, f"Expected 3 fraud cases, got {fraud_count}"
    
    # Save to CSV
    output_path = 'data/raw/transactions_15_with_3_fraud.csv'
    test_df.to_csv(output_path, index=False)
    
    print(f"✅ CSV saved: {output_path}")
    print(f"📊 Total transactions: {len(test_df)}")
    print(f"🚨 Fraud transactions: {fraud_count}")
    print(f"✅ Normal transactions: {len(test_df) - fraud_count}")
    print(f"📈 Fraud rate: {fraud_count/len(test_df)*100:.1f}%")
    
    print("\n📋 All transactions preview:")
    print(test_df[['transaction_id', 'user_id', 'amount', 'merchant_category', 'time_hour', 'previous_failed_attempts', 'is_fraud']].to_string(index=False))
    
    print("\n🎯 Fraud cases details:")
    fraud_cases = test_df[test_df['is_fraud'] == 1]
    for idx, row in fraud_cases.iterrows():
        print(f"  🚨 {row['transaction_id']}: ${row['amount']:.2f} at {row['time_hour']}:00, {row['previous_failed_attempts']} failed attempts, {row['merchant_category']}")
    
    print("\n🧪 CSV generation completed!")

if __name__ == "__main__":
    main()