#!/usr/bin/env python3

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(123)  # Different seed for variety
np.random.seed(123)
random.seed(123)

def generate_second_batch_transactions():
    """Generate another 20 test transactions with 5 fraud cases"""
    
    transactions = []
    
    # Generate 15 normal transactions
    for i in range(15):
        transaction = {
            'transaction_id': f'BATCH2_{i+1:04d}',
            'user_id': f'USER_{random.randint(5000, 9999)}',
            'amount': round(random.uniform(15, 600), 2),  # Slightly different range
            'merchant_category': random.choice(['grocery', 'gas_station', 'restaurant', 'retail', 'pharmacy', 'entertainment', 'utilities', 'clothing']),
            'location': random.choice(['Miami', 'Seattle', 'Denver', 'Boston', 'Atlanta', 'Dallas', 'Portland']),
            'time_hour': random.randint(7, 23),  # Extended hours
            'day_of_week': random.randint(0, 6),
            'is_weekend': random.choice([0, 1]),
            'previous_failed_attempts': random.randint(0, 3),  # Slightly higher range
            'account_age_days': random.randint(200, 1800),  # Different range
            'avg_transaction_amount': round(random.uniform(40, 350), 2),
            'transaction_frequency': random.randint(15, 60),  # Different range
            'is_fraud': 0
        }
        transactions.append(transaction)
    
    # Generate 5 fraud transactions with different suspicious patterns
    
    # Fraud case 1: Extremely high amount + very new account
    fraud_1 = {
        'transaction_id': 'FRAUD_B2_001',
        'user_id': 'USER_FRAUD_B2_001',
        'amount': 5500.00,  # Extremely high amount
        'merchant_category': 'jewelry',
        'location': 'Suspicious_Location',
        'time_hour': 5,  # Very early morning
        'day_of_week': 3,
        'is_weekend': 0,
        'previous_failed_attempts': 20,  # Extremely high failed attempts
        'account_age_days': 1,  # Brand new account
        'avg_transaction_amount': 15.00,  # Much lower than current transaction
        'transaction_frequency': 1,  # Very low frequency
        'is_fraud': 1
    }
    
    # Fraud case 2: Multiple red flags - late night + high amount + foreign location
    fraud_2 = {
        'transaction_id': 'FRAUD_B2_002',
        'user_id': 'USER_FRAUD_B2_002',
        'amount': 3750.00,  # High amount
        'merchant_category': 'electronics',
        'location': 'International_Unknown',
        'time_hour': 0,  # Midnight
        'day_of_week': 5,
        'is_weekend': 1,
        'previous_failed_attempts': 18,  # Very high failed attempts
        'account_age_days': 5,  # Very new account
        'avg_transaction_amount': 35.00,  # Much lower than current
        'transaction_frequency': 2,  # Very low frequency
        'is_fraud': 1
    }
    
    # Fraud case 3: Cryptocurrency/digital goods + suspicious timing
    fraud_3 = {
        'transaction_id': 'FRAUD_B2_003',
        'user_id': 'USER_FRAUD_B2_003',
        'amount': 2999.99,  # Just under $3000
        'merchant_category': 'cryptocurrency',
        'location': 'Digital_Platform',
        'time_hour': 4,  # Very early morning
        'day_of_week': 1,
        'is_weekend': 0,
        'previous_failed_attempts': 25,  # Extremely high
        'account_age_days': 2,  # Brand new
        'avg_transaction_amount': 22.50,  # Much lower
        'transaction_frequency': 1,  # Very low
        'is_fraud': 1
    }
    
    # Fraud case 4: Cash advance + multiple suspicious indicators
    fraud_4 = {
        'transaction_id': 'FRAUD_B2_004',
        'user_id': 'USER_FRAUD_B2_004',
        'amount': 1999.99,  # High amount, just under $2000
        'merchant_category': 'payday_loan',
        'location': 'Offshore_Entity',
        'time_hour': 2,  # Very late night
        'day_of_week': 6,
        'is_weekend': 1,
        'previous_failed_attempts': 14,  # High failed attempts
        'account_age_days': 3,  # Very new account
        'avg_transaction_amount': 18.75,  # Much lower
        'transaction_frequency': 1,  # Very low
        'is_fraud': 1
    }
    
    # Fraud case 5: Gift cards + suspicious pattern
    fraud_5 = {
        'transaction_id': 'FRAUD_B2_005',
        'user_id': 'USER_FRAUD_B2_005',
        'amount': 4999.99,  # Just under $5000
        'merchant_category': 'gift_cards',
        'location': 'Anonymous_Vendor',
        'time_hour': 1,  # Very late night
        'day_of_week': 0,
        'is_weekend': 1,
        'previous_failed_attempts': 30,  # Extremely high
        'account_age_days': 1,  # Brand new
        'avg_transaction_amount': 12.00,  # Much lower
        'transaction_frequency': 1,  # Very low
        'is_fraud': 1
    }
    
    # Add all fraud cases
    transactions.extend([fraud_1, fraud_2, fraud_3, fraud_4, fraud_5])
    
    # Shuffle to mix normal and fraud transactions
    random.shuffle(transactions)
    
    return pd.DataFrame(transactions)

def main():
    print("🧪 Generating second batch CSV with 20 rows (5 fraud cases)...")
    
    # Generate test data
    test_df = generate_second_batch_transactions()
    
    # Verify we have exactly 20 rows and 5 fraud cases
    assert len(test_df) == 20, f"Expected 20 rows, got {len(test_df)}"
    fraud_count = test_df['is_fraud'].sum()
    assert fraud_count == 5, f"Expected 5 fraud cases, got {fraud_count}"
    
    # Save to CSV
    output_path = 'data/raw/transactions_batch2_20_with_5_fraud.csv'
    test_df.to_csv(output_path, index=False)
    
    print(f"✅ Second batch CSV saved: {output_path}")
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
    
    print("\n🧪 Second batch CSV generation completed!")

if __name__ == "__main__":
    main()