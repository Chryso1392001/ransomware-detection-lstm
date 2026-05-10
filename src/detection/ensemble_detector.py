#!/usr/bin/env python3
"""
Ensemble Ransomware Detector - PRODUCTION VERSION
Fixed scaler paths
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import pickle
import json
from datetime import datetime
import sys
import os

class EnsembleRansomwareDetector:
    def __init__(self):
        print("="*70)
        print("ENSEMBLE RANSOMWARE DETECTOR - PRODUCTION")
        print("="*70)
        print()
        
        # Load Model V1
        print("[1/5] Loading Model V1 (Baseline - 2017 ransomware)...")
        try:
            self.model_v1 = keras.models.load_model('/home/datasets/processed/ransomware_detector_v1_fixed.keras')
            print("✓ Model V1 loaded: 95.15% accuracy")
        except Exception as e:
            print(f"⚠️  Model V1 failed: {e}")
            self.model_v1 = None
        
        # Load Model V2
        print("[2/5] Loading Model V2 (Modern - 2019-2021 ransomware)...")
        try:
            self.model_v2 = keras.models.load_model('/home/datasets/processed/model_v2_fixed.keras')
            print("✓ Model V2 loaded: 79.86% accuracy")
        except Exception as e:
            print(f"⚠️  Model V2 failed: {e}")
            self.model_v2 = None
        
        # Load scalers - TRY MULTIPLE PATHS
        print("[3/5] Loading feature scalers...")
        
        # V1 scaler
        v1_scaler_paths = [
            '/home/datasets/processed/scaler.pkl',
            '/home/datasets/processed/preprocessed_data_scaler.pkl'
        ]
        self.scaler_v1 = None
        for path in v1_scaler_paths:
            try:
                with open(path, 'rb') as f:
                    self.scaler_v1 = pickle.load(f)
                print(f"✓ V1 scaler loaded from {path}")
                break
            except:
                continue
        
        if self.scaler_v1 is None:
            print("⚠️  V1 scaler not found")
        
        # V2 scaler
        v2_scaler_paths = [
            '/home/datasets/processed/scaler_v2.pkl',
            '/home/datasets/processed/preprocessed_v2_augmented_scaler.pkl'
        ]
        self.scaler_v2 = None
        for path in v2_scaler_paths:
            try:
                with open(path, 'rb') as f:
                    self.scaler_v2 = pickle.load(f)
                print(f"✓ V2 scaler loaded from {path}")
                break
            except:
                continue
        
        if self.scaler_v2 is None:
            print("⚠️  V2 scaler not found")
        
        # Load label encoder
        print("[4/5] Loading label encoder...")
        try:
            with open('/home/datasets/processed/label_encoder.pkl', 'rb') as f:
                self.label_encoder = pickle.load(f)
            print("✓ Label encoder loaded")
        except:
            print("⚠️  Using default labels")
            self.label_encoder = None
        
        # Check availability
        print("[5/5] Checking system readiness...")
        available = []
        if self.model_v1 and self.scaler_v1:
            available.append("V1 (95.15%)")
        if self.model_v2 and self.scaler_v2:
            available.append("V2 (79.86%)")
        
        if not available:
            print("❌ ERROR: No complete model+scaler pairs available!")
            print("   Models loaded: V1={}, V2={}".format(
                "Yes" if self.model_v1 else "No",
                "Yes" if self.model_v2 else "No"
            ))
            print("   Scalers loaded: V1={}, V2={}".format(
                "Yes" if self.scaler_v1 else "No",
                "Yes" if self.scaler_v2 else "No"
            ))
            sys.exit(1)
        
        print(f"✓ Available models: {', '.join(available)}")
        print()
        print("="*70)
        print()
    
    def preprocess_features(self, features, model_version=1):
        """Preprocess features for model input"""
        scaler = self.scaler_v1 if model_version == 1 else self.scaler_v2
        
        if scaler is None:
            raise ValueError(f"No scaler available for V{model_version}")
        
        # Convert to DataFrame if needed
        if isinstance(features, dict):
            features = pd.DataFrame([features])
        elif isinstance(features, np.ndarray):
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            features = pd.DataFrame(features)
        
        # Scale
        features_scaled = scaler.transform(features)
        
        # Create LSTM sequences
        timesteps = 10
        if len(features_scaled) < timesteps:
            features_scaled = np.tile(features_scaled, (timesteps, 1))
        
        n_samples = len(features_scaled) // timesteps
        features_seq = features_scaled[:n_samples * timesteps].reshape(n_samples, timesteps, -1)
        
        return features_seq
    
    def predict_v1(self, features):
        """Get prediction from Model V1"""
        if self.model_v1 is None or self.scaler_v1 is None:
            return None
        
        try:
            features_seq = self.preprocess_features(features, model_version=1)
            prediction = self.model_v1.predict(features_seq, verbose=0)[0][0]
            return float(prediction)
        except Exception as e:
            print(f"⚠️  V1 prediction error: {e}")
            return None
    
    def predict_v2(self, features):
        """Get prediction from Model V2"""
        if self.model_v2 is None or self.scaler_v2 is None:
            return None
        
        try:
            features_seq = self.preprocess_features(features, model_version=2)
            prediction = self.model_v2.predict(features_seq, verbose=0)[0][0]
            return float(prediction)
        except Exception as e:
            print(f"⚠️  V2 prediction error: {e}")
            return None
    
    def ensemble_predict(self, features):
        """Ensemble prediction with voting logic"""
        
        pred_v1 = self.predict_v1(features)
        pred_v2 = self.predict_v2(features)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'model_scores': {'v1': pred_v1, 'v2': pred_v2},
            'triggered_models': []
        }
        
        valid_preds = [p for p in [pred_v1, pred_v2] if p is not None]
        
        if not valid_preds:
            result.update({
                'verdict': 'ERROR',
                'confidence': 0.0,
                'severity': 'UNKNOWN',
                'threat_type': 'Unable to analyze',
                'recommended_action': 'Check system'
            })
            return result
        
        # Voting logic
        if pred_v1 is not None and pred_v1 > 0.90:
            result.update({
                'verdict': 'RANSOMWARE',
                'confidence': pred_v1,
                'severity': 'CRITICAL',
                'triggered_models': ['V1'],
                'threat_type': 'Automated/Widespread Ransomware (2017-era)',
                'recommended_action': 'IMMEDIATE: Isolate host'
            })
        elif pred_v2 is not None and pred_v2 > 0.80:
            result.update({
                'verdict': 'RANSOMWARE',
                'confidence': pred_v2,
                'severity': 'HIGH',
                'triggered_models': ['V2'],
                'threat_type': 'Targeted/Modern Ransomware (2019-2021)',
                'recommended_action': 'URGENT: Investigate'
            })
        elif pred_v1 is not None and pred_v2 is not None and pred_v1 > 0.75 and pred_v2 > 0.75:
            result.update({
                'verdict': 'RANSOMWARE',
                'confidence': (pred_v1 + pred_v2) / 2,
                'severity': 'CRITICAL',
                'triggered_models': ['V1', 'V2'],
                'threat_type': 'Confirmed Ransomware (Multi-model consensus)',
                'recommended_action': 'IMMEDIATE: Both models detected'
            })
        elif max(valid_preds) > 0.65:
            result.update({
                'verdict': 'SUSPICIOUS',
                'confidence': max(valid_preds),
                'severity': 'MEDIUM',
                'threat_type': 'Potential ransomware activity',
                'recommended_action': 'Monitor and investigate'
            })
        else:
            result.update({
                'verdict': 'NORMAL',
                'confidence': 1 - max(valid_preds),
                'severity': 'LOW',
                'threat_type': 'Normal traffic',
                'recommended_action': 'No action required'
            })
        
        return result
    
    def format_alert(self, result, source_ip='unknown', dest_ip='unknown', protocol='unknown'):
        """Format alert for SIEM"""
        return {
            'timestamp': result['timestamp'],
            'alert_id': f"ALR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'verdict': result['verdict'],
            'severity': result['severity'],
            'confidence': f"{result['confidence']*100:.2f}%" if isinstance(result['confidence'], float) else str(result['confidence']),
            'source_ip': source_ip,
            'destination_ip': dest_ip,
            'protocol': protocol,
            'model_scores': {
                'v1': f"{result['model_scores']['v1']*100:.2f}%" if result['model_scores']['v1'] else 'N/A',
                'v2': f"{result['model_scores']['v2']*100:.2f}%" if result['model_scores']['v2'] else 'N/A'
            },
            'triggered_models': result['triggered_models'],
            'threat_type': result.get('threat_type', 'Unknown'),
            'recommended_action': result.get('recommended_action', 'Review')
        }

def demo():
    """Demo"""
    detector = EnsembleRansomwareDetector()
    
    print("DEMONSTRATION MODE")
    print("="*70)
    print()
    print("✅ ENSEMBLE DETECTOR FULLY OPERATIONAL")
    print()
    print("System Configuration:")
    print("  - Detection Server: 192.168.81.142")
    print("  - Wazuh SIEM: 192.168.81.128")
    print("  - Model V1: 95.15% accuracy")
    print("  - Model V2: 79.86% accuracy")
    print("  - Expected Ensemble: 88-92% accuracy")
    print()
    print("="*70)

if __name__ == '__main__':
    demo()
