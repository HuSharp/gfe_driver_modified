import glob
import os
import re

def extract_mean_from_line(line):
    """Extract the mean value from a metric line"""
    match = re.search(r'mean: (\d+)', line)
    if match:
        return int(match.group(1))
    return None

def extract_metrics_from_file(file_path):
    """Extract the four metric lines from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            metrics_lines = []
            for line in file:
                if '>>' in line:
                    metrics_lines.append(line.strip())
            
            if len(metrics_lines) >= 4:
                last_four = metrics_lines[-4:]
                required_metrics = ['BFS', 'CDLP', 'PageRank', 'WCC']
                if all(metric in ''.join(last_four) for metric in required_metrics):
                    return last_four
            return None
                
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

def calculate_averages(all_results):
    """Calculate average means for each metric type across all files"""
    metric_sums = {'BFS': [], 'CDLP': [], 'PageRank': [], 'WCC': []}
    
    # Collect all values for each metric
    for metrics in all_results.values():
        for line in metrics:
            for metric_type in metric_sums.keys():
                if line.startswith(f'>> {metric_type}'):
                    mean_value = extract_mean_from_line(line)
                    if mean_value is not None:
                        metric_sums[metric_type].append(mean_value)
    
    # Calculate averages
    averages = {}
    for metric_type, values in metric_sums.items():
        if values:
            averages[metric_type] = sum(values) / len(values)
    
    return averages

def collect_all_metrics(log_dir='../logs', pattern='vortex_mixed_all_22_log_contention_100000_snapshot_0.log_*'):
    """Collect metrics from all matching log files"""
    full_pattern = os.path.join(log_dir, pattern)
    all_results = {}
    
    for file_path in glob.glob(full_pattern):
        file_num = int(file_path.split('_')[-1])
        metrics = extract_metrics_from_file(file_path)
        
        if metrics:
            all_results[file_num] = metrics
            print(f"Processed file number {file_num}")
        else:
            print(f"No valid metrics found in file number {file_num}")
    
    return all_results

def save_results(results, averages, output_file='vortex_mixed_all_22_log_contention_100000_snapshot_0_metrics.txt'):
    """Save results and averages to file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            # Write individual file results
            for file_num in sorted(results.keys()):
                file.write(f"\nMetrics from file {file_num}:\n")
                file.write("-" * 40 + "\n")
                for line in results[file_num]:
                    file.write(line + "\n")
            
            # Write averages
            file.write("\nAVERAGE METRICS ACROSS ALL FILES:\n")
            file.write("-" * 40 + "\n")
            for metric, avg in averages.items():
                file.write(f">> {metric} Average mean: {avg:.2f}\n")
                
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    # Collect metrics from all files
    all_results = collect_all_metrics()
    
    if all_results:
        # Calculate averages
        averages = calculate_averages(all_results)
        
        # Print results to console
        print("\nCollected Results:")
        print("=================")
        for file_num in sorted(all_results.keys()):
            print(f"\nFile {file_num}:")
            print("-" * 20)
            for line in all_results[file_num]:
                print(line)
        
        # Print averages
        print("\nAVERAGE METRICS ACROSS ALL FILES:")
        print("-" * 40)
        for metric, avg in averages.items():
            print(f">> {metric} Average mean: {avg:.2f}")
        
        # Save to file
        save_results(all_results, averages)
    else:
        print("No results found in any files")

if __name__ == "__main__":
    main()