from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app.database import get_db
from app.models import AttendanceRecord, AttendanceSession, Student, AuditLog, Teacher, ClassRoom
from app.schemas import ScanRequest, ScanResponse, AttendanceRecordResponse, AttendanceOverrideRequest
from app.auth import get_current_teacher
from app.ai.decision_engine import process_attendance_scan
from app.routers.websockets import manager
from app.ai.face_engine import generate_face_embedding, compare_face_embeddings

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("/scan", response_model=ScanResponse)
async def scan_attendance(
    scan_req: ScanRequest,
    db: Session = Depends(get_db)
):
    """
    Live Camera Scan Endpoint:
    Processes base64 frame, executes ID card OCR + Face Verification pipeline,
    records attendance, and broadcasts WebSocket update to teacher dashboard!
    """
    result = process_attendance_scan(
        session_id=scan_req.session_id,
        image_base64=scan_req.image_base64,
        db=db
    )

    if result.get("success"):
        # Broadcast real-time WebSocket update
        await manager.broadcast_to_session(scan_req.session_id, {
            "type": "ATTENDANCE_MARKED",
            "student_id": result.get("student_id"),
            "student_name": result.get("student_name"),
            "status": result.get("status"),
            "confidence": result.get("overall_confidence"),
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

    return result


@router.post("/demo-scan", response_model=ScanResponse)
async def demo_simulated_scan(
    session_id: int,
    student_id_code: str,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """
    Hackathon Demo Scan Endpoint:
    Simulates a high-confidence ID Card + Face Verification scan for any enrolled student!
    Useful for demonstration even without physical card in front of camera.
    """
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    student = db.query(Student).filter(Student.student_id == student_id_code).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id_code}' not found")

    if student.class_id != session.class_id:
        return {
            "success": False,
            "message": f"Rejected: Student {student.name} is enrolled in another class, not {session.classroom.name}.",
            "card_verified": True,
            "face_matched": False,
            "overall_confidence": 0.50,
            "student_id": student.student_id,
            "student_name": student.name,
            "status": "REJECTED"
        }

    # Check duplicate
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == student.id
    ).first()

    if existing:
        return {
            "success": False,
            "message": f"Duplicate: Attendance already recorded for {student.name} ({existing.status.upper()})",
            "card_verified": True,
            "face_matched": True,
            "overall_confidence": 0.98,
            "student_id": student.student_id,
            "student_name": student.name,
            "status": "DUPLICATE"
        }

    now = datetime.datetime.now()
    attendance_status = "PRESENT"

    record = AttendanceRecord(
        session_id=session.id,
        student_id=student.id,
        status=attendance_status,
        timestamp=now,
        verification_method="demo_simulation",
        face_confidence=0.965,
        id_card_confidence=0.980,
        updated_by=f"Teacher_{teacher.name}"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Broadcast websocket update
    await manager.broadcast_to_session(session.id, {
        "type": "ATTENDANCE_MARKED",
        "student_id": student.student_id,
        "student_name": student.name,
        "status": attendance_status,
        "confidence": 97.2,
        "timestamp": now.strftime("%H:%M:%S")
    })

    return {
        "success": True,
        "message": f"Demo Scan Verified! Student: {student.name} ({student.student_id}) - {attendance_status}",
        "card_verified": True,
        "face_matched": True,
        "overall_confidence": 97.2,
        "student_id": student.student_id,
        "student_name": student.name,
        "class_name": session.classroom.name,
        "status": attendance_status,
        "details": {
            "card_status": "ID Card: Verified 3",
            "face_status": "Face: Matched 3",
            "face_confidence": 96.5,
            "id_card_confidence": 98.0
        }
    }


@router.get("/session/{session_id}", response_model=List[AttendanceRecordResponse])
def get_session_attendance(session_id: int, db: Session = Depends(get_db)):
    records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).order_by(AttendanceRecord.timestamp.desc()).all()
    results = []
    for r in records:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        res = AttendanceRecordResponse(
            id=r.id,
            session_id=r.session_id,
            student_id=r.student_id,
            student_code=student.student_id if student else "N/A",
            student_name=student.name if student else "Unknown",
            roll_number=student.roll_number if student else "N/A",
            status=r.status,
            timestamp=r.timestamp,
            verification_method=r.verification_method,
            face_confidence=r.face_confidence,
            id_card_confidence=r.id_card_confidence,
            override_reason=r.override_reason,
            updated_by=r.updated_by
        )
        results.append(res)
    return results


@router.post("/override")
async def override_attendance(
    req: AttendanceOverrideRequest,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == req.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    old_status = record.status
    record.status = req.new_status
    record.override_reason = req.reason
    record.updated_by = f"Teacher:{teacher.name}"
    record.verification_method = "manual_override"

    # Log to Audit Table
    audit = AuditLog(
        action=f"OVERRIDE_STATUS_{old_status.upper()}_TO_{req.new_status.upper()}",
        entity_type="AttendanceRecord",
        entity_id=record.id,
        user_name=teacher.name,
        details=f"Reason: {req.reason}"
    )
    db.add(audit)
    db.commit()

    student = db.query(Student).filter(Student.id == record.student_id).first()

    # Broadcast update
    await manager.broadcast_to_session(record.session_id, {
        "type": "ATTENDANCE_OVERRIDDEN",
        "student_id": student.student_id if student else "",
        "student_name": student.name if student else "",
        "new_status": req.new_status,
        "reason": req.reason,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    return {
        "message": f"Attendance updated from {old_status} to {req.new_status}",
        "record_id": record.id,
        "new_status": req.new_status
    }
