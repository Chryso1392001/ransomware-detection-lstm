#!/usr/bin/env python3
"""
train_model_original.py
Train original LSTM model (non-bidirectional) for ransomware detection

This is the simpler, better-performing model with:
- Standard LSTM (not bidirectional)
- Default 0.5 threshold
- 129K parameters
- Better recall (94.08%)

Usage:
    python train_model_original.py --data preprocessed_data.npz --output model.keras
"""

import numpy as np
import argparse
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, confusion_matrix, classification_report, 
                            roc_curve, auc)
import seaborn as sns

# TensorFlow imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# Enable XLA for performance
tf.config.optimizer.set_jit(True)

class RansomwareDetector:
    def __init__(self, sequence_length, n_features):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.history = None
        
    def build_base_lstm(self):
        """Build base LSTM model (standard, not bidirectional)"""
        print(f"\n{'='*60}")
        print("BUILDING BASE LSTM MODEL")
        print(f"{'='*60}\n")
        
        model = keras.Sequential([
            # First LSTM layer
            layers.LSTM(128, return_sequences=True, 
                       input_shape=(self.sequence_length, self.n_features),
                       name='lstm_1'),
            layers.Dropout(0.3, name='dropout_1'),
            
            # Second LSTM layer
            layers.LSTM(64, return_sequences=False, name='lstm_2'),
            layers.Dropout(0.3, name='dropout_2'),
            
            # Dense layer
            layers.Dense(32, activation='relu', name='dense_1'),
            layers.Dropout(0.2, name='dropout_3')
        ], name='base_model')
        
        print("Base LSTM architecture:")
        model.summary()
        
        return model
    
    def build_transfer_learning_model(self, freeze_base=False):
        """Build complete model with transfer learning"""
        print(f"\n{'='*60}")
        print("BUILDING TRANSFER LEARNING MODEL")
        print(f"{'='*60}\n")
        
        # Get base model
        base_model = self.build_base_lstm()
        
        # Freeze base layers if specified
        if freeze_base:
            for layer in base_model.layers:
                layer.trainable = False
            print("✓ Base model layers frozen")
        
        # Build complete model
        self.model = keras.Sequential([
            base_model,
            layers.Dense(16, activation='relu', name='task_dense'),
            layers.Dropout(0.2, name='task_dropout'),
            layers.Dense(1, activation='sigmoid', name='output')
        ], name='ransomware_detector')
        
        print("\nComplete model architecture:")
        self.model.summary()
        
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model"""
        print(f"\n{'='*60}")
        print("COMPILING MODEL")
        print(f"{'='*60}\n")
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        )
        
        print(f"✓ Model compiled")
        print(f"  Optimizer: Adam (lr={learning_rate})")
        print(f"  Loss: binary_crossentropy")
        print(f"  Metrics: accuracy, precision, recall, AUC")
    
    def train(self, X_train, y_train, X_val, y_val, 
              epochs=50, batch_size=32, model_path='best_model.keras'):
        """Train the model"""
        print(f"\n{'='*60}")
        print("TRAINING MODEL")
        print(f"{'='*60}\n")
        
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print()
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                model_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            )
        ]
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        print(f"\n✓ Training complete!")
        print(f"  Best model saved to: {model_path}")
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        print(f"\n{'='*60}")
        print("EVALUATING MODEL")
        print(f"{'='*60}\n")
        
        # Get predictions
        y_pred_prob = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn)
        
        # ROC AUC
        fpr_roc, tpr_roc, _ = roc_curve(y_test, y_pred_prob)
        roc_auc = auc(fpr_roc, tpr_roc)
        
        # Print results
        print("PERFORMANCE METRICS:")
        print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
        print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  FPR:       {fpr:.4f} ({fpr*100:.2f}%)")
        print(f"  AUC-ROC:   {roc_auc:.4f}")
        
        print(f"\nCONFUSION MATRIX:")
        print(f"  TN: {tn}  FP: {fp}")
        print(f"  FN: {fn}  TP: {tp}")
        
        print(f"\nCLASSIFICATION REPORT:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Normal', 'Ransomware']))
        
        # Check if targets met
        print(f"\n{'='*60}")
        print("TARGET VALIDATION")
        print(f"{'='*60}\n")
        
        targets = {
            'Accuracy ≥ 90%': accuracy >= 0.90,
            'Precision ≥ 85%': precision >= 0.85,
            'Recall ≥ 85%': recall >= 0.85,
            'F1-Score ≥ 0.85': f1 >= 0.85,
            'FPR < 5%': fpr < 0.05
        }
        
        for target, met in targets.items():
            status = "✓ MET" if met else "✗ NOT MET"
            print(f"  {target}: {status}")
        
        all_met = all(targets.values())
        if all_met:
            print(f"\n🎉 ALL TARGETS MET! Model is production-ready!")
        else:
            print(f"\n⚠️  Some targets not met.")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'fpr': fpr,
            'auc': roc_auc,
            'confusion_matrix': cm
        }
    
    def plot_training_history(self, output_dir='./'):
        """Plot training history"""
        print(f"\n{'='*60}")
        print("GENERATING PLOTS")
        print(f"{'='*60}\n")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Loss
        axes[0].plot(self.history.history['loss'], label='Training Loss', linewidth=2)
        axes[0].plot(self.history.history['val_loss'], label='Validation Loss', linewidth=2)
        axes[0].set_xlabel('Epoch', fontsize=12)
        axes[0].set_ylabel('Loss', fontsize=12)
        axes[0].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Accuracy
        axes[1].plot(self.history.history['accuracy'], label='Training Accuracy', linewidth=2)
        axes[1].plot(self.history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
        axes[1].set_xlabel('Epoch', fontsize=12)
        axes[1].set_ylabel('Accuracy', fontsize=12)
        axes[1].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = os.path.join(output_dir, 'training_history.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved training history: {plot_path}")
        plt.close()
    
    def plot_confusion_matrix(self, cm, output_dir='./'):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Normal', 'Ransomware'],
                   yticklabels=['Normal', 'Ransomware'],
                   cbar_kws={'label': 'Count'},
                   annot_kws={'size': 14})
        plt.xlabel('Predicted', fontsize=12, fontweight='bold')
        plt.ylabel('Actual', fontsize=12, fontweight='bold')
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        
        plot_path = os.path.join(output_dir, 'confusion_matrix.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved confusion matrix: {plot_path}")
        plt.close()
    
    def plot_roc_curve(self, X_test, y_test, output_dir='./'):
        """Plot ROC curve"""
        y_pred_prob = self.model.predict(X_test, verbose=0)
        fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
        plt.ylabel('True Positive Rate (Recall)', fontsize=12, fontweight='bold')
        plt.title('ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plot_path = os.path.join(output_dir, 'roc_curve.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved ROC curve: {plot_path}")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Train original LSTM model')
    parser.add_argument('--data', required=True, help='Preprocessed data file (.npz)')
    parser.add_argument('--output', default='ransomware_detector.keras', 
                       help='Output model file')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("RANSOMWARE DETECTION - ORIGINAL MODEL TRAINING")
    print(f"{'='*60}\n")
    
    # Load data
    print("Loading preprocessed data...")
    data = np.load(args.data)
    
    X_train = data['X_train']
    X_val = data['X_val']
    X_test = data['X_test']
    y_train = data['y_train']
    y_val = data['y_val']
    y_test = data['y_test']
    
    print(f"✓ Data loaded")
    print(f"  Training: {X_train.shape}")
    print(f"  Validation: {X_val.shape}")
    print(f"  Test: {X_test.shape}")
    
    # Get dimensions
    sequence_length = X_train.shape[1]
    n_features = X_train.shape[2]
    
    # Build model
    detector = RansomwareDetector(sequence_length, n_features)
    detector.build_transfer_learning_model(freeze_base=False)
    detector.compile_model(learning_rate=args.learning_rate)
    
    # Train
    detector.train(
        X_train, y_train,
        X_val, y_val,
        epochs=args.epochs,
        batch_size=args.batch_size,
        model_path=args.output
    )
    
    # Plot training history
    output_dir = os.path.dirname(args.output) or './'
    detector.plot_training_history(output_dir)
    
    # Evaluate
    metrics = detector.evaluate(X_test, y_test)
    
    # Plot confusion matrix and ROC curve
    detector.plot_confusion_matrix(metrics['confusion_matrix'], output_dir)
    detector.plot_roc_curve(X_test, y_test, output_dir)
    
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE!")
    print(f"{'='*60}\n")
    print(f"Model saved to: {args.output}")
    print(f"Plots saved to: {output_dir}")
    print(f"\nFinal Test Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"Final Test Recall: {metrics['recall']*100:.2f}%")

if __name__ == '__main__':
    main()
