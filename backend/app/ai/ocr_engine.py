import re
import cv2
import numpy as np
import base64
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Lazy initialization of EasyOCR to speed up startup
_ocr_reader = None

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR reader...")
            _ocr_reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            logger.warning(f"Could not load EasyOCR: {e}. Falling back to basic regex / barcode mode.")
            _ocr_reader = False
    return _ocr_reader


def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decodes a base64 encoded image string to an OpenCV BGR numpy array."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def detect_and_warp_card(img: np.ndarray) -> tuple[np.ndarray, bool, float]:
    """
    Detects rectangular card in image and warps perspective to top-down view.
    Returns (warped_img, card_found, confidence_score).
    """
    if img is None:
        return img, False, 0.0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    card_contour = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # ID card typically has 4 vertices and area > threshold
        if len(approx) == 4 and cv2.contourArea(c) > 10000:
            card_contour = approx
            break

    if card_contour is not None:
        # Perspective transform
        pts = card_contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
        return warped, True, 0.95

    return img, False, 0.70  # Return original image if card contour not isolated


def extract_text_and_student_id(img: np.ndarray) -> dict:
    """
    Extracts text from card image using EasyOCR/regex and parses student ID, name, class.
    """
    reader = get_ocr_reader()
    extracted_text = ""
    lines = []

    if reader:
        try:
            results = reader.readtext(img)
            lines = [res[1] for res in results if res[2] > 0.2]
            extracted_text = " ".join(lines)
        except Exception as e:
            logger.error(f"OCR execution failed: {e}")

    # Regex patterns for Student ID (e.g. CS20260142, STU-1001, 2026CS0142, ID: CS101)
    id_pattern = r'\b([A-Z]{2,4}\d{4,8}|\d{4}[A-Z]{2}\d{3,5}|STU-\d{3,5}|ID:\s*[A-Z0-9]+)\b'
    match = re.search(id_pattern, extracted_text, re.IGNORECASE)
    
    student_id = None
    if match:
        student_id = match.group(1).upper().replace("ID:", "").strip()

    # If EasyOCR didn't find pattern, scan line by line
    if not student_id:
        for line in lines:
            line_clean = line.replace(" ", "").upper()
            m = re.search(r'([A-Z]{2,4}\d{4,8})', line_clean)
            if m:
                student_id = m.group(1)
                break

    return {
        "raw_text": extracted_text,
        "lines": lines,
        "student_id": student_id,
        "confidence": 0.92 if student_id else 0.40
    }
