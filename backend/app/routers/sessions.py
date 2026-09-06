from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import datetime

from app.database import get_db
from app.models import AttendanceSession, ClassRoom, Subject, Student, AttendanceRecord, Teacher
from app.schemas import SessionCreate, SessionResponse
from app.auth import get_current_teacher
from app.routers.websockets import manager

router = APIRouter(prefix="/api/sessions", tags=["Attendance Sessions"])

@router.get("", response_model=List[SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(AttendanceSession).order_by(AttendanceSession.created_at.desc()).all()
    results = []
    for s in sessions:
        classroom = db.query(ClassRoom).filter(ClassRoom.id == s.class_id).first()
        subject = db.query(Subject).filter(Subject.id == s.subject_id).first()

        total_students = db.query(Student).filter(Student.class_id == s.class_id).count()
        present_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == s.id,
            AttendanceRecord.status == "present"
        ).count()
        late_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == s.id,
            AttendanceRecord.status == "late"
        ).count()
        absent_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == s.id,
            AttendanceRecord.status == "absent"
        ).count()

        rate = 0.0
        if total_students > 0:
            rate = round(((present_count + late_count) / total_students) * 100, 1)

        res = SessionResponse(
            id=s.id,
            class_id=s.class_id,
            subject_id=s.subject_id,
            teacher_id=s.teacher_id,
            date=s.date,
            start_time=s.start_time,
            end_time=s.end_time,
            status=s.status,
            late_threshold_minutes=s.late_threshold_minutes,
            verification_mode=s.verification_mode,
            class_name=classroom.name if classroom else "Unknown",
            subject_name=subject.name if subject else "Unknown",
            subject_code=subject.code if subject else "CS",
            total_students=total_students,
            present_count=present_count,
            late_count=late_count,
            absent_count=absent_count,
            attendance_rate=rate,
            created_at=s.created_at
        )
        results.append(res)
    return results


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    classroom = db.query(ClassRoom).filter(ClassRoom.id == session_in.class_id).first()
    if not classroom:
        raise HTTPException(status_code=400, detail="Invalid class_id")

    subject = db.query(Subject).filter(Subject.id == session_in.subject_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Invalid subject_id")

    new_session = AttendanceSession(
        class_id=session_in.class_id,
        subject_id=session_in.subject_id,
        teacher_id=teacher.id,
        date=session_in.date,
        start_time=session_in.start_time,
        end_time=session_in.end_time,
        late_threshold_minutes=session_in.late_threshold_minutes or 5,
        verification_mode=session_in.verification_mode or "ocr_face",
        status="active"  # Default to active when created
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    total_students = db.query(Student).filter(Student.class_id == classroom.id).count()

    return SessionResponse(
        id=new_session.id,
        class_id=new_session.class_id,
        subject_id=new_session.subject_id,
        teacher_id=new_session.teacher_id,
        date=new_session.date,
        start_time=new_session.start_time,
        end_time=new_session.end_time,
        status=new_session.status,
        late_threshold_minutes=new_session.late_threshold_minutes,
        verification_mode=new_session.verification_mode,
        class_name=classroom.name,
        subject_name=subject.name,
        subject_code=subject.code,
        total_students=total_students,
        present_count=0,
        late_count=0,
        absent_count=0,
        attendance_rate=0.0,
        created_at=new_session.created_at
    )


@router.post("/{session_id}/start")
async def start_session(
    session_id: int,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "active"
    db.commit()

    # Broadcast websocket update
    await manager.broadcast_to_session(session_id, {
        "type": "SESSION_STATUS_CHANGED",
        "status": "active",
        "message": f"Attendance Session #{session_id} is now ACTIVE"
    })

    return {"message": "Session started successfully", "status": "active"}


@router.post("/{session_id}/stop")
async def stop_session(
    session_id: int,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "closed"
    db.commit()

    # Automatic Absence logic: find all students in session class without attendance record, mark them ABSENT
    enrolled_students = db.query(Student).filter(Student.class_id == session.class_id, Student.active == True).all()
    absent_count = 0
    now = datetime.datetime.now()

    for student in enrolled_students:
        existing = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session.id,
            AttendanceRecord.student_id == student.id
        ).first()

        if not existing:
            absent_record = AttendanceRecord(
                session_id=session.id,
                student_id=student.id,
                status="absent",
                timestamp=now,
                verification_method="auto_close",
                updated_by="System_Auto_Absence"
            )
            db.add(absent_record)
            absent_count += 1

    db.commit()

    # Broadcast status change
    await manager.broadcast_to_session(session_id, {
        "type": "SESSION_STATUS_CHANGED",
        "status": "closed",
        "message": f"Attendance Session #{session_id} CLOSED. {absent_count} students marked ABSENT."
    })

    return {
        "message": f"Session closed. {absent_count} absent students automatically recorded.",
        "status": "closed",
        "auto_absent_count": absent_count
    }
