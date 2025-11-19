"""
Custom Dataset Example - BiasClean v2.0
Using BiasClean with your own dataset
"""

import sys
import os
sys.path.append('..')

from biasclean_v2 import BiasClean
import pandas as pd

def demonstrate_custom_data():
    print("BiasClean v2.0 - Custom Dataset Example")
    print("=" * 45)
    
    # Create a sample custom dataset (replace with your data)
    custom_data = {
        'Ethnicity': ['White']*600 + ['Asian']*200 + ['Black']*100 + ['Mixed']*60 + ['Other']*40,
        'Region': ['London']*300 + ['South East']*250 + ['North West']*200 + ['Scotland']*150 + ['Wales']*100,
        'Age': list(range(20, 65)) * 20,  # Repeat pattern to get 1000 samples
        'Gender': ['Male']*480 + ['Female']*500 + ['Other']*20,
        'DisabilityStatus': ['Yes']*220 + ['No']*780,
        'SocioeconomicStatus': ['High']*300 + ['Medium']*500 + ['Low']*200,
        'MigrationStatus': ['UK-born']*870 + ['Migrant']*130,
        'Outcome': [1]*600 + [0]*400  # Binary outcome with some bias
    }
    
    # Ensure we have exactly 1000 records
    df_custom = pd.DataFrame(custom_data).head(1000)
    
    print(f"✓ Created custom dataset: {len(df_custom)} records")
    print(f"✓ Columns: {list(df_custom.columns)}")
    
    # Test with education domain
    bias_clean = BiasClean().fit('education')
    
    initial_score = bias_clean.score(df_custom)
    print(f"✓ Initial bias score: {initial_score:.4f}")
    
    # Apply correction
    df_corrected = bias_clean.transform(df_custom, mode='soft')
    
    final_score = bias_clean.score(df_corrected)
    print(f"✓ Final bias score: {final_score:.4f}")
    
    report = bias_clean.report(df_custom, df_corrected)
    print(f"✓ Bias reduction: {report['reduction_percent']:.1f}%")
    print(f"✓ Data preservation: {report['records_after']} records remaining")
    
    print("\nUsage with your own data:")
    print("1. Load your DataFrame with the 7 fairness features")
    print("2. Call bias_clean.fit('your_domain')")
    print("3. Use score() to measure bias")
    print("4. Use transform() to correct bias")
    print("5. Use report() for detailed analysis")

if __name__ == "__main__":
    demonstrate_custom_data()