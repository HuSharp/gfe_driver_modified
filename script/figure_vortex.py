import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import os
import argparse

def create_dual_plot(data, config, fig, regular_ax, log_ax):
    """Create both regular and log scale plots"""
    x = data[config['x_col']].values
    y = data[config['y_col']].values
    
    # Filter out invalid values
    mask = ~(np.isinf(x) | np.isnan(x) | np.isinf(y) | np.isnan(y))
    x_valid = x[mask]
    y_valid = y[mask]
    
    # Regular scale plot
    regular_ax.scatter(x_valid, y_valid, s=20, alpha=0.6)
    if len(x_valid) > 1 and np.std(y_valid) != 0 and np.std(x_valid) != 0:
        try:
            p = np.polyfit(x_valid, y_valid, 1)
            x_trend = np.linspace(min(x_valid), max(x_valid), 100)
            y_trend = np.polyval(p, x_trend)
            regular_ax.plot(x_trend, y_trend, 'r--', linewidth=1.5)
        except Exception as e:
            print(f"Could not fit trend line for regular plot: {e}")
    
    regular_ax.set_xlabel(config['xlabel'])
    regular_ax.set_ylabel(config['ylabel'])
    regular_ax.set_title(f"{config['title']} (Linear Scale)")
    regular_ax.grid(True)
    
    # Log scale plot
    # Add small constant to handle zeros
    eps = 1e-10
    x_log = x_valid + eps
    y_log = y_valid + eps
    
    log_ax.scatter(x_log, y_log, s=20, alpha=0.6)
    if len(x_log) > 1 and np.std(np.log10(y_log)) != 0 and np.std(np.log10(x_log)) != 0:
        try:
            p = np.polyfit(np.log10(x_log), np.log10(y_log), 1)
            x_trend = np.logspace(np.log10(min(x_log)), np.log10(max(x_log)), 100)
            y_trend = 10**(p[0] * np.log10(x_trend) + p[1])
            log_ax.plot(x_trend, y_trend, 'r--', linewidth=1.5)
        except Exception as e:
            print(f"Could not fit trend line for log plot: {e}")
    
    log_ax.set_xscale('log')
    log_ax.set_yscale('log')
    log_ax.set_xlabel(f"{config['xlabel']} (log scale)")
    log_ax.set_ylabel(f"{config['ylabel']} (log scale)")
    log_ax.set_title(f"{config['title']} (Log Scale)")
    log_ax.grid(True)

def analyze_data(input_file):
    # Read data
    data = pd.read_csv(input_file, header=None)
    data.columns = ['Snapshot', 'size', 'total_wait', 'num_invokes', 'avg_wait']
    
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
            'title': 'Size vs Average'
        }
        # {
        #     'x_col': 'Snapshot',
        #     'y_col': 'size',
        #     'xlabel': 'Snapshot',
        #     'ylabel': 'Size',
        #     'title': 'Snapshot vs Size'
        # }
    ]
    
    # Create figure with both regular and log scale plots
    fig = plt.figure(figsize=(20, 24))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Create plots
    for i, config in enumerate(plot_configs):
        regular_ax = fig.add_subplot(gs[i, 0])
        log_ax = fig.add_subplot(gs[i, 1])
        create_dual_plot(data, config, fig, regular_ax, log_ax)
    
    # Adjust layout and set title
    fig.suptitle('Wait Time Analysis Based on Size\n(Linear and Log Scales)', y=0.95, fontsize=16)
    
    # Set figure background color to white
    fig.patch.set_facecolor('white')
    
    # Save the figure with high DPI for better quality
    truncated_file = input_file.split('/')[-1].split('.')[0]
    print("truncated_file: ", truncated_file)
    save_file = f'vortex_24_s1_100_{truncated_file}.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Figure has been saved as " + save_file)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze wait time data and create plots')
    parser.add_argument('input_file', help='Input CSV file path')
    args = parser.parse_args()

    # Enable parallel processing for numpy operations
    os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())
    os.environ["NUMEXPR_NUM_THREADS"] = str(os.cpu_count())
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    # Set up multiprocessing
    num_cores = os.cpu_count()
    print(f"Using {num_cores} CPU cores")
    analyze_data(args.input_file)

if __name__ == '__main__':
    main()