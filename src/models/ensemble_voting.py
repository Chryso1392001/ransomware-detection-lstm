#!/usr/bin/env python3
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

print("="*60)
print("ENSEMBLE MODEL: COMBINING V1 + V2")
print("="*60)

# Load models
print("\nLoading models...")
model_v1 = keras.models.load_model('/home/datasets/processed/ransomware_detector_final.keras')
model_v2 = keras.models.load_model('/home/datasets/processed/model_v2_complete.keras')
print("✓ Models loaded")

# Load V2 test data
print("\nLoading test data...")
data = np.load('/home/datasets/processed/preprocessed_v2_complete.npz')
X_test = data['X_test']
y_test = data['y_test']
print(f"✓ Test data: {X_test.shape}")

# Get predictions from both models
print("\nGenerating predictions...")
y_pred_v1 = model_v1.predict(X_test, verbose=0)
y_pred_v2 = model_v2.predict(X_test, verbose=0)

# Ensemble: Average probabilities
y_pred_ensemble = (y_pred_v1 + y_pred_v2) / 2
y_pred = (y_pred_ensemble > 0.5).astype(int).flatten()

# Evaluate
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n" + "="*60)
print("ENSEMBLE RESULTS")
print("="*60)
print(f"\nEnsemble Performance:")
print(f"  Accuracy:  {acc*100:.2f}%")
print(f"  Precision: {prec*100:.2f}%")
print(f"  Recall:    {rec*100:.2f}%")
print(f"  F1-Score:  {f1:.4f}")
print("\n" + "="*60)
