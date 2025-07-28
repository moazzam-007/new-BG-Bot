import uuid
import threading
import queue
import time

image_queue = queue.Queue()

def queue_image_job(image_url, user_id):
    job_id = str(uuid.uuid4())
    image_queue.put({"image_url": image_url, "user_id": user_id, "job_id": job_id})
    return job_id

def start_background_worker():
    from bot.userbot import send_to_rembg_bot  # avoid circular import

    def worker():
        while True:
            job = image_queue.get()
            if job:
                try:
                    send_to_rembg_bot(job["image_url"], job["user_id"])
                except Exception as e:
                    print("❌ Error in worker:", e)
            time.sleep(1)

    threading.Thread(target=worker, daemon=True).start()
