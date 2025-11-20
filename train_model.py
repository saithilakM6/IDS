import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score

# Load dataset
df = pd.read_csv(r"C:\Users\saith\OneDrive\Desktop\NIDS\finalids\02-14-2018.csv", low_memory=False)
df = df.dropna(axis=1, how='all')

# Convert timestamp into hour, minute, second
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce', dayfirst=True)
df['Hour'] = df['Timestamp'].dt.hour
df['Minute'] = df['Timestamp'].dt.minute
df['Second'] = df['Timestamp'].dt.second

# Define selected features
selected_features = [
    "Flow Duration", "Protocol", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Fwd Pkt Len Max", "Bwd Pkt Len Max", "Flow Byts/s", "Flow Pkts/s",
    "Hour", "Minute", "Second"
]



# Drop rows with missing values in selected features
df = df.dropna(subset=selected_features + ['Label'])

# Encode labels
le = LabelEncoder()
df['Label'] = le.fit_transform(df['Label'])

X = df[selected_features].apply(pd.to_numeric, errors='coerce')

# Replace inf/-inf with NaN
X.replace([np.inf, -np.inf], np.nan, inplace=True)

# Fill NaNs with 0 or use a better strategy (e.g., median)
X.fillna(0, inplace=True)

y = df['Label']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train models
models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(eval_metric='logloss'),
    "LogisticRegression": LogisticRegression(max_iter=1000)
}

best_model = None
best_f1 = 0
best_model_name = ""

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"\n{name} Results:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("F1-Score:", f1_score(y_test, y_pred, average='weighted'))
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    score = f1_score(y_test, y_pred, average='weighted')
    if score > best_f1:
        best_model = model
        best_f1 = score
        best_model_name = name

# Save model and scalers
pickle.dump(best_model, open("best_nids_model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))
pickle.dump(le, open("label_encoder.pkl", "wb"))

print(f"\nBest model saved: {best_model_name} with F1: {best_f1:.4f}")
