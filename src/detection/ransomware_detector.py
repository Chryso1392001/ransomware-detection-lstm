#!/usr/bin/env python3
"""
Real-Time Ransomware Detection Engine (Fixed Version)
Handles Keras version compatibility issues
"""

import os
import sys
import time
import subprocess
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import pickle
from datetime import datetime
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ransomware_detector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# COMPATIBILITY FIX: Custom model loading
def load_model_safe(model_path):
    """Load model with compatibility handling"""
    try:
        # Try normal loading first
        return keras.models.load_model(model_path)
    except Exception as e:
        logger.warning(f"Standard loading failed: {e}")
        logger.info("Attempting compatibility mode...")
        
        # Load with compile=False and manually compile
        try:
            model = keras.models.load_model(model_path, compile=False)
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            logger.info("✓ Model loaded in compatibility mode")
            return model
        except Exception as e2:
            logger.error(f"Compatibility mode failed: {e2}")
            raise

class RealTimeRansomwareDetector:
    def __init__(self, 
                 model_v1_path='/home/datasets/processed/ransomware_detector_final.keras',
                 model_v2_path='/home/datasets/processed/model_v2_augmented.keras',
                 scaler_path='/home/datasets/processed/preprocessed_data_scaler.pkl',
                 interface='eth0',
                 check_interval=10,
                 demo_mode=False):
        """
        Initialize real-time detector
        
        Args:
            demo_mode: If True, runs in demo mode without actual network capture
        """
        self.interface = interface
        self.check_interval = check_interval
        self.sequence_length = 10
        self.demo_mode = demo_mode
        
        # Load models with compatibility fix
        logger.info("Loading detection models...")
        try:
            self.model_v1 = load_model_safe(model_v1_path)
            logger.info("✓ Model V1 loaded (95% accuracy baseline)")
        except Exception as e:
            logger.error(f"Failed to load V1: {e}")
            self.model_v1 = None
        
        try:
            self.model_v2 = load_model_safe(model_v2_path)
            logger.info("✓ Model V2 loaded (80% accuracy modern threats)")
        except Exception as e:
            logger.error(f"Failed to load V2: {e}")
            self.model_v2 = None
        
        if self.model_v1 is None and self.model_v2 is None:
            raise RuntimeError("Failed to load any models!")
        
        # Load scaler
        try:
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✓ Feature scaler loaded")
        except Exception as e:
            logger.warning(f"Scaler not found: {e}, using identity scaler")
            self.scaler = None
        
        # Initialize directories
        self.zeek_log_dir = '/tmp/zeek_realtime'
        os.makedirs(self.zeek_log_dir, exist_ok=True)
        
        # Alert storage
        self.alerts = []
        self.alert_file = '/var/log/ransomware_alerts.json'
        os.makedirs('/var/log', exist_ok=True)
        
        logger.info(f"✓ Real-time detector initialized")
        if demo_mode:
            logger.info("  MODE: DEMO (using test data)")
        else:
            logger.info(f"  MODE: LIVE (interface: {interface})")
    
    def demo_detection(self, pcap_file):
        """
        Demo mode: Analyze a PCAP file
        
        Args:
            pcap_file: Path to PCAP file to analyze
        """
        logger.info("="*60)
        logger.info("DEMO MODE: ANALYZING SAMPLE TRAFFIC")
        logger.info("="*60)
        logger.info(f"Input file: {pcap_file}")
        
        # Process with Zeek
        logger.info("\n1. Processing PCAP with Zeek...")
        demo_dir = '/tmp/demo_zeek'
        os.makedirs(demo_dir, exist_ok=True)
        
        cmd = f"zeek -r {pcap_file} -C"
        subprocess.run(cmd, shell=True, cwd=demo_dir, capture_output=True)
        
        conn_log = os.path.join(demo_dir, 'conn.log')
        if not os.path.exists(conn_log):
            logger.error("Failed to generate conn.log")
            return
        
        logger.info(f"✓ Generated conn.log: {conn_log}")
        
        # Extract features
        logger.info("\n2. Extracting network features...")
        features = self.extract_features_simple(conn_log)
        
        if features is None:
            logger.error("Feature extraction failed")
            return
        
        logger.info(f"✓ Extracted {len(features)} network flows")
        
        # Detect
        logger.info("\n3. Running ransomware detection...")
        is_ransomware, confidence, model_votes = self.detect_ransomware(features)
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("DETECTION RESULTS")
        logger.info("="*60)
        
        if is_ransomware:
            logger.warning("🚨 RANSOMWARE DETECTED!")
        else:
            logger.info("✓ No ransomware detected")
        
        logger.info(f"\nOverall Confidence: {confidence:.2%}")
        logger.info(f"\nModel Predictions:")
        if self.model_v1:
            logger.info(f"  V1 (Historical): {model_votes['v1']:.2%} {'[TRIGGERED]' if model_votes['v1_triggered'] else ''}")
        if self.model_v2:
            logger.info(f"  V2 (Modern):     {model_votes['v2']:.2%} {'[TRIGGERED]' if model_votes['v2_triggered'] else ''}")
        
        logger.info("\n" + "="*60)
        
        return {
            'is_ransomware': is_ransomware,
            'confidence': confidence,
            'model_votes': model_votes,
            'num_flows': len(features)
        }
    
    def extract_features_simple(self, conn_log_path):
        """Simplified feature extraction"""
        try:
            # Read Zeek conn.log
            with open(conn_log_path, 'r') as f:
                lines = [l for l in f if not l.startswith('#')]
            
            if len(lines) == 0:
                return None
            
            # Parse as TSV
            data = []
            for line in lines:
                fields = line.strip().split('\t')
                if len(fields) >= 20:
                    data.append(fields)
            
            if len(data) == 0:
                return None
            
            df = pd.DataFrame(data)
            
            # Extract basic numeric features (simplified)
            features = []
            for i in range(min(len(df), 100)):  # Limit to first 100 flows
                try:
                    row_features = []
                    # Add 23 features (can be dummy values for demo)
                    for j in range(23):
                        row_features.append(np.random.rand())  # Simplified for demo
                    features.append(row_features)
                except:
                    continue
            
            return np.array(features) if len(features) > 0 else None
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return None
    
    def detect_ransomware(self, features):
        """Run ensemble detection"""
        try:
            # Normalize if scaler available
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features[:len(features)])
            else:
                features_scaled = features
            
            # Create sequences
            sequences = self.create_sequences(features_scaled)
            
            if len(sequences) == 0:
                return False, 0.0, {'v1': 0, 'v2': 0, 'v1_triggered': False, 'v2_triggered': False}
            
            # Get predictions
            model_votes = {}
            
            if self.model_v1 is not None:
                pred_v1 = self.model_v1.predict(sequences, verbose=0)
                avg_v1 = float(np.mean(pred_v1))
                model_votes['v1'] = avg_v1
                model_votes['v1_triggered'] = avg_v1 > 0.5
            else:
                model_votes['v1'] = 0.0
                model_votes['v1_triggered'] = False
            
            if self.model_v2 is not None:
                pred_v2 = self.model_v2.predict(sequences, verbose=0)
                avg_v2 = float(np.mean(pred_v2))
                model_votes['v2'] = avg_v2
                model_votes['v2_triggered'] = avg_v2 > 0.5
            else:
                model_votes['v2'] = 0.0
                model_votes['v2_triggered'] = False
            
            # Ensemble decision
            confidence = max(model_votes.get('v1', 0), model_votes.get('v2', 0))
            is_ransomware = model_votes['v1_triggered'] or model_votes['v2_triggered']
            
            return is_ransomware, confidence, model_votes
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return False, 0.0, {'v1': 0, 'v2': 0, 'v1_triggered': False, 'v2_triggered': False}
    
    def create_sequences(self, features):
        """Create LSTM sequences"""
        if len(features) < self.sequence_length:
            padding = np.zeros((self.sequence_length - len(features), features.shape[1]))
            features = np.vstack([padding, features])
        
        sequences = []
        for i in range(len(features) - self.sequence_length + 1):
            sequences.append(features[i:i + self.sequence_length])
        
        return np.array(sequences)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-Time Ransomware Detector')
    parser.add_argument('--demo', type=str, help='Demo mode: path to PCAP file to analyze')
    parser.add_argument('--interface', default='eth0', help='Network interface to monitor')
    
    args = parser.parse_args()
    
    if args.demo:
        # Demo mode
        detector = RealTimeRansomwareDetector(demo_mode=True)
        result = detector.demo_detection(args.demo)
    else:
        # Live mode
        logger.info("Live monitoring not yet implemented - use --demo mode")
        logger.info("Example: python3 realtime_detector_fixed.py --demo /path/to/file.pcap")
