#!/usr/bin/env python3
"""
Demo Mock Data for Email Attachment Processor

This file contains mock data and utilities for testing the email processor
without requiring actual email API access.
"""

import json
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any

class MockDataGenerator:
    """Generate mock email data for testing"""
    
    @staticmethod
    def generate_sample_emails() -> List[Dict[str, Any]]:
        """Generate a comprehensive set of mock emails with various attachment types"""
        
        # Sample PDF content (base64 encoded)
        sample_pdf_content = base64.b64encode(b"Mock PDF content for testing").decode('utf-8')
        
        # Sample Excel content (base64 encoded)
        sample_excel_content = base64.b64encode(b"Mock Excel content for testing").decode('utf-8')
        
        # Sample Word document content (base64 encoded)
        sample_word_content = base64.b64encode(b"Mock Word document content for testing").decode('utf-8')
        
        # Sample text content (base64 encoded)
        sample_text_content = base64.b64encode(b"Mock text content for testing").decode('utf-8')
        
        # Sample CSV content (base64 encoded)
        sample_csv_content = base64.b64encode(b"Mock CSV content for testing").decode('utf-8')
        
        mock_emails = [
            {
                "id": "email_001",
                "subject": "Monthly Financial Report - January 2024",
                "sender": "finance@company.com",
                "recipient": "management@company.com",
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "priority": "high",
                "attachments": [
                    {
                        "filename": "monthly_financial_report.pdf",
                        "size": 2048576,  # 2MB
                        "content_type": "application/pdf",
                        "data": sample_pdf_content,
                        "checksum": "abc123def456"
                    },
                    {
                        "filename": "budget_analysis.xlsx",
                        "size": 1024000,  # 1MB
                        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "data": sample_excel_content,
                        "checksum": "def456ghi789"
                    }
                ]
            },
            {
                "id": "email_002",
                "subject": "Invoice #INV-2024-001",
                "sender": "billing@vendor.com",
                "recipient": "accounts@company.com",
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
                "priority": "medium",
                "attachments": [
                    {
                        "filename": "invoice_INV-2024-001.pdf",
                        "size": 512000,  # 500KB
                        "content_type": "application/pdf",
                        "data": sample_pdf_content,
                        "checksum": "ghi789jkl012"
                    }
                ]
            },
            {
                "id": "email_003",
                "subject": "Contract Documents for Review",
                "sender": "legal@lawfirm.com",
                "recipient": "legal@company.com",
                "date": (datetime.now() - timedelta(days=3)).isoformat(),
                "priority": "high",
                "attachments": [
                    {
                        "filename": "service_agreement.docx",
                        "size": 1536000,  # 1.5MB
                        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "data": sample_word_content,
                        "checksum": "jkl012mno345"
                    },
                    {
                        "filename": "terms_and_conditions.txt",
                        "size": 25600,  # 25KB
                        "content_type": "text/plain",
                        "data": sample_text_content,
                        "checksum": "mno345pqr678"
                    }
                ]
            },
            {
                "id": "email_004",
                "subject": "Customer Data Export",
                "sender": "data@company.com",
                "recipient": "analytics@company.com",
                "date": (datetime.now() - timedelta(days=4)).isoformat(),
                "priority": "low",
                "attachments": [
                    {
                        "filename": "customer_data_export.csv",
                        "size": 3072000,  # 3MB
                        "content_type": "text/csv",
                        "data": sample_csv_content,
                        "checksum": "pqr678stu901"
                    }
                ]
            },
            {
                "id": "email_005",
                "subject": "Project Documentation",
                "sender": "project@company.com",
                "recipient": "team@company.com",
                "date": (datetime.now() - timedelta(days=5)).isoformat(),
                "priority": "medium",
                "attachments": [
                    {
                        "filename": "project_specification.pdf",
                        "size": 4096000,  # 4MB
                        "content_type": "application/pdf",
                        "data": sample_pdf_content,
                        "checksum": "stu901vwx234"
                    },
                    {
                        "filename": "timeline.xlsx",
                        "size": 512000,  # 500KB
                        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "data": sample_excel_content,
                        "checksum": "vwx234yza567"
                    },
                    {
                        "filename": "requirements.docx",
                        "size": 768000,  # 750KB
                        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "data": sample_word_content,
                        "checksum": "yza567bcd890"
                    }
                ]
            },
            {
                "id": "email_006",
                "subject": "System Logs - Error Analysis",
                "sender": "system@company.com",
                "recipient": "devops@company.com",
                "date": (datetime.now() - timedelta(days=6)).isoformat(),
                "priority": "high",
                "attachments": [
                    {
                        "filename": "error_logs.txt",
                        "size": 102400,  # 100KB
                        "content_type": "text/plain",
                        "data": sample_text_content,
                        "checksum": "bcd890efg123"
                    }
                ]
            }
        ]
        
        return mock_emails
    
    @staticmethod
    def generate_large_attachment_email() -> Dict[str, Any]:
        """Generate an email with a large attachment to test size limits"""
        large_content = base64.b64encode(b"X" * (15 * 1024 * 1024)).decode('utf-8')  # 15MB
        
        return {
            "id": "email_large",
            "subject": "Large File Attachment",
            "sender": "test@company.com",
            "recipient": "test@company.com",
            "date": datetime.now().isoformat(),
            "priority": "low",
            "attachments": [
                {
                    "filename": "large_file.pdf",
                    "size": 15 * 1024 * 1024,  # 15MB
                    "content_type": "application/pdf",
                    "data": large_content,
                    "checksum": "large_file_hash"
                }
            ]
        }
    
    @staticmethod
    def generate_unsupported_file_type_email() -> Dict[str, Any]:
        """Generate an email with unsupported file types"""
        return {
            "id": "email_unsupported",
            "subject": "Unsupported File Types",
            "sender": "test@company.com",
            "recipient": "test@company.com",
            "date": datetime.now().isoformat(),
            "priority": "low",
            "attachments": [
                {
                    "filename": "image.png",
                    "size": 1024000,  # 1MB
                    "content_type": "image/png",
                    "data": base64.b64encode(b"Mock PNG content").decode('utf-8'),
                    "checksum": "png_hash"
                },
                {
                    "filename": "video.mp4",
                    "size": 2048000,  # 2MB
                    "content_type": "video/mp4",
                    "data": base64.b64encode(b"Mock MP4 content").decode('utf-8'),
                    "checksum": "mp4_hash"
                }
            ]
        }
    
    @staticmethod
    def save_mock_data_to_file(filename: str = "mock_emails.json"):
        """Save mock data to a JSON file for testing"""
        mock_emails = MockDataGenerator.generate_sample_emails()
        
        with open(filename, 'w') as f:
            json.dump(mock_emails, f, indent=2)
        
        print(f"Mock data saved to {filename}")
        return mock_emails
    
    @staticmethod
    def load_mock_data_from_file(filename: str = "mock_emails.json") -> List[Dict[str, Any]]:
        """Load mock data from a JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {filename} not found. Generating new mock data...")
            return MockDataGenerator.save_mock_data_to_file(filename)


def demo_usage():
    """Demonstrate how to use the mock data generator"""
    print("=== Email Attachment Processor - Mock Data Demo ===\n")
    
    # Generate mock emails
    mock_emails = MockDataGenerator.generate_sample_emails()
    print(f"Generated {len(mock_emails)} mock emails")
    
    # Display summary
    total_attachments = sum(len(email.get('attachments', [])) for email in mock_emails)
    print(f"Total attachments: {total_attachments}")
    
    # Show attachment types
    attachment_types = set()
    for email in mock_emails:
        for attachment in email.get('attachments', []):
            content_type = attachment.get('content_type', 'unknown')
            attachment_types.add(content_type)
    
    print(f"Attachment types: {', '.join(attachment_types)}")
    
    # Show file size distribution
    sizes = []
    for email in mock_emails:
        for attachment in email.get('attachments', []):
            sizes.append(attachment.get('size', 0))
    
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        print(f"File sizes - Min: {min_size/1024:.1f}KB, Max: {max_size/1024:.1f}KB, Avg: {avg_size/1024:.1f}KB")
    
    # Save to file
    MockDataGenerator.save_mock_data_to_file()
    
    print("\n=== Mock Data Generation Complete ===")


if __name__ == "__main__":
    demo_usage()
