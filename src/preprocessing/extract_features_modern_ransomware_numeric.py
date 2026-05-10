#!/usr/bin/env python3
"""
extract_features_modern_ransomware_numeric.py
Extract features from modern_ransomware_combined.log
Label is numeric: 1 (ransomware)
"""

import pandas as pd
import os
from datetime import datetime

class ZeekFeatureExtractor:
    def __init__(self, log_file):
        self.conn_log = log_file
        self.label = 1  # numeric label for ransomware

    def read_zeek_log(self, log_file):
        if not os.path.exists(log_file):
            print(f"⚠ Warning: {log_file} not found")
            return None
        try:
            column_names = None
            with open(log_file, 'r') as f:
                for line in f:
                    if line.startswith('#fields'):
                        column_names = line.strip().split('\t')[1:]
                        break
            if column_names is None:
                print(f"✗ Could not find #fields line in {log_file}")
                return None
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

    def extract_features(self, conn_df):
        features_list = []
        print("\nExtracting features...")
        for idx, row in conn_df.iterrows():
            if idx % 1000 == 0:
                print(f"  Processing row {idx}/{len(conn_df)}...")
            try:
                f = {}
                f['duration'] = float(row.get('duration', 0))
                f['ts'] = float(row.get('ts', 0))
                orig_bytes = float(row.get('orig_bytes', 0) if pd.notna(row.get('orig_bytes')) else 0)
                resp_bytes = float(row.get('resp_bytes', 0) if pd.notna(row.get('resp_bytes')) else 0)
                orig_pkts = float(row.get('orig_pkts', 0) if pd.notna(row.get('orig_pkts')) else 0)
                resp_pkts = float(row.get('resp_pkts', 0) if pd.notna(row.get('resp_pkts')) else 0)
                f['orig_bytes'] = orig_bytes
                f['resp_bytes'] = resp_bytes
                f['total_bytes'] = orig_bytes + resp_bytes
                f['orig_pkts'] = orig_pkts
                f['resp_pkts'] = resp_pkts
                f['total_pkts'] = orig_pkts + resp_pkts
                f['bytes_ratio'] = orig_bytes / (resp_bytes + 1)
                f['pkts_ratio'] = orig_pkts / (resp_pkts + 1)
                f['avg_orig_pkt_size'] = orig_bytes / (orig_pkts + 1)
                f['avg_resp_pkt_size'] = resp_bytes / (resp_pkts + 1)
                duration = f['duration']
                f['packets_per_second'] = (orig_pkts + resp_pkts) / duration if duration > 0 else 0
                f['conn_state'] = str(row.get('conn_state', '-'))
                f['protocol'] = str(row.get('proto', '-'))
                f['service'] = str(row.get('service', '-'))
                resp_port = row.get('id.resp_p', 0)
                f['resp_port'] = int(resp_port) if pd.notna(resp_port) else 0
                f['history'] = str(row.get('history', '-'))
                orig_ip = float(row.get('orig_ip_bytes', 0) if pd.notna(row.get('orig_ip_bytes')) else 0)
                resp_ip = float(row.get('resp_ip_bytes', 0) if pd.notna(row.get('resp_ip_bytes')) else 0)
                f['orig_ip_bytes'] = orig_ip
                f['resp_ip_bytes'] = resp_ip
                f['ssl_version'] = '-'
                f['ssl_cipher'] = '-'
                f['ssl_server_name'] = '-'
                f['ssl_cert_length'] = 0
                f['uid'] = str(row.get('uid', '-'))
                f['orig_h'] = str(row.get('id.orig_h', '-'))
                f['resp_h'] = str(row.get('id.resp_h', '-'))
                f['label'] = self.label
                features_list.append(f)
            except Exception as e:
                print(f"  ⚠ Error processing row {idx}: {e}")
        return pd.DataFrame(features_list)

    def extract_all_features(self):
        print(f"\n{'='*60}")
        print(f"Extracting features from: {self.conn_log}")
        print(f"Label: {self.label}")
        print(f"{'='*60}\n")
        conn_df = self.read_zeek_log(self.conn_log)
        if conn_df is None or len(conn_df) == 0:
            print("✗ No connection data found!")
            return None
        features_df = self.extract_features(conn_df)
        print(f"\n✓ Feature extraction complete!")
        print(f"  Total flows: {len(features_df)}")
        print(f"  Total features: {len(features_df.columns) - 1}")
        print(f"  Label distribution: {features_df['label'].value_counts().to_dict()}")
        return features_df

    def save_features(self, features_df, output_path):
        if features_df is None:
            print("✗ No features to save")
            return
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        features_df.to_csv(output_path, index=False)
        print(f"\n✓ Features saved to: {output_path}")
        print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")


def main():
    log_file = '/home/datasets/public/modern_ransomware_combined.log'
    output_dir = '/home/datasets/processed'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'features_label1_{timestamp}.csv')

    extractor = ZeekFeatureExtractor(log_file)
    features_df = extractor.extract_all_features()
    extractor.save_features(features_df, output_path)

    if features_df is not None:
        print("\nSAMPLE DATA (first 5 rows):")
        print(features_df.head())


if __name__ == '__main__':
    main()
