"""
Multi-Domain Testing - BiasClean v2.0
Comprehensive testing across all 7 domains
"""

import sys
import os
sys.path.append('..')

from biasclean_v2 import BiasClean, generate_synthetic_data
import pandas as pd

def test_all_domains():
    print("BiasClean v2.0 - Multi-Domain Validation")
    print("=" * 50)
    
    domains = ['justice', 'health', 'finance', 'education', 'hiring', 'business', 'governance']
    results = []
    
    for domain in domains:
        print(f"\nTesting domain: {domain.upper()}")
        
        # Initialize for current domain
        bias_clean = BiasClean().fit(domain)
        df = generate_synthetic_data(domain, n_samples=1500)
        
        # Calculate scores
        initial_score = bias_clean.score(df)
        df_corrected = bias_clean.transform(df, mode='soft')
        final_score = bias_clean.score(df_corrected)
        
        # Store results
        results.append({
            'domain': domain,
            'initial_score': initial_score,
            'final_score': final_score,
            'reduction_percent': ((initial_score - final_score) / initial_score) * 100,
            'records_after': len(df_corrected),
            'data_loss_percent': ((1500 - len(df_corrected)) / 1500) * 100
        })
        
        print(f"  Initial: {initial_score:.4f}, Final: {final_score:.4f}, Reduction: {results[-1]['reduction_percent']:.1f}%")
    
    # Display summary
    results_df = pd.DataFrame(results)
    print("\n" + "=" * 60)
    print("COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 60)
    print(results_df.round(4).to_string(index=False))
    
    # Statistics
    avg_reduction = results_df['reduction_percent'].mean()
    most_biased = results_df.loc[results_df['initial_score'].idxmax()]
    least_biased = results_df.loc[results_df['initial_score'].idxmin()]
    
    print(f"\nKey Insights:")
    print(f"• Average bias reduction: {avg_reduction:.2f}%")
    print(f"• Most biased domain: {most_biased['domain']} (score: {most_biased['initial_score']:.4f})")
    print(f"• Least biased domain: {least_biased['domain']} (score: {least_biased['initial_score']:.4f})")
    print(f"• Consistent data loss: {results_df['data_loss_percent'].iloc[0]:.1f}% across domains")

if __name__ == "__main__":
    test_all_domains()