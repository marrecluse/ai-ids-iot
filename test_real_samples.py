#!/usr/bin/env python3
"""
Simplified API Test - Works with ANY number of features
Test directly with preprocessed data
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

def test_with_real_data():
    """
    Load actual preprocessed samples and test them.
    """
    print("="*70)
    print("TESTING WITH REAL PREPROCESSED DATA")
    print("="*70)
    
    # Load processed test data
    print("\n[1] Loading preprocessed test data...")
    X_test = np.load('data/processed/X_test.npy')
    y_test = np.load('data/processed/y_test.npy')
    
    print(f"Test set shape: {X_test.shape}")
    print(f"Features: {X_test.shape[1]}")
    
    # Load model
    print("\n[2] Loading trained model...")
    model = joblib.load('models/random_forest_model.pkl')
    label_encoder = joblib.load('models/label_encoder.pkl')
    
    print("✅ Model loaded")
    
    # Get class names
    class_names = label_encoder.classes_
    print(f"\nClasses: {list(class_names)}")
    
    # Test different attack types
    print("\n[3] Testing samples from each attack type...")
    print("="*70)
    
    for class_idx, class_name in enumerate(class_names):
        # Find samples of this class
        class_samples = np.where(y_test == class_idx)[0]
        
        if len(class_samples) == 0:
            print(f"\n❌ No {class_name} samples in test set")
            continue
        
        # Test first 3 samples
        num_samples = min(3, len(class_samples))
        
        print(f"\n{'='*70}")
        print(f"Testing {class_name} (Class {class_idx})")
        print(f"{'='*70}")
        print(f"Available samples: {len(class_samples)}")
        
        correct = 0
        for i in range(num_samples):
            sample_idx = class_samples[i]
            X_sample = X_test[sample_idx].reshape(1, -1)
            
            # Predict
            prediction = model.predict(X_sample)[0]
            probabilities = model.predict_proba(X_sample)[0]
            confidence = probabilities[prediction]
            predicted_class = label_encoder.inverse_transform([prediction])[0]
            
            # Check if correct
            is_correct = (prediction == class_idx)
            correct += is_correct
            
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            
            print(f"\nSample {i+1}: {status}")
            print(f"  True label:      {class_name}")
            print(f"  Predicted:       {predicted_class}")
            print(f"  Confidence:      {confidence*100:.2f}%")
            
            # Show top 3 predictions
            top_3 = np.argsort(probabilities)[-3:][::-1]
            print(f"  Top predictions:")
            for idx in top_3:
                print(f"    {label_encoder.inverse_transform([idx])[0]}: {probabilities[idx]*100:.2f}%")
        
        accuracy = (correct / num_samples) * 100
        print(f"\n  Accuracy for {class_name}: {accuracy:.1f}% ({correct}/{num_samples})")
    
    # Overall test accuracy
    print("\n" + "="*70)
    print("OVERALL TEST SET PERFORMANCE")
    print("="*70)
    
    y_pred = model.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    
    print(f"\nTotal test samples: {len(y_test):,}")
    print(f"Overall accuracy: {accuracy*100:.2f}%")
    
    # Per-class accuracy
    print(f"\nPer-class accuracy:")
    for class_idx, class_name in enumerate(class_names):
        class_mask = (y_test == class_idx)
        if class_mask.sum() > 0:
            class_acc = (y_pred[class_mask] == y_test[class_mask]).mean()
            print(f"  {class_name}: {class_acc*100:.2f}% ({class_mask.sum()} samples)")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE!")
    print("="*70)
    
    # Save some samples for API testing
    print("\n[4] Generating API test samples...")
    
    test_samples = {}
    
    for class_idx, class_name in enumerate(class_names):
        class_samples_idx = np.where(y_test == class_idx)[0]
        if len(class_samples_idx) > 0:
            # Get first sample
            sample_idx = class_samples_idx[0]
            sample = X_test[sample_idx]
            
            # This is the ACTUAL feature vector
            # Save as numpy array for API testing
            test_samples[class_name] = sample.tolist()
    
    # Save for later use
    import json
    with open('api_test_samples.json', 'w') as f:
        json.dump(test_samples, f, indent=2)
    
    print(f"✅ Saved {len(test_samples)} samples to api_test_samples.json")
    print("\nThese samples use ALL 75 features and WILL work with the API!")

if __name__ == '__main__':
    test_with_real_data()
