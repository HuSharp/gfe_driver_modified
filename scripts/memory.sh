#!/bin/bash

# Check if parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <pid> <output_suffix>"
    exit 1
fi

pid=$1
suffix=$2
peak=0
timestamp=$(date +"%Y%m%d_%H%M%S")
output_file="${suffix}_memory_peak_${timestamp}.log"

# Check if PID exists
if ! kill -0 $pid 2>/dev/null; then
    echo "PID $pid does not exist"
    exit 1
fi

# Start logging initial info
echo "Start monitoring PID: $pid at $(date)" > $output_file
echo "Time,RSS(KB)" >> $output_file

while kill -0 $pid 2>/dev/null; do
    mem=$(ps -o rss= -p $pid)
    current_time=$(date +"%H:%M:%S")
    
    # Update peak if current memory is higher
    if [ $mem -gt $peak ]; then
        peak=$mem
    fi
    
    # Log current memory
    echo "$current_time,$mem" >> $output_file
    sleep 1
done

# Write final results
echo "-------------------" >> $output_file
echo "Monitoring ended at: $(date)" >> $output_file
echo "Peak memory usage: $((peak/1024)) MB" >> $output_file

echo "Results written to $output_file"