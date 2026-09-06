#!/bin/bash
# Script to run Docker Compose with proper user permissions

# Get current user ID and group ID
export UID=$(id -u)
export GID=$(id -g)

# Create directories with proper permissions if they don't exist
mkdir -p ./instance ./data
chmod 755 ./instance ./data

echo "Starting Todo Manager with user ID: $UID, group ID: $GID"
echo "This ensures that files created in volumes have correct ownership."

# Run Docker Compose with environment variables
docker-compose up "$@"
