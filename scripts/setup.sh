#!/bin/bash

echo "===== MCStatusBot Setup ====="
echo "This script will help you set up MCStatusBot"
echo

command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "Pip3 is required but not installed. Aborting."; exit 1; }

mkdir -p logs
mkdir -p cogs
mkdir -p utils
mkdir -p scripts
mkdir -p docker

chmod +x scripts/run.sh
chmod +x scripts/docker-run.sh
chmod +x scripts/setup.sh

echo "Installing dependencies..."
pip3 install -r requirements.txt

if grep -q "<PUT YOUR TOKEN>" config.json; then
    echo
    echo "===== Bot Configuration ====="
    echo "You need to configure your bot before running it."
    echo "Please edit the config.json file with your settings:"
    echo
    echo "1. Get a bot token from https://discord.com/developers/applications"
    echo "2. Add your Discord user ID as the owner_id"
    echo "3. Set your Discord server ID and channel ID for status updates"
    echo "4. Configure the Minecraft servers you want to monitor"
    echo
fi

echo "===== Deployment Options ====="
echo "Do you want to run the bot using Docker? (y/n)"
read -r use_docker

if [[ "$use_docker" =~ ^[Yy]$ ]]; then
    command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Please install Docker first."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Please install Docker Compose first."; exit 1; }
    
    echo "Starting bot with Docker Compose..."
    cd docker && docker-compose up -d
    
    echo
    echo "MCStatusBot is now running in a Docker container!"
    echo "Use 'docker-compose logs -f' to view the logs"
else
    echo "You can start the bot by running: ./scripts/run.sh"
fi

echo
echo "===== Setup Complete ====="
echo "Type '*help' in your Discord server to see available commands"
echo "Remember to run '*createstatusmsg' in your status channel to initialize the status message"