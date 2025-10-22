#!/bin/bash
# Manage cron jobs for email processor

case "$1" in
    "list")
        echo "Current cron jobs:"
        crontab -l 2>/dev/null | grep -E "(email_processor|run_email_processor)" || echo "No email processor jobs found"
        ;;
    "stop")
        echo "Stopping email processor cron jobs..."
        # Remove email processor jobs
        crontab -l 2>/dev/null | grep -v -E "(email_processor|run_email_processor)" | crontab -
        echo "Cron jobs removed"
        
        # Kill any running processes
        pkill -f email_processor.py 2>/dev/null && echo "Running processes killed" || echo "No running processes found"
        ;;
    "status")
        echo "Checking email processor status..."
        echo "Cron jobs:"
        crontab -l 2>/dev/null | grep -E "(email_processor|run_email_processor)" || echo "  None"
        echo "Running processes:"
        ps aux | grep -E "(email_processor|run_email_processor)" | grep -v grep || echo "  None"
        ;;
    "kill")
        echo "Killing running email processor processes..."
        pkill -f email_processor.py && echo "Processes killed" || echo "No processes to kill"
        ;;
    *)
        echo "Usage: $0 {list|stop|status|kill}"
        echo "  list   - Show current cron jobs"
        echo "  stop   - Remove cron jobs and kill processes"
        echo "  status - Show current status"
        echo "  kill   - Kill running processes only"
        exit 1
        ;;
esac
