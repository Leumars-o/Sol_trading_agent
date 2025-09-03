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
import os
from typing import Union
from config import Config


def fetch_transaction_details(signature: str) -> Union[dict, None]:
    tx_url = "https://mainnet.helius-rpc.com"  # Base URL
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "maxSupportedTransactionVersion": 0,
                "encoding": "jsonParsed",
                "commitment": "finalized"
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
    }

    for attempt in range(1, Config.TX["fetch_max_tries"] + 1):
        print(f"Attempt {attempt} of {Config.TX['fetch_max_tries']} to fetch transaction details...")
        
        try:
            response = requests.post(
                f"{tx_url}?api-key={Config.HELIUS_API_KEY}",
                json=payload,
                headers=headers,
                timeout=Config.TX["get_timeout"] / 1000
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"Fetching transaction: {signature}")
            print(f"Response status: {response.status_code}")

            # with open("raydium-2.json", "w") as f:
            #     json.dump(data, f, indent=2)
            

            if "error" in data:
                raise ValueError(f"RPC error: {data['error']}")

            result = data.get("result", {})

            # if not result:
            #     raise ValueError("No transaction data returned in result")
    
            transaction = result.get("transaction", {})
            # if not transaction:
            #     raise ValueError("No transaction found in inner instructions.")

            # Extract transaction message and instructions
            message = transaction.get("message", {})
            # if not message:
            #     raise ValueError("No message found in transaction.")
            
            instructions = message.get("instructions", [])
            # if not instructions:
            #     raise ValueError("No instructions found in transaction.")
            
            
            # Find Raydium instruction
            ray_id = Config.LIQUIDITY_POOL["raydium_program_id"]
            # matched_instr = next(
            #     print(ix for ix in instructions if ix.get("programId") == ray_id),
            #     None
            # )
            count = 1
            for ix in instructions:
                if ix.get("programId").lower() == ray_id.lower():
                    matched_instr = ix
                    break
                else:
                    count += 1
                    matched_instr = None
            
            if not matched_instr:
                print("No Raydium instruction found in transaction.")
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
                print("====================================\n")
                print(f"Found Raydium instruction for token: {acc9}")
                return {
                    "solMint": acc8,
                    "tokenMint": acc9
                }
            else:
                print("====================================\n")
                print(f"Found Raydium instruction for token: {acc8}")
                return {
                    "solMint": acc9,
                    "tokenMint": acc8
                }

        except Exception as e:
            if attempt < Config.TX["fetch_max_tries"]:
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
        return False

    url = f"https://api.rugcheck.xyz/v1/tokens/{token_mint}/report"

    try:
        response = requests.get(url, timeout=Config.TX["get_timeout"] / 100)
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
        (token_mint.lower().endswith("pump") or token_mint.lower().endswith("fun")):
            print("❌ Token name ends with 'pump' or 'fun'; Ignoring...")
            return False
        
        print("✅ Token passed basic Rug Check.")
        return True
    except Exception as e:
        print(f"RugCheck error (ignoring): {e}")
        return True
    

def fetch_dexscreener_token_details(token_mint: str, skip_check=False) -> Union[dict, None]:
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
    chain_id = Config.DEXSCREENER["chainId"]
    final_url = f"{dex_base_url}{chain_id}/{token_mint}"

    max_retries = Config.DEXSCREENER["fetch_max_tries"]
    max_token_time = Config.RUG_CHECK["max_created_at"]

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries} to fetch token details...")
        try:
            response = requests.get(final_url, timeout=Config.TX["get_timeout"] / 100)
            response.raise_for_status()
            print(f"Response status: {response.status_code}")

            data = response.json()
            print(f"Data: {data}")

            if not data or not isinstance(data, list):
                raise ValueError("Dexscreener returned an empty list.")
                    
            matched_pair = data[0]

            print("====================================\n")
            print(f"new data: {matched_pair}")
                
            if matched_pair.get("dexId") != dex_pair_filter:
                if not skip_check:
                    raise ValueError(f"No {dex_pair_filter} pair found in Dexscreener data.")
            
            base_token = matched_pair.get("baseToken", {})
            token_name = base_token.get("name", token_mint)
            token_symbol = base_token.get("symbol", "N/A")
            price_usd = float(matched_pair.get("priceUsd", 0))
            market_cap = float(matched_pair.get("marketCap", 0))
            liquidity_usd = float(matched_pair.get("liquidity", {}).get("usd", 0))
            pair_created_at = matched_pair.get("pairCreatedAt", 0)

            # Calculate time ago
            if pair_created_at > 0:
                # initial_check = True
                # if pair_created_at > max_token_time * 1000 and initial_check:
                #     print("token was created more than 60 seconds ago")
                #     return None
                # initial_check = False
                time_ago = arrow.get(pair_created_at / 1000).humanize()

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
            print(social_length)
            social_icon = "🔴" if social_length == 0 else "🟢"

            return {
                "tokenName": token_name,
                "tokenSymbol": token_symbol,
                "currentPrice": price_usd,
                "marketCap": market_cap,
                "liquidity": liquidity_usd,
                "timeAgo": time_ago,
                "dexPair": dex_pair_filter,
                "socialLength": social_length,
                "pumpfunIcon": pumpfun_icon,
                "isPumpFun": is_pumpfun,
                "pairsAvailable": len(data),
                "socialsIcon": social_icon,
            }
    
        except Exception as e:
            print(f"Specific error: {str(e)}") 
            if attempt < max_retries:
                time.sleep(os.getenv("DELAY", 5000) / 100)
            else:
                print(f"Error fetching token details from Dexscreener after {attempt} attempts: {e}")
            continue
    print("i entered the last return")
    return None