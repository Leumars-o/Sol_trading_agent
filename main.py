"""main.py

This is the main file for the project.

- It opens a websocket to Helius to detect new Raydium liquidity pools.
- Fetches transaction details for the new token mint in multiple tries.
- Runs a Rug Check
- Repeatedly fetches token details from Dexscreener (up to 10 tries with 5 seconds delay)
- Logs the token details and sends a Telegram notification with the token details.

"""

import json
import time
import websocket

from config import Config
from env_validator import validate_environment
from transactions import (
    fetch_transaction_details,
    get_rug_check_confirmed,
    fetch_dexscreener_token_details,
)

from telegram_utils import send_telegram_message


def on_open(ws):
    """on_open

    Callback function for websocket on_open event
    that subscribes to logs from Raydium's program ID.

    Args:
        ws (websocket.WebSocketApp): The websocket object.

    """
    print("Websocket Connection to Raydium Successful")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "logsSubscribe",
        "params": [
            {
                "mentions": [Config.LIQUIDITY_POOL["raydium_program_id"]],
            },
            {
                "commitment": "processed",
            }
        ]
    }

    ws.send(json.dumps(request))
    print("Subscription request sent. Waiting confirmation...")


def on_message(ws, message):
    """on_message
    This function is called when a message is received from the websocket.
    If a new liquidity pool creation is found, it calls process_transaction().

    Args:
        ws (websocket.WebSocketApp): The websocket object.
        message (_type_): _description_
    """

    try:
        parsed = json.loads(message)
        if "result" in parsed and not parsed.get("error"):
            print("Subscription confirmed. Waiting for new liquidity pools...")
            return
        
        val = parsed.get("params", {}).get("result", {}).get("value", {})
        logs = val.get("logs", [])
        signature = val.get("signature", "")

        if not logs or not signature:
            return
        
        # Loop through logs to find new liquidity pool creation
        found_initialize = any(
            "Program log: initialize2: InitializeInstruction2" in log
            for log in logs if isinstance(log, str)
        )
        if not found_initialize:
            return
        
        process_transaction(signature)
    except Exception as e:
        print(f"Error processing WebSocket message: {e}")

    
    def on_error(ws, error):
        """on_error
        This function is called if there is a websocket error.

        Args:
            ws (websocket.WebSocketApp): The websocket object.
            error (_type_): _description_
        """
        return ""
    
    def process_transaction(signature: str):
        """process_transaction
        This function is called when a new liquidity pool creation is detected.

        - Fetches transaction details for the new token mint in multiple tries.
        - Runs a Rug Check
        - Repeatedly fetches token details from Dexscreener (up to 10 tries with 5 seconds delay)
        - Logs the token details and sends a Telegram notification with the token details.

        Args:
            signature (str): _description_
        """

        print("\n======================================================")
        print("🔎 New Liquidity Pool found.")
        print("🔁 Fetching transaction details...")

        tx_data = fetch_transaction_details(signature)
        if not tx_data:
            print("❌ Transaction details not found. Looking for new tokens...")
            return
        
        token_mint = tx_data.get("token_mint")
        if not token_mint:
            print("❌ Incomplete transaction data. Skipping...\n")
            return
        
        if not get_rug_check_confirmed(token_mint):
            print("❌ Rug check failed. Skipping token...\n")
            return
        
        print("⏳ Waiting 30 seconds for DexScreener to update token info...")
        time.sleep(30)

        ds_info = fetch_dexscreener_token_details(token_mint)
        if not ds_info:
            print("❌ Dexscreener data unavailable. Skipping...\n")
            return
        
        # Print in processed format
        print("[ Token Information ]")
        print(f"{ds_info['socialsIcon']} This token has {ds_info['socialLenght']} socials.")
        print(f"👀 View on Dex https://descreener.com/{Config.DEXSCREENER['chainId']}/{token_mint}")
        print(
            f"🕒 This token pair was created {ds_info['timeAgo']} and has "
            f"{ds_info['pairsAvailable']} pairs available including {ds_info['dexPairn']}"
        )
        print(f"💹 Current Price: ${ds_info['currentPrice']}")
        print(f"📦 Current Mkt Cap: ${ds_info['marketCap']}")
        print(f"💦 Current Liquidity: ${ds_info['liquidity']}")
        print(f"🚀 Pumpfun token: {ds_info['pumpfunIcom']} {ds_info['isPumpFun']}")
        print(f"📛 Token Name: {ds_info['tokenName']} Symbol: {ds_info['tokenSymbol']}")