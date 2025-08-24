# Telegram Bot for Token Trade Monitoring

## Overview
This Python script implements a Telegram bot that monitors token trades on the TON blockchain using the `geckoterminal.com` and `tonapi.io` APIs. The bot sends real-time trade notifications to a specified Telegram group, including details like transaction volume, wallet address, market cap, and holder count. It also supports inline buttons for user interaction.

## Features
- Monitors token trades for a specified pool on the TON blockchain.
- Sends formatted trade notifications to a Telegram group with details such as:
  - Transaction type (buy/sell)
  - TON and USD value
  - Token amount
  - Wallet address (shortened, with a link to `tonviewer.com`)
  - Transaction hash (with a link to `tonviewer.com`)
  - Current price and market cap
  - Holder count and new holder status
- Includes inline buttons for buying the token, joining a chat, or inviting friends.
- Filters transactions below a specified value (optional, default: 10 TON).
- Logs activities and errors for debugging.
- Runs continuously with configurable request frequency.

## Requirements
- Python 3.6+
- Required libraries:
  - `requests`
  - `pyTelegramBotAPI` (telebot)
  - `threading`
  - `logging`
  - `time`

Install the required libraries:
```bash
pip install requests pyTelegramBotAPI
```

## Configuration
Before running the script, configure the following settings in the code:
- `BOT_TOKEN`: Your Telegram bot token (obtained from BotFather).
- `GROUP_CHAT_ID`: The Telegram group chat ID (without quotes).
- `TOKEN_NAME`: The name of the token being monitored.
- `TOKEN_ADDRESS`: The token's address on the TON blockchain.
- `POOL_ID`: The pool ID from `geckoterminal.com`.
- `BASE_URL`: The base API URL for `geckoterminal.com` (default: `https://api.geckoterminal.com/api/v2`).
- `IS_CHECKING`: Enable/disable filtering of transactions below `CHECKING_VALUE` (True/False).
- `CHECKING_VALUE`: Minimum TON value for transactions to be reported (default: 10).
- `TIMEOUT`: Request frequency in seconds (minimum: 1 second).
- Inline button URLs:
  - `button1`: URL for "BUY $RRMONEY" button.
  - `button2`: URL for "OUR CHAT" button.
  - `button3`: URL for "INVITE FRIENDS" button.

## Usage
1. Configure the settings as described above.
2. Run the script:
```bash
python bot.py
```

The bot will start monitoring trades and sending notifications to the specified Telegram group.

## Output
The bot sends messages to the Telegram group in Markdown format, including:
- Token name with a link to the pool on `geckoterminal.com`.
- Transaction details (TON/USD value, token amount, wallet, transaction link).
- Price, market cap, holder count, and new holder status.
- Inline buttons for user interaction.

### Example Output
```
[TOKEN_NAME](https://www.geckoterminal.com/ru/ton/pools/POOL_ID) BUY
TON: 15.23 ($50.45)
Token: 1,000 TOKEN_NAME
Wallet: [abcd...wxyz](https://tonviewer.com/wallet_address) | [TXN](https://tonviewer.com/transaction/tx_hash)
Price: $0.05
Market Cap: $1,234,567
Holders: 5,678
New Holder: True
```

## Error Handling
- Logs network errors during API requests.
- Handles invalid API responses.
- Catches and logs Telegram polling errors.
- Skips transactions below the `CHECKING_VALUE` if `IS_CHECKING` is enabled.

## Notes
- Requires an active internet connection to access `geckoterminal.com` and `tonapi.io` APIs.
- The `TIMEOUT` should not be set below 1 second to avoid API rate limits.
- Ensure the `BOT_TOKEN`, `GROUP_CHAT_ID`, `TOKEN_ADDRESS`, and `POOL_ID` are valid.
- The bot runs in a separate thread for trade monitoring while polling Telegram messages.
