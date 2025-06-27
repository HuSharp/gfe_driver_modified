#!/bin/bash
# writer_threads_values=(16 32 48)
# reader_threads_values=(1 2 4 8 12 16 20 24 28 30 32)
writer_threads_values=(48)
reader_threads_values=(1 32)
contention_values=(8 128 256 300 450 500 512)
elapsed_time_values=(500)
rate_limit=0
# writer_threads_values=(1)
# reader_threads_values=(2 12 16 20 24 28 30 32)
# reader_threads_values=32
# writer_threads_values=(31 30 28 24 20 16 12 8   4  1)
# reader_threads_values=(1 2   4  8 12 16 20 24 28 31)

# writer_threads_values=(12 8 4 2 1)
# reader_threads_values=(20 24 28 30 31)

SCRIPT_DIR="/DS/dsg-blockchain/work"
export LD_LIBRARY_PATH=$SCRIPT_DIR:$LD_LIBRARY_PATH

for i in "${contention_values[@]}"; do
    contention=$i
    echo "Contention: $contention"
    for j in "${elapsed_time_values[@]}"; do
        elapsed_time=$j
        echo "Elapsed Time: $elapsed_time"
        for index in "${!writer_threads_values[@]}"; do
            writer_threads=${writer_threads_values[$index]}
            # reader_threads=${reader_threads_values[$index]}
            for reader_threads in "${reader_threads_values[@]}"; do
                # for run in {1..4}; do
                # echo "Run #$run"
                log_file="/DS/dsg-blockchain/work/output/gfe_driver/vortex/c${contention}_s1/pr/notime_pointer1_graph22_s1_c${contention}_e${elapsed_time}_r${rate_limit}_w${writer_threads}_r${reader_threads}.log"

                # if [ "$run" -eq 4 ]; then
                /DS/dsg-blockchain/work/gfe_driver2/data/vortex/rollback_single/pr/nogc_pointer1_contention_e_gfe_driver -G /DS/dsg-blockchain/nobackup/graph500/graph500-22.properties \
                -u --log /DS/dsg-blockchain/nobackup/graph500/graph500-22-1.0.graphlog \
                -l vortex -w "$writer_threads" -r "$reader_threads" --block_size 256 -d results.sqlite3 \
                --aging_timeout 2h -R 1 --latency 1 --mixed_workload true --blacklist lcc,sssp,cdlp,bfs,wcc \
                --contention "$contention" --elapsed_time "$elapsed_time" --rate_limit "$rate_limit" > "$log_file"
            # fi
            done
        done
    done
done
