from flask import request, jsonify
from app import app
from app.processor import process_image
import os

@app.route('/process_internal', methods=['POST']) # Naam badal diya taaki direct access na ho
def handle_internal_request():
    data = request.json
    image_path = data.get('image_path')
    # chat_id abhi yahan direct use nahi hoga, bot isko handle karega
    template_id = data.get('template_id', '1')

    if not image_path:
        # chat_id ki zarurat nahi kyunki bot hi reply karega
        return jsonify({'error': 'Missing image_path'}), 400

    try:
        result_path = process_image(image_path, template_id)
        return jsonify({'result_path': result_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check route
@app.route('/')
def health_check():
    return "Bot is running!"
