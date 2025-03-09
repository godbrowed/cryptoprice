import os
import requests
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, filters, Application

def get_price(crypto):
    api_key = ""
    url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms=USD"
    headers = {"Authorization": f"Apikey {api_key}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["USD"]


def add_price_to_image(image_path, price):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
    
    width, height = img.size
    text = f"${price:.2f}"
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1] 
    offset_x = 90  # Зміщення вправо
    offset_y = 50  # Зміщення вгору

    position = ((width - text_width) // 2 + offset_x, height - 140 - offset_y)
    # Draw text on the image
    draw.text(position, text, font=font, fill=(138, 43, 255))
    
    return img

def extract_amount_and_crypto(text):
    match = re.match(r"^(\d+(\.\d+)?)\s*(\w+)$", text)
    amount = float(match.group(1))
    crypto = match.group(3)
    return amount, crypto

async def handle_message(update: Update, context):
    text = update.message.text
    chat_id = update.message.chat_id

    # Перевіряємо, чи є в тексті число та валюта (наприклад, "1 BTC", "10 ETH")
    match = re.match(r"^(\d+(\.\d+)?)\s+([A-Za-z]+)$", text)
    if not match:
        return
    
    try:
        amount, crypto = extract_amount_and_crypto(text)
        
        price = get_price(crypto)
        
        total_price = price * amount
        
        image_path = "images/image.jpg"
        img = add_price_to_image(image_path, total_price)
        
        img_path = "images/price_image.png"
        img.save(img_path, "PNG")
        
        crypto_link = f"https://www.tradingview.com/symbols/{crypto.upper()}USD/?exchange=CRYPTO"
        
        with open(img_path, "rb") as photo:
            caption = f"💰 Price: ${total_price:.2f}"
            button = InlineKeyboardButton("View Chart", url=crypto_link)
            reply_markup = InlineKeyboardMarkup([[button]])
            await context.bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# Main function to start the bot
def main():
    # Initialize the bot
    bot = Bot(token="")
    application = Application.builder().token("").build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
