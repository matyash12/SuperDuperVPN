#!/bin/bash
#This script is to be runned on host to communicate with wireguard


# Set the paths to the source and destination files
source_file="/etc/wireguard/edited_wg0.conf"
destination_file="/etc/wireguard/wg0.conf"

# Check if the source file exists
if [ -e "$source_file" ]; then
    # Check if the source and destination files are different
    if ! cmp -s "$source_file" "$destination_file"; then
        # Stop the wg-quick@wg0 service
        systemctl stop wg-quick@wg0

        # Copy the source file to the destination
        cp "$source_file" "$destination_file"
        echo "File copied successfully."

        # Start the wg-quick@wg0 service
        systemctl start wg-quick@wg0
    else
        echo "Source and destination files are identical. No need to copy."
    fi
else
    echo "Source file does not exist."
fi
