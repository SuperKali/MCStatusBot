#!/bin/bash


while true; do
    echo "Starting MCStatusBot..."
    python main.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 42 ]; then
        echo "Update completed. Restarting..."
        sleep 2
    else
        echo "Bot terminated with exit code $EXIT_CODE"
        break
    fi
done