# Email Attachment Processor

This repository runs a cron job that fetches email attachments (Gmail IMAP), parses them, uploads to Google Cloud Storage (GCS), and sends notifications via SendGrid.

## Quick start

1. Create a Python virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy and edit `config/config.env` with your secrets and configuration. Important variables:

- EMAIL_ADDRESS - Gmail address (e.g. dev42a@gmail.com)
- EMAIL_PASSWORD - Gmail app password (or OAuth token if configured)
- IMAP_SERVER - normally `imap.gmail.com`
- IMAP_PORT - `993`
- EMAIL_API_KEY - SendGrid API key
- NOTIFICATION_EMAIL - where to send run reports
- DATASTORE_TYPE - set to `GCS`
- DATASTORE_PROJECT_ID - GCS project id
- DATASTORE_CREDENTIALS_FILE - absolute path to GCS JSON credentials
- DATASTORE_BUCKET - bucket name to upload attachments
- PROCESSING_BATCH_SIZE - number of emails to fetch per run (default in config)
- TARGET_SENDER - optional: search for emails from this sender

4. Run locally (mock mode):

```bash
python src/email_processor.py  # by default will use test_mode=False; pass env TEST_MODE=1 for mock
```

To run in targeted/mock mode:

```bash
# targeted sender
TARGET_SENDER=someone@example.com python src/email_processor.py

# mock test
TEST_MODE=1 python src/email_processor.py
```

## Tests

- Unit tests and integration tests are in `tests/`.

Run all tests:

```bash
pytest -q
```

Integration tests that require GCS or Gmail credentials will fail if the `config/config.env` is missing required values — these tests can be skipped by setting relevant env vars or running only unit tests.

## Cron

A helper script is provided in `scripts/schedule_job.sh` and `scripts/run_email_processor.sh`. Example crontab entry to run every hour:

```cron
0 * * * * /Users/$(whoami)/Downloads/Dev/scripts/run_email_processor.sh >> /var/log/email_processor.log 2>&1
```

To install the crontab using the helper script (will prompt):

```bash
bash scripts/schedule_job.sh
```
