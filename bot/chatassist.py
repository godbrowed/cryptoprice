import sqlite3
import requests
from telegram import Update
from telegram.ext import CommandHandler
from google import genai
from PIL import Image
from google.genai import types
from io import BytesIO

GEMINI_API_KEY = ""
client = genai.Client(api_key=GEMINI_API_KEY)

conn = sqlite3.connect("bot_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        request TEXT,
        response TEXT
    )
''')
conn.commit()

def load_instructions():
    with open("D:\\IT\\tgbots\\Python tg\\bot\\kakashka.txt", "r", encoding="utf-8") as file:
        return file.read()

system_instruction = load_instructions()

def save_to_db(user_id, request, response):
    cursor.execute("INSERT INTO history (user_id, request, response) VALUES (?, ?, ?)", 
                   (user_id, request, response))
    conn.commit()

def get_last_dialogue(user_id, limit=5):
    cursor.execute("SELECT request, response FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?", 
                   (user_id, limit))
    return cursor.fetchall()

def generate_text(prompt, user_id):
    last_dialogue = get_last_dialogue(user_id)

    context = "\n".join([f"User: {req}\Bot: {resp}" for req, resp in last_dialogue])
    full_prompt = f"{context}\User: {prompt}\nBot:"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
            ]
        )
    )
    return response.text

async def generate_command(update: Update, context):
    user_id = update.message.chat_id
    if context.args:
        prompt = " ".join(context.args)
        # Generating response
        response = generate_text(prompt, user_id=user_id)
        # Save to db
        save_to_db(user_id, prompt, response)

        await update.message.reply_text(response, parse_mode="HTML")

def generate_image(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation", #Important
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
    )
    )
    return response

async def generate_command(update: Update, context):
    user_id = update.message.chat_id
    if context.args:
        prompt = " ".join(context.args)
        response = generate_text(prompt, user_id)
        await update.message.reply_text(response, parse_mode="HTML")

# Removed misplaced loop

async def generate_image_command(update: Update, context):
    if context.args:
        prompt = " ".join(context.args)
        response = generate_image(prompt)
        if isinstance(response, str):
            await update.message.reply_text(response)
async def generate_image_command(update: Update, context):
    if context.args:
        prompt = " ".join(context.args)
        response = generate_image(prompt)
        if isinstance(response, str):
            await update.message.reply_text(response)
        else:
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    await update.message.reply_text(part.text)
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save('gemini-native-image.png')
                    await update.message.reply_photo(photo='gemini-native-image.png')

def add_chatassist_handlers(application):
    application.add_handler(CommandHandler("gen", generate_command))
    application.add_handler(CommandHandler("genimg", generate_image_command))
