import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import API_KEY
from bot.time import handle_time_request

def get_price(crypto):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto.upper()}&tsyms=USD"
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, headers=headers)
    return response.json().get("USD", 0)

def extract_crypto(text):
    return re.findall(r"(\d+(\.\d+)?)\s+([a-zA-Z]+)", text)

async def multiply_crypto(update: Update, context):
    text = update.message.text.strip()
    chat_id = update.message.chat_id
    if re.search(r"[+\-*/]", text):
        return
    try:
        tokens = extract_crypto(text)
        if not tokens:
            await handle_time_request(update, context)
            return
        aggregated = {}
        for amount_str, _, crypto in tokens:
            crypto_lower = crypto.lower()
            if crypto_lower in ("utc", "gmt"):
                continue
            aggregated[crypto_lower] = aggregated.get(crypto_lower, 0) + float(amount_str)
        if not aggregated:
            await handle_time_request(update, context)
            return
        formatted_text = ""
        buttons = []
        mapping = {"btc": "Bitcoin", "eth": "Ethereum", "sol": "Solana"}
        for crypto, total_amount in aggregated.items():
            price = get_price(crypto)
            total_price = price * total_amount
            crypto_name = mapping.get(crypto, crypto.upper())
            formatted_text += f"<code>{crypto_name} ({crypto}):</code>\n"
            if total_amount != 1:
                formatted_text += f"<code>Amount: {total_amount}</code>\n"
            formatted_text += f"<code>Price: ${total_price:.2f} USD</code>\n\n"
            crypto_link = f"https://www.tradingview.com/symbols/{crypto.upper()}USD/?exchange=CRYPTO"
            buttons.append([InlineKeyboardButton(crypto_name, url=crypto_link)])
        reply_markup = InlineKeyboardMarkup(buttons)
        with open("images/image.jpg", "rb") as banner:
            await context.bot.send_photo(chat_id, banner, caption=formatted_text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", parse_mode="HTML")
