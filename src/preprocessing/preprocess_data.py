#!/usr/bin/env python3
"""
preprocess_data.py
Preprocess extracted features for LSTM model training

Usage:
    python preprocess_data.py --input final_dataset.csv --output preprocessed_data.npz
"""

import pandas as pd
import numpy as np
import argparse
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.categorical_encoders = {}
        
    def load_data(self, filepath):
        """Load the dataset"""
        print(f"\n{'='*60}")
        print(f"LOADING DATA")
        print(f"{'='*60}\n")
        
        df = pd.read_csv(filepath)
        print(f"✓ Loaded dataset: {len(df)} rows, {len(df.columns)} columns")
        print(f"\nLabel distribution:")
        print(df['label'].value_counts())
        
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values"""
        print(f"\n{'='*60}")
        print(f"HANDLING MISSING VALUES")
        print(f"{'='*60}\n")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print("Missing values found:")
            print(missing[missing > 0])
            
            # Fill numeric columns with 0
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
            # Fill categorical columns with '-'
            categorical_cols = df.select_dtypes(include=['object']).columns
            df[categorical_cols] = df[categorical_cols].fillna('-')
            
            print("✓ Missing values filled")
        else:
            print("✓ No missing values found")
        
        return df
    
    def encode_categorical_features(self, df):
        """Encode categorical features"""
        print(f"\n{'='*60}")
        print(f"ENCODING CATEGORICAL FEATURES")
        print(f"{'='*60}\n")
        
        # Categorical columns to encode (excluding IPs and UIDs which we'll drop)
        categorical_cols = ['conn_state', 'protocol', 'service', 'history', 
                          'ssl_version', 'ssl_cipher', 'ssl_server_name']
        
        for col in categorical_cols:
            if col in df.columns:
                # Label encode
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.categorical_encoders[col] = le
                print(f"✓ Encoded {col}: {len(le.classes_)} unique values")
        
        return df
    
    def select_features(self, df):
        """Select relevant features for training"""
        print(f"\n{'='*60}")
        print(f"FEATURE SELECTION")
        print(f"{'='*60}\n")
        
        # Features to DROP (metadata, not useful for ML)
        drop_features = ['uid', 'orig_h', 'resp_h', 'ts']
        
        # Keep all other features
        feature_cols = [col for col in df.columns 
                       if col not in drop_features and col != 'label']
        
        print(f"Selected {len(feature_cols)} features:")
        for i, col in enumerate(feature_cols, 1):
            print(f"  {i}. {col}")
        
        return df[feature_cols], df['label']
    
    def normalize_features(self, X_train, X_val, X_test):
        """Normalize features using StandardScaler"""
        print(f"\n{'='*60}")
        print(f"NORMALIZING FEATURES")
        print(f"{'='*60}\n")
        
        # Fit scaler on training data only
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✓ Features normalized")
        print(f"  Mean: {X_train_scaled.mean():.4f}")
        print(f"  Std: {X_train_scaled.std():.4f}")
        
        return X_train_scaled, X_val_scaled, X_test_scaled
    
    def create_sequences(self, X, y, sequence_length=10):
        """
        Create sequences for LSTM
        Each sequence is a window of consecutive flows
        """
        print(f"\n{'='*60}")
        print(f"CREATING SEQUENCES FOR LSTM")
        print(f"{'='*60}\n")
        print(f"Sequence length: {sequence_length}")
        
        sequences = []
        labels = []
        
        # Create overlapping sequences
        for i in range(len(X) - sequence_length + 1):
            seq = X[i:i + sequence_length]
            # Label is based on the last flow in the sequence
            label = y[i + sequence_length - 1]
            
            sequences.append(seq)
            labels.append(label)
        
        sequences = np.array(sequences)
        labels = np.array(labels)
        
        print(f"✓ Created {len(sequences)} sequences")
        print(f"  Sequence shape: {sequences.shape}")
        print(f"  Labels shape: {labels.shape}")
        
        return sequences, labels
    
    def encode_labels(self, y_train, y_val, y_test):
        """Encode labels to binary (0=normal, 1=ransomware)"""
        print(f"\n{'='*60}")
        print(f"ENCODING LABELS")
        print(f"{'='*60}\n")
        
        # Fit on training labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_val_encoded = self.label_encoder.transform(y_val)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        print(f"Label mapping:")
        for i, label in enumerate(self.label_encoder.classes_):
            print(f"  {label} → {i}")
        
        return y_train_encoded, y_val_encoded, y_test_encoded
    
    def split_data(self, X, y, test_size=0.15, val_size=0.15):
        """Split data into train/validation/test sets"""
        print(f"\n{'='*60}")
        print(f"SPLITTING DATA")
        print(f"{'='*60}\n")
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )
        
        print(f"✓ Data split complete:")
        print(f"  Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
        print(f"  Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
        print(f"  Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def save_preprocessed_data(self, output_path, X_train, X_val, X_test, 
                               y_train, y_val, y_test, feature_names):
        """Save preprocessed data"""
        print(f"\n{'='*60}")
        print(f"SAVING PREPROCESSED DATA")
        print(f"{'='*60}\n")
        
        # Save data
        np.savez_compressed(
            output_path,
            X_train=X_train,
            X_val=X_val,
            X_test=X_test,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
            feature_names=feature_names
        )
        
        # Save scalers and encoders
        scaler_path = output_path.replace('.npz', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'categorical_encoders': self.categorical_encoders
            }, f)
        
        print(f"✓ Saved preprocessed data: {output_path}")
        print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        print(f"✓ Saved scalers: {scaler_path}")
    
    def preprocess(self, input_path, output_path, sequence_length=10):
        """Main preprocessing pipeline"""
        print(f"\n{'='*60}")
        print(f"RANSOMWARE DETECTION - DATA PREPROCESSING")
        print(f"{'='*60}")
        
        # Load data
        df = self.load_data(input_path)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df)
        
        # Select features
        X, y = self.select_features(df)
        feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(
            X.values, y.values
        )
        
        # Normalize features
        X_train, X_val, X_test = self.normalize_features(
            X_train, X_val, X_test
        )
        
        # Create sequences for LSTM
        X_train_seq, y_train_seq = self.create_sequences(
            X_train, y_train, sequence_length
        )
        X_val_seq, y_val_seq = self.create_sequences(
            X_val, y_val, sequence_length
        )
        X_test_seq, y_test_seq = self.create_sequences(
            X_test, y_test, sequence_length
        )
        
        # Encode labels
        y_train_final, y_val_final, y_test_final = self.encode_labels(
            y_train_seq, y_val_seq, y_test_seq
        )
        
        # Save
        self.save_preprocessed_data(
            output_path,
            X_train_seq, X_val_seq, X_test_seq,
            y_train_final, y_val_final, y_test_final,
            feature_names
        )
        
        print(f"\n{'='*60}")
        print(f"PREPROCESSING COMPLETE!")
        print(f"{'='*60}\n")
        
        # Print final summary
        print("FINAL DATA SUMMARY:")
        print(f"  Training sequences: {X_train_seq.shape}")
        print(f"  Validation sequences: {X_val_seq.shape}")
        print(f"  Test sequences: {X_test_seq.shape}")
        print(f"  Sequence length: {sequence_length}")
        print(f"  Number of features: {X_train_seq.shape[2]}")
        print(f"\nLabel distribution (training):")
        unique, counts = np.unique(y_train_final, return_counts=True)
        for label, count in zip(unique, counts):
            label_name = self.label_encoder.inverse_transform([label])[0]
            print(f"  {label_name}: {count} ({count/len(y_train_final)*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='Preprocess ransomware detection data')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', default='preprocessed_data.npz', help='Output file')
    parser.add_argument('--sequence-length', type=int, default=10, 
                       help='Sequence length for LSTM (default: 10)')
    
    args = parser.parse_args()
    
    # Preprocess
    preprocessor = DataPreprocessor()
    preprocessor.preprocess(args.input, args.output, args.sequence_length)
    
    print("\n✓ Ready for model training!")
    print(f"  Load data with: np.load('{args.output}')")

if __name__ == '__main__':
    main()
