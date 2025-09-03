# Telegram Trading Bot

A comprehensive Solana token analysis and monitoring system with real-time liquidity pool detection and AI-powered token evaluation via Telegram.

## 🚀 Features

### WebSocket Service
- **Real-time Monitoring**: Connects to Helius WebSocket to detect new Raydium liquidity pools instantly
- **Transaction Analysis**: Automatically fetches and parses Raydium liquidity pool creation transactions
- **Token Validation**: Integrates rug check validation and DexScreener data fetching
- **Telegram Notifications**: Sends instant alerts with token details and trading links

### AI Service  
- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent token evaluation
- **Interactive Bot**: Telegram bot with `/analyze` command for on-demand token screening
- **Risk Assessment**: Provides rug analysis, sentiment evaluation, and trading recommendations
- **Comprehensive Reports**: Detailed token analysis with leverage advice and trading strategies

### Core Features
- **Rug Check Integration**: Validates tokens against rugcheck.xyz database
- **DexScreener Integration**: Fetches real-time token data including price, market cap, and liquidity
- **Multi-service Architecture**: Containerized microservices for scalability
- **Environment Validation**: Comprehensive configuration validation on startup

## 🏗️ Architecture

```
telegram-trading-bot/
├── websocket_service/          # Real-time liquidity monitoring
│   ├── main.py                # WebSocket connection and transaction processing
│   └── Dockerfile             # Container configuration
├── ai_service/                # AI token analysis
│   ├── ai_token_screener.py   # Telegram bot with AI integration
│   ├── gemini_prompt.txt      # AI analysis prompt template
│   └── Dockerfile             # Container configuration
├── config.py                  # Centralized configuration management
├── transactions.py            # Transaction processing and API integrations
├── telegram_utils.py          # Telegram messaging utilities
├── env_validator.py           # Environment validation
├── docker-compose.yml         # Service orchestration
└── requirements.txt           # Python dependencies
```

##  Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- Helius RPC API access
- Telegram Bot API token
- Google Gemini AI API key

##  Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd telegram-trading-bot
```

### 2. Environment Setup
Create a `.env` file in the root directory:

```env
# Helius Configuration
HELIUS_WS_URI=wss://atlas-mainnet.helius-rpc.com/?api-key=YOUR_API_KEY
HELIUS_HTTPS_URI_TX=https://mainnet.helius-rpc.com
HELIUS_API_KEY=your_helius_api_key

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# AI Configuration
GENAI_API_KEY=your_gemini_api_key

# Optional: Raydium Configuration
RAYDIUM_PROGRAM_ID=675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
WSOL_PC_MINT=So11111111111111111111111111111111111111112

# Optional: Trading Parameters
MAX_TRIES=10
DELAY=3000
GET_TIMEOUT=1000

# Optional: Rug Check Configuration
RUG_CHECK_ENABLED=True
RUG_CHECK_MAX_SCORE=0
RUG_CHECK_MAX_CREATED_AT=60

# Optional: DexScreener Configuration
CHAIN_ID=solana
DEX_PAIR_FILTER=raydium
DEXSCREENER_FETCH_MAX_TRIES=10
DEXSCREENER_FETCH_RETRY_DELAY=5
```

### 3. Installation Options

#### Option A: Docker Deployment (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

#### Option B: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run WebSocket service
python websocket_service/main.py

# Run AI service (in separate terminal)
python ai_service/ai_token_screener.py
```

##  Usage

### WebSocket Service
The WebSocket service runs automatically and:
1. Monitors Raydium for new liquidity pool creations
2. Performs rug checks on detected tokens
3. Fetches token data from DexScreener
4. Sends formatted notifications to Telegram

### AI Service (Telegram Bot)
Interact with the AI bot via Telegram:

- `/start` - Initialize the bot
- `/analyze <token_address>` - Get comprehensive AI analysis
- `/help` - Show available commands

Example:
```
/analyze EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

##  Workflow

### Automated Monitoring (WebSocket Service)
1. **Detection**: WebSocket monitors Raydium program logs
2. **Validation**: Extracts transaction details and validates token mints
3. **Screening**: Performs rug check validation
4. **Analysis**: Fetches comprehensive token data from DexScreener
5. **Notification**: Sends formatted alerts to Telegram with trading links

### Manual Analysis (AI Service)
1. **Request**: User sends `/analyze <token_address>` to Telegram bot
2. **Screening**: Bot performs rug check and data validation
3. **AI Analysis**: Google Gemini AI evaluates token data
4. **Response**: Bot sends detailed analysis with recommendations

##  Token Analysis Features

- **Risk Assessment**: Rug pull detection and security analysis
- **Market Data**: Real-time price, market cap, and liquidity information
- **Social Metrics**: Social media presence and community analysis
- **Trading Intelligence**: AI-generated trading recommendations and leverage advice
- **Pump.fun Detection**: Identifies tokens launched on Pump.fun
- **Time Analysis**: Token creation timing and pair availability

##  Configuration

### Core Settings
- **Transaction Fetching**: Configurable retry attempts and delays
- **Rug Check**: Comprehensive validation rules and thresholds
- **DexScreener**: API integration with filtering options
- **AI Analysis**: Customizable prompt templates and model parameters

### Security Features
- **Environment Validation**: Ensures all required configuration is present
- **Error Handling**: Comprehensive exception handling and retry logic
- **Rate Limiting**: Built-in delays to prevent API abuse

##  Monitoring & Logs

Monitor service health:
```bash
# View service logs
docker-compose logs -f websocket
docker-compose logs -f analyzer

# Check service status
docker-compose ps
```

##  Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## ⚠️ Disclaimer

This software is for educational and informational purposes only. Trading cryptocurrencies involves substantial risk and may result in significant financial losses. Users should conduct their own research and consult with financial advisors before making investment decisions.

##  License

This project is licensed under the MIT License - see the LICENSE file for details.
