#!/usr/bin/env python3
"""
FIXED ML Model Training Script
Trains Random Forest and SVM on preprocessed CICIDS2017 data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.model_selection import GridSearchCV
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

class IDSModelTrainer:
    """
    Train and evaluate ML models for intrusion detection.
    """
    
    def __init__(self, data_dir='data/processed', output_dir='models'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("AI-ASSISTED IDS FOR IOT NETWORKS")
        print("Machine Learning Model Training Pipeline")
        print("="*70)
        print(f"[INFO] Dataset: {self.data_dir}")
        print(f"[INFO] Output directory: {self.output_dir}")
        
        self.models = {}
        self.results = {}
    
    def load_and_preprocess_data(self):
        """Load preprocessed data from NumPy files."""
        print("\n[STEP 1] Loading and preprocessing data...")
        
        try:
            # Load training data
            self.X_train = np.load(self.data_dir / 'X_train.npy')
            self.y_train = np.load(self.data_dir / 'y_train.npy')
            
            # Load validation data
            self.X_val = np.load(self.data_dir / 'X_val.npy')
            self.y_val = np.load(self.data_dir / 'y_val.npy')
            
            # Load test data
            self.X_test = np.load(self.data_dir / 'X_test.npy')
            self.y_test = np.load(self.data_dir / 'y_test.npy')
            
            # Load metadata
            with open(self.data_dir / 'metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            print(f"  ✅ Training set: {self.X_train.shape}")
            print(f"  ✅ Validation set: {self.X_val.shape}")
            print(f"  ✅ Test set: {self.X_test.shape}")
            print(f"  ✅ Number of features: {self.metadata['n_features']}")
            print(f"  ✅ Number of classes: {self.metadata['n_classes']}")
            print(f"  ✅ Classes: {self.metadata['class_names']}")
            
            # Check class distribution
            print("\n  Class distribution in training set:")
            unique, counts = np.unique(self.y_train, return_counts=True)
            for cls, count in zip(unique, counts):
                class_name = self.metadata['class_names'][cls]
                print(f"    {class_name} ({cls}): {count:,} ({count/len(self.y_train)*100:.1f}%)")
            
        except FileNotFoundError as e:
            print(f"\n  ❌ ERROR: Could not find preprocessed data files!")
            print(f"  Missing file: {e.filename}")
            print(f"\n  Please run preprocessing first:")
            print(f"  python preprocess_data.py --input data/raw/cicids2017_sample.csv")
            raise
        
        return self
    
    def apply_smote(self):
        """Apply SMOTE to handle class imbalance."""
        print("\n[STEP 2] Applying SMOTE for class balancing...")
        
        print(f"  Before SMOTE: {self.X_train.shape}")
        
        # Apply SMOTE
        smote = SMOTE(random_state=42, k_neighbors=3)
        self.X_train_balanced, self.y_train_balanced = smote.fit_resample(
            self.X_train, self.y_train
        )
        
        print(f"  After SMOTE: {self.X_train_balanced.shape}")
        
        # Show new distribution
        print("\n  Balanced class distribution:")
        unique, counts = np.unique(self.y_train_balanced, return_counts=True)
        for cls, count in zip(unique, counts):
            class_name = self.metadata['class_names'][cls]
            print(f"    {class_name} ({cls}): {count:,} ({count/len(self.y_train_balanced)*100:.1f}%)")
        
        return self
    
    def train_random_forest(self):
        """Train Random Forest classifier with GridSearchCV."""
        print("\n[STEP 3] Training Random Forest...")
        print("  Running GridSearchCV (this may take 5-10 minutes)...")
        
        # Define parameter grid (reduced for faster training)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [20, 30],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }
        
        # Initialize Random Forest
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        # GridSearchCV
        grid_search = GridSearchCV(
            rf,
            param_grid,
            cv=3,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        # Fit on balanced training data
        grid_search.fit(self.X_train_balanced, self.y_train_balanced)
        
        # Best model
        self.models['random_forest'] = grid_search.best_estimator_
        
        print(f"\n  ✅ Best parameters: {grid_search.best_params_}")
        print(f"  ✅ Best CV score: {grid_search.best_score_:.4f}")
        
        return self
    
    def train_svm(self):
        """Train SVM classifier with GridSearchCV."""
        print("\n[STEP 4] Training SVM...")
        print("  Running GridSearchCV (this may take 5-10 minutes)...")
        
        # Define parameter grid (reduced for faster training)
        param_grid = {
            'C': [1, 10],
            'gamma': ['scale', 0.01],
            'kernel': ['rbf']
        }
        
        # Initialize SVM
        svm = SVC(random_state=42, probability=True)
        
        # GridSearchCV
        grid_search = GridSearchCV(
            svm,
            param_grid,
            cv=3,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        # Fit on balanced training data
        grid_search.fit(self.X_train_balanced, self.y_train_balanced)
        
        # Best model
        self.models['svm'] = grid_search.best_estimator_
        
        print(f"\n  ✅ Best parameters: {grid_search.best_params_}")
        print(f"  ✅ Best CV score: {grid_search.best_score_:.4f}")
        
        return self
    
    def evaluate_model(self, model_name, model):
        """Evaluate a single model."""
        print(f"\n[EVALUATION] {model_name.upper()}")
        
        # Predict on test set
        y_pred = model.predict(self.X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(self.y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(self.y_test, y_pred, average='weighted', zero_division=0)
        
        # Store results
        self.results[model_name] = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
        
        print(f"  Accuracy:  {accuracy*100:.2f}%")
        print(f"  Precision: {precision*100:.2f}%")
        print(f"  Recall:    {recall*100:.2f}%")
        print(f"  F1-Score:  {f1*100:.2f}%")
        
        # Classification report
        print(f"\n  Classification Report:")
        print(classification_report(
            self.y_test, y_pred,
            target_names=self.metadata['class_names'],
            zero_division=0
        ))
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        self.plot_confusion_matrix(cm, model_name)
        
        return self
    
    def plot_confusion_matrix(self, cm, model_name):
        """Plot and save confusion matrix."""
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.metadata['class_names'],
            yticklabels=self.metadata['class_names']
        )
        plt.title(f'Confusion Matrix - {model_name.upper()}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        output_path = self.output_dir / f'confusion_matrix_{model_name}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Confusion matrix saved: {output_path}")
    
    def evaluate_baseline(self):
        """Simple rule-based baseline for comparison."""
        print("\n[BASELINE] Rule-Based Detector")
        
        # Simple rules (this won't work well with scaled data, but for comparison)
        # Just predict most common class (BENIGN) for everything
        y_pred_baseline = np.zeros_like(self.y_test)
        
        accuracy = accuracy_score(self.y_test, y_pred_baseline)
        
        self.results['baseline'] = {
            'accuracy': float(accuracy),
            'description': 'Always predicts BENIGN class'
        }
        
        print(f"  Accuracy: {accuracy*100:.2f}%")
        print(f"  (Always predicts most common class)")
        
        return self
    
    def save_models(self):
        """Save trained models and results."""
        print("\n[STEP 5] Saving models...")
        
        # Save Random Forest
        joblib.dump(
            self.models['random_forest'],
            self.output_dir / 'random_forest_model.pkl'
        )
        print(f"  ✅ Saved: random_forest_model.pkl")
        
        # Save SVM
        joblib.dump(
            self.models['svm'],
            self.output_dir / 'svm_model.pkl'
        )
        print(f"  ✅ Saved: svm_model.pkl")
        
        # Copy scaler and label encoder to models directory
        import shutil
        shutil.copy(
            self.data_dir / 'scaler.pkl',
            self.output_dir / 'scaler.pkl'
        )
        print(f"  ✅ Copied: scaler.pkl")
        
        shutil.copy(
            self.data_dir / 'label_encoder.pkl',
            self.output_dir / 'label_encoder.pkl'
        )
        print(f"  ✅ Copied: label_encoder.pkl")
        
        # Save results
        with open(self.output_dir / 'training_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"  ✅ Saved: training_results.json")
        
        return self
    
    def print_summary(self):
        """Print final summary."""
        print("\n" + "="*70)
        print("TRAINING COMPLETE - RESULTS SUMMARY")
        print("="*70)
        
        print("\n📊 Model Performance Comparison:\n")
        print(f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
        print("-" * 70)
        
        for model_name in ['random_forest', 'svm', 'baseline']:
            if model_name in self.results:
                r = self.results[model_name]
                acc = r['accuracy'] * 100
                
                if model_name == 'baseline':
                    print(f"{model_name.upper():<20} {acc:>10.2f}%  {'N/A':<12} {'N/A':<12} {'N/A':<12}")
                else:
                    prec = r['precision'] * 100
                    rec = r['recall'] * 100
                    f1 = r['f1_score'] * 100
                    print(f"{model_name.upper():<20} {acc:>10.2f}%  {prec:>10.2f}%  {rec:>10.2f}%  {f1:>10.2f}%")
        
        print("\n" + "="*70)
        print("✅ All models saved to:", self.output_dir)
        print("✅ Confusion matrices saved as PNG files")
        print("✅ Ready for deployment!")
        print("\n📝 Next step: python main_api.py")
        print("="*70)
    
    def run_training_pipeline(self):
        """Run complete training pipeline."""
        try:
            self.load_and_preprocess_data()
            self.apply_smote()
            self.train_random_forest()
            self.evaluate_model('random_forest', self.models['random_forest'])
            self.train_svm()
            self.evaluate_model('svm', self.models['svm'])
            self.evaluate_baseline()
            self.save_models()
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ ERROR during training: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        return self

def main():
    """
    Main training function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Train IDS ML models')
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Directory containing preprocessed data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Directory to save trained models'
    )
    
    args = parser.parse_args()
    
    # Run training
    trainer = IDSModelTrainer(args.data_dir, args.output_dir)
    trainer.run_training_pipeline()

if __name__ == '__main__':
    main()
