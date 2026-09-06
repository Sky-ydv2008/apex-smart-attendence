import cv2
import numpy as np
import json
import base64
import logging

logger = logging.getLogger(__name__)

# Load Haar cascade classifier for frontal face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(img: np.ndarray) -> list:
    """
    Detects faces in image BGR array.
    Returns list of bounding boxes (x, y, w, h).
    """
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40)
    )
    return list(faces)


def generate_face_embedding(img: np.ndarray, face_box: tuple = None) -> list:
    """
    Generates a 128-dimensional normalized feature embedding for a face image.
    Uses multi-scale spatial histogram + gradient orientation features.
    """
    if img is None:
        return []

    # If face_box provided, crop face region
    if face_box is not None:
        x, y, w, h = face_box
        # Expand slightly for boundary context
        pad_x, pad_y = int(w * 0.1), int(h * 0.1)
        y1, y2 = max(0, y - pad_y), min(img.shape[0], y + h + pad_y)
        x1, x2 = max(0, x - pad_x), min(img.shape[1], x + w + pad_x)
        face = img[y1:y2, x1:x2]
    else:
        # Detect face first
        faces = detect_faces(img)
        if len(faces) == 0:
            face = img
        else:
            x, y, w, h = faces[0]
            face = img[y:y+h, x:x+w]

    if face.size == 0:
        return []

    # Normalize face crop to 128x128 grayscale
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if len(face.shape) == 3 else face
    resized = cv2.resize(gray, (128, 128))
    equalized = cv2.equalizeHist(resized)

    # 1. HOG features (64 dims)
    win_size = (128, 128)
    block_size = (64, 64)
    block_stride = (32, 32)
    cell_size = (32, 32)
    nbins = 8
    hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins)
    hog_feats = hog.compute(equalized).flatten()

    # Subsample or interpolate hog_feats to exactly 64 values
    if len(hog_feats) > 64:
        indices = np.linspace(0, len(hog_feats) - 1, 64, dtype=int)
        hog_feats = hog_feats[indices]

    # 2. Grid Spatial Color & Texture Intensity Stats (64 dims)
    # 4x4 grid over 128x128 image = 16 cells, each cell yields [mean, std, min, max] = 64 values
    cell_feats = []
    for row in range(4):
        for col in range(4):
            cell = equalized[row*32:(row+1)*32, col*32:(col+1)*32]
            cell_feats.extend([
                float(np.mean(cell)),
                float(np.std(cell)),
                float(np.min(cell)),
                float(np.max(cell))
            ])

    embedding = np.concatenate([hog_feats, cell_feats])

    # L2 normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    return embedding.tolist()


def compare_face_embeddings(emb1: list, emb2: list) -> float:
    """
    Computes cosine similarity between two face embedding vectors (0.0 to 1.0).
    """
    if not emb1 or not emb2 or len(emb1) != len(emb2):
        return 0.0

    v1 = np.array(emb1, dtype=np.float32)
    v2 = np.array(emb2, dtype=np.float32)

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = float(np.dot(v1, v2) / (norm1 * norm2))
    # Map [-1, 1] range to [0, 1]
    similarity = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
    return round(similarity, 4)


def verify_live_face_against_enrolled(live_img: np.ndarray, enrolled_emb_json: str) -> tuple[bool, float, dict]:
    """
    Verifies live camera face against stored enrolled face embedding JSON.
    Returns (is_matched, similarity_score, details_dict).
    """
    if not enrolled_emb_json:
        return False, 0.0, {"error": "No enrolled face embedding found for student"}

    try:
        enrolled_emb = json.loads(enrolled_emb_json)
    except Exception as e:
        logger.error(f"Failed to parse enrolled embedding JSON: {e}")
        return False, 0.0, {"error": "Corrupt enrolled embedding data"}

    faces = detect_faces(live_img)
    if not faces:
        return False, 0.0, {"error": "No face detected in live scan", "faces_count": 0}
    if len(faces) > 1:
        return False, 0.0, {"error": "Multiple faces detected! Please ensure only 1 student is in frame.", "faces_count": len(faces)}

    # Generate live face embedding
    live_emb = generate_face_embedding(live_img, faces[0])
    similarity = compare_face_embeddings(live_emb, enrolled_emb)

    from app.config import FACE_SIMILARITY_THRESHOLD
    # Consider matched if similarity >= threshold (default 0.65)
    is_matched = similarity >= FACE_SIMILARITY_THRESHOLD

    return is_matched, similarity, {
        "faces_count": 1,
        "face_box": [int(x) for x in faces[0]],
        "similarity": similarity,
        "threshold": FACE_SIMILARITY_THRESHOLD
    }
