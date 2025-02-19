#!/bin/bash

# Check if directory parameter is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_path>"
    exit 1
fi

directory="$1"

# Check if directory exists
if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' does not exist"
    exit 1
fi

# Find all CSV files in the specified directory and process each one
for csv_file in "$directory"/*.csv; do
    # Check if file exists and is a regular file
    if [ -f "$csv_file" ]; then
        echo "Processing $csv_file..."
        nohup python3 figure_sortledton.py "$csv_file" &2>&1 &
    fi
done