from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import google.generativeai as genai
from config import Config
from transactions import (
    get_rug_check_confirmed,
    fetch_dexscreener_token_details,
)
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GENAI_API_KEY'))

# AI Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize AI model
model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)

# Create chat session
chat_session = model.start_chat(history=[])

def get_ai_analysis(token_data):
    """Get AI analysis for token data"""
    try:
        with open('gemini_prompt.txt', 'r') as file:
            base_prompt = file.read()
        
        full_prompt = f"{base_prompt}\n\nAnalyze this token data:\n{token_data}"

        # Send token data to AI model
        response = chat_session.send_message(full_prompt)
        return response.text
    
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to Verger AI, a Solana Token Analyzer Bot! 🔍\n"
        "Use /analyze <token_address> to get detailed token analysis.\n"
        "Example: /analyze ABC123..."
    )

async def analyze_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze token with both screening and AI analysis."""
    if not context.args:
        await update.message.reply_text("❌ Please provide a valid Solana token address.\nUsage: /analyze <token_address>")
        return

    token_mint = context.args[0]
    
    # Send initial processing message
    processing_message = await update.message.reply_text("🔍 Processing token... Please wait.")
    
    try:
        # Perform rug check
        if not get_rug_check_confirmed(token_mint):
            await processing_message.edit_text("❌ Rug check failed. Token appears unsafe.")
            return
        
        await processing_message.edit_text("⏳ Waiting for DexScreener to update token info...")
        
        # Fetch token details
        ds_info = fetch_dexscreener_token_details(token_mint, skip_check=True)
        if not ds_info:
            await processing_message.edit_text("❌ Dexscreener data unavailable. Unable to process token.")
            return
        
        # Format initial screening message
        screening_msg = (
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
        
        # Send screening results
        await processing_message.edit_text(screening_msg, parse_mode='HTML')
        
        # Send AI analysis status
        ai_message = await update.message.reply_text("🤖 Generating AI analysis... Please wait.")
        
        # Get AI analysis
        ai_analysis = get_ai_analysis(ds_info)
        
        # Format AI analysis message
        ai_msg = (
            "<b>[ AI Token Analysis ]</b>\n"
            f"{ai_analysis}\n"
            
            "---------------------------------------------"
        )
        
        # Update AI analysis message
        await ai_message.edit_text(ai_msg, parse_mode='HTML')
        
    except Exception as e:
        await processing_message.edit_text(f"❌ An error occurred during analysis: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/analyze <token_address> - Get complete token analysis\n"
        "/help - Show this help message"
    )

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_token))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()