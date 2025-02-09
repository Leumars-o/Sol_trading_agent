"""config.py

Configuration file for the application and environment variables.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv() 

class Config:
    """Set Flask configuration vars from .env file."""

    # RPC URL for Solana Mainnet
    HELIUS_WS_URI: str = os.getenv("HELIUS_WS_URI", "")
    HELIUS_HTTPS_URI_TX: str = os.getenv("HELIUS_HTTPS_URI_TX", "")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Raydium Program ID
    LIQUIDITY_POOL = {
        "raydium_program_id": os.getenv("RAYDIUM_PROGRAM_ID", "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"),
        "wsol_pc_mint": os.getenv("WSOL_PC_MINT", "So11111111111111111111111111111111111111112"),
    }

    # Transaction Fetching Config
    TX = {
        "fetch_max_tries": int(os.getenv("MAX_TRIES", 10)),
        "fetch_tx_initial_delay": int(os.getenv("DELAY", 3000)), # in milliseconds
        "get_timeout": int(os.getenv("GET_TIMEOUT", 1000)), # in milliseconds
    }

    # Rug Check Config
    RUG_CHECK = {
        "enabled": os.getenv("RUG_CHECK_ENABLED", "False"),
        "verbose_log": os.getenv("RUG_CHECK_VERBOSE_LOG", "True"),
        "allow_mint_authority": os.getenv("RUG_CHECK_ALLOW_MINT_AUTHORITY", "True"),
        "allow_not_initialized": os.getenv("RUG_CHECK_ALLOW_NOT_INITIALIZED", "False"),
        "allow_freeze_authority": os.getenv("RUG_CHECK_ALLOW_FREEZE_AUTHORITY", "True"),
        "allow_rugged": os.getenv("RUG_CHECK_ALLOW_RUGGED", "True"),
        "allow_mutable": os.getenv("RUG_CHECK_ALLOW_MUTABLE", "True"),
        "block_returning_token_names": os.getenv("RUG_CHECK_BLOCK_RETURNING_TOKEN_NAMES", "True"),
        "block_returning_token_creatores": os.getenv("RUG_CHECK_BLOCK_RETURNING_TOKEN_CREATORS", "True"),
        "block_symbols": json.loads(os.getenv("RUG_CHECK_BLOCK_SYMBOLS", '["XXX"]')),
        "block_names": json.loads(os.getenv("RUG_CHECK_BLOCK_NAMES", '["RUG"]')),
        "allow_insider_topholders": os.getenv("RUG_CHECK_ALLOW_INSIDER_TOPHOLDERS", "False"),
        "insider_topholders_threshold": int(os.getenv("RUG_CHECK_INSIDER_TOPHOLDERS_THRESHOLD", 50)), # in percentage
        "exclude_lp_from_top_holders": os.getenv("RUG_CHECK_EXCLUDE_LP_FROM_TOP_HOLDERS", "True"),
        "min_total_markets": int(os.getenv("RUG_CHECK_MIN_TOTAL_MARKETS", 10)),
        "min_total_lp_providers": int(os.getenv("RUG_CHECK_MIN_TOTAL_LP_PROVIDERS", 5)),
        "min_total_market_liquidity": int(os.getenv("RUG_CHECK_MIN_TOTAL_MARKET_LIQUIDITY", 20000)),
        "ignore_pump_fun": os.getenv("RUG_CHECK_IGNORE_PUMP_FUN", "False"),
        "max_score": int(os.getenv("RUG_CHECK_MAX_SCORE", 0)), # 0 means no max score
        "legacy_not_allowed": os.getenv("RUG_CHECK_LEGACY_NOT_ALLOWED", ["Copycat token",],)
    }

    # Dexscreener Config
    DEXSCREENER = {
        "chainId": (os.getenv("CHAIN_ID", "solana")),
        "url": "https://api.dexscreener.com/tokens/v1/",
        "dex_pair_filter": os.getenv("DEX_PAIR_FILTER", "raydium"), # filter for Raydium pairs
        "fetch_max_tries": int(os.getenv("DEXSCREENER_FETCH_MAX_TRIES", 10)),
        "fetch_retry_delay": int(os.getenv("DEXSCREENER_FETCH_RETRY_DELAY", 5)), # in seconds
    }