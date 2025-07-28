import os
from datetime import datetime
import random

def get_unique_filename(extension=".png"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    return f"{timestamp}_{random_suffix}{extension}"

# Temporary directory for downloaded images
TEMP_DIR = "temp_downloads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
