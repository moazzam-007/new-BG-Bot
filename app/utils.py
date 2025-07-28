import os

async def save_temp_file(client, message):
    file_path = f"temp_{message.from_user.id}.jpg"
    await client.download_media(message, file_path)
    return file_path

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
