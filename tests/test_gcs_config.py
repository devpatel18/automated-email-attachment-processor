from google.cloud import storage
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

def test_gcs_connection():
    # Load environment variables
    load_dotenv('config/config.env')
    
    # Get GCS configuration
    project_id = os.getenv('DATASTORE_PROJECT_ID')
    bucket_name = os.getenv('DATASTORE_BUCKET')
    credentials_file = os.getenv('DATASTORE_CREDENTIALS_FILE')
    
    try:
        # Set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        
        # Initialize storage client
        storage_client = storage.Client(project=project_id)
        
        # Try to get the bucket
        bucket = storage_client.get_bucket(bucket_name)
        
        print("✅ Successfully connected to GCS!")
        print(f"✅ Successfully accessed bucket: {bucket_name}")
        print(f"✅ Location: {bucket.location}")
        print(f"✅ Storage class: {bucket.storage_class}")
        print(f"✅ Project: {project_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    # Get configuration
    project_id = os.getenv('DATASTORE_PROJECT_ID')
    credentials_file = os.getenv('DATASTORE_CREDENTIALS_FILE')
    bucket_name = os.getenv('DATASTORE_BUCKET')
    
    # Validate configuration
    if not all([project_id, credentials_file, bucket_name]):
        print("Error: Missing required configuration")
        print(f"Project ID: {'✓' if project_id else '✗'}")
        print(f"Credentials File: {'✓' if credentials_file else '✗'}")
        print(f"Bucket Name: {'✓' if bucket_name else '✗'}")
        sys.exit(1)
    
    try:
        # Set credentials
        if not os.path.exists(credentials_file):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_file}")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        
        # Initialize storage client
        storage_client = storage.Client()
        
        # Try to get the bucket
        bucket = storage_client.get_bucket(bucket_name)
        
        # Try to list objects (limited to 1 to minimize API usage)
        next(bucket.list_blobs(max_results=1))
        
        print("✅ Successfully connected to GCS!")
        print(f"✅ Successfully accessed bucket: {bucket_name}")
        print(f"✅ Location: {bucket.location}")
        print(f"✅ Storage class: {bucket.storage_class}")
        print(f"✅ Project: {project_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_gcs_connection()
