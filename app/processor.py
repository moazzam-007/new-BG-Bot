import os
from rembg import remove
from PIL import Image

async def process_image_with_template(input_path, template_id):
    # Remove background
    with open(input_path, "rb") as f:
        output_data = remove(f.read())

    no_bg_path = input_path.replace(".jpg", "_nobg.png")
    with open(no_bg_path, "wb") as f:
        f.write(output_data)

    # Overlay template
    template_path = os.path.join("overlays", f"template{template_id}.png")
    background = Image.open(template_path).convert("RGBA")
    subject = Image.open(no_bg_path).convert("RGBA")
    background.paste(subject, (0, 0), subject)

    final_path = input_path.replace(".jpg", "_final.png")
    background.save(final_path)
    return final_path
