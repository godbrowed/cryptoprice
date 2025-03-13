# main.py
from telegram.ext import Application, MessageHandler, filters
from bot.config import TOKEN
from bot.eval import handle_eval_request
from bot.cryptoeval import cryptoeval
from bot.multiplycrypto import multiply_crypto
from bot.time import handle_time_request
import re

def is_time_request(text: str):
    return bool(re.fullmatch(r"\d{1,2}(?::\d{2})?\s*(UTC|GMT)", text, re.IGNORECASE))

def is_crypto_calculation(text: str):
    return bool(re.search(r"[+\-*/]", text)) and bool(re.search(r"\d+\s*[a-zA-Z]+", text)) and not is_time_request(text)

def is_crypto_multiplication(text: str):
    return bool(re.fullmatch(r"(\d+(\.\d+)?\s+[a-zA-Z]+\s*)+", text)) and not re.search(r"[+\-*/]", text) and not is_time_request(text)

def is_single_crypto_price_request(text: str):
    return bool(re.fullmatch(r"\d+(\.\d+)?\s+[a-zA-Z]+", text)) and not is_time_request(text)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda update, context: (
            handle_time_request(update, context) if is_time_request(update.message.text.strip())
            else multiply_crypto(update, context) if is_crypto_multiplication(update.message.text.strip())
            else cryptoeval(update, context) if is_crypto_calculation(update.message.text.strip())
            else handle_eval_request(update, context) if is_single_crypto_price_request(update.message.text.strip())
            else handle_eval_request(update, context)
        )
    ))
    application.run_polling()

if __name__ == "__main__":
    main()
