#!/bin/bash

# Get the directory where this script is located
script_dir="$(dirname "$0")"

# Define an array of script names
script_array=("wireguard_logs.sh" "apply_wireguard_conf.sh")

# Loop through the array and execute each script from the same directory
for script in "${script_array[@]}"; do
    full_script_path="$script_dir/$script"
    if [ -f "$full_script_path" ]; then
        echo "Running $script..."
        bash "$full_script_path"
        echo "Finished running $script."
    else
        echo "Script $script not found in $script_dir."
    fi
done
