#!/bin/bash

echo "Starting MCStatusBot..."

while true; do
    python3 main.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 42 ]; then
        echo "Update completed. Restarting in 2 seconds..."
        sleep 2
    else
        if [ $EXIT_CODE -ne 0 ] && [ $EXIT_CODE -ne 130 ]; then
            echo "Bot crashed with exit code $EXIT_CODE. Restarting in 5 seconds..."
            sleep 5
        else
            echo "Bot terminated with exit code $EXIT_CODE. Exiting..."
            break
        fi
    fi
done