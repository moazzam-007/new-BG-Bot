import os
import threading
import logging
from dotenv import load_dotenv

# .env file se environment variables load karein
load_dotenv()

# Flask app ko import karein
from app import app as flask_app # Alias diya taaki confusion na ho

# Pyrogram bot start karne ka function import karein
# Hamara bot/main.py mein ab `start_pyrogram_bot` function hoga
from bot.main import start_pyrogram_bot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.info("Starting Pyrogram bot in a separate thread...")
    bot_thread = threading.Thread(target=start_pyrogram_bot)
    bot_thread.daemon = True  # Daemon thread will exit when main program exits
    bot_thread.start()

    logging.info("Pyrogram bot thread started. Now starting Flask app...")
    # Gunicorn isko `flask_app` variable se load karega
    # Jab Render `gunicorn run:app` chalayega, toh wo `run.py` file mein
    # `app` naam ke variable ko dhundhega. Humne `flask_app` naam rakha hai.
    # Toh yahan hum `app` ko `flask_app` assign kar denge.
    app = flask_app # Gunicorn needs a variable named 'app'
    
    # Ye block Gunicorn run nahi karega, sirf local testing ke liye hai.
    # Gunicorn khud hi WSGI server start kar dega.
    # flask_app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))
