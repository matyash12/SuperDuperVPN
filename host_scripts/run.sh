#!/bin/bash

# Define an array of script names
script_array=("wireguard_logs.sh","apply_wireguard_conf.sh")

# Loop through the array and execute each script
for script in "${script_array[@]}"; do
    if [ -f "$script" ]; then
        echo "Running $script..."
        bash "$script"
        echo "Finished running $script."
    else
        echo "Script $script not found."
    fi
done
