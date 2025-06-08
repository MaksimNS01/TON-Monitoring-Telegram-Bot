# Импорт библиотек
import threading
import time
import requests
import logging
import telebot

from telebot import types

# Настриваемые параметры
BOT_TOKEN = "YOUR_TOKEN_BOT" # Токен ТГ бота (обязательно в кавычках)
GROUP_CHAT_ID = -0000000000 # ID чата (обязательно БЕЗ кавычек)
TOKEN_NAME = "TOKEN_NAME" # Название токена
TOKEN_ADDRESS = "TOKEN_ADDRESS" # Адрес токена
POOL_ID = "POOL_ID" # Адрес пула
BASE_URL = "https://api.geckoterminal.com/api/v2" # API URL
IS_CHECKING = False # Если вкл., то транзакции объемом менее CHECKING_VALUE будут пропущены (True/False)
CHECKING_VALUE = 10 # Величина для проверки объема транзакций 
TIMEOUT = 10 # Частота запроса (секунд). ! Не ставить меньше 1 секунды !
# Кнопки
markup = types.InlineKeyboardMarkup()
button1 = types.InlineKeyboardButton("BUY $RRMONEY", url="https://example.com/buy")
button2 = types.InlineKeyboardButton("OUR CHAT", url="https://example.com/chat")
button3 = types.InlineKeyboardButton("INVITE FRIENDS", url="https://example.com/invite")
markup.add(button1, button2)
markup.add(button3)

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
previous_holders_count = 0
TOKEN = f'[{TOKEN_NAME}](https://www.geckoterminal.com/ru/ton/pools/{POOL_ID})'
HEADERS = {"Accept": "application/json;version=20230302"} 


# Функция для форматирования чисел с запятыми
def format_number(number):
    return "{:,}".format(number)


def process_trade(trade):
    logging.debug(f"Received trade: {trade}")
    attributes = trade.get("attributes", {})
    wallet = attributes.get("tx_from_address", "")
    usd_value = round(float(attributes.get('volume_in_usd', 0)), 2)
    usd_value = format_number(usd_value)
    shortened_wallet = f'[{wallet[:4]}...{wallet[-4:]}](https://tonviewer.com/{wallet})'
    trans_url = attributes.get('tx_hash', '')
    TXN = f"[TXN](https://tonviewer.com/transaction/{trans_url})"
    market_cap = get_token_info()
    market_cap = round(market_cap)
    market_cap = format_number(market_cap)
    holders_count, is_new_holder = get_holders_info()
    holders_count = format_number(holders_count)

    if attributes.get("kind", "") == "buy":
        ton_value = round(float(attributes.get('from_token_amount', 0)), 2)
        ton_value_formatted = format_number(ton_value)
        token_amount = attributes.get('to_token_amount', 0)
        token_amount = format_number(float(token_amount))
        msg = (
            f"{TOKEN} {attributes.get('kind', '').upper()}\n"
            f"\nTON: {ton_value_formatted} (${usd_value})\n"
            f"Token: {token_amount} {TOKEN_NAME}\n"
            f"Wallet: {shortened_wallet} | {TXN}\n"
            f"Price: ${attributes.get('price_to_in_usd', 0)}\n"
            f"Market Cap: ${market_cap}\n"
            f"Holders: {holders_count}\n"
            f"New Holder: {is_new_holder}\n"
        )
    else: 
        ton_value = round(float(attributes.get('to_token_amount', 0)), 2)
        ton_value_formatted = format_number(ton_value)
        token_amount = attributes.get('from_token_amount', 0)
        token_amount = format_number(float(token_amount))
        msg = (
            f"{TOKEN} {attributes.get('kind', '').upper()}\n"
            f"\nTON: {ton_value_formatted} (${usd_value})\n"
            f"Token: {token_amount} {TOKEN_NAME}\n"
            f"Wallet: {shortened_wallet} | {TXN}\n"
            f"Price: ${attributes.get('price_from_in_usd', 0)}\n"
            f"Market Cap: ${market_cap}\n"
            f"Holders: {holders_count}\n"
            f"New Holder: {is_new_holder}\n"
        )
    try:
        if ton_value > CHECKING_VALUE or not IS_CHECKING:
            bot.send_message(GROUP_CHAT_ID, msg, parse_mode="MARKDOWN", disable_web_page_preview = True, reply_markup=markup)
            logging.info(f"Sent message to group {GROUP_CHAT_ID}: {msg}")
        else: 
            logging.info(f"Skipped because TON value is below 10: {ton_value}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")


def get_token_info():
    url = f"https://api.geckoterminal.com/api/v2/networks/ton/pools/{POOL_ID}"
    logging.debug(f"Requesting token info from {url}")
    try:
        r = requests.get(url, headers={"Accept": "application/json;version=20230302"}, timeout=10)
        if r.status_code != 200:
            logging.error(f"Token info request returned {r.status_code}")
            return {"price": 0, "market_cap": 0, "holders": 0}
    except Exception as e:
        logging.error(f"Error while requesting token info: {e}")
        return {"price": 0, "market_cap": 0, "holders": 0}
    data = r.json().get("data", {})
    attributes = data.get("attributes", {})
    market_cap = attributes.get("fdv_usd", 0)
    logging.debug(f"Retrieved token info: market_cap={market_cap}")
    market_cap = float(market_cap)
    return market_cap


def get_holders_info():
    global previous_holders_count
    url = f"https://tonapi.io/v2/jettons/{TOKEN_ADDRESS}/holders"
    logging.debug(f"Requesting token info from {url}")
    try:
        r = requests.get(url, headers={"Accept": "application/json;version=20230302"}, timeout=10)
        if r.status_code != 200:
            logging.error(f"Token info request returned {r.status_code}")
            return {"price": 0, "market_cap": 0, "holders": 0}
    except Exception as e:
        logging.error(f"Error while requesting token info: {e}")
        return {"price": 0, "market_cap": 0, "holders": 0}
    holders_count = r.json().get("total", {})
    if holders_count > previous_holders_count:
        is_new_holder = True
    else:
        is_new_holder = False
    previous_holders_count = holders_count
    logging.debug(f"Retrieved token info: holders={holders_count}")
    return holders_count, is_new_holder


def fetch_trades(last_timestamp):
    url = f"{BASE_URL}/networks/ton/pools/{POOL_ID}/trades"
    logging.debug(f"Fetching trades from {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        logging.error(f"Error while fetching trades: {e}")
        return []
    if r.status_code != 200:
        logging.error(f"Trades endpoint returned {r.status_code} for url: {url}")
        return []

    trades = r.json().get("data", [])
    new_trades = []
    for trade in trades:
        attributes = trade.get("attributes", {})
        ts = attributes.get("block_timestamp", "1970-01-01T00:00:00Z")
        try:
            ts_epoch = int(time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
        except Exception as e:
            logging.error(f"Error converting timestamp {ts} to epoch: {e}")
            continue
        if ts_epoch > last_timestamp:
            new_trades.append(trade)
    logging.debug(f"Fetched {len(new_trades)} new trades")
    return new_trades


def monitor(callback):
    last_timestamp = 0
    logging.info("Starting trade monitoring...")
    while True:
        trades = fetch_trades(last_timestamp)
        if trades:
            for trade in trades:
                attributes = trade.get("attributes", {})
                ts = attributes.get("block_timestamp", "1970-01-01T00:00:00Z")
                try:
                    ts_epoch = int(time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
                except Exception as e:
                    logging.error(f"Error converting timestamp {ts} to epoch: {e}")
                    continue
                if ts_epoch > last_timestamp:
                    last_timestamp = ts_epoch
                    logging.debug(f"Processing trade with timestamp: {ts}")
                    callback(trade)
        else:
            logging.debug("No new trades fetched\n")
        time.sleep(TIMEOUT)


def start_monitoring():
    logging.info("Starting monitoring thread")
    monitor(process_trade)


if __name__ == "__main__":
    threading.Thread(target=start_monitoring, daemon=True).start()
    logging.info("Bot polling started")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Infinity polling error: {e}")
