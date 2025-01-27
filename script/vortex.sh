#!/bin/zsh

# Define the command to run
command="../build/gfe_driver_vortex_s0 -G /local/jinhaohu/graph/dataset/graph500-22.properties \
-u --log /local/jinhaohu/graph/dataset/graph500-22-1.0.graphlog \
-l sortledton.4 -w 8 -r 8 --block_size 512 -d results.sqlite3 \
--aging_timeout 2h -R 1 --mixed_workload true --blacklist lcc,sssp"

# --mixed_workload true
# Log directory and base log file name
log_dir="../logs"
log_base="vortex_mixed_all_22_log_contention_100000_snapshot_0.log"

# Start the for loop in nohup
nohup zsh -c "
for i in {0..10}; do
    $command > $log_dir/${log_base}_\$i 2>&1
done
" &
