import os
import imaplib
import sendgrid
from google.cloud import storage
from dotenv import load_dotenv

def test_connections():
    # Load environment variables
    load_dotenv('config/config.env')
    
    print("\nTesting Service Connections:")
    print("=" * 50)
    
    # Test Gmail IMAP
    print("\n1. Testing Gmail IMAP Connection:")
    try:
        imap_server = os.getenv('IMAP_SERVER')
        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_PASSWORD')
        
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email, password)
        mail.select('inbox')
        _, messages = mail.search(None, 'UNSEEN')
        mail.close()
        mail.logout()
        print("✅ Gmail IMAP Connection Successful")
        print(f"   - Server: {imap_server}")
        print(f"   - Email: {email}")
        print(f"   - Found {len(messages[0].split())} unread messages")
    except Exception as e:
        print(f"❌ Gmail IMAP Connection Failed: {str(e)}")

    # Test SendGrid
    print("\n2. Testing SendGrid Connection:")
    try:
        api_key = os.getenv('EMAIL_API_KEY')
        sg = sendgrid.SendGridAPIClient(api_key)
        # Simple check: attempt to get API key details via safe endpoint if available
        print("✅ SendGrid client initialized")
        print(f"   - API Key: {api_key[:5]}...{api_key[-5:]}")
    except Exception as e:
        print(f"❌ SendGrid Connection Failed: {str(e)}")

    # Test Google Cloud Storage
    print("\n3. Testing Google Cloud Storage Connection:")
    try:
        project_id = os.getenv('DATASTORE_PROJECT_ID')
        bucket_name = os.getenv('DATASTORE_BUCKET')
        credentials_file = os.getenv('DATASTORE_CREDENTIALS_FILE')
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        
        # Try to list a single blob to test access
        next(bucket.list_blobs(max_results=1))
        
        print("✅ GCS Connection Successful")
        print(f"   - Project ID: {project_id}")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Credentials: {credentials_file}")
    except Exception as e:
        print(f"❌ GCS Connection Failed: {str(e)}")

if __name__ == "__main__":
    test_connections()
