# Email Attachment Processor

A configurable cron job system for fetching email attachments, parsing them, and storing them in a datastore.

## 📁 Project Structure

```
email-cron-job/
├── src/                          # Source code
│   ├── email_processor.py        # Main email processor
│   └── demo_mock_data.py         # Mock data generator
├── scripts/                      # Management scripts
│   ├── schedule_job.sh           # Cron job scheduler
│   ├── manage_cron.sh            # Cron job manager
│   └── run_email_processor.sh    # Wrapper script for cron
├── config/                       # Configuration files
│   ├── config.env               # Environment configuration
│   └── crontab_example          # Cron job examples
├── logs/                         # Log files
│   └── email_processor.log       # Main log file
├── docs/                         # Documentation
│   └── README.md                 # This file
├── email_processor.py            # Main entry point
├── setup.sh                     # Setup script
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Run the setup script
./setup.sh

# Or manually:
pip install -r requirements.txt
```

### 2. Configure Settings
Edit `config/config.env` with your actual configuration:
```bash
# Email API Configuration
EMAIL_API_URL=https://your-email-api.com/emails
EMAIL_API_KEY=your_actual_api_key
EMAIL_API_SECRET=your_actual_api_secret

# DataStore Configuration
DATASTORE_API_URL=https://your-datastore-api.com/upload
DATASTORE_API_KEY=your_actual_datastore_key
```

### 3. Test with Mock Data
```bash
# Generate mock data
python3 src/demo_mock_data.py

# Test the processor
python3 email_processor.py
```

### 4. Schedule Jobs
```bash
# Schedule every minute
./scripts/schedule_job.sh "* * * * *" -a

# Schedule every 30 minutes
./scripts/schedule_job.sh "*/30 * * * *" -a

# Schedule daily at midnight
./scripts/schedule_job.sh "0 0 * * *" -a
```

## 📋 Features

- **Configurable Parameters**: All settings managed through environment variables
- **Mock Data Support**: Includes demo data for testing without real email API
- **Flexible File Processing**: Supports various file types (PDF, DOC, DOCX, TXT, CSV, XLSX)
- **Size Filtering**: Configurable file size limits
- **Parallel Processing**: Concurrent processing of multiple attachments
- **Retry Logic**: Built-in retry mechanism for failed operations
- **Logging**: Comprehensive logging with configurable levels
- **Notifications**: Optional notification system for processing results
- **Cron Job Ready**: Designed to run as scheduled cron jobs

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_API_URL` | Email API endpoint | Required |
| `EMAIL_API_KEY` | Email API authentication key | Required |
| `EMAIL_API_SECRET` | Email API secret | Required |
| `EMAIL_ADDRESS` | Email address to process | Optional |
| `DATASTORE_API_URL` | Datastore upload endpoint | Required |
| `DATASTORE_API_KEY` | Datastore authentication key | Required |
| `DATASTORE_BUCKET` | Datastore bucket name | `email-attachments` |
| `ATTACHMENT_TYPES` | Comma-separated file types | `pdf,doc,docx,txt,csv,xlsx` |
| `MAX_ATTACHMENT_SIZE_MB` | Maximum file size in MB | `10` |
| `PROCESSING_BATCH_SIZE` | Number of emails to process at once | `5` |
| `MAX_WORKERS` | Number of parallel workers for attachment processing | `4` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `LOG_FILE` | Log file path | `./logs/email_processor.log` |
| `RETRY_ATTEMPTS` | Number of retry attempts | `3` |
| `RETRY_DELAY_SECONDS` | Delay between retries | `30` |
| `NOTIFICATION_EMAIL` | Email for notifications | Optional |
| `ENABLE_NOTIFICATIONS` | Enable/disable notifications | `true` |

## 🔧 Usage

### Running the Processor
```bash
# Run once
python3 email_processor.py

# Run with specific log level
LOG_LEVEL=DEBUG python3 email_processor.py
```

### Scheduling Jobs
```bash
# Dry run (prints the cron line)
./scripts/schedule_job.sh "*/30 * * * *"

# Apply to crontab
./scripts/schedule_job.sh "*/30 * * * *" -a

# Every 2 hours
./scripts/schedule_job.sh "0 */2 * * *" -a

# Daily at midnight
./scripts/schedule_job.sh "0 0 * * *" -a

# Weekly on Sunday
./scripts/schedule_job.sh "0 0 * * 0" -a

# Monthly on 1st
./scripts/schedule_job.sh "0 0 1 * *" -a
```

### Managing Jobs
```bash
# Check status
./scripts/manage_cron.sh status

# Stop all jobs
./scripts/manage_cron.sh stop

# Kill running processes
./scripts/manage_cron.sh kill

# List current jobs
./scripts/manage_cron.sh list
```

## 📊 Monitoring

### View Logs
```bash
# Watch logs in real-time
tail -f logs/email_processor.log

# View recent logs
tail -20 logs/email_processor.log

# Search for specific patterns
grep "ERROR" logs/email_processor.log
```

### Check Status
```bash
# Check if jobs are scheduled
./scripts/manage_cron.sh status

# Check cron jobs directly
crontab -l

# Check running processes
ps aux | grep email_processor
```

## 🛠️ Development

### Project Structure
- **`src/`**: Main source code
- **`scripts/`**: Management and scheduling scripts
- **`config/`**: Configuration files
- **`logs/`**: Log files
- **`docs/`**: Documentation

### Adding Features
1. **New file types**: Update `ATTACHMENT_TYPES` in config and implement parsing logic
2. **New datastore**: Implement upload logic in `upload_to_datastore()` method
3. **New notifications**: Implement notification logic in `send_notification()` method

### Testing
```bash
# Generate mock data
python3 src/demo_mock_data.py

# Test processor
python3 email_processor.py

# Test with debug logging
LOG_LEVEL=DEBUG python3 email_processor.py
```

## 🔒 Security Considerations

- Store sensitive configuration in environment variables
- Use secure authentication methods for APIs
- Implement proper access controls for datastore
- Regular security updates for dependencies
- Monitor logs for suspicious activity

## 📝 License

This project is open source. Please check the license file for details.