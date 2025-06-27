import re
import argparse

def parse_log_file(filename):
    """Parse log file and extract operations data with progress markers"""
    operations_data = []
    progress_markers = {}
    
    with open(filename, 'r') as file:
        for line_num, line in enumerate(file, 1):
            # writer time 
            # [Aging2] Updates performed with 48 threads in 17:34 mins
            writer_time_match = re.search(r'\[Aging2\] Updates performed with \d+ threads in (\d+:\d+) mins', line.strip())
            if writer_time_match:
                writer_time = writer_time_match.group(1)
                # transform time to seconds
                minutes, seconds = map(int, writer_time.split(':'))
                total_seconds = minutes * 60 + seconds
                print(f"Writer Time: {total_seconds} seconds")

            # reader time
            # >> PageRank N: 14, mean: 67361210, median: 67855150, std. dev.: 71127573661306, min: 51937656, max: 91145454, perc 90: 71218577, perc 95: 73413760, perc 99: 73413760, num timeouts: 0]
            reader_time_match = re.search(r'>> PageRank N: \d+, mean: (\d+), median: (\d+), std\. dev\.: (\d+), min: (\d+), max: (\d+), perc 90: (\d+), perc 95: (\d+), perc 99: (\d+), num timeouts: \d+', line.strip())
            if reader_time_match:
                print(f"Reader Time: {line.strip()}")

            # Extract operations using regex
            # [Aging2] Progress: 63031274 operations performed
            ops_match = re.search(r'\[Aging2\] Progress: (\d+) operations performed', line.strip())
            if ops_match:
                operations = int(ops_match.group(1))
                operations_data.append((line_num, operations))
            
            # Extract progress markers
            # [thread: 7753, worker_id: 8] Progress: 10%
            progress_match = re.search(r'Progress: (\d+)%', line.strip())
            if progress_match:
                progress = int(progress_match.group(1))
                progress_markers[progress] = line_num

            # Extract latency line
            # [Aging2] Average latency of updates: 19 microsecs, 99th percentile: 31 microsecs
            latency_match = re.search(r'\[Aging2\] Average latency of updates: (\d+) microsecs, 99th percentile: (\d+) microsecs', line.strip())
            if latency_match:
                latency_line = line.strip()
                print(f"Latency Line: {latency_line}")
    
    return operations_data, progress_markers

def filter_operations_by_progress(operations_data, progress_markers, start_percent=10, end_percent=90):
    """Filter operations data to only include entries between start_percent and end_percent"""
    if start_percent not in progress_markers or end_percent not in progress_markers:
        print(f"Warning: Could not find {start_percent}% or {end_percent}% progress markers")
        return operations_data
    
    start_line = progress_markers[start_percent]
    end_line = progress_markers[end_percent]
    
    print(f"Filtering operations between line {start_line} ({start_percent}%) and line {end_line} ({end_percent}%)")
    
    # Filter operations data to only include entries between the progress markers
    filtered_data = [
        (line_num, ops) for line_num, ops in operations_data 
        if start_line <= line_num <= end_line
    ]
    
    return filtered_data

def analyze_logs(filename):
    """Main function to analyze log file and calculate statistics"""
    try:
        # Parse the log file
        operations_data, progress_markers = parse_log_file(filename)
        if len(operations_data) < 2:
            print("Need at least 2 data points to calculate throughput")
            return
        
        # Filter operations between 10% and 90%
        filtered_data = filter_operations_by_progress(operations_data, progress_markers, 10, 90)
        if len(filtered_data) < 2:
            print("Need at least 2 data points in the 10%-90% range to calculate throughput")
            return
        
        print(f"Using {len(filtered_data)} operation entries between 10% and 90%")
        
        # Extract just the operations values from filtered data
        operations = [ops for line_num, ops in filtered_data]
        
        print(f"Operations range (10%-90%): {operations[0]:,} to {operations[-1]:,}")
        
        # Calculate operation differences (throughput per log entry)
        throughputs = []
        
        for i in range(1, len(operations)):
            diff = operations[i] - operations[i-1]
            throughputs.append(diff)
        
        if not throughputs:
            print("No valid throughput calculations possible")
            return
        
        # Calculate statistics
        max_throughput = max(throughputs)
        avg_throughput = sum(throughputs) / len(throughputs)
        total_operations = operations[-1] - operations[0]
        
        print(f"Max operations per interval: {max_throughput:,}")
        print(f"Average operations per interval: {avg_throughput:,.2f}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Aging2 operations throughput between 10% and 90%')
    parser.add_argument('input_file', help='Input log file path')
    args = parser.parse_args()

    analyze_logs(args.input_file)