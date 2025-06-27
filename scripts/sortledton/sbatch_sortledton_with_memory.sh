#!/bin/bash
# Memory monitoring function
monitor_memory() {
    local pid=$1
    local output_file=$2
    local peak=0
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Check if PID exists
    if ! kill -0 $pid 2>/dev/null; then
        echo "PID $pid does not exist"
        return 1
    fi
    
    # Start logging initial info
    echo "Start monitoring PID: $pid at $(date)" > $output_file
    echo "Time,RSS(KB)" >> $output_file
    
    while kill -0 $pid 2>/dev/null; do
        mem=$(ps -o rss= -p $pid 2>/dev/null)
        if [ -z "$mem" ]; then
            break
        fi
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
    
    echo "Memory monitoring results written to $output_file"
}

# writer_threads_values=(31 30 28 24 20 16 12 8   4  1)
# reader_threads_values=(1 2   4  8 12 16 20 24 28 31)
writer_threads_values=(48)
reader_threads_values=1
rate_limit=1500000
# writer_threads_values=(1  2   4  8 12 16 20 24 28 31)
# writer_threads_values=32
# reader_threads_values=(31 30 28 24 20 16 12 8   4  1)
# reader_threads_values=32

SCRIPT_DIR="/DS/dsg-blockchain/work"
export LD_LIBRARY_PATH=$SCRIPT_DIR:$LD_LIBRARY_PATH

# Outer loop to run the script 4 times
for index in "${!writer_threads_values[@]}"; do
    writer_threads=${writer_threads_values[$index]}
    # reader_threads=${reader_threads_values[$index]}
    for reader_threads in "${reader_threads_values[@]}"; do
        # for run in {1..4}; do
        # echo "Run #$run"
        log_file="/DS/dsg-blockchain/work/output/gfe_driver/sortledton/pr/test_gc_r${rate_limit}_graph22_${writer_threads}_${reader_threads}.log_5"
        # log_file="/DS/dsg-blockchain/work/gfe_driver2/build/sortledton_r${rate_limit}_w${writer_threads}_r${reader_threads}.log"

        # /DS/dsg-blockchain/work/gfe_driver2/build/sortledton_driver \
        /DS/dsg-blockchain/work/gfe_driver2/data/sortledton/pr/test_gc_rate_gfe_driver \
        -G /DS/dsg-blockchain/nobackup/graph500/graph500-22.properties -u --log /DS/dsg-blockchain/nobackup/graph500/graph500-22-1.0.graphlog \
        -l vortex -w "$writer_threads" -r "$reader_threads" --block_size 256 -d results.sqlite3 \
        --aging_timeout 2h -R 1 --latency 1 --mixed_workload true --blacklist lcc,sssp,wcc,bfs,cdlp --rate_limit "$rate_limit" > "$log_file" &

        main_pid=$!
        memory_file="/DS/dsg-blockchain/work/output/gfe_driver/sortledton/pr/memory_graph22_r${rate_limit}_w${writer_threads}_r${reader_threads}.log"
        # memory_file="/DS/dsg-blockchain/work/gfe_driver2/build/memory_sortledton_r${rate_limit}_w${writer_threads}_r${reader_threads}.log"
        # Start memory monitoring in background
        monitor_memory $main_pid $memory_file &
        monitor_pid=$!

        echo "Started process PID: $main_pid with memory monitoring PID: $monitor_pid"

        # Wait for the main process to complete
        wait $main_pid
        main_exit_code=$?
                
        # Wait a bit for memory monitoring to finish
        sleep 2
                
        # Kill memory monitoring if it's still running
        if kill -0 $monitor_pid 2>/dev/null; then
            kill $monitor_pid 2>/dev/null
        fi
    done
done