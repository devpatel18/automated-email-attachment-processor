#!/usr/bin/env python3
"""
Test script for email processor using mock data (moved into tests/)
"""

from src.email_processor import EmailProcessor
from src.demo_mock_data import MockDataGenerator
import logging

def test_with_mock_data():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting email processor test with mock data")
    
    # Generate mock data first
    mock_generator = MockDataGenerator()
    mock_emails = mock_generator.generate_sample_emails()
    logger.info(f"Generated {len(mock_emails)} mock emails")
    
    # Add some edge cases
    large_email = mock_generator.generate_large_attachment_email()
    unsupported_email = mock_generator.generate_unsupported_file_type_email()
    
    logger.info("Testing with different scenarios:")
    logger.info("1. Regular attachments (PDFs, Excel, Word, etc.)")
    logger.info("2. Large attachment (15MB file)")
    logger.info("3. Unsupported file types (PNG, MP4)")
    
    # Initialize and run the email processor
    processor = EmailProcessor()
    
    # Process regular mock emails
    logger.info("\nProcessing regular mock emails...")
    processor.process_emails(test_mode=True)
    
    # Process edge cases
    logger.info("\nProcessing large attachment...")
    processor.process_single_attachment(
        large_email['attachments'][0],
        large_email['subject']
    )
    
    logger.info("\nProcessing unsupported file types...")
    for attachment in unsupported_email['attachments']:
        processor.process_single_attachment(
            attachment,
            unsupported_email['subject']
        )

if __name__ == "__main__":
    test_with_mock_data()
