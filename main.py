from pyrogram import Client, filters
import asyncio
import os
import requests
from app.utils import get_unique_filename, TEMP_DIR
from app import app, bot # Flask app aur Pyrogram bot ko import karein
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        response = await client.listen(TARGET_BOT, filters.photo, timeout=60) # Only listen for photos

        if response and response.photo:
            removed_bg_filename = get_unique_filename("_removed_bg.png")
            removed_bg_path = os.path.join(TEMP_DIR, removed_bg_filename)
            await response.download(file_name=removed_bg_path)
            logging.info(f"Received background removed image: {removed_bg_path}")

            await message.reply_text("Background remove ho gaya hai, ab template apply kar raha hoon...")

            # Call Flask API to process with template
            # Ab hum internal endpoint ko call karenge
            # Ye request localhost par jayegi, kyunki Flask aur bot ek hi container mein hain.
            template_id = "1"  # TODO: User se dynamically lena
            
            flask_api_url = "http://localhost:5000/process_internal" # Flask internal URL
            
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
            logging.warning(f"No photo response from {TARGET_BOT} for user {message.from_user.id}")

    except asyncio.TimeoutError:
        await message.reply("Operation mein time lag gaya. Dobara try karein, please.")
        logging.error(f"Timeout waiting for response from {TARGET_BOT} for user {message.from_user.id}")
    except Exception as e:
        await message.reply(f"Kuch galti ho gayi: {e}")
        logging.exception(f"An unexpected error occurred for user {message.from_user.id}")
    finally:
        # Clean up temporary files
        if os.path.exists(image_path):
            os.remove(image_path)
            logging.info(f"Cleaned up {image_path}")
        if 'removed_bg_path' in locals() and os.path.exists(removed_bg_path):
            os.remove(removed_bg_path)
            logging.info(f"Cleaned up {removed_bg_path}")
        if 'final_path' in locals() and os.path.exists(final_path):
            os.remove(final_path)
            logging.info(f"Cleaned up {final_path}")


def start_bot():
    """Starts the Pyrogram bot in a separate thread."""
    logging.info("Starting Pyrogram bot...")
    bot.run() # This is a blocking call, so run in a thread

if __name__ == "__main__":
    # Start Pyrogram bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True # Daemon thread will exit when main program exits
    bot_thread.start()

    logging.info("Starting Flask app...")
    # Start Flask app using Gunicorn for production
    # Ye command Render par chalega.
    # Flask development server ko direct run na karein production mein.
    # For local testing, you can use: app.run(host='0.0.0.0', port=5000)
    # Gunicorn command will be in render.yaml or start command
