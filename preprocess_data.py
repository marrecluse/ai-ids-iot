#!/usr/bin/env python3
"""
Fixed Data Preprocessing Pipeline for CICIDS2017
Handles real-world dataset issues: mixed types, inf values, missing columns
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

class CICIDS2017Preprocessor:
    """
    Preprocessing pipeline specifically for CICIDS2017 dataset.
    """
    
    def __init__(self, input_path, output_dir='data/processed'):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        self.feature_columns = None
        self.label_column = None
        
        print("="*70)
        print("CICIDS2017 DATA PREPROCESSING PIPELINE")
        print("="*70)
        print(f"Input: {self.input_path}")
        print(f"Output: {self.output_dir}")
    
    def load_data(self):
        """Load raw data from CSV with proper handling."""
        print("\n[STEP 1] Loading data...")
        
        # Read CSV with mixed types handling
        self.df = pd.read_csv(
            self.input_path,
            low_memory=False,
            encoding='utf-8',
            on_bad_lines='skip'  # Skip bad lines
        )
        
        print(f"  Loaded: {len(self.df):,} samples")
        print(f"  Columns: {len(self.df.columns)}")
        
        # Clean column names
        self.df.columns = self.df.columns.str.strip()
        
        # Find label column (try common variations)
        label_candidates = ['Label', 'label', ' Label', 'class', 'attack']
        self.label_column = None
        
        for candidate in label_candidates:
            if candidate in self.df.columns:
                self.label_column = candidate
                print(f"  Found label column: '{self.label_column}'")
                break
        
        if self.label_column is None:
            raise ValueError("Could not find label column! Available columns: " + str(list(self.df.columns)[:10]))
        
        # Show label distribution
        print(f"\n  Label distribution:")
        for label, count in self.df[self.label_column].value_counts().items():
            print(f"    {label}: {count:,} ({count/len(self.df)*100:.1f}%)")
        
        return self
    
    def clean_data(self):
        """Clean and fix data types."""
        print("\n[STEP 2] Cleaning data...")
        
        # Separate features and labels
        self.y = self.df[self.label_column].copy()
        self.X = self.df.drop(columns=[self.label_column])
        
        # Get initial feature names
        self.feature_columns = list(self.X.columns)
        print(f"  Initial features: {len(self.feature_columns)}")
        
        # Convert all columns to numeric, coerce errors to NaN
        print("  Converting to numeric...")
        for col in self.X.columns:
            self.X[col] = pd.to_numeric(self.X[col], errors='coerce')
        
        # Remove columns that are all NaN
        nan_cols = self.X.columns[self.X.isna().all()].tolist()
        if nan_cols:
            print(f"  Removing {len(nan_cols)} all-NaN columns")
            self.X = self.X.drop(columns=nan_cols)
        
        # Remove columns with >90% missing values
        missing_pct = self.X.isna().sum() / len(self.X)
        high_missing_cols = missing_pct[missing_pct > 0.9].index.tolist()
        if high_missing_cols:
            print(f"  Removing {len(high_missing_cols)} columns with >90% missing")
            self.X = self.X.drop(columns=high_missing_cols)
        
        self.feature_columns = list(self.X.columns)
        print(f"  Features after cleaning: {len(self.feature_columns)}")
        
        return self
    
    def handle_missing_values(self):
        """Handle remaining missing values."""
        print("\n[STEP 3] Handling missing values...")
        
        missing_before = self.X.isna().sum().sum()
        print(f"  Missing values before: {missing_before:,}")
        
        if missing_before > 0:
            # Fill with median for numerical columns
            self.X = self.X.fillna(self.X.median())
            
            # If any remaining NaN (all values were NaN), fill with 0
            self.X = self.X.fillna(0)
        
        missing_after = self.X.isna().sum().sum()
        print(f"  Missing values after: {missing_after:,}")
        
        return self
    
    def handle_inf_values(self):
        """Replace infinite values."""
        print("\n[STEP 4] Handling infinite values...")
        
        # Replace inf with NaN, then fill with column max/min
        inf_before = np.isinf(self.X.values).sum()
        print(f"  Infinite values before: {inf_before:,}")
        
        # Replace +inf with column max, -inf with column min
        for col in self.X.columns:
            col_data = self.X[col]
            
            # Get finite values only
            finite_vals = col_data[np.isfinite(col_data)]
            
            if len(finite_vals) > 0:
                col_max = finite_vals.max()
                col_min = finite_vals.min()
                
                # Replace infinities
                self.X[col] = col_data.replace([np.inf], col_max)
                self.X[col] = self.X[col].replace([-np.inf], col_min)
            else:
                # If no finite values, fill with 0
                self.X[col] = 0
        
        inf_after = np.isinf(self.X.values).sum()
        print(f"  Infinite values after: {inf_after:,}")
        
        return self
    
    def remove_duplicates(self):
        """Remove duplicate rows."""
        print("\n[STEP 5] Removing duplicates...")
        
        before = len(self.X)
        
        # Combine X and y for duplicate removal
        combined = pd.concat([self.X.reset_index(drop=True), self.y.reset_index(drop=True)], axis=1)
        combined = combined.drop_duplicates()
        
        self.X = combined[self.feature_columns]
        self.y = combined[self.label_column]
        
        after = len(self.X)
        
        print(f"  Removed {before - after:,} duplicates")
        print(f"  Remaining: {after:,} samples")
        
        return self
    
    def encode_labels(self):
        """Encode string labels to integers."""
        print("\n[STEP 6] Encoding labels...")
        
        # Clean label strings
        self.y = self.y.astype(str).str.strip()
        
        # Encode labels
        self.y_encoded = self.label_encoder.fit_transform(self.y)
        
        print(f"  Label mapping:")
        for i, label in enumerate(self.label_encoder.classes_):
            count = np.sum(self.y_encoded == i)
            print(f"    {label} → {i} ({count:,} samples)")
        
        return self
    
    def split_data(self, test_size=0.2, val_size=0.2, random_state=42):
        """Split data into train/val/test sets."""
        print("\n[STEP 7] Splitting data...")
        
        # First split: train+val vs test
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            self.X, self.y_encoded,
            test_size=test_size,
            random_state=random_state,
            stratify=self.y_encoded
        )
        
        # Second split: train vs val
        val_size_adjusted = val_size / (1 - test_size)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=random_state,
            stratify=y_temp
        )
        
        print(f"  Training set: {len(self.X_train):,} samples ({len(self.X_train)/len(self.X)*100:.1f}%)")
        print(f"  Validation set: {len(self.X_val):,} samples ({len(self.X_val)/len(self.X)*100:.1f}%)")
        print(f"  Test set: {len(self.X_test):,} samples ({len(self.X_test)/len(self.X)*100:.1f}%)")
        
        return self
    
    def scale_features(self):
        """Scale features using StandardScaler."""
        print("\n[STEP 8] Scaling features...")
        
        # Fit scaler on training data only
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_val_scaled = self.scaler.transform(self.X_val)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"  Features scaled successfully")
        print(f"  Feature count: {len(self.feature_columns)}")
        
        return self
    
    def save_processed_data(self):
        """Save all processed data and artifacts."""
        print("\n[STEP 9] Saving processed data...")
        
        # Save splits as CSV
        pd.DataFrame(
            self.X_train_scaled,
            columns=self.feature_columns
        ).assign(label=self.y_train).to_csv(
            self.output_dir / 'train.csv',
            index=False
        )
        
        pd.DataFrame(
            self.X_val_scaled,
            columns=self.feature_columns
        ).assign(label=self.y_val).to_csv(
            self.output_dir / 'validation.csv',
            index=False
        )
        
        pd.DataFrame(
            self.X_test_scaled,
            columns=self.feature_columns
        ).assign(label=self.y_test).to_csv(
            self.output_dir / 'test.csv',
            index=False
        )
        
        print(f"  ✅ Saved: train.csv")
        print(f"  ✅ Saved: validation.csv")
        print(f"  ✅ Saved: test.csv")
        
        # Save numpy arrays
        np.save(self.output_dir / 'X_train.npy', self.X_train_scaled)
        np.save(self.output_dir / 'X_val.npy', self.X_val_scaled)
        np.save(self.output_dir / 'X_test.npy', self.X_test_scaled)
        np.save(self.output_dir / 'y_train.npy', self.y_train)
        np.save(self.output_dir / 'y_val.npy', self.y_val)
        np.save(self.output_dir / 'y_test.npy', self.y_test)
        
        print(f"  ✅ Saved: NumPy arrays (.npy)")
        
        # Save scaler and label encoder
        joblib.dump(self.scaler, self.output_dir / 'scaler.pkl')
        joblib.dump(self.label_encoder, self.output_dir / 'label_encoder.pkl')
        
        print(f"  ✅ Saved: scaler.pkl")
        print(f"  ✅ Saved: label_encoder.pkl")
        
        # Save metadata
        metadata = {
            'n_features': len(self.feature_columns),
            'feature_names': self.feature_columns,
            'n_classes': len(self.label_encoder.classes_),
            'class_names': list(self.label_encoder.classes_),
            'n_train': len(self.X_train),
            'n_val': len(self.X_val),
            'n_test': len(self.X_test),
            'n_total': len(self.X)
        }
        
        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✅ Saved: metadata.json")
        
        return self
    
    def run_pipeline(self):
        """Run complete preprocessing pipeline."""
        try:
            self.load_data()
            self.clean_data()
            self.handle_missing_values()
            self.handle_inf_values()
            self.remove_duplicates()
            self.encode_labels()
            self.split_data()
            self.scale_features()
            self.save_processed_data()
            
            print("\n" + "="*70)
            print("✅ PREPROCESSING COMPLETE!")
            print("="*70)
            print(f"\n📁 Processed data location: {self.output_dir}")
            print(f"📊 Ready for model training!")
            print(f"\nNext step: python train_model.py")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        return self

def main():
    """
    Main preprocessing function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Preprocess CICIDS2017 network flow data')
    parser.add_argument(
        '--input',
        type=str,
        default='data/raw/cicids2017_sample.csv',
        help='Input CSV file path'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Run preprocessing
    preprocessor = CICIDS2017Preprocessor(args.input, args.output)
    preprocessor.run_pipeline()

if __name__ == '__main__':
    main()
