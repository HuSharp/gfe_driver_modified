import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

def analyze_zones(data):
    data = data[data['avg_wait'] > 0]
    """Analyze number of nodes in each size zone and find highest wait time in each zone"""
    # Define size zones
    size_zones = [
        # (1, 1e3, "1-1K"),
        (1, 50, "1-50"),
        (50, 100, "50-100"),
        (100, 500, "100-500"),
        (500, 1e3, "500-1k"),
        (1e3, 5e3, "1K-5K"),
        (5e3, 1e4, "5K-10K"),
        (1e4, 5e4, "10K-50K"),
        (5e4, 1e5, "50K-100K"),
        (1e5, 1e6, "100K-1M"),
        (1e6, 1e7, "1M-10M"),
        (1e7, float('inf'), ">10M")
    ]
    
    # Calculate nodes per zone and find highest values
    zone_counts = []

    for start, end, name in size_zones:
        # Filter data for this size zone
        zone_data = data[(data['size'] >= start) & (data['size'] < end) & (data['num_invokes'] > 0)]
        
        zone_points = len(zone_data)
        avg_wait = zone_data['avg_wait'].mean() if not zone_data.empty else 0
        
        # Find maximum value in this zone
        max_wait = zone_data['avg_wait'].max() if not zone_data.empty else 0
        max_item_index = zone_data['avg_wait'].idxmax() if not zone_data.empty else None
        max_item_size = zone_data.loc[max_item_index, 'size'] if max_item_index is not None else 0
        
        # Store results
        if zone_points > 0: 
            zone_counts.append({
                'zone': name,
                'total_points': zone_points,
                'avg_wait_time': avg_wait,
                'max_wait_time': max_wait,
                'max_item_size': max_item_size
            })

    # Convert to DataFrames
    zone_df = pd.DataFrame(zone_counts)

    # Calculate overall zone averages
    overall_data_avg = data['avg_wait'].mean()
    overall_max = data['avg_wait'].max()
    
    # Print detailed statistics for zones
    print("\nDetailed Zone Analysis")
    print("-" * 100)
    print(f"{'Zone':12}{'Total Points':>15} {'Avg Wait Time':>15} {'Highest Wait Time':>20} {'Size of Max Item':>15}")
    print("-" * 100)
    if not zone_df.empty:
        for _, row in zone_df.iterrows():
            print(f"{row['zone']:12}  {row['total_points']:>15,} {row['avg_wait_time']:>15.2f} {row['max_wait_time']:>20.2f} {row['max_item_size']:>15,.0f}")
        print("-" * 100)
        print(f"{'OVERALL':13} {len(data['avg_wait']):>15} {overall_data_avg:>15.2f} {overall_max:>20.2f}")
    else:
        print("No nodes found in the data.")
    return

def main():
    parser = argparse.ArgumentParser(description='Analyze node distribution across size zones')
    parser.add_argument('input_file', help='Input CSV file path')
    args = parser.parse_args()
    
    # Read data
    data = pd.read_csv(args.input_file, header=None)
    data.columns = ['size', 'total_wait', 'num_invokes', 'avg_wait']
    
    # Analyze zones
    analyze_zones(data)

if __name__ == '__main__':
    main()