#!/usr/bin/env python3
"""
Email Attachment Processor Cron Job

This script fetches email attachments from an email API, parses them,
and stores them in a datastore. It's designed to run as a cron job.
"""

import os
import sys
import json
import logging
import time
import requests
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from google.cloud import storage
import imaplib
import email
from email.header import decode_header
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Load environment variables
load_dotenv('config/config.env')

class EmailProcessor:
    """Main class for processing email attachments"""
    
    def __init__(self):
        """Initialize the email processor with configuration"""
        self.setup_logging()
        self.load_config()
        self.session = requests.Session()
        self.setup_session()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_file = os.getenv('LOG_FILE', '/tmp/email_processor.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load configuration from environment variables"""
        self.config = {
            # Email Configuration (SendGrid)
            'email_api_url': os.getenv('EMAIL_API_URL'),
            'email_api_key': os.getenv('EMAIL_API_KEY'),
            'email_address': os.getenv('EMAIL_ADDRESS'),
            
            # Email Account Settings (Gmail)
            'email_password': os.getenv('EMAIL_PASSWORD'),
            'imap_server': os.getenv('IMAP_SERVER'),
            'imap_port': int(os.getenv('IMAP_PORT', '993')),
            
            # GCS Configuration
            'datastore_type': os.getenv('DATASTORE_TYPE'),
            'datastore_project_id': os.getenv('DATASTORE_PROJECT_ID'),
            'datastore_credentials_file': os.getenv('DATASTORE_CREDENTIALS_FILE'),
            'datastore_bucket': os.getenv('DATASTORE_BUCKET'),
            'datastore_location': os.getenv('DATASTORE_LOCATION'),
            
            # Processing Configuration
            'attachment_types': os.getenv('ATTACHMENT_TYPES', 'pdf,doc,docx,txt,csv,xlsx').split(','),
            'max_attachment_size_mb': int(os.getenv('MAX_ATTACHMENT_SIZE_MB', '25')),
            'processing_batch_size': int(os.getenv('PROCESSING_BATCH_SIZE', '5')),
            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', '3')),
            'retry_delay_seconds': int(os.getenv('RETRY_DELAY_SECONDS', '30')),
            
            # Notification Settings
            'notification_email': os.getenv('NOTIFICATION_EMAIL'),
            'enable_notifications': os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        }
        
        # Initialize GCS client
        if self.config['datastore_type'] == 'GCS':
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config['datastore_credentials_file']
            self.storage_client = storage.Client(project=self.config['datastore_project_id'])
            self.bucket = self.storage_client.bucket(self.config['datastore_bucket'])
        
        # Validate required configuration
        required_fields = [
            'email_api_key',           # SendGrid API key
            'email_address',           # Gmail address
            'email_password',          # Gmail app password
            'imap_server',            # Gmail IMAP server
            'datastore_bucket',       # GCS bucket name
            'datastore_project_id',   # GCS project ID
            'datastore_credentials_file'  # GCS credentials file
        ]
        
        missing_fields = [field for field in required_fields if not self.config[field]]
        
        if missing_fields:
            self.logger.error(f"Missing required configuration: {missing_fields}")
            sys.exit(1)
            
    def setup_session(self):
        """Setup HTTP session with authentication"""
        self.session.headers.update({
            'Authorization': f"Bearer {self.config['email_api_key']}",
            'Content-Type': 'application/json',
            'User-Agent': 'EmailProcessor/1.0'
        })
        
    def fetch_emails(self, use_mock: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch emails from either mock data or Gmail
        
        Args:
            use_mock: If True, use mock data instead of actual Gmail
        
        Returns:
            List of email objects with attachments
        """
        if use_mock:
            self.logger.info("Using mock email data for testing...")
            # Import from package path so tests running from workspace can resolve module
            from src.demo_mock_data import MockDataGenerator
            mock_emails = MockDataGenerator.generate_sample_emails()
            self.logger.info(f"Loaded {len(mock_emails)} mock emails")
            return mock_emails
            
        self.logger.info("Fetching emails from Gmail...")
        emails = []
        
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['email_address'], self.config['email_password'])
            
            # Select inbox
            mail.select('inbox')

            # Search for recent unread emails (last 24 hours)
            date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
            self.logger.info(f"Searching for emails since {date}")

            # Get total unread count
            try:
                _, all_messages = mail.search(None, 'UNSEEN')
                all_unread = all_messages[0].split() if all_messages and all_messages[0] else []
            except Exception:
                all_unread = []
            self.logger.info(f"Total unread emails: {len(all_unread)}")

            # Now search with date filter (default: recent unread)
            target_sender = os.getenv('TARGET_SENDER')
            if target_sender:
                # If a target sender is specified, search ALL mail for messages from that sender (ignore read/unread)
                self.logger.info(f"TARGET_SENDER set: will search for messages from {target_sender}")
                try:
                    # Use FROM search on ALL mailbox
                    mail.select('inbox')
                    _, messages = mail.search(None, f'FROM "{target_sender}"')
                    email_ids = messages[0].split() if messages and messages[0] else []
                except Exception as e:
                    self.logger.error(f"Error searching for TARGET_SENDER {target_sender}: {e}")
                    email_ids = []
                self.logger.info(f"Found {len(email_ids)} messages from {target_sender}")
            else:
                try:
                    _, messages = mail.search(None, f'(SINCE {date}) UNSEEN')
                    email_ids = messages[0].split() if messages and messages[0] else []
                except Exception:
                    email_ids = []
                self.logger.info(f"Unread emails in last 24 hours: {len(email_ids)}")

            # Show details of up to 3 sample emails for debugging
            for idx, eid in enumerate(email_ids[:3]):
                try:
                    _, msg_data = mail.fetch(eid, '(RFC822)')
                    sample_msg = email.message_from_bytes(msg_data[0][1])
                    self.logger.debug(f"Sample {idx+1} - Subject: {sample_msg.get('subject')}")
                    self.logger.debug(f"Sample {idx+1} - From: {sample_msg.get('from')}")
                    self.logger.debug(f"Sample {idx+1} - Date: {sample_msg.get('date')}")
                    sample_has_attachments = any(part.get_filename() for part in sample_msg.walk())
                    self.logger.debug(f"Sample {idx+1} - Has attachments: {sample_has_attachments}")
                except Exception as e:
                    self.logger.error(f"Error fetching sample email {eid}: {e}")

            # Limit the number of emails to process (configurable)
            max_emails = int(os.getenv('PROCESSING_BATCH_SIZE', '10'))
            if len(email_ids) > max_emails:
                self.logger.info(f"Limiting to {max_emails} emails out of {len(email_ids)} found")
                email_ids = email_ids[:max_emails]
            else:
                self.logger.info(f"Processing all {len(email_ids)} emails")

            for email_id in email_ids:
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                # Decode subject
                subject = decode_header(message['subject'])[0]
                if isinstance(subject[0], bytes):
                    try:
                        subject = subject[0].decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            subject = subject[0].decode('latin1')
                        except UnicodeDecodeError:
                            subject = "Undecodable Subject"
                else:
                    subject = subject[0] or "No Subject"
                
                # Get sender
                sender = message['from']
                
                # Process attachments
                attachments = []
                
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        # Get file content
                        content = part.get_payload(decode=True)
                        content_type = part.get_content_type()
                        # Debug information (reduced verbosity)
                        self.logger.debug(f"Found attachment: {filename}")
                        self.logger.debug(f"Content type: {content_type}")
                        self.logger.debug(f"Size: {len(content)} bytes")

                        attachments.append({
                            'filename': filename,
                            'size': len(content),
                            'content_type': content_type,
                            'data': base64.b64encode(content).decode('utf-8')
                        })
                
                if attachments:
                    emails.append({
                        'id': email_id.decode(),
                        'subject': subject,
                        'sender': sender,
                        'date': message['date'],
                        'attachments': attachments
                    })
            
            mail.close()
            mail.logout()
            
            self.logger.info(f"Fetched {len(emails)} emails with attachments")
            return emails
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []
    
    def get_mock_emails(self) -> List[Dict[str, Any]]:
        """
        Get mock email data for testing
        
        Returns:
            List of mock email objects
        """
        mock_emails = [
            {
                "id": "email_001",
                "subject": "Monthly Report - Q1 2024",
                "sender": "reports@company.com",
                "date": "2024-01-15T10:30:00Z",
                "attachments": [
                    {
                        "filename": "monthly_report.pdf",
                        "size": 2048576,  # 2MB
                        "content_type": "application/pdf",
                        "data": "base64_encoded_pdf_data_here"
                    },
                    {
                        "filename": "data_analysis.xlsx",
                        "size": 1024000,  # 1MB
                        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "data": "base64_encoded_xlsx_data_here"
                    }
                ]
            },
            {
                "id": "email_002",
                "subject": "Invoice #12345",
                "sender": "billing@vendor.com",
                "date": "2024-01-14T14:20:00Z",
                "attachments": [
                    {
                        "filename": "invoice_12345.pdf",
                        "size": 512000,  # 500KB
                        "content_type": "application/pdf",
                        "data": "base64_encoded_invoice_data_here"
                    }
                ]
            },
            {
                "id": "email_003",
                "subject": "Contract Documents",
                "sender": "legal@lawfirm.com",
                "date": "2024-01-13T09:15:00Z",
                "attachments": [
                    {
                        "filename": "contract_agreement.docx",
                        "size": 1536000,  # 1.5MB
                        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "data": "base64_encoded_docx_data_here"
                    },
                    {
                        "filename": "terms_conditions.txt",
                        "size": 25600,  # 25KB
                        "content_type": "text/plain",
                        "data": "base64_encoded_txt_data_here"
                    }
                ]
            }
        ]
        
        self.logger.debug(f"Using mock data: {len(mock_emails)} emails")
        return mock_emails
    
    def filter_attachments(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter attachments based on type and size constraints
        
        Args:
            attachments: List of attachment objects
            
        Returns:
            Filtered list of attachments
        """
        filtered = []
        max_size_bytes = self.config['max_attachment_size_mb'] * 1024 * 1024
        
        for attachment in attachments:
            # Check file type
            filename = attachment.get('filename', '')
            file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
            
            if file_extension not in self.config['attachment_types']:
                self.logger.warning(f"Skipping attachment {filename} - unsupported type")
                continue
                
            # Check file size
            if attachment.get('size', 0) > max_size_bytes:
                self.logger.warning(f"Skipping attachment {filename} - too large")
                continue
                
            filtered.append(attachment)
            
        return filtered
    
    def parse_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse attachment content (placeholder for future implementation)
        
        Args:
            attachment: Attachment object with metadata and data
            
        Returns:
            Parsed attachment data
        """
        self.logger.debug(f"Parsing attachment: {attachment.get('filename')}")
        
        # TODO: Implement actual parsing logic based on file type
        # This is a placeholder for future implementation
        
        parsed_data = {
            'filename': attachment.get('filename'),
            'content_type': attachment.get('content_type'),
            'size': attachment.get('size'),
            'parsed_content': None,  # Will be populated by actual parsing logic
            'metadata': {
                'parsed_at': datetime.now().isoformat(),
                'parser_version': '1.0.0',
                'status': 'pending_implementation'
            }
        }
        
        self.logger.debug(f"Parsing completed for {attachment.get('filename')}")
        return parsed_data
    
    def upload_to_datastore(self, parsed_attachment: Dict[str, Any]) -> bool:
        """
        Upload parsed attachment to Google Cloud Storage
        
        Args:
            parsed_attachment: Parsed attachment data
            
        Returns:
            True if upload successful, False otherwise
        """
        filename = parsed_attachment.get('filename')
        self.logger.info(f"Uploading to GCS: {filename}")
        
        try:
            # Create blob
            current_date = datetime.now().strftime('%Y/%m/%d')
            blob_path = f"{current_date}/{filename}"
            blob = self.bucket.blob(blob_path)
            
            # Set metadata
            metadata = {
                'content_type': parsed_attachment.get('content_type'),
                'original_size': str(parsed_attachment.get('size')),
                'parsed_at': parsed_attachment.get('metadata', {}).get('parsed_at'),
                'parser_version': parsed_attachment.get('metadata', {}).get('parser_version'),
                'uploaded_at': datetime.now().isoformat()
            }
            blob.metadata = metadata
            
            # Upload the content
            data = base64.b64decode(parsed_attachment.get('data', ''))
            blob.upload_from_string(
                data,
                content_type=parsed_attachment.get('content_type')
            )
            
            self.logger.info(f"Successfully uploaded {filename} to GCS at {blob_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading {filename} to GCS: {e}")
            return False
    
    def process_single_attachment(self, attachment: Dict[str, Any], email_subject: str) -> Dict[str, Any]:
        """
        Process a single attachment (parse and upload)
        
        Args:
            attachment: Attachment object with metadata and data
            email_subject: Subject of the email for logging context
            
        Returns:
            Dictionary with processing results
        """
        thread_id = threading.current_thread().ident
        filename = attachment.get('filename', 'unknown')
        
        self.logger.info(f"[Thread-{thread_id}] Processing attachment: {filename} from email: {email_subject}")
        
        result = {
            'filename': filename,
            'email_subject': email_subject,
            'success': False,
            'error': None,
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Parse attachment
            parsed_attachment = self.parse_attachment(attachment)
            
            # Upload to datastore
            if self.upload_to_datastore(parsed_attachment):
                result['success'] = True
                self.logger.info(f"[Thread-{thread_id}] Successfully processed {filename}")
            else:
                result['error'] = "Upload failed"
                self.logger.error(f"[Thread-{thread_id}] Upload failed for {filename}")
                
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"[Thread-{thread_id}] Error processing {filename}: {e}")
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def process_emails(self, test_mode: bool = False):
        """
        Main method to process emails and attachments
        
        Args:
            test_mode: If True, use mock data instead of actual Gmail
        """
        self.logger.info("Starting email processing job")
        
        try:
            # Fetch emails
            emails = self.fetch_emails(use_mock=test_mode)
            if not emails:
                self.logger.info("No emails to process")
                return
            
            total_emails = len(emails)
            emails_with_attachments = 0
            total_attachments = 0
            processed_attachments = 0
            
            # Collect all attachments for parallel processing
            all_attachments = []
            
            # Process each email
            for email in emails:
                self.logger.info(f"Processing email: {email.get('subject', 'No Subject')}")
                
                attachments = email.get('attachments', [])
                if not attachments:
                    self.logger.warning(f"No attachments found in email: {email.get('subject', 'No Subject')}")
                    continue
                
                emails_with_attachments += 1
                
                # Filter attachments
                filtered_attachments = self.filter_attachments(attachments)
                total_attachments += len(filtered_attachments)
                
                # Add to processing queue with email context
                for attachment in filtered_attachments:
                    all_attachments.append({
                        'attachment': attachment,
                        'email_subject': email.get('subject', 'No Subject')
                    })
            
            # Process attachments in parallel
            if all_attachments:
                self.logger.info(f"Processing {len(all_attachments)} attachments using {self.config['max_workers']} workers")
                
                with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
                    # Submit all tasks
                    future_to_attachment = {
                        executor.submit(
                            self.process_single_attachment, 
                            item['attachment'], 
                            item['email_subject']
                        ): item for item in all_attachments
                    }
                    
                    # Process completed tasks
                    for future in as_completed(future_to_attachment):
                        try:
                            result = future.result()
                            if result['success']:
                                processed_attachments += 1
                                self.logger.info(f"Completed: {result['filename']} in {result['processing_time']:.2f}s")
                            else:
                                self.logger.error(f"Failed: {result['filename']} - {result['error']}")
                        except Exception as e:
                            self.logger.error(f"Unexpected error in parallel processing: {e}")
            
            # Log processing summary
            self.logger.info(f"Processing completed:")
            self.logger.info(f"  - Total emails: {total_emails}")
            self.logger.info(f"  - Emails with attachments: {emails_with_attachments}")
            self.logger.info(f"  - Emails without attachments: {total_emails - emails_with_attachments}")
            self.logger.info(f"  - Total attachments: {total_attachments}")
            self.logger.info(f"  - Processed attachments: {processed_attachments}")
            
            # Check if we expected attachments but didn't find any
            if total_emails > 0 and emails_with_attachments == 0:
                self.logger.warning("No emails contained attachments - this might indicate an issue")
            
            # Send notification if enabled
            if self.config['enable_notifications']:
                self.send_notification(processed_attachments, total_attachments, emails_with_attachments, total_emails)
                
        except Exception as e:
            self.logger.error(f"Error in email processing: {e}")
            raise
    
    def send_notification(self, processed: int, total: int, emails_with_attachments: int, total_emails: int):
        """
        Send notification about processing results using SendGrid
        
        Args:
            processed: Number of successfully processed attachments
            total: Total number of attachments
            emails_with_attachments: Number of emails that had attachments
            total_emails: Total number of emails processed
        """
        if not self.config['notification_email'] or not self.config['email_api_key']:
            return
            
        self.logger.info(f"Sending notification to {self.config['notification_email']}")
        
        try:
            # Create SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=self.config['email_api_key'])
            
            # Create email content
            status = 'success' if processed == total else 'partial'
            warning = total_emails > 0 and emails_with_attachments == 0
            
            html_content = f"""
            <h2>Email Processor Report</h2>
            <p><strong>Status:</strong> {status}</p>
            <h3>Processing Summary:</h3>
            <ul>
                <li>Total Emails Processed: {total_emails}</li>
                <li>Emails with Attachments: {emails_with_attachments}</li>
                <li>Total Attachments Found: {total}</li>
                <li>Successfully Processed: {processed}</li>
                <li>Failed to Process: {total - processed}</li>
            </ul>
            <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            {'<p style="color: red;"><strong>Warning:</strong> No attachments found in any emails.</p>' if warning else ''}
            """
            
            # Create message
            message = Mail(
                from_email=Email(self.config['email_address']),
                to_emails=To(self.config['notification_email']),
                subject=f"Email Processor Report - {status.title()}",
                html_content=Content("text/html", html_content)
            )
            
            # Send email
            response = sg.send(message)
            if response.status_code == 202:
                self.logger.info("Notification sent successfully")
            else:
                self.logger.error(f"Failed to send notification: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    def run_with_retry(self):
        """Run the processor with retry logic"""
        for attempt in range(1, self.config['retry_attempts'] + 1):
            try:
                self.logger.info(f"Processing attempt {attempt}/{self.config['retry_attempts']}")
                self.process_emails()
                self.logger.info("Processing completed successfully")
                return
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed: {e}")
                
                if attempt < self.config['retry_attempts']:
                    self.logger.info(f"Retrying in {self.config['retry_delay_seconds']} seconds...")
                    time.sleep(self.config['retry_delay_seconds'])
                else:
                    self.logger.error("All retry attempts failed")
                    raise


def main():
    """Main entry point for the cron job"""
    try:
        processor = EmailProcessor()
        processor.run_with_retry()
    except Exception as e:
        logging.error(f"Email processor failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
