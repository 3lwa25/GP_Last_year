"""
Configuration-based settings using ConfigManager.
This demonstrates a professional approach using a configuration manager class.
"""

from .base import *
from ..config import config

# Get configuration from ConfigManager
SECRET_KEY = config.get_secret_key()
DEBUG = config.is_debug()

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*.herokuapp.com']

# Database configuration
DATABASES = config.get_database_config()

# Email configuration from ConfigManager
email_config = config.get_email_config()
globals().update(email_config)

print(f"🔧 Configuration-based settings loaded")
print(f"📧 Email backend: {email_config['EMAIL_BACKEND']}")
print(f"🐛 Debug mode: {DEBUG}") 