from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from app.processor import process_image_with_template
from app.utils import save_temp_file, cleanup_files

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

bot = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=session_string)

# Dictionary to track which user sent which image
user_image_map = {}

@bot.on_message(filters.photo)
async def handle_photo(client, message):
    file_path = await save_temp_file(client, message)
    user_image_map[message.from_user.id] = file_path

    # Send template options
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Template 1", callback_data="template_1")],
        [InlineKeyboardButton("Template 2", callback_data="template_2")],
        [InlineKeyboardButton("Template 3", callback_data="template_3")]
    ])
    await message.reply("🖼 Choose a template:", reply_markup=keyboard)

@bot.on_callback_query()
async def template_selected(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_image_map:
        await callback_query.answer("❌ No image found. Please send an image first.", show_alert=True)
        return

    # Extract template number
    template_id = callback_query.data.split("_")[1]
    input_path = user_image_map[user_id]

    output_path = await process_image_with_template(input_path, template_id)
    await client.send_photo(chat_id=user_id, photo=output_path)

    # Clean up
    cleanup_files(input_path, output_path)
    del user_image_map[user_id]
    await callback_query.answer("✅ Done!")
