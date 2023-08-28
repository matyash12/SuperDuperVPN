#!/bin/bash
#this script is for reading info from wireguard


# Define the output directory
output_dir="/etc/wireguard/wireguard_logs"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Generate the filename using the current date and time
filename=$(date +"%Y-%m-%d_%H-%M-%S").txt

# Run the 'wg' command and save its output to the specified file
wg > "$output_dir/$filename"

# Optionally, you can add a message indicating that the command has been run
echo "WireGuard command executed and output saved to $output_dir/$filename"
