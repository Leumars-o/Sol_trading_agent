"""env_validator.py

This file contains the function to validate the environment variables.
"""

import sys
from config import Config

def validate_environment() -> None:
    """Verify that essential environment variables for Helius and telegram are set
    Exit the program if any of the environment variables are missing.
    """

    missing = []

    if not Config.HELIUS_WS_URL:
        missing.append("HELIUS_WS_URI")
    if not Config.HELIUS_HTTPS_URL:
        missing.append("HELIUS_HTTPS_URI_TX")
    if not Config.TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not Config.TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")

    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
