# Binance Futures Trading Bot

A professional Python trading bot for **Binance Futures Testnet** with support for multiple order types and advanced trading strategies.

---

## 🚀 Features

### Core Features
- ✅ **Market Orders** – Execute immediate buy/sell at current market price  
- ✅ **Limit Orders** – Place orders at specific price levels  
- ✅ **Stop-Limit Orders** – Automated stop-loss and take-profit orders  
- ✅ **OCO Orders** – One-Cancels-Other order pairs  
- ✅ **TWAP Orders** – Time-Weighted Average Price execution  

### Additional Features
- 📊 Real-time account balance tracking  
- 📈 Current price checking  
- 📝 Comprehensive logging (file + console)  
- 🎨 Color-coded CLI interface  
- ✅ Input validation and error handling  
- 🔐 Secure API credential management  
- 🧪 Full Testnet support (no real money at risk)  

---

## 📋 Requirements

- Python 3.8 or higher  
- Binance Futures Testnet account  
- API Key and Secret from testnet  

---

## 🛠️ Installation

### 1. Clone or Download Project
```bash
cd C:\Users\YourUsername\projects
mkdir binance-trading-bot
cd binance-trading-bot

### 2. Create Virtual Environment
```bash 
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Configure API Credentials
Create a .env file in the project root:
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_key_here
TESTNET=True

🎮 Usage
Start the Bot
python bot.py

| Command   | Description                    |
| --------- | ------------------------------ |
| `help`    | Show all commands              |
| `price`   | Get current price for a symbol |
| `balance` | View account balance           |
| `market`  | Place a market order           |
| `limit`   | Place a limit order            |
| `status`  | Check order status             |
| `cancel`  | Cancel an order                |
| `exit`    | Quit the bot                   |

🧠 Example Session
Enter command: price
Enter symbol: BTCUSDT
Current price of BTCUSDT: 68,452.31 USDT

Enter command: market
Symbol: BTCUSDT
Side: BUY
Quantity: 0.001
✓ Market order placed successfully

📁 Project Structure
binance-trading-bot/
│
├── venv/                  # Virtual environment
├── logs/                  # Log files
│   └── trading_bot.log   # Main log file
│
├── bot.py                # Main bot class and CLI
├── orders.py             # Order execution logic
├── utils.py              # Helper functions
├── config.py             # Configuration management
│
├── .env                  # API credentials (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
└── README.md           # This file

🧪 Testing

Run the bot and try:

Checking price: price

Placing order: market

Cancelling order: cancel


📊 Order Types Explained
Market Order
Executes immediately at the current market price. Best for quick entries/exits.
Limit Order
Executes only at your specified price or better. Good for targeting specific price levels.
Stop-Limit Order
Triggers a limit order when price reaches your stop price. Useful for stop-losses and breakout entries.
OCO (One-Cancels-Other)
Places two orders simultaneously - when one executes, the other is automatically cancelled. Perfect for take-profit + stop-loss scenarios.
TWAP (Time-Weighted Average Price)
Splits a large order into smaller chunks executed over time to reduce market impact and get better average prices.

