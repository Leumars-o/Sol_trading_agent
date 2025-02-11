import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import Config
from transactions import (
    get_rug_check_confirmed,
    fetch_dexscreener_token_details,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to Verdger, the Solana Ai Trading Bot! 🔍\n"
        "Use /screen <token_address> to analyze a Solana token.\n"
        "Example: /screen ABC123..."
    )

async def screen_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Screen a token based on the provided address."""
    if not context.args:
        await update.message.reply_text("❌ Please provide a valid Solana token address.\nUsage: /screen <token_address>")
        return

    token_mint = context.args[0]
    
    # Send initial processing message
    processing_message = await update.message.reply_text("🔍 Processing token... Please wait.")
    
    try:
        # Perform rug check
        if not get_rug_check_confirmed(token_mint):
            await processing_message.edit_text("❌ Rug check failed. Token appears unsafe.")
            return
        
        await processing_message.edit_text("⏳ Analyzing the token...")
        time.sleep(30)
        
        # Fetch token details
        ds_info = fetch_dexscreener_token_details(token_mint)
        if not ds_info:
            await processing_message.edit_text("❌ Dexscreener data unavailable. Unable to process token.")
            return
        
        # Format message
        msg = (
            "<b>[ Token Information ]</b>\n"
            f"🚀 Token Analysis Results:\n"
            f"{ds_info['socialsIcon']} This token has {ds_info['socialLength']} socials.\n"
            f"📛 Token Name: {ds_info['tokenName']} Symbol: {ds_info['tokenSymbol']}\n"
            f"💹 Current Price: ${ds_info['currentPrice']}\n"
            f"📦 Current Mkt Cap: ${ds_info['marketCap']}\n"
            f"💦 Current Liquidity: ${ds_info['liquidity']}\n"
            f"🚀 Pumpfun token: {ds_info['pumpfunIcon']} {ds_info['isPumpFun']}\n"
            f"👀 View on Dex https://dexscreener.com/{Config.DEXSCREENER['chainId']}/{token_mint}\n"
            f"🕒 This token pair was created {ds_info['timeAgo']} and has {ds_info['pairsAvailable']} pairs available\n"
            f"🔗 Buy via SudoBot https://t.me/SudoCatBot?start=ref_cBVzFkKXms-{token_mint}\n"
            f"---------------------------------------------"
        )
        
        # Update the processing message with results
        await processing_message.edit_text(msg, parse_mode='HTML')
        
    except Exception as e:
        await processing_message.edit_text(f"❌ An error occurred while processing the token: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/screen <token_address> - Screen a Solana token\n"
        "/help - Show this help message"
    )

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("screen", screen_token))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()