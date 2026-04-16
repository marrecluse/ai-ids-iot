#!/usr/bin/env python3
"""
Extract and prepare CICIDS2017 dataset
This script processes the downloaded CICIDS2017 data
"""

import pandas as pd
import zipfile
from pathlib import Path
import os

def extract_cicids2017(data_dir='data/raw/CICIDS2017'):
    """
    Extract CICIDS2017 ZIP files and combine CSVs.
    """
    print("="*70)
    print("EXTRACTING CICIDS2017 DATASET")
    print("="*70)
    
    data_path = Path(data_dir)
    
    # Find ZIP files
    zip_files = list(data_path.glob('*.zip'))
    print(f"\nFound {len(zip_files)} ZIP files:")
    for zf in zip_files:
        print(f"  - {zf.name}")
    
    # Extract all ZIPs
    print("\nExtracting ZIP files...")
    for zip_file in zip_files:
        print(f"  Extracting {zip_file.name}...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(data_path)
    
    print("✅ Extraction complete!")
    
    # Find all CSV files
    csv_files = list(data_path.glob('**/*.csv'))
    print(f"\n📊 Found {len(csv_files)} CSV files:")
    for csv in csv_files:
        print(f"  - {csv.name}")
    
    return csv_files

def combine_cicids2017_csvs(csv_files, output_path='data/raw/cicids2017_combined.csv'):
    """
    Combine all CICIDS2017 CSV files into one.
    """
    print("\n" + "="*70)
    print("COMBINING CSV FILES")
    print("="*70)
    
    all_data = []
    total_rows = 0
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\n[{i}/{len(csv_files)}] Reading {csv_file.name}...")
        try:
            # Read CSV with flexible encoding
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
            
            # Handle potential encoding issues
            if df is None or df.empty:
                df = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)
            
            # Clean column names (remove spaces, special chars)
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
            
            rows = len(df)
            total_rows += rows
            print(f"  Loaded: {rows:,} rows, {len(df.columns)} columns")
            
            all_data.append(df)
            
        except Exception as e:
            print(f"  ⚠️  Error reading {csv_file.name}: {e}")
            continue
    
    # Combine all dataframes
    print(f"\n🔄 Combining {len(all_data)} dataframes...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n✅ Combined dataset:")
    print(f"  Total rows: {len(combined_df):,}")
    print(f"  Total columns: {len(combined_df.columns)}")
    
    # Check for label column (might be named differently)
    label_candidates = ['label', 'Label', ' Label', 'class', 'attack']
    label_col = None
    for candidate in label_candidates:
        if candidate in combined_df.columns:
            label_col = candidate
            break
    
    if label_col:
        print(f"\n📋 Label distribution:")
        print(combined_df[label_col].value_counts())
    else:
        print("\n⚠️  Warning: Could not find label column")
        print(f"Available columns: {list(combined_df.columns)[:10]}...")
    
    # Save combined dataset
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving combined dataset to: {output_path}")
    combined_df.to_csv(output_path, index=False)
    
    print(f"✅ Saved: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return combined_df, output_path

def sample_dataset(input_path, sample_size=100000, output_path='data/raw/cicids2017_sample.csv'):
    """
    Create a smaller sample for faster development/testing.
    """
    print("\n" + "="*70)
    print("CREATING SAMPLE DATASET")
    print("="*70)
    
    print(f"\nReading full dataset from: {input_path}")
    df = pd.read_csv(input_path, low_memory=False)
    
    print(f"Original size: {len(df):,} rows")
    
    # Stratified sample to preserve label distribution
    if 'label' in df.columns:
        sample = df.groupby('label', group_keys=False).apply(
            lambda x: x.sample(min(len(x), sample_size // len(df['label'].unique())))
        ).reset_index(drop=True)
    else:
        sample = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    print(f"Sample size: {len(sample):,} rows")
    
    if 'label' in sample.columns:
        print(f"\nSample label distribution:")
        print(sample['label'].value_counts())
    
    # Save sample
    output_path = Path(output_path)
    sample.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved sample to: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return sample

def main():
    """
    Main function to prepare CICIDS2017 dataset.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare CICIDS2017 dataset')
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/raw/CICIDS2017',
        help='Directory containing CICIDS2017 ZIP files'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create a sample dataset for testing'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=100000,
        help='Sample size (default: 100000)'
    )
    
    args = parser.parse_args()
    
    # Step 1: Extract ZIPs
    csv_files = extract_cicids2017(args.data_dir)
    
    if not csv_files:
        print("\n❌ No CSV files found! Make sure ZIP files are extracted.")
        return
    
    # Step 2: Combine CSVs
    combined_df, combined_path = combine_cicids2017_csvs(csv_files)
    
    # Step 3: Create sample if requested
    if args.sample:
        sample_dataset(combined_path, sample_size=args.sample_size)
    
    print("\n" + "="*70)
    print("✅ CICIDS2017 DATASET PREPARATION COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. python preprocess_data.py --input data/raw/cicids2017_combined.csv")
    print("   OR (for faster testing):")
    print("1. python preprocess_data.py --input data/raw/cicids2017_sample.csv")
    print("2. python train_model.py")
    print("3. python main_api.py")

if __name__ == '__main__':
    main()
