import joblib
import numpy as np
import random
import os

model_path = r'E:\ThreatChain\threatchain-backend\threathchain_xgboost.joblib'
bundle = joblib.load(model_path)
model = bundle['model']

print("Searching for a malicious payload that triggers >90% confidence...")

for i in range(10000):
    # Generate random features, trying to simulate weird traffic
    payload = [0] * 77
    
    # Randomly assign values
    payload[0] = random.choice([80, 443, 22, 21, 3389])
    payload[1] = random.choice([6, 17])
    payload[2] = random.randint(1000, 10000000)
    
    # Spikes
    payload[3] = random.randint(100, 50000)
    payload[4] = random.randint(100, 50000)
    payload[10] = random.randint(50000, 1000000)
    payload[15] = random.randint(0, 1)
    payload[16] = random.randint(0, 1)
    
    # Fill remaining with random noise
    for j in range(5, 77):
        if payload[j] == 0:
            payload[j] = random.random() * random.choice([10, 100, 1000])

    input_data = np.array(payload).reshape(1, -1)
    prob = model.predict_proba(input_data)[0][1]
    
    if prob > 0.90:
        print(f"FOUND MALICIOUS PAYLOAD! (Score: {prob})")
        print(payload)
        break
else:
    print("Could not find a high-confidence payload in 10000 tries.")
