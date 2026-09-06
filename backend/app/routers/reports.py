from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import datetime

from app.database import get_db
from app.models import AttendanceRecord, AttendanceSession, Student, ClassRoom, Subject
from app.auth import get_current_teacher
from app.utils.export import generate_csv_report, generate_excel_report, generate_pdf_report

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

def _gather_report_data(db: Session, class_id: Optional[int] = None, date: Optional[str] = None):
    query = db.query(AttendanceRecord)

    if class_id or date:
        query = query.join(AttendanceSession)
        if class_id:
            query = query.filter(AttendanceSession.class_id == class_id)
        if date:
            query = query.filter(AttendanceSession.date == date)

    records = query.order_by(AttendanceRecord.timestamp.desc()).all()
    results = []
    for r in records:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        session = db.query(AttendanceSession).filter(AttendanceSession.id == r.session_id).first()
        classroom = db.query(ClassRoom).filter(ClassRoom.id == session.class_id).first() if session else None
        subject = db.query(Subject).filter(Subject.id == session.subject_id).first() if session else None

        results.append({
            "id": r.id,
            "student_id": student.student_id if student else "N/A",
            "student_name": student.name if student else "Unknown",
            "roll_number": student.roll_number if student else "N/A",
            "class_name": classroom.name if classroom else "N/A",
            "subject_name": subject.name if subject else "N/A",
            "date": session.date if session else "N/A",
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": r.status,
            "verification_method": r.verification_method,
            "face_confidence": r.face_confidence,
            "id_card_confidence": r.id_card_confidence,
            "override_reason": r.override_reason or ""
        })
    return results


@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_students = db.query(Student).filter(Student.active == True).count()
    total_classes = db.query(ClassRoom).count()
    total_sessions = db.query(AttendanceSession).count()
    
    total_records = db.query(AttendanceRecord).count()
    present_records = db.query(AttendanceRecord).filter(AttendanceRecord.status.in_(["present", "late"])).count()
    overall_rate = round((present_records / total_records * 100), 1) if total_records > 0 else 0.0

    # Low attendance student count (<75%)
    low_attendance_students = []
    students = db.query(Student).filter(Student.active == True).all()
    for s in students:
        s_total = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id).count()
        s_present = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id, AttendanceRecord.status.in_(["present", "late"])).count()
        s_rate = (s_present / s_total * 100) if s_total > 0 else 100.0
        if s_total > 0 and s_rate < 75.0:
            classroom = db.query(ClassRoom).filter(ClassRoom.id == s.class_id).first()
            low_attendance_students.append({
                "student_id": s.student_id,
                "name": s.name,
                "class_name": classroom.name if classroom else "N/A",
                "attendance_rate": round(s_rate, 1)
            })

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "total_sessions": total_sessions,
        "overall_attendance_rate": overall_rate,
        "low_attendance_count": len(low_attendance_students),
        "low_attendance_alerts": low_attendance_students
    }


@router.get("/daily")
def get_daily_report(date: Optional[str] = None, db: Session = Depends(get_db)):
    target_date = date or datetime.datetime.now().strftime("%Y-%m-%d")
    data = _gather_report_data(db, date=target_date)
    return {"date": target_date, "total_records": len(data), "records": data}


@router.get("/export/csv")
def export_csv(class_id: Optional[int] = None, date: Optional[str] = None, db: Session = Depends(get_db)):
    data = _gather_report_data(db, class_id=class_id, date=date)
    csv_content = generate_csv_report(data)
    filename = f"Attendance_Report_{date or 'all'}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/excel")
def export_excel(class_id: Optional[int] = None, date: Optional[str] = None, db: Session = Depends(get_db)):
    data = _gather_report_data(db, class_id=class_id, date=date)
    buffer = generate_excel_report(data, title=f"Attendance Report ({date or 'All'})")
    filename = f"Attendance_Report_{date or 'all'}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf")
def export_pdf(class_id: Optional[int] = None, date: Optional[str] = None, db: Session = Depends(get_db)):
    data = _gather_report_data(db, class_id=class_id, date=date)
    buffer = generate_pdf_report(data, title=f"Attendance Report ({date or 'All'})")
    filename = f"Attendance_Report_{date or 'all'}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
