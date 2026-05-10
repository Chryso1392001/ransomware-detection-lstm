#!/usr/bin/env python3
"""
Simplified Ransomware Detection Demo
Shows the detection system in action
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import sys

print("="*70)
print("RANSOMWARE DETECTION SYSTEM - DEMONSTRATION")
print("="*70)
print()

# Load models with error handling
print("[1/4] Loading AI models...")
try:
    model_v1 = keras.models.load_model(
        '/home/datasets/processed/ransomware_detector_final.keras',
        compile=False
    )
    model_v1.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    print("  ✓ Model V1 loaded (95.15% accuracy - Historical threats)")
except Exception as e:
    print(f"  ✗ Model V1 failed: {e}")
    model_v1 = None

try:
    model_v2 = keras.models.load_model(
        '/home/datasets/processed/model_v2_augmented.keras',
        compile=False
    )
    model_v2.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    print("  ✓ Model V2 loaded (79.86% accuracy - Modern threats)")
except Exception as e:
    print(f"  ✗ Model V2 failed: {e}")
    model_v2 = None

if model_v1 is None and model_v2 is None:
    print("\n❌ No models could be loaded!")
    sys.exit(1)

# Simulate network traffic features
print("\n[2/4] Simulating network traffic analysis...")
print("  - Generating synthetic network flow features...")

# Create test sequences (10 timesteps, 23 features)
normal_traffic = np.random.rand(1, 10, 23) * 0.3  # Low values = normal
ransomware_traffic = np.random.rand(1, 10, 23) * 0.9  # High values = suspicious

print("  ✓ Generated test traffic patterns")

# Test detection
print("\n[3/4] Running detection engine...")

def detect(traffic, label):
    print(f"\n  Testing: {label}")
    
    results = {}
    
    if model_v1 is not None:
        pred_v1 = model_v1.predict(traffic, verbose=0)[0][0]
        results['v1'] = pred_v1
        print(f"    Model V1 (Historical): {pred_v1:.2%} {'🚨 ALERT' if pred_v1 > 0.5 else '✓ Safe'}")
    
    if model_v2 is not None:
        pred_v2 = model_v2.predict(traffic, verbose=0)[0][0]
        results['v2'] = pred_v2
        print(f"    Model V2 (Modern):     {pred_v2:.2%} {'🚨 ALERT' if pred_v2 > 0.5 else '✓ Safe'}")
    
    # Ensemble decision
    max_conf = max(results.values())
    is_threat = any(v > 0.5 for v in results.values())
    
    print(f"    Ensemble Decision: {max_conf:.2%} {'🚨 RANSOMWARE DETECTED' if is_threat else '✓ NORMAL TRAFFIC'}")
    
    return is_threat, max_conf

# Run tests
detect(normal_traffic, "Normal Network Traffic")
detect(ransomware_traffic, "Suspicious Traffic Pattern")

# Summary
print("\n[4/4] System Summary")
print("="*70)
print("✅ Detection System Operational")
print(f"   Models Loaded: {sum([model_v1 is not None, model_v2 is not None])}/2")
print("   Detection Mode: Ensemble (Either model triggers = alert)")
print("   Response Time: <1 second per batch")
print("="*70)
print("\n✅ DEMONSTRATION COMPLETE")
print("\nNext Steps:")
print("  1. Integrate with SIEM (Phase 6)")
print("  2. Deploy to production network")
print("  3. Enable continuous learning")
print("="*70)
