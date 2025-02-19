#!/bin/bash

# Find all CSV files and process each one
for csv_file in ../data/vortex/24_update_s1_100/*.csv; do
    # Check if file exists and is a regular file
    if [ -f "$csv_file" ]; then
        echo "Processing $csv_file..."
        # nohup python3 figure_sortledton.py ../build/"$csv_file" &2>&1 &
        nohup python3 figure_vortex.py "$csv_file" &2>&1 &
    fi
done