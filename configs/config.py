import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Zendesk Configuration
ZENDESK_DOMAIN = os.getenv('ZENDESK_DOMAIN')
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')

# Intercom Configuration
INTERCOM_ACCESS_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')

# Chatwoot Configuration
CHATWOOT_BASE_URL = os.getenv('CHATWOOT_BASE_URL')
CHATWOOT_API_ACCESS_TOKEN = os.getenv('CHATWOOT_API_ACCESS_TOKEN')
CHATWOOT_ACCOUNT_ID = int(os.getenv('CHATWOOT_ACCOUNT_ID', 2))

# Rate Limiting
ZENDESK_RATE_LIMIT = int(os.getenv('ZENDESK_RATE_LIMIT', 700))
INTERCOM_RATE_LIMIT = int(os.getenv('INTERCOM_RATE_LIMIT', 1000))
CHATWOOT_RATE_LIMIT = int(os.getenv('CHATWOOT_RATE_LIMIT', 600))

# Batch Processing
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))

# Paths
OUTPUT_DIR = 'outputs'
ZENDESK_OUTPUT_DIR = f'{OUTPUT_DIR}/zendesk'
INTERCOM_OUTPUT_DIR = f'{OUTPUT_DIR}/intercom'
CHATWOOT_OUTPUT_DIR = f'{OUTPUT_DIR}/chatwoot'

# Validation function
def validate_config():
    """Check if all required environment variables are set"""
    required_vars = [
        ZENDESK_DOMAIN,
        ZENDESK_EMAIL, 
        ZENDESK_API_TOKEN,
        INTERCOM_ACCESS_TOKEN,
        CHATWOOT_BASE_URL,
        CHATWOOT_API_ACCESS_TOKEN
    ]
    
    missing_vars = []
    if not ZENDESK_DOMAIN:
        missing_vars.append('ZENDESK_DOMAIN')
    if not ZENDESK_EMAIL:
        missing_vars.append('ZENDESK_EMAIL')
    if not ZENDESK_API_TOKEN:
        missing_vars.append('ZENDESK_API_TOKEN')
    if not INTERCOM_ACCESS_TOKEN:
        missing_vars.append('INTERCOM_ACCESS_TOKEN')
    if not CHATWOOT_BASE_URL:
        missing_vars.append('CHATWOOT_BASE_URL')
    if not CHATWOOT_API_ACCESS_TOKEN:
        missing_vars.append('CHATWOOT_API_ACCESS_TOKEN')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    print("✅ All configuration variables are set!")
    return True