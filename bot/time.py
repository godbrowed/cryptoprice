import re
import arrow
from telegram import Update
from telegram.ext import ContextTypes

def convert_time(time_str):
    pattern = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(UTC|GMT)", re.IGNORECASE)
    match = re.match(pattern, time_str.strip())
    if not match:
        return "Invalid time format"
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    tz = match.group(3).upper()

    base_time = arrow.get(f"{hour:02d}:{minute:02d}", "HH:mm").replace(tzinfo="UTC")

    msk = base_time.to("Europe/Moscow").shift(minutes=30).format("HH:mm")  # adding 30 minutes for MSK
    kiev = base_time.to("Europe/Kiev").shift(minutes=-2).format("HH:mm")  # minus 2 minutes for Kiev
    cet = base_time.to("CET").format("HH:mm")
    utc_str = base_time.format("HH:mm")
    
    result = (
        f"<code>{hour:02d}:{minute:02d} ({utc_str}) {tz} ┬─> {msk} MSK\n"
        f"\t                 ├─> {kiev} KIEV\n"
        f"\t                 ├─> {cet} CET\n"
        f"\t                 └─> {utc_str} UTC</code>"
    )
    return result

async def handle_time_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()
    result = convert_time(time_str)
    with open("images/image.jpg", "rb") as banner:
         await context.bot.send_photo(update.message.chat_id, banner, caption=result, parse_mode="HTML")
