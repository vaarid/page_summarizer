#!/bin/bash

# Script for updating Page Summarizer application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Log file
LOG_FILE="/var/log/page-summarizer-cron.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Starting Page Summarizer update process"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_message "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    log_message "${RED}Error: docker-compose.yml not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    log_message "${YELLOW}Warning: .env file not found, creating from envExample${NC}"
    if [ -f "envExample" ]; then
        cp envExample .env
        log_message "Created .env file from envExample"
    else
        log_message "${RED}Error: envExample file not found${NC}"
        exit 1
    fi
fi

# Stop current containers
log_message "Stopping current containers..."
docker-compose down >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log_message "${GREEN}Containers stopped successfully${NC}"
else
    log_message "${YELLOW}Warning: Some containers may not have been stopped${NC}"
fi

# Pull latest image
log_message "Pulling latest Docker image..."
docker pull vaarid/page-summarizer:latest >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log_message "${GREEN}Latest image pulled successfully${NC}"
else
    log_message "${RED}Error: Failed to pull latest image${NC}"
    exit 1
fi

# Create necessary directories
log_message "Creating necessary directories..."
mkdir -p logs data >> "$LOG_FILE" 2>&1

# Start containers
log_message "Starting containers with latest image..."
docker-compose up -d >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log_message "${GREEN}Containers started successfully${NC}"
else
    log_message "${RED}Error: Failed to start containers${NC}"
    exit 1
fi

# Wait for application to start
log_message "Waiting for application to start..."
sleep 30

# Check if application is running
log_message "Checking application status..."
if curl -f http://localhost:5000/health >> "$LOG_FILE" 2>&1; then
    log_message "${GREEN}Application is running and healthy${NC}"
else
    log_message "${YELLOW}Warning: Health check failed, but containers are running${NC}"
fi

# Clean up old images
log_message "Cleaning up old Docker images..."
docker image prune -f >> "$LOG_FILE" 2>&1

# Show container status
log_message "Container status:"
docker-compose ps >> "$LOG_FILE" 2>&1

log_message "${GREEN}Update process completed successfully${NC}"
log_message "Application available at: http://localhost:5000" 