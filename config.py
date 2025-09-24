"""
Azure DevOps MCP Server - Configuration
"""

import os

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass

# Configuration from environment variables
AZURE_DEVOPS_ORG = os.getenv("AZURE_DEVOPS_ORG", "executeauto")
AZURE_DEVOPS_PROJECT = os.getenv("AZURE_DEVOPS_PROJECT", "Udemy") 
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

# Validate required environment variables
if not AZURE_DEVOPS_PAT:
    raise ValueError("AZURE_DEVOPS_PAT environment variable is required")

# SSL Configuration
DISABLE_SSL_VERIFY = os.getenv("AZURE_DEVOPS_DISABLE_SSL_VERIFY", "").lower() == "true"

# Timeout settings
REQUEST_TIMEOUT = 30

# Retry settings
RETRY_TOTAL = 3
RETRY_BACKOFF_FACTOR = 1
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

# API version
API_VERSION = "7.1-preview.3"
WIQL_API_VERSION = "7.1-preview.2"