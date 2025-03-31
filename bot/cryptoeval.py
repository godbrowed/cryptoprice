import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import API_KEY

def get_price(crypto):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms=USD"
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, headers=headers)
    return response.json().get("USD", 0)

def parse_crypto_expression(expr):
    tokens = re.findall(r"(\d+(\.\d+)?)\s*([a-zA-Z]+)|([+\-*/])", expr)
    
    parsed_expr = []
    prices = {}

    for token in tokens:
        num, dec, crypto, op_token = token
        if num:
            amount = float(num)
            if crypto not in prices:
                prices[crypto] = get_price(crypto)
            parsed_expr.append(f"({amount * prices[crypto]})")
        elif op_token:
            parsed_expr.append(op_token)
    
    return "".join(parsed_expr), prices

def safe_eval(expr):
    try:
        return eval(expr, {"__builtins__": None}, {})
    except Exception:
        return None

async def cryptoeval(update: Update, context):
    text = update.message.text.strip()
    chat_id = update.message.chat_id

    # List of supported cryptos(full name)
    crypto_names = {
        "btc": "Bitcoin",
        "eth": "Ethereum",
        "sol": "Solana",
        "xrp": "Ripple",
        "ltc": "Litecoin",
        "doge": "Dogecoin"
    }

    try:
        parsed_expr, prices = parse_crypto_expression(text)
        result = safe_eval(parsed_expr)
        if result is None:
            return

        if isinstance(result, (int, float)):
            result_text = f"${result:.2f}"
        else:
            result_text = f"{result}"

        formatted_text = f"<b>{text}</b> = <code>{result_text}</code>"

        buttons = []
        for crypto in prices.keys():
            # Full crypto name(add the list of cryptos you want to support)
            crypto_name = crypto_names.get(crypto.lower(), crypto.upper())
            crypto_link = f"https://www.tradingview.com/symbols/{crypto.upper()}USD/?exchange=CRYPTO"
            buttons.append([InlineKeyboardButton(crypto_name, url=crypto_link)])

        reply_markup = InlineKeyboardMarkup(buttons)
        if len(text) < 10:
            return
        with open("images/image.jpg", "rb") as banner:
            await context.bot.send_photo(chat_id, banner, caption=formatted_text, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
