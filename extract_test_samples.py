#!/usr/bin/env python3
"""
Extract Real Attack Samples from CICIDS2017
Use these samples to test the API with actual malicious traffic
"""

import pandas as pd
import json
from pathlib import Path

def extract_attack_samples(
    input_path='data/raw/cicids2017_sample.csv',
    output_path='test_samples.json',
    samples_per_class=3
):
    """
    Extract real attack samples from CICIDS2017 dataset.
    """
    print("="*70)
    print("EXTRACTING REAL ATTACK SAMPLES FROM CICIDS2017")
    print("="*70)
    
    # Load data
    print(f"\nLoading data from: {input_path}")
    df = pd.read_csv(input_path, low_memory=False)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Find label column
    label_col = None
    for candidate in ['Label', 'label', ' Label']:
        if candidate in df.columns:
            label_col = candidate
            break
    
    if not label_col:
        print("❌ Could not find label column!")
        return
    
    print(f"Found label column: '{label_col}'")
    
    # Show available attack types
    print(f"\nAvailable attack types:")
    label_counts = df[label_col].value_counts()
    for label, count in label_counts.items():
        print(f"  {label}: {count:,} samples")
    
    # Features we need for API
    required_features = [
        'flow_duration',
        'total_fwd_packets', 
        'total_bwd_packets',
        'flow_bytes_per_sec',
        'flow_packets_per_sec',
        'flow_iat_mean',
        'flow_iat_std',
        'fwd_iat_total',
        'bwd_iat_total'
    ]
    
    # Extract samples for each attack type
    samples = {}
    
    for attack_type in label_counts.index:
        if attack_type == 'BENIGN':
            continue  # Skip benign for now
        
        print(f"\nExtracting {samples_per_class} samples of: {attack_type}")
        
        # Get samples of this attack type
        attack_df = df[df[label_col] == attack_type].head(samples_per_class)
        
        samples[attack_type] = []
        
        for idx, row in attack_df.iterrows():
            sample = {}
            
            # Try to extract each required feature
            for feature in required_features:
                # Try different column name variations
                found = False
                
                for col in df.columns:
                    col_clean = col.strip().lower().replace(' ', '_').replace('__', '_')
                    feature_clean = feature.lower().replace(' ', '_')
                    
                    if col_clean == feature_clean or feature_clean in col_clean:
                        value = row[col]
                        
                        # Convert to float, handle errors
                        try:
                            sample[feature] = float(value)
                            found = True
                            break
                        except:
                            sample[feature] = 0.0
                            found = True
                            break
                
                if not found:
                    sample[feature] = 0.0
            
            samples[attack_type].append(sample)
            print(f"  Sample {len(samples[attack_type])}: {sample['flow_packets_per_sec']:.2f} packets/sec")
    
    # Also extract BENIGN samples
    print(f"\nExtracting {samples_per_class} BENIGN samples")
    benign_df = df[df[label_col] == 'BENIGN'].head(samples_per_class)
    samples['BENIGN'] = []
    
    for idx, row in benign_df.iterrows():
        sample = {}
        for feature in required_features:
            found = False
            for col in df.columns:
                col_clean = col.strip().lower().replace(' ', '_').replace('__', '_')
                feature_clean = feature.lower().replace(' ', '_')
                if col_clean == feature_clean or feature_clean in col_clean:
                    try:
                        sample[feature] = float(row[col])
                        found = True
                        break
                    except:
                        sample[feature] = 0.0
                        found = True
                        break
            if not found:
                sample[feature] = 0.0
        samples['BENIGN'].append(sample)
    
    # Save to JSON
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        json.dump(samples, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ SAMPLES EXTRACTED!")
    print(f"{'='*70}")
    print(f"\nSaved to: {output_path}")
    print(f"Total samples: {sum(len(v) for v in samples.values())}")
    print(f"\nAttack types extracted:")
    for attack_type, attack_samples in samples.items():
        print(f"  {attack_type}: {len(attack_samples)} samples")
    
    return samples

def print_curl_command(attack_type, sample):
    """Print a curl command to test this sample."""
    print(f"\n# Test {attack_type} attack:")
    print(f"curl -X POST http://localhost:8000/api/detect \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{")
    
    for i, (key, value) in enumerate(sample.items()):
        comma = "," if i < len(sample) - 1 else ""
        print(f'    "{key}": {value}{comma}')
    
    print(f"  }}'")
    print()

def main():
    """Extract samples and generate test commands."""
    
    # Extract samples
    samples = extract_attack_samples()
    
    if not samples:
        return
    
    print("\n" + "="*70)
    print("CURL TEST COMMANDS")
    print("="*70)
    print("\nCopy and paste these commands to test the API:\n")
    
    # Print curl commands for each attack type
    for attack_type, attack_samples in samples.items():
        if attack_samples:
            print(f"\n{'#'*70}")
            print(f"# {attack_type} SAMPLES")
            print(f"{'#'*70}")
            
            for i, sample in enumerate(attack_samples[:2], 1):  # First 2 samples
                print(f"\n## Sample {i}")
                print_curl_command(attack_type, sample)

if __name__ == '__main__':
    main()
