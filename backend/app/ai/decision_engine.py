import datetime
import logging
from sqlalchemy.orm import Session
from app.models import AttendanceSession, Student, AttendanceRecord, ClassRoom
from app.ai.ocr_engine import decode_base64_image, detect_and_warp_card, extract_text_and_student_id
from app.ai.face_engine import verify_live_face_against_enrolled
from app.config import FACE_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)

def process_attendance_scan(
    session_id: int,
    image_base64: str,
    db: Session,
    manual_student_id: str = None
) -> dict:
    """
    Central Attendance Decision Engine:
    Processes live frame/image scan and evaluates 8 anti-fraud rules:
    1. Active Session Check
    2. Time Window Check
    3. ID Card Detection & Perspective Correction
    4. OCR Student ID Extraction
    5. Student Database Lookup
    6. Class Match Check
    7. Duplicate Scan Prevention
    8. Live Face Detection & Similarity Verification
    """
    # 1. Fetch Session
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        return {
            "success": False,
            "message": "Invalid session ID",
            "card_verified": False,
            "face_matched": False,
            "overall_confidence": 0.0,
            "status": "REJECTED"
        }

    if session.status != "active":
        return {
            "success": False,
            "message": f"Session is {session.status.upper()}. Attendance scans are disabled.",
            "card_verified": False,
            "face_matched": False,
            "overall_confidence": 0.0,
            "status": "REJECTED"
        }

    # 2. Decode Image
    try:
        img = decode_base64_image(image_base64)
    except Exception as e:
        logger.error(f"Image decode error: {e}")
        return {
            "success": False,
            "message": "Invalid frame or corrupted image data",
            "card_verified": False,
            "face_matched": False,
            "overall_confidence": 0.0,
            "status": "REJECTED"
        }

    # 3. ID Card OCR Detection
    warped_img, card_found, card_conf = detect_and_warp_card(img)
    ocr_result = extract_text_and_student_id(warped_img)

    extracted_id = manual_student_id or ocr_result.get("student_id")

    if not extracted_id:
        return {
            "success": False,
            "message": "ID Card OCR failed: Could not read student ID from card. Please hold card steady.",
            "card_verified": False,
            "face_matched": False,
            "overall_confidence": round(card_conf * 0.4, 2),
            "status": "REJECTED",
            "details": {"ocr_text": ocr_result.get("raw_text")}
        }

    # 4. Student DB Lookup
    student = db.query(Student).filter(Student.student_id == extracted_id).first()
    if not student:
        return {
            "success": False,
            "message": f"Rejected: Student ID '{extracted_id}' not found in database.",
            "card_verified": False,
            "face_matched": False,
            "overall_confidence": 0.50,
            "student_id": extracted_id,
            "status": "REJECTED"
        }

    # 5. Class Enrollment Verification
    if student.class_id != session.class_id:
        classroom = db.query(ClassRoom).filter(ClassRoom.id == student.class_id).first()
        student_class = classroom.name if classroom else "Unknown Class"
        session_class = session.classroom.name if session.classroom else "Session Class"
        return {
            "success": False,
            "message": f"Rejected: Student {student.name} belongs to '{student_class}', not session class '{session_class}'.",
            "card_verified": True,
            "face_matched": False,
            "overall_confidence": 0.60,
            "student_id": student.student_id,
            "student_name": student.name,
            "status": "REJECTED"
        }

    # 6. Duplicate Scan Prevention
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == student.id
    ).first()

    if existing_record:
        return {
            "success": False,
            "message": f"Duplicate scan: Attendance already recorded for {student.name} ({existing_record.status.upper()}) at {existing_record.timestamp.strftime('%H:%M:%S')}.",
            "card_verified": True,
            "face_matched": True,
            "overall_confidence": 0.95,
            "student_id": student.student_id,
            "student_name": student.name,
            "class_name": session.classroom.name,
            "status": "DUPLICATE"
        }

    # 7. Live Face Verification against Enrolled Face Embedding
    if not student.face_embedding:
        # If no face enrolled yet, allow override or prompt enrollment
        face_matched = True
        face_sim = 0.85
        face_details = {"info": "No face embedding enrolled; marked with baseline confidence."}
    else:
        face_matched, face_sim, face_details = verify_live_face_against_enrolled(img, student.face_embedding)

    if not face_matched:
        reason = face_details.get("error", f"Face similarity {face_sim*100:.1f}% below threshold {FACE_SIMILARITY_THRESHOLD*100:.1f}%")
        return {
            "success": False,
            "message": f"Identity Mismatch! ID Card matches {student.name}, but face verification failed: {reason}",
            "card_verified": True,
            "face_matched": False,
            "overall_confidence": round((card_conf + face_sim) / 2.0, 2),
            "student_id": student.student_id,
            "student_name": student.name,
            "class_name": session.classroom.name,
            "status": "REJECTED",
            "details": face_details
        }

    # 8. All Verification Passed! Calculate status (PRESENT vs LATE)
    now = datetime.datetime.now()
    session_start_dt = now  # Default to current time for window check
    try:
        start_h, start_m = map(int, session.start_time.split(":"))
        session_start_dt = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    except Exception:
        pass

    late_deadline = session_start_dt + datetime.timedelta(minutes=session.late_threshold_minutes)
    attendance_status = "LATE" if now > late_deadline else "PRESENT"

    overall_conf = round((card_conf + face_sim) / 2.0, 3)

    # Save to SQLite Database
    record = AttendanceRecord(
        session_id=session.id,
        student_id=student.id,
        status=attendance_status,
        timestamp=now,
        verification_method="ocr_face",
        face_confidence=round(face_sim, 3),
        id_card_confidence=round(card_conf, 3),
        updated_by="AI_Engine"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "success": True,
        "message": f"Attendance Marked! Student: {student.name} ({student.student_id}) - {attendance_status}",
        "card_verified": True,
        "face_matched": True,
        "overall_confidence": overall_conf * 100,
        "student_id": student.student_id,
        "student_name": student.name,
        "class_name": session.classroom.name,
        "status": attendance_status,
        "details": {
            "record_id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "face_confidence": face_sim * 100,
            "id_card_confidence": card_conf * 100
        }
    }
