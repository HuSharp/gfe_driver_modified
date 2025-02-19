import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import os
import argparse

def create_dual_plot(data1, data2, data3, data4, config, fig, regular_ax, log_ax):
    """Create both regular and log scale plots for two datasets"""
    # Process first dataset
    x1 = data1[config['x_col']].values
    y1 = data1[config['y_col']].values
    mask1 = ~(np.isinf(x1) | np.isnan(x1) | np.isinf(y1) | np.isnan(y1))
    x1_valid = x1[mask1]
    y1_valid = y1[mask1]
    
    # Process second dataset
    x2 = data2[config['x_col']].values
    y2 = data2[config['y_col']].values
    mask2 = ~(np.isinf(x2) | np.isnan(x2) | np.isinf(y2) | np.isnan(y2))
    x2_valid = x2[mask2]
    y2_valid = y2[mask2]

    x3 = data3[config['x_col']].values
    y3 = data3[config['y_col']].values
    mask3 = ~(np.isinf(x3) | np.isnan(x3) | np.isinf(y3) | np.isnan(y3))
    x3_valid = x3[mask3]
    y3_valid = y3[mask3]

    x4 = data4[config['x_col']].values
    y4 = data4[config['y_col']].values
    mask4 = ~(np.isinf(x4) | np.isnan(x4) | np.isinf(y4) | np.isnan(y4))
    x4_valid = x4[mask4]
    y4_valid = y4[mask4]
    
    # Regular scale plot
    regular_ax.scatter(x1_valid, y1_valid, s=20, alpha=0.6, color='red', label='sortledton')
    regular_ax.scatter(x2_valid, y2_valid, s=20, alpha=0.6, color='blue', label='vortex_read_latest')
    regular_ax.scatter(x3_valid, y3_valid, s=20, alpha=0.6, color='green', label='vortex_stale_read_10s')
    regular_ax.scatter(x4_valid, y4_valid, s=20, alpha=0.6, color='orange', label='vortex_stale_read_15s')

    
    # Fit trend lines for both datasets
    for x_valid, y_valid, color in [(x1_valid, y1_valid, 'blue'), (x2_valid, y2_valid, 'red'), (x3_valid, y3_valid, 'green'), (x4_valid, y4_valid, 'orange')]:
        if len(x_valid) > 1 and np.std(y_valid) != 0 and np.std(x_valid) != 0:
            try:
                p = np.polyfit(x_valid, y_valid, 1)
                x_trend = np.linspace(min(x_valid), max(x_valid), 100)
                y_trend = np.polyval(p, x_trend)
                regular_ax.plot(x_trend, y_trend, '--', color=color, linewidth=1.5)
            except Exception as e:
                print(f"Could not fit trend line for regular plot: {e}")
    
    regular_ax.set_xlabel(config['xlabel'])
    regular_ax.set_ylabel(config['ylabel'])
    regular_ax.set_title(f"{config['title']} (Linear Scale)")
    regular_ax.grid(True)
    regular_ax.legend()
    
    # Log scale plot
    eps = 1e-10
    
    # Plot both datasets in log scale
    for x_valid, y_valid, color, label in [
        (x1_valid, y1_valid, 'red', 'sortledton'),
        (x2_valid, y2_valid, 'blue', 'vortex_read_latest'),
        (x3_valid, y3_valid, 'green', 'vortex_stale_read_10s'),
        (x4_valid, y4_valid, 'orange', 'vortex_stale_read_15s')
    ]:
        x_log = x_valid + eps
        y_log = y_valid + eps
        
        log_ax.scatter(x_log, y_log, s=20, alpha=0.6, color=color, label=label)
        
        if len(x_log) > 1 and np.std(np.log10(y_log)) != 0 and np.std(np.log10(x_log)) != 0:
            try:
                p = np.polyfit(np.log10(x_log), np.log10(y_log), 1)
                x_trend = np.logspace(np.log10(min(x_log)), np.log10(max(x_log)), 100)
                y_trend = 10**(p[0] * np.log10(x_trend) + p[1])
                log_ax.plot(x_trend, y_trend, '--', color=color, linewidth=1.5)
            except Exception as e:
                print(f"Could not fit trend line for log plot: {e}")
    
    log_ax.set_xscale('log')
    log_ax.set_yscale('log')
    log_ax.set_xlabel(f"{config['xlabel']} (log scale)")
    log_ax.set_ylabel(f"{config['ylabel']} (log scale)")
    log_ax.set_title(f"{config['title']} (Log Scale)")
    log_ax.grid(True)
    log_ax.legend()

def analyze_data(sortledton, vortex_read_latest, vortex_stale_read_10s, vortex_stale_read_15s):
    # Read data from both files
    data1 = pd.read_csv(sortledton, header=None)
    data2 = pd.read_csv(vortex_read_latest, header=None)
    data3 = pd.read_csv(vortex_stale_read_10s, header=None)
    data4 = pd.read_csv(vortex_stale_read_15s, header=None)
    
    # Set column names for both datasets
    vortex_columns = ['snapshot', 'size', 'total_wait', 'num_invokes', 'avg_wait']
    sortledton_columns = ['size', 'total_wait', 'num_invokes', 'avg_wait']
    data1.columns = sortledton_columns
    data2.columns = vortex_columns
    data3.columns = vortex_columns
    data4.columns = vortex_columns
    
    # Define plot configurations
    plot_configs = [
        {
            'x_col': 'size',
            'y_col': 'total_wait',
            'xlabel': 'Size',
            'ylabel': 'Total Wait Time',
            'title': 'Size vs Total Wait Time'
        },
        {
            'x_col': 'size',
            'y_col': 'num_invokes',
            'xlabel': 'Size',
            'ylabel': 'Number of Invocations',
            'title': 'Size vs Number of Invocations'
        },
        {
            'x_col': 'size',
            'y_col': 'avg_wait',
            'xlabel': 'Size',
            'ylabel': 'Average Wait Time',
            'title': 'Size vs Average Wait Time'
        }
    ]
    
    # Create figure with both regular and log scale plots
    fig = plt.figure(figsize=(20, 24))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Create plots
    for i, config in enumerate(plot_configs):
        regular_ax = fig.add_subplot(gs[i, 0])
        log_ax = fig.add_subplot(gs[i, 1])
        create_dual_plot(data1, data2, data3, data4, config, fig, regular_ax, log_ax)
    
    # Get filenames for title
    # file1_name = sortledton.split('/')[-1].split('.')[0]
    # file2_name = vortex_read_latest.split('/')[-1].split('.')[0]
    
    # Adjust layout and set title
    # fig.suptitle(f'Wait Time Analysis Comparison\n{sortledton} vs {vortex_read_latest}\n(Linear and Log Scales)', 
    #              y=0.95, fontsize=16)
    
    # Set figure background color to white
    fig.patch.set_facecolor('white')
    
    # Save the figure with high DPI for better quality
    save_file = f'comparison_stale_read(s2_c100).png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Figure has been saved as " + save_file)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Compare wait time data from two files and create plots')
    parser.add_argument('sortledton', help='First input CSV file path')
    parser.add_argument('vortex_read_latest', help='Second input CSV file path')
    parser.add_argument('vortex_stale_read_10s', help='Second input CSV file path')
    parser.add_argument('vortex_stale_read_15s', help='Second input CSV file path')
    args = parser.parse_args()

    # Enable parallel processing for numpy operations
    os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())
    os.environ["NUMEXPR_NUM_THREADS"] = str(os.cpu_count())
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    # Set up multiprocessing
    num_cores = os.cpu_count()
    print(f"Using {num_cores} CPU cores")
    
    # Analyze both datasets
    analyze_data(args.sortledton, args.vortex_read_latest, args.vortex_stale_read_10s, args.vortex_stale_read_15s)

if __name__ == '__main__':
    main()