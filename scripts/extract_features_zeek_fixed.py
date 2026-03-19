#!/usr/bin/env python3
"""
extract_features_zeek_fixed.py
Extract flow-based features from Zeek logs for ML training
FIXED VERSION - Properly parses Zeek log format

Usage:
    python extract_features_zeek_fixed.py --input /path/to/zeek/logs --label normal
    python extract_features_zeek_fixed.py --input /path/to/zeek/logs --label ransomware
"""

import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime

class ZeekFeatureExtractor:
    def __init__(self, zeek_logs_dir, label):
        self.zeek_logs_dir = zeek_logs_dir
        self.label = label
        self.conn_log = os.path.join(zeek_logs_dir, 'conn.log')
        self.ssl_log = os.path.join(zeek_logs_dir, 'ssl.log')
        
    def read_zeek_log(self, log_file):
        """
        Read Zeek log file - FIXED VERSION
        Zeek format has special header lines starting with #
        """
        if not os.path.exists(log_file):
            print(f"⚠️  Warning: {log_file} not found")
            return None
        
        try:
            # First, extract column names from #fields line
            column_names = None
            with open(log_file, 'r') as f:
                for line in f:
                    if line.startswith('#fields'):
                        # Extract column names
                        column_names = line.strip().split('\t')[1:]  # Skip '#fields'
                        break
            
            if column_names is None:
                print(f"✗ Could not find #fields line in {log_file}")
                return None
            
            # Now read the actual data (skip all # lines)
            df = pd.read_csv(
                log_file,
                sep='\t',
                comment='#',
                names=column_names,
                na_values=['-', '(empty)'],
                low_memory=False
            )
            
            print(f"✓ Loaded {log_file}: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"✗ Error reading {log_file}: {e}")
            return None
    
    def extract_features(self, conn_df, ssl_df=None):
        """
        Extract flow-based features from connection data
        """
        features_list = []
        
        print("\nExtracting features...")
        for idx, row in conn_df.iterrows():
            if idx % 1000 == 0:
                print(f"  Processing row {idx}/{len(conn_df)}...")
            
            try:
                feature_dict = {}
                
                # Temporal features
                feature_dict['duration'] = float(row.get('duration', 0))
                feature_dict['ts'] = float(row.get('ts', 0))
                
                # Volume features
                orig_bytes = float(row.get('orig_bytes', 0) if pd.notna(row.get('orig_bytes')) else 0)
                resp_bytes = float(row.get('resp_bytes', 0) if pd.notna(row.get('resp_bytes')) else 0)
                orig_pkts = float(row.get('orig_pkts', 0) if pd.notna(row.get('orig_pkts')) else 0)
                resp_pkts = float(row.get('resp_pkts', 0) if pd.notna(row.get('resp_pkts')) else 0)
                
                feature_dict['orig_bytes'] = orig_bytes
                feature_dict['resp_bytes'] = resp_bytes
                feature_dict['total_bytes'] = orig_bytes + resp_bytes
                feature_dict['orig_pkts'] = orig_pkts
                feature_dict['resp_pkts'] = resp_pkts
                feature_dict['total_pkts'] = orig_pkts + resp_pkts
                
                # Ratios (avoid division by zero)
                feature_dict['bytes_ratio'] = orig_bytes / (resp_bytes + 1)
                feature_dict['pkts_ratio'] = orig_pkts / (resp_pkts + 1)
                
                # Average packet sizes
                feature_dict['avg_orig_pkt_size'] = orig_bytes / (orig_pkts + 1)
                feature_dict['avg_resp_pkt_size'] = resp_bytes / (resp_pkts + 1)
                
                # Packets per second
                duration = feature_dict['duration']
                if duration > 0:
                    feature_dict['packets_per_second'] = (orig_pkts + resp_pkts) / duration
                else:
                    feature_dict['packets_per_second'] = 0
                
                # Behavioral features
                feature_dict['conn_state'] = str(row.get('conn_state', '-'))
                feature_dict['protocol'] = str(row.get('proto', '-'))
                feature_dict['service'] = str(row.get('service', '-'))
                
                # Get port from id.resp_p column
                resp_port = row.get('id.resp_p', 0)
                feature_dict['resp_port'] = int(resp_port) if pd.notna(resp_port) else 0
                
                feature_dict['history'] = str(row.get('history', '-'))
                
                # IP bytes
                orig_ip = float(row.get('orig_ip_bytes', 0) if pd.notna(row.get('orig_ip_bytes')) else 0)
                resp_ip = float(row.get('resp_ip_bytes', 0) if pd.notna(row.get('resp_ip_bytes')) else 0)
                feature_dict['orig_ip_bytes'] = orig_ip
                feature_dict['resp_ip_bytes'] = resp_ip
                
                # SSL features (empty for now, will add if SSL log available)
                feature_dict['ssl_version'] = '-'
                feature_dict['ssl_cipher'] = '-'
                feature_dict['ssl_server_name'] = '-'
                feature_dict['ssl_cert_length'] = 0
                
                # Metadata
                feature_dict['uid'] = str(row.get('uid', '-'))
                feature_dict['orig_h'] = str(row.get('id.orig_h', '-'))
                feature_dict['resp_h'] = str(row.get('id.resp_h', '-'))
                
                # Label
                feature_dict['label'] = self.label
                
                features_list.append(feature_dict)
                
            except Exception as e:
                print(f"  ⚠ Error processing row {idx}: {e}")
                continue
        
        return pd.DataFrame(features_list)
    
    def extract_all_features(self):
        """
        Main extraction pipeline
        """
        print(f"\n{'='*60}")
        print(f"Extracting features from: {self.zeek_logs_dir}")
        print(f"Label: {self.label}")
        print(f"{'='*60}\n")
        
        # Load connection log
        conn_df = self.read_zeek_log(self.conn_log)
        if conn_df is None or len(conn_df) == 0:
            print("✗ No connection data found!")
            return None
        
        # Load SSL log (optional)
        ssl_df = self.read_zeek_log(self.ssl_log)
        
        # Extract features
        features_df = self.extract_features(conn_df, ssl_df)
        
        print(f"\n✓ Feature extraction complete!")
        print(f"  Total flows: {len(features_df)}")
        print(f"  Total features: {len(features_df.columns) - 1}")  # -1 for label
        print(f"  Label distribution: {features_df['label'].value_counts().to_dict()}")
        
        return features_df
    
    def save_features(self, features_df, output_path):
        """Save extracted features to CSV"""
        if features_df is None:
            print("✗ No features to save")
            return
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        features_df.to_csv(output_path, index=False)
        
        print(f"\n✓ Features saved to: {output_path}")
        print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

def main():
    parser = argparse.ArgumentParser(
        description='Extract features from Zeek logs (FIXED VERSION)'
    )
    parser.add_argument('--input', required=True, help='Directory with Zeek logs')
    parser.add_argument('--label', required=True, choices=['normal', 'ransomware'])
    parser.add_argument('--output', default=None, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Auto-generate output path
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = '/home/datasets/processed'
        os.makedirs(output_dir, exist_ok=True)
        args.output = os.path.join(output_dir, f'features_{args.label}_{timestamp}.csv')
    
    # Extract features
    extractor = ZeekFeatureExtractor(args.input, args.label)
    features_df = extractor.extract_all_features()
    
    # Save
    if features_df is not None:
        extractor.save_features(features_df, args.output)
        
        # Show sample
        print("\n" + "="*60)
        print("SAMPLE DATA (first 5 rows)")
        print("="*60)
        print(features_df.head())
        print("\n" + "="*60)
        print("FEATURE STATISTICS")
        print("="*60)
        print(features_df.describe())

if __name__ == '__main__':
    main()
