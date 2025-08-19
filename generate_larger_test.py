import pandas as pd
import numpy as np
from datetime import datetime

# Generate larger test data with multiple fraud cases
np.random.seed(777)
n_samples = 20
n_fraud = 4

# Create base data
data = {
    'transaction_id': [f'LARGE_{i:03d}' for i in range(1, n_samples + 1)],
    'user_id': [f'USER_{2000 + i}' for i in range(n_samples)],
    'amount': np.random.uniform(50, 800, n_samples),
    'time_hour': np.random.randint(0, 24, n_samples),
    'day_of_week': np.random.randint(0, 7, n_samples),
    'is_weekend': np.random.choice([0, 1], n_samples),
    'previous_failed_attempts': np.random.randint(0, 4, n_samples),
    'account_age_days': np.random.randint(30, 800, n_samples),
    'avg_transaction_amount': np.random.uniform(100, 400, n_samples),
    'transaction_frequency': np.random.uniform(1, 8, n_samples),
    'is_fraud': [0] * n_samples
}

# Create multiple fraud cases
fraud_indices = [0, 1, 2, 3]
for idx in fraud_indices:
    data['amount'][idx] = np.random.uniform(8000, 15000)  # Very high amount
    data['time_hour'][idx] = np.random.choice([1, 2, 3, 4])  # Late night
    data['previous_failed_attempts'][idx] = np.random.randint(8, 20)  # Many failed attempts
    data['account_age_days'][idx] = np.random.randint(1, 10)  # Very new account
    data['transaction_frequency'][idx] = np.random.uniform(30, 80)  # High frequency
    data['is_fraud'][idx] = 1

# Create DataFrame and save
df = pd.DataFrame(data)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'data/raw/large_test_{timestamp}.csv'
df.to_csv(filename, index=False)

print(f'Generated {filename} with sufficient samples:')
print(f'Total rows: {len(df)}')
print(f'Fraud cases: {df["is_fraud"].sum()}')
print(f'Normal cases: {len(df) - df["is_fraud"].sum()}')
print('\nFraud case details:')
for idx in fraud_indices:
    print(f'  Row {idx+1}: Amount=${data["amount"][idx]:.2f}, Hour={data["time_hour"][idx]}, Failed_attempts={data["previous_failed_attempts"][idx]}')