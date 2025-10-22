#!/bin/bash
# Schedule the email_processor.py via crontab using a cron string
# Usage examples:
#   ./schedule_job.sh "*/30 * * * *"              # every 30 minutes
#   ./schedule_job.sh "0 */2 * * *"               # every 2 hours
#   ./schedule_job.sh "0 0 * * *"                # daily at midnight
#   ./schedule_job.sh "0 0 * * 0"                # weekly on Sunday
#   ./schedule_job.sh "0 0 1 * *"                # monthly on 1st
#   ./schedule_job.sh "*/15 * * * *" -a          # apply to crontab (default is dry-run)
#   ./schedule_job.sh "0 9 * * 1-5" -p /abs/path/to/email_processor.py

set -euo pipefail

APPLY=false
PYTHON_BIN=${PYTHON_BIN:-/usr/bin/python3}
PROCESSOR_PATH="/Users/jenilgandhi/Home/projects/Dev/scripts/run_email_processor.sh"
LOG_PATH="/Users/jenilgandhi/Home/projects/Dev/logs/email_processor.log"

print_help() {
  cat <<USAGE
Schedule the email processor using crontab.

Usage: $0 "CRON_STRING" [OPTIONS]

CRON_STRING: Standard cron expression (minute hour day month weekday)
  Examples:
    "*/30 * * * *"    # every 30 minutes
    "0 */2 * * *"     # every 2 hours  
    "0 0 * * *"       # daily at midnight
    "0 0 * * 0"       # weekly on Sunday
    "0 0 1 * *"       # monthly on 1st
    "0 9 * * 1-5"     # weekdays at 9 AM

Options:
  -a      Apply the entry to crontab (otherwise dry-run)
  -p PATH Absolute path to email_processor.py (default: $PROCESSOR_PATH)
  -b PATH Python binary path (default: $PYTHON_BIN)
  -l PATH Log file path (default: $LOG_PATH)
  -h      Show this help

Examples:
  $0 "*/30 * * * *"
  $0 "0 */6 * * *" -a
  $0 "0 2 * * *" -p /abs/path/email_processor.py
USAGE
}

# Parse arguments
CRON_STRING=""
while [[ $# -gt 0 ]]; do
  case $1 in
    -a) APPLY=true; shift ;;
    -p) PROCESSOR_PATH="$2"; shift 2 ;;
    -b) PYTHON_BIN="$2"; shift 2 ;;
    -l) LOG_PATH="$2"; shift 2 ;;
    -h|--help) print_help; exit 0 ;;
    -*)
      echo "Unknown option: $1" >&2
      print_help
      exit 1
      ;;
    *)
      if [[ -z "$CRON_STRING" ]]; then
        CRON_STRING="$1"
      else
        echo "Error: Multiple cron strings provided" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

# Validate cron string provided
if [[ -z "$CRON_STRING" ]]; then
  echo "Error: Cron string is required" >&2
  print_help
  exit 1
fi

# Validate cron string format (basic check for 5 fields)
# Count spaces to determine field count (should be 4 spaces = 5 fields)
SPACE_COUNT=$(echo "$CRON_STRING" | tr -cd ' ' | wc -c)
if [[ $SPACE_COUNT -ne 4 ]]; then
  echo "Error: Invalid cron string format. Expected 5 fields: minute hour day month weekday" >&2
  echo "Got: '$CRON_STRING' ($((SPACE_COUNT + 1)) fields)" >&2
  exit 1
fi

# Build command and cron entry
CMD="$PYTHON_BIN $PROCESSOR_PATH >> $LOG_PATH 2>&1"
ENTRY="$CRON_STRING $CMD"

echo "Cron entry:"
echo "$ENTRY"

if [[ "$APPLY" == true ]]; then
  # Install: keep existing entries, append ours if not present
  TMPFILE=$(mktemp)
  crontab -l 2>/dev/null > "$TMPFILE" || true
  
  # Avoid duplicate entries
  if grep -Fq "$CMD" "$TMPFILE"; then
    echo "Entry already exists; replacing it."
    grep -vF "$CMD" "$TMPFILE" > "${TMPFILE}.new" && mv "${TMPFILE}.new" "$TMPFILE"
  fi
  
  echo "$ENTRY" >> "$TMPFILE"
  crontab "$TMPFILE"
  rm -f "$TMPFILE"
  echo "Crontab updated."
else
  echo "Dry run. Use -a to apply to crontab."
fi