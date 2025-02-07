"""transactions.py

This file contains the functions to fetch transaction details and run a rug check.

- fetch_transaction_details: Fetches transaction details for the new token mint from Helius
    in multiple attempts.
- get_rug_check_confirmed: Runs a rug check on the token mint details.
- fetch_dexscreener_token_details: Fetches token details from Dexscreener.
"""

import json
import requests
import time
import arrow
from config import Config


def fetch_transaction_details(signature: str) -> dict | None:
    """Fetch transaction details for the new token mint in multiple tries.

    Args:
        signature (str): The transaction signature.

    Returns:
        dict | None: The transaction details if found, else None.

    """
    tx_url = f"{Config.HELIUS_HTTPS_URL}/tx/{signature}"
    max_retries = Config.TX["fetch_max_tries"]
    initial_delay_sec = Config.TX["fetch_tx_initial_delay"]

    # Brief delay before fetching transaction details
    time.sleep(initial_delay_sec / 1000)

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries} to fetch transaction details...")

        try:
            body = {
                "transactions": [signature],
                "commitment": "finalized",
                "encoding": "jsonParsed",
            }
            response = requests.post(
                tx_url,
                json=body,
                timeout= Config.TX["get_timeout"] / 1000,
            )
            response.raise_for_status()

            data = response.json()
            if not data or len(data) == 0:
                raise ValueError("No data found in response.")
            
            first_tx = data[0]
            instructions = first_tx.get("transaction", [])
            if not instructions:
                raise ValueError("No instructions found in transaction.")
            
            # find Raydium instruction
            ray_id = Config.LIQUIDITY_POOL["raydium_program_id"]
            matched_instr = next(
                (ix for ix in instructions if ix.get("programId") == ray_id),
                None
            )
            if not matched_instr:
                raise ValueError("No Raydium instruction found in transaction.")
            
            accounts = matched_instr.get("accounts", [])
            if len(accounts) < 10:
                raise ValueError("Not enough accounts found in Raydium instruction.")
            
            acc8 = accounts[8]
            acc9 = accounts[9]
            if not acc8 or not acc9:
                raise ValueError("Required Accounts not found.")
            
            wsol_mint = Config.LIQUIDITY_POOL["wsol_pc_mint"]
            if acc8 == wsol_mint:
                return {
                    "soMint": acc8,
                    "tokenMint": acc9
                }
            else:
                return {
                    "soMint": acc9,
                    "tokenMint": acc8
                }
        except Exception as e:
            # if not the last attempt, wait before retrying
            # or do an exponential backoff
            if attempt < max_retries:
                delay = min(4.0 * (1.5 ** (attempt - 1)), 15.0)
                time.sleep(delay)
            else:
                print(f"Failed to fetch transaction details: {e}")
                return None
    return None


def get_rug_check_confirmed(token_mint: str) -> bool:
    """Run a rug check on the token mint details.

    Args:
        token_mint (str): The token mint address.

    Returns:
        bool: True if the token is confirmed, else False.

    """
    if not Config.RUG_CHECK["enabled"] or not token_mint:
        return True

    url = f"https://api.rugcheck.xyz/v1/tokens/{token_mint}/repport"

    try:
        response = requests.get(url, timeout=Config.TX["get_timeout"] / 1000)
        response.raise_for_status()

        data = response.json()
        if not data or "error" in data:
            print("Empty response from Rug Check, Ignoring...")
            return True
        
        is_rugged = data.get("rugged", False)
        if is_rugged and not Config.RUG_CHECK["allow_rugged"]:
            print("❌ Token is flagged as Rugged.")
            return False
        
        # Optionally ignore tokens ending with "pump" or "fun"
        if Config.RUG_CHECK["ignore_pump_fun"] and \
        token_mint.lower().endswith("pump") or token_mint.lower().endswith("fun"):
            print("❌ Token name ends with 'pump' or 'fun'; Ignoring...")
            return False
            
        return True
    except Exception as e:
        print(f"RugCheck error (ignoring): {e}")
        return True
    

def fetch_dexscreener_token_details(token_mint: str) -> dict | None:
    """Fetch token details from Dexscreener.

    Args:
        token_mint (str): The token mint address.

    Returns:
        dict | None: The token details if found, else None.
        - 'tokenName', 'tokenSymbol'
        - 'currentPrice', 'marketCap', 'liquidity'
        - 'timeAgo', 'dexPair'
        - socialLength', 'socialsIcon'
        - 'pumpfunIcon', 'isPumpFun'
        - 'pairsAvailable'
    """

    dex_base_url = Config.DEXSCREENER["url"]
    dex_pair_filter = Config.DEXSCREENER["dex_pair_filter"]
    final_url = f"{dex_base_url}{token_mint}"

    max_retries = Config.DEXSCREENER["fetch_max_tries"]
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt} of {max_retries} to fetch token details...")
            response = requests.get(final_url, timeout=Config.TX["get_timeout"] / 1000)
            response.raise_for_status()

            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Dexscreener returned an invalied Json Structure.")
                
            pairs = data.get("pairs", [])
            matched_pair = next(
                (p for p in pairs if p.get("dexId") == dex_pair_filter), 
                None
            )
            if not matched_pair:
                raise ValueError("No Raydium pair found in Dexscreener data.")
            
            base_token = matched_pair.get("baseToken", {})
            token_name = base_token.get("name", token_mint)
            token_symbol = base_token.get("symbol", "N/A")
            price_usd = float(matched_pair.get("priceUSD", 0))
            market_cap = float(matched_pair.get("marketCap", 0))
            liquidity_usd = float(matched_pair.get("liquidity", {}.get("usd", 0))
            pair_created_at = matched_pair.get("createdAt", 0)

            # Calculate time ago
            if pair_created_at > 0:
                time_agp = arrow.get(pair_created_at / 1000).humanize()
            else:
                time_ago = "N/A"
            
            #Pumpfun Check
            if token_mint.lower().endswith("pump") or token_mint.lower().endswith("fun"):
                pumpfun_icon = "🟢"
                is_pumpfun = "Yes"
            else:
                pumpfun_icon = "🔴"
                is_pumpfun = "No"      

            # Socials
            info_obj = matched_pair.get("info", {})
            socials = info_obj.get("socials", [])
            social_length = len(socials)
            social_icon = "🔴" if social_length == 0 else "🟢"

            return {
                "tokenName": token_name,
                "tokenSymbol": token_symbol,
                "currentPrice": price_usd,
                "marketCap": market_cap,
                "Liquidity": liquidity_usd,
                "timeAgo": time_ago,
                "dexPair": dex_pair_filter,
                "socialLength": social_length,
                "pumpfunIcon": pumpfun_icon,
                "isPumpFun": is_pumpfun,
                "pairsAvailable": len(pairs),
            }
        except Exception as e:
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                print(f"Error fetching token details from Dexscreener after {attempt} attempts: {e}")
            return None
    return None