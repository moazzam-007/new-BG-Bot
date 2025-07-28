from flask import Blueprint, request, jsonify
from .processor import queue_image_job

bp = Blueprint("routes", __name__)

@bp.route("/", methods=["GET"])
def home():
    return "🟢 Bot is running!"

@bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    data = request.json
    image_url = data.get("image_url")
    user_id = data.get("user_id", "default")  # optional tag
    if not image_url:
        return jsonify({"error": "Missing image_url"}), 400

    job_id = queue_image_job(image_url, user_id)
    return jsonify({"status": "queued", "job_id": job_id})
