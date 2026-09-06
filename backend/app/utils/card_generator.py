from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
from pathlib import Path
from app.config import CARDS_DIR, BASE_DIR

def generate_student_id_card(student, class_name: str) -> str:
    """
    Generates a professional student ID card PNG image.
    Saves to DATA_DIR/id_cards/card_<student_id>.png.
    Returns relative URL path '/uploads/cards/card_<student_id>.png'.
    """
    card_filename = f"card_{student.student_id}.png"
    output_path = CARDS_DIR / card_filename

    # Card dimensions: standard ID-1 credit card aspect ratio (600 x 380 px)
    width, height = 600, 380
    image = Image.new("RGB", (width, height), color="#0F172A") # Dark slate slate-900 background
    draw = ImageDraw.Draw(image)

    # 1. Header banner (Indigo gradient effect)
    draw.rectangle([0, 0, width, 80], fill="#4F46E5") # Indigo-600
    
    # Try loading default font or load fallback
    try:
        font_header = ImageFont.truetype("arial.ttf", 24)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arialbd.ttf", 20)
        font_body = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except Exception:
        font_header = ImageFont.load_default()
        font_sub = font_header
        font_title = font_header
        font_body = font_header
        font_bold = font_header

    # Header text
    draw.text((20, 18), "ATTENDAI ACADEMY", fill="#FFFFFF", font=font_header)
    draw.text((20, 48), "OFFLINE SMART ATTENDANCE SYSTEM", fill="#E0E7FF", font=font_sub)

    # Accent decorative line
    draw.rectangle([0, 78, width, 82], fill="#818CF8")

    # 2. Student Photo Box
    photo_box = [30, 105, 170, 265]
    draw.rectangle(photo_box, fill="#1E293B", outline="#6366F1", width=2)

    # If student photo exists, paste photo inside box
    photo_loaded = False
    if student.photo_url:
        try:
            # Resolve file path
            photo_filename = student.photo_url.split("/")[-1]
            photo_path = BASE_DIR / "data" / "uploads" / photo_filename
            if photo_path.exists():
                student_photo = Image.open(photo_path).convert("RGB")
                student_photo = student_photo.resize((136, 156))
                image.paste(student_photo, (32, 107))
                photo_loaded = True
        except Exception:
            pass

    if not photo_loaded:
        draw.text((60, 175), "NO PHOTO", fill="#64748B", font=font_sub)

    # 3. Student Details Text
    draw.text((190, 105), student.name, fill="#F8FAFC", font=font_title)
    
    # Detail fields
    draw.text((190, 145), "STUDENT ID:", fill="#94A3B8", font=font_body)
    draw.text((310, 145), str(student.student_id), fill="#38BDF8", font=font_bold)

    draw.text((190, 180), "CLASS:", fill="#94A3B8", font=font_body)
    draw.text((310, 180), f"{class_name}", fill="#F1F5F9", font=font_body)

    draw.text((190, 215), "ROLL NO:", fill="#94A3B8", font=font_body)
    draw.text((310, 215), str(student.roll_number), fill="#F1F5F9", font=font_body)

    draw.text((190, 250), "STATUS:", fill="#94A3B8", font=font_body)
    draw.text((310, 250), "ENROLLED / ACTIVE", fill="#4ADE80", font=font_bold)

    # 4. Generate & Paste QR Code for instant scannability
    try:
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(f"ID:{student.student_id}|NAME:{student.name}|CLASS:{class_name}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGB")
        image.paste(qr_img, (470, 105))
    except Exception:
        pass

    # Footer bar
    draw.rectangle([0, 340, width, height], fill="#1E293B")
    draw.text((20, 352), f"VALID FOR SESSION 2026  •  PROPERTY OF ATTENDAI", fill="#94A3B8", font=font_sub)

    image.save(output_path)
    return f"/uploads/cards/{card_filename}"
