import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Function to clean numeric values (remove commas and convert to float)
def clean_numeric(value):
    if pd.isna(value) or value == '' or value is None:
        return np.nan
    return float(str(value).replace(',', '').replace('"', ''))

# Function to extract contention number from string like "contention 64"
def extract_contention(value):
    if 'baseline' in str(value).lower():
        return 'baseline'
    try:
        return int(str(value).split()[-1])
    except:
        return np.nan

# Read the CSV file
# Replace 'your_file.csv' with the actual path to your file
file_path = 'content.csv'  # Update this path

try:
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Clean column names (remove any extra spaces)
    df.columns = df.columns.str.strip()
    
    # Extract contention levels
    df['contention'] = df['contention / neighbor_size'].apply(extract_contention)
    
    # Clean numeric columns
    df['read_time'] = df['read time'].apply(clean_numeric)
    df['avg_throughput'] = df['avg throughput/s'].apply(clean_numeric)
    df['avg_latency'] = df['avg latency/ms'].apply(clean_numeric)
    # Convert read time from nanoseconds to seconds (assuming the large numbers are nanoseconds)
    # Based on your data, these look like nanosecond values
    df['read_time_seconds'] = df['read_time'] / 1e6
    df['memory'] = df['memory'].apply(clean_numeric) / 1024  / 10  # Convert memory from bytes to GB
    
    # Filter out rows with missing data and separate baseline
    baseline_data = df[df['contention'] == 'baseline'].iloc[0]
    contention_data = df[(df['contention'] != 'baseline') & 
                        (pd.notna(df['read_time'])) & 
                        (pd.notna(df['avg_throughput'])) & 
                        (pd.notna(df['memory'])) &
                        (pd.notna(df['avg_latency']))].copy()
    
    # Sort by contention level
    contention_data = contention_data.sort_values('contention')
    
    baseline_read_time_seconds = baseline_data['read_time'] / 1e6
    baseline_throughput = baseline_data['avg_throughput']
    baseline_latency = baseline_data['avg_latency']
    baseline_memory = baseline_data['memory']
    print("Processed data:")
    print(contention_data[['contention', 'read_time_seconds', 'avg_throughput', 'avg_latency', 'memory']])
    print(f"\nBaseline values:")
    print(f"Read time: {baseline_read_time_seconds}s")
    print(f"Throughput: {baseline_throughput} ops/s")
    print(f"Latency: {baseline_latency} ms")
    print(f"Memory: {baseline_memory} GB")
    
except FileNotFoundError:
    print("File not found. Using the data from your message directly.")

# Ensure all data is numeric and clean
contention_levels = contention_data['contention'].astype(float).values
read_times = contention_data['read_time_seconds'].astype(float).values
throughputs = contention_data['avg_throughput'].astype(float).values
latencies = contention_data['avg_latency'].astype(float).values
memory_usage = contention_data['memory'].astype(float).values

# Create the performance chart (Read Time vs Throughput)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 16))

# Chart 1: Performance Analysis
color1 = '#dc2626'
color2 = '#2563eb'

# Plot read time on left y-axis
ax1.plot(contention_levels, read_times, 
         color=color1, linewidth=3, marker='o', markersize=8, label='Read Time (s)', zorder=3)
ax1.axhline(y=float(baseline_read_time_seconds), color=color1, linestyle='--', linewidth=2, 
            alpha=0.8, label='Baseline Read Time', zorder=1)
ax1.set_ylabel('Read Time (s)', color=color1, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color1)

# Set y-axis limits for read time to create better spacing
read_time_min = min(read_times.min(), baseline_read_time_seconds)
read_time_max = max(read_times.max(), baseline_read_time_seconds)
read_time_range = read_time_max - read_time_min
# ax1.set_ylim(read_time_min - 0.2 * read_time_range, read_time_max + 0.3 * read_time_range)
ax1.set_ylim(0, read_time_max * 1.15)

# Create secondary y-axis for throughput
ax1_twin = ax1.twinx()

# Plot throughput on right y-axis
ax1_twin.plot(contention_levels, throughputs, 
              color=color2, linewidth=3, marker='s', markersize=8, label='Avg Throughput (ops/s)', zorder=3)
ax1_twin.axhline(y=float(baseline_throughput), color=color2, linestyle='--', linewidth=2, 
                 alpha=0.8, label='Baseline Throughput', zorder=2)
ax1_twin.set_ylabel('Avg Throughput (ops/s)', color=color2, fontsize=12)
ax1_twin.tick_params(axis='y', labelcolor=color2)

# Set y-axis limits for throughput to create better spacing
throughput_min = min(throughputs.min(), baseline_throughput)
throughput_max = max(throughputs.max(), baseline_throughput)
throughput_range = throughput_max - throughput_min
# ax1_twin.set_ylim(throughput_min - 0.15 * throughput_range, throughput_max + 0.4 * throughput_range)
ax1_twin.set_ylim(0, throughput_max * 1.35)

ax1.set_xlabel('Contention Level', fontsize=12)
ax1.set_title('Performance Analysis: Read Time & Throughput vs Contention', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Combined legend for first chart
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Format axes - simplified to avoid type issues
ax1_twin.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))

# Chart 2: Latency Analysis
color3 = '#059669'
ax2.plot(contention_levels, latencies, 
         color=color3, linewidth=3, marker='^', markersize=8, label='Avg Latency (ms)')
ax2.axhline(y=float(baseline_latency), color=color3, linestyle='--', linewidth=2, 
            alpha=0.8, label='Baseline Latency')

ax2.set_xlabel('Contention Level', fontsize=12)
ax2.set_ylabel('Average Latency (ms)', color=color3, fontsize=12)
ax2.set_title('Latency Analysis: Average Latency vs Contention', fontsize=14, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color3)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right')
latency_max = max(latencies.max(), baseline_latency)
ax2.set_ylim(0, latency_max * 1.1)

# Chart 3: Memory Consumption Analysis
color4 = '#7c3aed'
ax3.plot(contention_levels, memory_usage, 
         color=color4, linewidth=3, marker='D', markersize=8, label='Memory Usage')
ax3.axhline(y=float(baseline_memory), color=color4, linestyle='--', linewidth=2, 
            alpha=0.8, label='Baseline Memory')

ax3.set_xlabel('Contention Level', fontsize=12)
ax3.set_ylabel('Memory Usage(GB)', color=color4, fontsize=12)
ax3.set_title('Memory Analysis: Memory Consumption vs Contention', fontsize=14, fontweight='bold')
ax3.tick_params(axis='y', labelcolor=color4)
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper right')

# Set y-axis limits for memory to create better spacing
memory_min = min(memory_usage.min(), baseline_memory)
memory_max = max(memory_usage.max(), baseline_memory)
memory_range = memory_max - memory_min
# ax3.set_ylim(memory_min - 0.1 * memory_range, memory_max + 0.2 * memory_range)
ax3.set_ylim(0, memory_max * 1.1)

# Set x-axis ticks for all charts
for ax in [ax1, ax2, ax3]:
    ax.set_xticks(contention_levels)
    ax.set_xticklabels([f'{int(x)}' for x in contention_levels], rotation=45)

# Use subplots_adjust instead of tight_layout to avoid the error
plt.subplots_adjust(hspace=0.3, bottom=0.1, top=0.95, left=0.1, right=0.9)
plt.savefig('contention_performance_latency_analysis.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

# Performance analysis
# print("\n=== Performance Analysis ===")
# print(f"Baseline Read Time: {baseline_read_time_seconds:.6f}s")
# print(f"Baseline Throughput: {baseline_throughput:,} ops/s")
# print(f"Baseline Latency: {baseline_latency} ms")

# print(f"\nBest Read Time: {contention_data['read_time_seconds'].min():.6f}s at contention {contention_data.loc[contention_data['read_time_seconds'].idxmin(), 'contention']}")
# print(f"Best Throughput: {contention_data['avg_throughput'].max():,} ops/s at contention {contention_data.loc[contention_data['avg_throughput'].idxmax(), 'contention']}")
# print(f"Best Latency: {contention_data['avg_latency'].min()} ms at contention {contention_data.loc[contention_data['avg_latency'].idxmin(), 'contention']}")

# print(f"\n=== Comparison to Baseline ===")
# for _, row in contention_data.iterrows():
#     level = int(row['contention'])
#     read_improvement = ((baseline_read_time_seconds - row['read_time_seconds']) / baseline_read_time_seconds) * 100
#     throughput_improvement = ((row['avg_throughput'] - baseline_throughput) / baseline_throughput) * 100
#     latency_improvement = ((baseline_latency - row['avg_latency']) / baseline_latency) * 100
    
#     print(f"\nContention {level}:")
#     print(f"  Read Time: {read_improvement:+.1f}% vs baseline")
#     print(f"  Throughput: {throughput_improvement:+.1f}% vs baseline")
#     print(f"  Latency: {latency_improvement:+.1f}% vs baseline")