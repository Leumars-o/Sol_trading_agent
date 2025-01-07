"""telegram_utils.py

This file contains the function to send a message to a Telegram chat.
"""

import requests
from config import Config


def send_telegram_message(message: str) -> None:
    """Send a message to a Telegram chat.

    Args:
        message (str): The message to send.

    """

    token = Config.TELEGRAM_BOT_TOKEN
    chat_id = Config.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        raise ValueError("Telegram bot token or chat ID not set.")


    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to send message to Telegram. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Exception in sending message to Telegram: {e}")
        