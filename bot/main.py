from pyrogram import Client, filters
import asyncio
import os
import requests
from app.utils import get_unique_filename, TEMP_DIR
import logging
from dotenv import load_dotenv # Import for local testing, Render will load them

# Load environment variables (for local testing, Render will handle it)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_DIR = "session"

# Make sure the session directory exists
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

bot = Client("my_session", api_id=API_ID, api_hash=API_HASH, workdir=SESSION_DIR, no_updates=True)

TARGET_BOT = "BgRemover_ai_bot"

@bot.on_message(filters.private & filters.photo)
async def handle_user_image(client, message):
    logging.info(f"Image received from user: {message.from_user.id}")
    
    await message.reply_text("Image receive ho gayi hai, background remove kar raha hoon...")

    unique_img_filename = get_unique_filename(".png")
    image_path = os.path.join(TEMP_DIR, unique_img_filename)

    try:
        # Download user image
        await message.download(file_name=image_path)
        logging.info(f"Image saved to: {image_path}")

        # Forward image to background remover bot
        logging.info(f"Forwarding image to {TARGET_BOT}")
        bg_msg = await client.send_photo(TARGET_BOT, image_path)
        
        # Wait for response (within 60 sec)
        logging.info(f"Waiting for response from {TARGET_BOT}...")
        # Pyrogram's listen needs filters if you want specific message types
        response = await client.listen(TARGET_BOT, filters.photo, timeout=60) 

        if response and response.photo:
            removed_bg_filename = get_unique_filename("_removed_bg.png")
            removed_bg_path = os.path.join(TEMP_DIR, removed_bg_filename)
            await response.download(file_name=removed_bg_path)
            logging.info(f"Received background removed image: {removed_bg_path}")

            await message.reply_text("Background remove ho gaya hai, ab template apply kar raha hoon...")

            # Call Flask API to process with template
            template_id = "1"  # TODO: User se dynamically lena
            
            flask_api_url = "http://localhost:5000/process_internal" # Flask internal URL
            
            # Using `requests` needs to be in a separate thread if called from an async function directly
            # For simplicity in this userbot, we'll keep it as is, but in a true async context,
            # you might want to use aiohttp or run requests in executor.
            # However, Pyrogram's @on_message handlers are generally safe for blocking calls.
            res = requests.post(flask_api_url, json={
                "image_path": removed_bg_path,
                "template_id": template_id
            })

            if res.status_code == 200:
                final_path = res.json()['result_path']
                if os.path.exists(final_path):
                    await message.reply_photo(final_path, caption="Aapki final image!")
                    logging.info(f"Final image sent to user: {final_path}")
                else:
                    await message.reply("Error: Final image file not found after processing.")
                    logging.error(f"Final image file not found: {final_path}")
            else:
                await message.reply(f"Error processing image with template: {res.json().get('error', 'Unknown error')}")
                logging.error(f"Flask API error: {res.status_code} - {res.json()}")
        else:
            await message.reply("Maaf kijiye, @BgRemover_ai_bot se koi response nahi mila ya photo nahi mili.")
            logging.warning(f"No photo response or unexpected response from {TARGET_BOT} for user {message.from_user.id}")

    except asyncio.TimeoutError:
        await message.reply("Operation mein time lag gaya. Dobara try karein, please.")
        logging.error(f"Timeout waiting for response from {TARGET_BOT} for user {message.from_user.id}")
    except Exception as e:
        await message.reply(f"Kuch galti ho gayi: {e}")
        logging.exception(f"An unexpected error occurred for user {message.from_user.id}")
    finally:
        # Clean up temporary files
        temp_files_to_clean = [image_path]
        if 'removed_bg_path' in locals():
            temp_files_to_clean.append(removed_bg_path)
        if 'final_path' in locals():
            temp_files_to_clean.append(final_path)

        for f_path in temp_files_to_clean:
            if os.path.exists(f_path):
                os.remove(f_path)
                logging.info(f"Cleaned up {f_path}")


def start_pyrogram_bot():
    """Starts the Pyrogram bot. This is a blocking call."""
    logging.info("Starting Pyrogram bot...")
    bot.run()
