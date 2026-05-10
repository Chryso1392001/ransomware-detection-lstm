#!/usr/bin/env python3
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import argparse

# Attention Layer
class AttentionLayer(layers.Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
    
    def build(self, input_shape):
        self.W = self.add_weight(name='attention_weight', 
                                shape=(input_shape[-1], 1),
                                initializer='random_normal',
                                trainable=True)
        self.b = self.add_weight(name='attention_bias',
                                shape=(input_shape[1], 1),
                                initializer='zeros',
                                trainable=True)
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, x):
        e = keras.backend.tanh(keras.backend.dot(x, self.W) + self.b)
        a = keras.backend.softmax(e, axis=1)
        output = x * a
        return keras.backend.sum(output, axis=1)

print("="*60)
print("ADVANCED LSTM WITH ATTENTION MECHANISM")
print("="*60)

parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--epochs', type=int, default=150)
args = parser.parse_args()

# Load data
data = np.load(args.data)
X_train = data['X_train']
y_train = data['y_train']
X_val = data['X_val']
y_val = data['y_val']
X_test = data['X_test']
y_test = data['y_test']

print(f"\n✓ Data loaded: {X_train.shape}")

# Class weights
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {i: w for i, w in enumerate(class_weights)}
print(f"✓ Class weights: {class_weight_dict}")

# Advanced Model: Bidirectional LSTM + Attention
print("\nBuilding advanced model...")

model = models.Sequential([
    # First Bidirectional LSTM
    layers.Bidirectional(
        layers.LSTM(256, return_sequences=True),
        input_shape=(X_train.shape[1], X_train.shape[2])
    ),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    
    # Second Bidirectional LSTM
    layers.Bidirectional(
        layers.LSTM(128, return_sequences=True)
    ),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    
    # Attention mechanism
    AttentionLayer(),
    
    # Dense layers
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.4),
    
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    
    layers.Dense(32, activation='relu'),
    layers.Dropout(0.2),
    
    layers.Dense(1, activation='sigmoid')
], name='advanced_ransomware_detector')

model.summary()

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(0.0003),
    loss='binary_crossentropy',
    metrics=['accuracy', 
             keras.metrics.Precision(name='precision'),
             keras.metrics.Recall(name='recall'),
             keras.metrics.AUC(name='auc')]
)

# Callbacks
early_stop = callbacks.EarlyStopping(
    monitor='val_recall',  # Focus on recall!
    patience=25,
    mode='max',
    restore_best_weights=True,
    verbose=1
)

reduce_lr = callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.3,
    patience=10,
    min_lr=1e-7,
    verbose=1
)

checkpoint = callbacks.ModelCheckpoint(
    args.output,
    monitor='val_recall',
    mode='max',
    save_best_only=True,
    verbose=1
)

# Train
print("\nTraining...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=args.epochs,
    batch_size=64,  # Larger batch for stability
    class_weight=class_weight_dict,
    callbacks=[early_stop, reduce_lr, checkpoint],
    verbose=1
)

# Evaluate
print("\n" + "="*60)
print("FINAL EVALUATION")
print("="*60)

y_pred = (model.predict(X_test, verbose=0) > 0.5).astype(int).flatten()

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print(f"\n✓ RESULTS:")
print(f"  Accuracy:  {acc*100:.2f}%")
print(f"  Precision: {prec*100:.2f}%")
print(f"  Recall:    {rec*100:.2f}%")
print(f"  F1-Score:  {f1:.4f}")
print(f"\n  TN: {tn}  FP: {fp}")
print(f"  FN: {fn}  TP: {tp}")
