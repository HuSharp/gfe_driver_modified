import glob
import os
import re

def extract_mean_from_line(line):
    """Extract the mean value from a metric line"""
    match = re.search(r'mean: (\d+)', line)
    if match:
        return int(match.group(1))
    return None

def extract_thread0_stats(file_content):
    """Extract the last 6 Thread0 statistics from the file content"""
    thread0_stats = []
    thread0_pattern = r'Thread0 (?:had|read) (\d+) (.+)'
    
    # Find all Thread0 lines
    for line in file_content.split('\n'):
        if line.startswith('Thread0'):
            match = re.match(thread0_pattern, line)
            if match:
                value = int(match.group(1))
                metric = match.group(2)
                thread0_stats.append((metric, value))
    
    # Return only the last 6 statistics if available
    return thread0_stats[-9:] if len(thread0_stats) >= 9 else thread0_stats

def extract_metrics_from_file(file_path):
    """Extract both performance metrics and Thread0 statistics from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            
            # Extract performance metrics
            metrics_lines = []
            for line in file_content.split('\n'):
                if '>>' in line:
                    metrics_lines.append(line.strip())
            
            # Get the last four performance metrics
            last_four = None
            if len(metrics_lines) >= 4:
                last_four = metrics_lines[-4:]
                required_metrics = ['CDLP']
                if not all(metric in ''.join(last_four) for metric in required_metrics):
                    last_four = None
            
            # Extract Thread0 statistics
            thread0_stats = extract_thread0_stats(file_content)
            
            return last_four, thread0_stats
                
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None, None

def calculate_averages(all_results):
    """Calculate average means for each metric type and Thread0 statistic across all files"""
    metric_sums = {'CDLP': []}
    thread0_sums = {}
    
    # Collect all values for each metric and Thread0 statistic
    for metrics, thread0_stats in all_results.values():
        # Process performance metrics
        if metrics:
            for line in metrics:
                for metric_type in metric_sums.keys():
                    if line.startswith(f'>> {metric_type}'):
                        mean_value = extract_mean_from_line(line)
                        if mean_value is not None:
                            metric_sums[metric_type].append(mean_value)
        
        # Process Thread0 statistics
        if thread0_stats:
            for metric, value in thread0_stats:
                if metric not in thread0_sums:
                    thread0_sums[metric] = []
                thread0_sums[metric].append(value)
    
    # Calculate averages for performance metrics
    perf_averages = {}
    for metric_type, values in metric_sums.items():
        if values:
            perf_averages[metric_type] = sum(values) / len(values)
    
    # Calculate averages for Thread0 statistics
    thread0_averages = {}
    for metric, values in thread0_sums.items():
        if values:
            thread0_averages[metric] = sum(values) / len(values)
    
    return perf_averages, thread0_averages

def collect_all_metrics(log_dir='../logs', pattern='profile_sortledton_mixed_cdlp_22.log_*'):
    """Collect metrics from all matching log files"""
    full_pattern = os.path.join(log_dir, pattern)
    all_results = {}
    
    for file_path in glob.glob(full_pattern):
        file_num = int(file_path.split('_')[-1])
        metrics, thread0_stats = extract_metrics_from_file(file_path)
        
        if metrics or thread0_stats:
            all_results[file_num] = (metrics, thread0_stats)
            print(f"Processed file number {file_num}")
        else:
            print(f"No valid metrics found in file number {file_num}")
    
    return all_results

def save_results(results, perf_averages, thread0_averages, output_file='vortex_mixed_pr_22_log_contention_1000_snapshot_1.txt'):
    """Save results and averages to file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            # Write individual file results
            for file_num in sorted(results.keys()):
                metrics, thread0_stats = results[file_num]
                file.write(f"\nMetrics from file {file_num}:\n")
                file.write("-" * 40 + "\n")
                
                if metrics:
                    for line in metrics:
                        file.write(line + "\n")
                
                if thread0_stats:
                    file.write("\nThread0 Statistics:\n")
                    for metric, value in thread0_stats:
                        file.write(f"Thread0 had {value} {metric}\n")
            
            # Write performance averages
            file.write("\nAVERAGE PERFORMANCE METRICS ACROSS ALL FILES:\n")
            file.write("-" * 40 + "\n")
            for metric, avg in perf_averages.items():
                file.write(f">> {metric} Average mean: {avg:.2f}\n")
            
            # Write Thread0 averages
            file.write("\nAVERAGE THREAD0 STATISTICS ACROSS ALL FILES:\n")
            file.write("-" * 40 + "\n")
            for metric, avg in thread0_averages.items():
                file.write(f"Thread0 average {metric}: {avg:.2f}\n")
                
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    # Collect metrics from all files
    all_results = collect_all_metrics()
    
    if all_results:
        # Calculate averages
        perf_averages, thread0_averages = calculate_averages(all_results)
        
        # Print results to console
        print("\nCollected Results:")
        print("=================")
        for file_num in sorted(all_results.keys()):
            metrics, thread0_stats = all_results[file_num]
            print(f"\nFile {file_num}:")
            print("-" * 20)
            
            if metrics:
                for line in metrics:
                    print(line)
            
            if thread0_stats:
                print("\nThread0 Statistics:")
                for metric, value in thread0_stats:
                    print(f"Thread0 had {value} {metric}")
        
        # Print performance averages
        print("\nAVERAGE PERFORMANCE METRICS ACROSS ALL FILES:")
        print("-" * 40)
        for metric, avg in perf_averages.items():
            print(f">> {metric} Average mean: {avg:.2f}")
        
        # Print Thread0 averages
        print("\nAVERAGE THREAD0 STATISTICS ACROSS ALL FILES:")
        print("-" * 40)
        for metric, avg in thread0_averages.items():
            print(f"Thread0 average {metric}: {avg:.2f}")
        
        # Save to file
        save_results(all_results, perf_averages, thread0_averages)
    else:
        print("No results found in any files")

if __name__ == "__main__":
    main()