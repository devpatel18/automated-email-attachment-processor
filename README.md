# Email Attachment Parser - TypeScript

Automated email attachment processor that fetches CSV/Excel files from targeted Gmail senders, parses them, and displays the data in a beautiful ASCII table format. Runs as a Node.js cron job with a built-in REST API.

## 🎯 What This Does

1. **Connects to Gmail** via IMAP every 2 minutes (configurable)
2. **Searches for emails** from specific senders with "Company Report" in the subject
3. **Downloads CSV/Excel attachments** from those emails
4. **Parses the data** and extracts rows and columns
5. **Displays in console** as a formatted ASCII table
6. **Provides REST API** to access the parsed data

## ⚡ Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your details
nano .env
```

Required configuration:
```env
# Your Gmail credentials
EMAIL_ADDRESS=dev42a@gmail.com
EMAIL_PASSWORD=your-gmail-app-password

# Filter by these senders (comma-separated)
TARGET_SENDERS=sender1@example.com,sender2@example.com

# Only process emails with this in the subject
TARGET_SUBJECT=Company Report

# How often to check (every 2 minutes by default)
CRON_SCHEDULE=*/2 * * * *

# API server port
PORT=3000
```

### 3. Generate Gmail App Password

⚠️ **Important**: You need a Gmail App Password, not your regular password.

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Generate new app password for "Mail"
5. Copy the 16-character password to `.env` as `EMAIL_PASSWORD`

### 4. Run the Application
```bash
npm start
```

The server will:
- ✅ Start on `http://localhost:3000`
- ✅ Run immediately to fetch emails
- ✅ Schedule cron job to run every 2 minutes
- ✅ Display parsed data in console as ASCII tables

## 📋 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `EMAIL_ADDRESS` | ✅ Yes | Your Gmail address | `dev42a@gmail.com` |
| `EMAIL_PASSWORD` | ✅ Yes | Gmail App Password | `abcd efgh ijkl mnop` |
| `TARGET_SENDERS` | ⚠️ Recommended | Comma-separated sender emails | `sales@company.com,finance@company.com` |
| `TARGET_SUBJECT` | ⚠️ Recommended | Filter by subject (partial match) | `Company Report` |
| `CRON_SCHEDULE` | ❌ Optional | Cron expression | `*/2 * * * *` (every 2 minutes) |
| `PORT` | ❌ Optional | API server port | `3000` |
| `IMAP_SERVER` | ❌ Optional | IMAP server | `imap.gmail.com` |
| `IMAP_PORT` | ❌ Optional | IMAP port | `993` |

### Cron Schedule Examples

```env
*/2 * * * *      # Every 2 minutes (default)
*/5 * * * *      # Every 5 minutes
*/10 * * * *     # Every 10 minutes
0 * * * *        # Every hour
0 9 * * *        # Daily at 9 AM
0 9,17 * * *     # Daily at 9 AM and 5 PM
0 9 * * 1-5      # Weekdays at 9 AM
```

Use [crontab.guru](https://crontab.guru/) to test cron expressions.

## 🚀 Commands

```bash
# Start the application (build + run)
npm start

# Build TypeScript to JavaScript
npm run build

# Development mode with auto-reload
npm run dev

# Watch mode (auto-rebuild on changes)
npm run watch
```

## 📡 REST API Endpoints

Once running, access these endpoints:

### `GET http://localhost:3000/`
Server status and information
```json
{
  "status": "running",
  "message": "Email Attachment Parser - TypeScript Edition",
  "uptime": 123.45,
  "lastProcessed": "2025-10-24T10:30:00.000Z",
  "cronSchedule": "*/2 * * * *"
}
```

### `GET http://localhost:3000/api/latest`
Latest parsed data in JSON format
```json
{
  "data": {
    "filename": "report.csv",
    "rows": [...],
    "columns": ["Name", "Email", "Amount"],
    "rowCount": 100,
    "columnCount": 3
  },
  "processedAt": "2025-10-24T10:30:00.000Z"
}
```

### `GET http://localhost:3000/api/table`
Latest data as ASCII table (plain text)

### `POST http://localhost:3000/api/trigger`
Manually trigger email fetch and parsing
```bash
curl -X POST http://localhost:3000/api/trigger
```

### `GET http://localhost:3000/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T10:30:00.000Z",
  "uptime": 123.45
}
```

## 📊 How It Works

### The Flow

```
npm start
    ↓
Server starts on port 3000
    ↓
Cron job scheduled (every 2 minutes)
    ↓
Runs immediately once
    ↓
╔════════════════════════════════════════╗
║  Every 2 minutes (or manual trigger)   ║
╚════════════════════════════════════════╝
    ↓
1. Connect to Gmail via IMAP
    ↓
2. Search for emails from TARGET_SENDERS
    ↓
3. Filter by TARGET_SUBJECT ("Company Report")
    ↓
4. Download CSV/Excel attachments
    ↓
5. Parse the file (extract rows/columns)
    ↓
6. Format as ASCII table
    ↓
7. Print to console
    ↓
8. Cache for API access
```

### File Processing

- ✅ **CSV files** (`.csv`) - Parsed with csv-parser
- ✅ **Excel files** (`.xlsx`, `.xls`) - Parsed with xlsx library
- ❌ **Other files** - Ignored (PDF, DOC, etc.)

### Email Filtering

**Multiple Senders**: Processes emails from ANY of the listed senders
```env
TARGET_SENDERS=sender1@company.com,sender2@company.com,sender3@company.com
```

**Subject Matching**: Case-insensitive partial match
```env
TARGET_SUBJECT=Company Report
```
Matches:
- ✅ "Company Report"
- ✅ "Daily Company Report"
- ✅ "Company Report - October 2025"
- ✅ "RE: Company Report Analysis"

## 📊 Example Console Output

```
================================================================================
🚀 EMAIL ATTACHMENT PARSER - TYPESCRIPT EDITION
================================================================================

✅ Server running on http://localhost:3000

📡 Available endpoints:
   GET  /              - Server status
   GET  /api/latest    - Latest parsed data (JSON)
   GET  /api/table     - Latest data as table (text)
   POST /api/trigger   - Manually trigger parsing
   GET  /health        - Health check

⏰ Cron Schedule: */2 * * * *
================================================================================

⏰ Cron job scheduled: */2 * * * *

🔄 Running initial fetch...

================================================================================
🚀 Starting email fetch and parse process...
⏰ Time: 10/24/2025, 10:30:00 AM
================================================================================

🔍 Connecting to email server...
✅ Connected to email server
📬 Inbox opened. Total messages: 42
📧 Filtering emails from 2 sender(s): sales@company.com, finance@company.com
📋 Filtering by subject: "Company Report"
📧 Found 5 email(s) from sales@company.com, finance@company.com
📨 Processing message #5
📬 Email Subject: Daily Company Report
👤 From: sales@company.com
📅 Date: Thu, 24 Oct 2025 09:00:00 +0000
✅ Subject matches filter: "Company Report"
📎 Found 1 attachment(s)
✅ Found CSV attachment: sales-report.csv

✅ Successfully fetched attachment: sales-report.csv

📄 Parsing CSV file: sales-report.csv
📦 File size: 15.32 KB
✅ Parsed 100 rows and 5 columns

================================================================================
📊 Data from: sales-report.csv
📈 Total Rows: 100 | Columns: 5
================================================================================

┌──────────────────┬──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Product          │ Quantity         │ Price            │ Total            │ Date             │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Widget A         │ 100              │ 10.50            │ 1050.00          │ 2025-10-01       │
│ Widget B         │ 50               │ 25.00            │ 1250.00          │ 2025-10-02       │
│ Widget C         │ 75               │ 15.75            │ 1181.25          │ 2025-10-03       │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────┘

================================================================================

📊 DATA SUMMARY
────────────────────────────────────────
Filename: sales-report.csv
Rows: 100
Columns: 5
Column Names: Product, Quantity, Price, Total, Date
────────────────────────────────────────

✅ Processing completed successfully!
```

## 🏗️ Project Structure

```
automated-email-attachment-processor/
│
├── src/                          # TypeScript source code
│   ├── server.ts                 # Main: Express server + cron scheduler
│   ├── emailProcessor.ts         # Gmail IMAP fetching
│   ├── parser.ts                 # CSV/Excel parsing & formatting
│   └── types/
│       └── mailparser.d.ts       # Type definitions
│
├── dist/                         # Compiled JavaScript (auto-generated)
├── node_modules/                 # Dependencies
│
├── .env                          # Your configuration (create from .env.example)
├── .env.example                  # Configuration template
├── package.json                  # Dependencies & scripts
├── tsconfig.json                 # TypeScript config
└── README.md                     # This file
```

## 🛠️ Technologies

- **TypeScript** - Type-safe JavaScript
- **Node.js** - Runtime environment
- **Express** - Web server framework
- **node-cron** - Cron job scheduling
- **imap** - Gmail IMAP connection
- **mailparser** - Email parsing
- **csv-parser** - CSV file parsing
- **xlsx** - Excel file parsing (XLSX/XLS)
- **cli-table3** - ASCII table formatting

## 🔧 Troubleshooting

### "Email credentials not configured"
- **Problem**: Missing `EMAIL_ADDRESS` or `EMAIL_PASSWORD` in `.env`
- **Solution**: Add both to your `.env` file

### "Authentication failed"
- **Problem**: Invalid Gmail App Password
- **Solution**: Generate a new App Password from Google Account Settings

### "No emails found"
- **Problem**: `TARGET_SENDERS` doesn't match any emails
- **Solution**: 
  - Verify sender email addresses
  - Temporarily remove `TARGET_SENDERS` to test all emails
  - Check your Gmail inbox manually

### "Subject doesn't match filter"
- **Problem**: `TARGET_SUBJECT` is too specific
- **Solution**: Use a more general phrase (e.g., "Report" instead of "Full Company Report Q4 2025")

### "Port 3000 already in use"
- **Problem**: Another application is using port 3000
- **Solution**: Change `PORT=3001` in `.env` or kill the process:
  ```bash
  lsof -ti:3000 | xargs kill -9
  ```

### TypeScript compilation errors
- **Solution**: 
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  npm run build
  ```

## 📝 License

ISC
