from PIL import Image
import os

def process_image(img_path, template_id):
    template_path = f"templates/template{template_id}.png"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    bg_removed = Image.open(img_path).convert("RGBA")
    template = Image.open(template_path).convert("RGBA")

    # Image ko template ke center mein rakhte hain, aap adjust kar sakte hain
    # Calculate position to center the image on the template
    template_width, template_height = template.size
    img_width, img_height = bg_removed.size

    # Scale the image down if it's too large for the template
    if img_width > template_width or img_height > template_height:
        scale_factor = min(template_width / img_width, template_height / img_height) * 0.8 # 80% of max fit
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        bg_removed = bg_removed.resize((new_width, new_height), Image.LANCZOS)
        img_width, img_height = bg_removed.size # Update dimensions after resizing

    x_offset = (template_width - img_width) // 2
    y_offset = (template_height - img_height) // 2

    # template.paste(bg_removed, (100, 100), bg_removed)  # Old hardcoded position
    template.paste(bg_removed, (x_offset, y_offset), bg_removed) # Centered position
    
    # Output file ka naam unique rakhein taaki conflicts na hon
    output_filename = os.path.basename(img_path).replace(".png", "_final.png")
    # Ye assume kar raha hai ki image_path mein file temp mein hai,
    # toh output bhi wahin save karte hain.
    output_path = os.path.join(os.path.dirname(img_path), output_filename)
    template.save(output_path)

    return output_path
