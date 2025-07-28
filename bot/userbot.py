from pyrogram import Client
import asyncio
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "bot/session"

user = Client(session_name, api_id=api_id, api_hash=api_hash)

async def send_image_and_get_output(image_url, user_id):
    async with user:
        bot_chat = "@BgRemover_ai_bot"
        msg = await user.send_message(bot_chat, image_url)
        print(f"🟡 Sent to BG bot: {msg.message_id}")

        # Listen for reply
        response = await user.listen(bot_chat)
        if response.photo:
            path = await user.download_media(response)
            print(f"✅ BG removed: {path}")
        else:
            print("❌ BG bot did not return image.")

def send_to_rembg_bot(image_url, user_id):
    asyncio.run(send_image_and_get_output(image_url, user_id))
