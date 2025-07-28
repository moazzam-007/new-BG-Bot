from flask import Flask
import os
from dotenv import load_dotenv
from pyrogram import Client

# .env file se environment variables load karein
load_dotenv()

app = Flask(__name__)

# Pyrogram client ko Flask app ke saath initialize karein
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_DIR = "session"

# Make sure the session directory exists
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# Bot instance globally accessible
bot = Client("my_session", api_id=API_ID, api_hash=API_HASH, workdir=SESSION_DIR, no_updates=True)

# Important: Agar aap webhook use kar rahe hain, toh no_updates=True rakhein
# Aur alag se Pyrogram client ko start karein.
# Hum yahan userbot mode mein hain, toh polling use kar rahe hain.
# Isko abhi `bot/main.py` mein handle karenge.

from app import routes
