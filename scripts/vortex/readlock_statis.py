import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

def analyze_zones(data):
    data = data[data['avg_wait'] > 0]
    """Analyze number of nodes in each size zone and calculate zone averages"""
    # Define size zones
    wait_zones = [
        (0, 1, "0-1"),
        (1, 50, "1-50"),
        (50, 100, "50-100"),
        (100, 500, "100-500"),
        (500, 1e3, "500-1k"),
        (1e3, 2e3, "1k-2k"),
        # (1e3, 1.1e3, "1-1.1k"),
        # (1e3, 1.1e3, "1-1.1k"),
        # (1.1e3, 1.2e3, "1.1-1.2k"),
        # (1.2e3, 1.3e3, "1.2-1.3k"),
        # (1.3e3, 1.4e3, "1.3-1.4k"),
        # (1.4e3, 1.5e3, "1.4-1.5k"),
        # (1.5e3, 1.6e3, "1.5-1.6k"),
        # (1.6e3, 1.7e3, "1.6-1.7k"),
        # (1.7e3, 1.8e3, "1.7-1.8k"),
        # (1.8e3, 1.9e3, "1.8-1.9k"),
        # (1.9e3, 2e3, "1.9-2k"),
        (2e3, 4e3, "2K-4K"),
        (4e3, 1e4, "4K-10K"),
        (1e4, 1e5, "10K-20K"),
        (1e5, 2e5, "20K-50K"),
        (2e5, 5e5, "50K-100K"),
        (1e7, float('inf'), ">100k")
    ]
    
    # Calculate nodes per zone
    zone_counts_non_snapshot_data = []
    zone_counts_take_snapshot = []
    zone_all_counts = []
    
    # Variables for overall zone averages
    total_non_snapshot_data_wait = 0
    total_non_snapshot_points = 0
    total_take_snapshot_wait = 0
    total_take_snapshot_points = 0
    
    for start, end, name in wait_zones:
        # Filter data for this size zone
        zone_data = data[(data['avg_wait'] >= start) & (data['avg_wait'] < end) & (data['num_invokes'] > 0)]
        
        # non_snapshot_data nodes (Snapshot value is not 0)
        non_snapshot_data = zone_data[zone_data['Snapshot'] == 0]
        non_snapshot_data_node_count = len(set(non_snapshot_data['Snapshot']))  # Count unique nodes
        non_snapshot_points = len(non_snapshot_data)
        non_snapshot_data_avg_wait = non_snapshot_data['avg_wait'].mean() if not non_snapshot_data.empty else 0
        
        # Find max wait time for non_snapshot_data
        non_snapshot_max_wait = non_snapshot_data['avg_wait'].max() if not non_snapshot_data.empty else 0
        non_snapshot_max_idx = non_snapshot_data['avg_wait'].idxmax() if not non_snapshot_data.empty else None
        non_snapshot_max_size = non_snapshot_data.loc[non_snapshot_max_idx, 'size'] if non_snapshot_max_idx is not None else 0
        
        # Update totals for overall zone average calculation
        if not non_snapshot_data.empty:
            total_non_snapshot_data_wait += non_snapshot_data['avg_wait'].sum()
            total_non_snapshot_points += non_snapshot_points
        
        # take_snapshot nodes (Snapshot value is 0)
        take_snapshot_data = zone_data[zone_data['Snapshot'] != 0]
        take_snapshot_count = len(set(take_snapshot_data['Snapshot']))  # Will be 1 or 0
        take_snapshot_points = len(take_snapshot_data)
        take_snapshot_avg_wait = take_snapshot_data['avg_wait'].mean() if not take_snapshot_data.empty else 0

        # Find max wait time for take_snapshot
        take_snapshot_max_wait = take_snapshot_data['avg_wait'].max() if not take_snapshot_data.empty else 0
        take_snapshot_max_idx = take_snapshot_data['avg_wait'].idxmax() if not take_snapshot_data.empty else None
        take_snapshot_max_size = take_snapshot_data.loc[take_snapshot_max_idx, 'size'] if take_snapshot_max_idx is not None else 0

        all_average_wait = (non_snapshot_data_avg_wait * non_snapshot_points + take_snapshot_avg_wait * take_snapshot_points) / (non_snapshot_points + take_snapshot_points) if (non_snapshot_points + take_snapshot_points) > 0 else 0
        
        # Find max wait time for all data in this zone
        all_max_wait = zone_data['avg_wait'].max() if not zone_data.empty else 0
        all_max_idx = zone_data['avg_wait'].idxmax() if not zone_data.empty else None
        all_max_size = zone_data.loc[all_max_idx, 'size'] if all_max_idx is not None else 0
        
        # Update totals for overall zone average calculation
        if not take_snapshot_data.empty:
            total_take_snapshot_wait += take_snapshot_data['avg_wait'].sum()
            total_take_snapshot_points += take_snapshot_points
        
        # Store results
        if non_snapshot_points > 0:
            zone_counts_non_snapshot_data.append({
                'zone': name,
                'unique_snapshot': non_snapshot_data_node_count,
                'total_points': non_snapshot_points,
                'avg_wait_time': non_snapshot_data_avg_wait,
                'max_wait_time': non_snapshot_max_wait,
                'max_size': non_snapshot_max_size
            })
        
        if take_snapshot_points > 0:
            zone_counts_take_snapshot.append({
                'zone': name,
                'unique_snapshot': take_snapshot_count,
                'total_points': take_snapshot_points,
                'avg_wait_time': take_snapshot_avg_wait,
                'max_wait_time': take_snapshot_max_wait,
                'max_size': take_snapshot_max_size
            })

        zone_all_counts.append({
            'zone': name,
            'unique_snapshot': non_snapshot_data_node_count + take_snapshot_count,
            'total_points': non_snapshot_points + take_snapshot_points,
            'avg_wait_time': all_average_wait,
            'max_wait_time': all_max_wait,
            'max_size': all_max_size
        })
        
    
    # Convert to DataFrames
    non_snapshot_data_df = pd.DataFrame(zone_counts_non_snapshot_data)
    take_snapshot_df = pd.DataFrame(zone_counts_take_snapshot)
    zone_all_counts_df = pd.DataFrame(zone_all_counts)
    
    # Calculate overall zone averages
    overall_non_snapshot_data_avg = total_non_snapshot_data_wait / total_non_snapshot_points if total_non_snapshot_points > 0 else 0
    overall_take_snapshot_avg = total_take_snapshot_wait / total_take_snapshot_points if total_take_snapshot_points > 0 else 0
    overall_all_avg = (total_non_snapshot_data_wait + total_take_snapshot_wait) / (total_non_snapshot_points + total_take_snapshot_points) if (total_non_snapshot_points + total_take_snapshot_points) > 0 else 0
    
    # Calculate overall max values
    overall_non_snapshot_max = data[data['Snapshot'] == 0]['avg_wait'].max() if not data[data['Snapshot'] == 0].empty else 0
    overall_take_snapshot_max = data[data['Snapshot'] != 0]['avg_wait'].max() if not data[data['Snapshot'] != 0].empty else 0
    overall_all_max = data['avg_wait'].max() if not data.empty else 0
    
    # Print detailed statistics for non_snapshot_data list nodes
    print("\nDetailed Zone Analysis Non Snapshot")
    print("-" * 100)
    print(f"{'Zone':12} {'Unique Snapshots':>15} {'Total Points':>15} {'Avg Wait Time':>15} {'Max Wait Time':>15} {'Size of Max':>15}")
    print("-" * 100)
    if not non_snapshot_data_df.empty:
        for _, row in non_snapshot_data_df.iterrows():
            print(f"{row['zone']:12} {row['unique_snapshot']:>15,} {row['total_points']:>15,} {row['avg_wait_time']:>15.2f} {row['max_wait_time']:>15.2f} {row['max_size']:>15,.0f}")
        print("-" * 100)
        print(f"{'OVERALL':12} {non_snapshot_data_df['unique_snapshot'].sum():>15,} {total_non_snapshot_points:>15,} {overall_non_snapshot_data_avg:>15.2f} {overall_non_snapshot_max:>15.2f}")
    else:
        print("No non_snapshot_data list nodes found in the data.")

    # Print detailed statistics for take_snapshot block nodes
    print("\nDetailed Zone Analysis Take Snapshot")
    print("-" * 100)
    print(f"{'Zone':12} {'Unique Snapshots':>15} {'Total Points':>15} {'Avg Wait Time':>15} {'Max Wait Time':>15} {'Size of Max':>15}")
    print("-" * 100)
    if not take_snapshot_df.empty:
        for _, row in take_snapshot_df.iterrows():
            print(f"{row['zone']:12} {row['unique_snapshot']:>15,} {row['total_points']:>15,} {row['avg_wait_time']:>15.2f} {row['max_wait_time']:>15.2f} {row['max_size']:>15,.0f}")
        print("-" * 100)
        print(f"{'OVERALL':12} {take_snapshot_df['unique_snapshot'].sum():>15,} {total_take_snapshot_points:>15,} {overall_take_snapshot_avg:>15.2f} {overall_take_snapshot_max:>15.2f}")
    else:
        print("No take_snapshot block nodes found in the data.")

    #print averages for all zones
    print("\nAll Data")
    print("-" * 100)
    print(f"{'Zone':12} {'Unique Snapshots':>15} {'Total Points':>15} {'Avg Wait Time':>15} {'Max Wait Time':>15} {'Size of Max':>15}")
    print("-" * 100)
    if not zone_all_counts_df.empty:
        for _, row in zone_all_counts_df.iterrows():
            print(f"{row['zone']:12} {row['unique_snapshot']:>15,} {row['total_points']:>15,} {row['avg_wait_time']:>15.2f} {row['max_wait_time']:>15.2f} {row['max_size']:>15,.0f}")
        print("-" * 100)
        print(f"{'OVERALL':12} {zone_all_counts_df['unique_snapshot'].sum():>15,} {zone_all_counts_df['total_points'].sum():>15,} {overall_all_avg:>15.2f} {overall_all_max:>15.2f}")
    else:
        print("No data found in the all zones.")
    
    # Calculate and print zone-size weighted average wait times
    if not non_snapshot_data_df.empty:
        weighted_non_snapshot_data_avg = np.average(
            non_snapshot_data_df['avg_wait_time'], 
            weights=non_snapshot_data_df['total_points']
        )
        print(f"\nWeighted average wait time for non_snapshot_data list nodes: {weighted_non_snapshot_data_avg:.2f}")
    
    if not take_snapshot_df.empty:
        weighted_take_snapshot_avg = np.average(
            take_snapshot_df['avg_wait_time'], 
            weights=take_snapshot_df['total_points']
        )
        print(f"Weighted average wait time for take_snapshot block nodes: {weighted_take_snapshot_avg:.2f}")
    
    return

def main():
    parser = argparse.ArgumentParser(description='Analyze node distribution across size zones')
    parser.add_argument('input_file', help='Input CSV file path')
    args = parser.parse_args()
    
    # Read data
    data = pd.read_csv(args.input_file, header=None)
    data.columns = ['Snapshot', 'size', 'total_wait', 'num_invokes', 'avg_wait']
    
    # Analyze zones
    analyze_zones(data)

if __name__ == '__main__':
    main()