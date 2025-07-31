#!/bin/bash

# Script for setting up automatic Page Summarizer updates via cron

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up automatic Page Summarizer updates${NC}"
echo

# Get path to update script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATE_SCRIPT="$SCRIPT_DIR/update-app.sh"

# Make update script executable
chmod +x "$UPDATE_SCRIPT"

echo -e "${YELLOW}Available update options:${NC}"
echo "1. Every hour"
echo "2. Every 6 hours"
echo "3. Every day at 2:00"
echo "4. Every 30 minutes"
echo "5. Every week on Sunday at 3:00"
echo "6. Manual setup"
echo

read -p "Choose option (1-6): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 * * * *"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * *"
        ;;
    4)
        CRON_SCHEDULE="*/30 * * * *"
        ;;
    5)
        CRON_SCHEDULE="0 3 * * 0"
        ;;
    6)
        echo -e "${YELLOW}Enter cron schedule (e.g., 0 2 * * * for daily update at 2:00):${NC}"
        read -p "Cron schedule: " CRON_SCHEDULE
        ;;
    *)
        echo "Invalid choice. Using daily update at 2:00"
        CRON_SCHEDULE="0 2 * * *"
        ;;
esac

# Create temporary file with cron task
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null > "$TEMP_CRON"

# Add new task
echo "# Automatic Page Summarizer update" >> "$TEMP_CRON"
echo "$CRON_SCHEDULE $UPDATE_SCRIPT >> /var/log/page-summarizer-cron.log 2>&1" >> "$TEMP_CRON"

# Set new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo
echo -e "${GREEN}✅ Automatic updates configured!${NC}"
echo -e "${YELLOW}Schedule:${NC} $CRON_SCHEDULE"
echo -e "${YELLOW}Script:${NC} $UPDATE_SCRIPT"
echo -e "${YELLOW}Logs:${NC} /var/log/page-summarizer-cron.log"
echo

# Show current crontab
echo -e "${YELLOW}Current cron tasks:${NC}"
crontab -l

echo
echo -e "${GREEN}For manual update use:${NC}"
echo "sudo $UPDATE_SCRIPT"
echo
echo -e "${GREEN}To view logs:${NC}"
echo "tail -f /var/log/page-summarizer-cron.log"
echo
echo -e "${GREEN}To remove automatic updates:${NC}"
echo "crontab -e"
echo "Then delete the line with: $UPDATE_SCRIPT" 