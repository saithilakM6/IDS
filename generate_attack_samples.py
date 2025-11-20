import pandas as pd

# Load your dataset
df = pd.read_csv(r"C:\Users\saith\OneDrive\Desktop\NIDS\finalids\02-14-2018.csv", low_memory=False)

# Convert Timestamp to Hour, Minute, Second
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Hour'] = df['Timestamp'].dt.hour
df['Minute'] = df['Timestamp'].dt.minute
df['Second'] = df['Timestamp'].dt.second

# Define the selected features
features = [
    "Flow Duration", "Protocol", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Fwd Pkt Len Max", "Bwd Pkt Len Max", "Flow Byts/s", "Flow Pkts/s",
    "Hour", "Minute", "Second"
]

# Target classes
classes = df['Label'].unique()

# Collect samples
attack_samples = {}

for label in classes:
    subset = df[df['Label'] == label]
    top_samples = subset[features].dropna().head(3)
    attack_samples[label] = top_samples.values.tolist()

import json
print(json.dumps(attack_samples, indent=2))
