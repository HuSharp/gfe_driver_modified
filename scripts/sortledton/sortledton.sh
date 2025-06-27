#!/bin/zsh

# Define the command to run
command="../build/gfe_driver_sortleton_profile -G /local/jinhaohu/graph/dataset/graph500-22.properties \
-u --log /local/jinhaohu/graph/dataset/graph500-22-1.0.graphlog \
-l sortledton.4 -w 20 -r 8 --block_size 512 -d results2.sqlite3 \
--aging_timeout 2h -R 1 --mixed_workload true  --blacklist lcc,sssp,cdlp,wcc,bfs"
# --mixed_workload true 
# Log directory and base log file name
log_dir="../logs"
log_base="profile_sortledton_w_20_r_8_mixed_pagerank_22.log"

# Start the for loop in nohup
nohup zsh -c "
for i in {0..10}; do
    $command > $log_dir/${log_base}_\$i 2>&1
done
" &
