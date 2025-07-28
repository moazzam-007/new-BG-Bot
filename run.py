import os
import threading
import logging
from dotenv import load_dotenv

# .env file se environment variables load karein
load_dotenv()

# Flask app ko import karein aur use सीधे 'app' variable mein store karein
from app import app as flask_app # Flask app instance from app/__init__.py

# Pyrogram bot start karne ka function import karein
from bot.main import start_pyrogram_bot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Gunicorn expects a variable named 'app'
# So, assign the imported flask_app to 'app'
app = flask_app

if __name__ == '__main__':
    logging.info("Starting Pyrogram bot in a separate thread...")
    bot_thread = threading.Thread(target=start_pyrogram_bot)
    bot_thread.daemon = True  # Daemon thread will exit when main program exits
    bot_thread.start()

    logging.info("Pyrogram bot thread started. Flask app will be run by Gunicorn.")
    # Local testing ke liye Flask app chalane ki zarurat nahi hai yahan
    # Kyunki Gunicorn hi chalayega.
    # Agar aap phir bhi local testing karna chahte hain, toh aise karein:
    # app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))
