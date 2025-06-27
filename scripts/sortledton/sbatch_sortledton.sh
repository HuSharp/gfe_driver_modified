#!/bin/bash
# writer_threads_values=(31 30 28 24 20 16 12 8   4  1)
# reader_threads_values=(1 2   4  8 12 16 20 24 28 31)
writer_threads_values=(48)
reader_threads_values=(1 2 4 8 12 16 20 24 28 30 32)
rate_limit=0
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
        log_file="/DS/dsg-blockchain/work/output/gfe_driver/sortledton/pr/test_gc_r${rate_limit}_graph22_${writer_threads}_${reader_threads}.log_4"

        /DS/dsg-blockchain/work/gfe_driver2/data/sortledton/pr/test_gc_rate_gfe_driver -G /DS/dsg-blockchain/nobackup/graph500/graph500-22.properties \
        -u --log /DS/dsg-blockchain/nobackup/graph500/graph500-22-1.0.graphlog \
        -l vortex -w "$writer_threads" -r "$reader_threads" --block_size 256 -d results.sqlite3 \
        --aging_timeout 2h -R 1 --latency 1 --mixed_workload true --blacklist lcc,sssp,wcc,bfs,cdlp --rate_limit "$rate_limit" > "$log_file"
        # done
    done
done