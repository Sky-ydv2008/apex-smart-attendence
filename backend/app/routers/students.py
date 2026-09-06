import json
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database import get_db
from app.models import Student, ClassRoom, Teacher
from app.schemas import StudentCreate, StudentResponse
from app.auth import get_current_teacher
from app.config import UPLOADS_DIR
from app.ai.ocr_engine import decode_base64_image
from app.ai.face_engine import generate_face_embedding
from app.utils.card_generator import generate_student_id_card

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("", response_model=List[StudentResponse])
def get_students(
    class_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if class_id:
        query = query.filter(Student.class_id == class_id)
    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.student_id.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%"))
        )

    students = query.all()
    results = []
    for s in students:
        classroom = db.query(ClassRoom).filter(ClassRoom.id == s.class_id).first()
        res = StudentResponse(
            id=s.id,
            student_id=s.student_id,
            name=s.name,
            class_id=s.class_id,
            roll_number=s.roll_number,
            photo_url=s.photo_url,
            has_face_enrolled=bool(s.face_embedding),
            class_name=classroom.name if classroom else "Unknown",
            created_at=s.created_at
        )
        results.append(res)
    return results


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    existing = db.query(Student).filter(Student.student_id == student_in.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{student_in.student_id}' already exists")

    classroom = db.query(ClassRoom).filter(ClassRoom.id == student_in.class_id).first()
    if not classroom:
        raise HTTPException(status_code=400, detail="Invalid class_id")

    student = Student(
        student_id=student_in.student_id,
        name=student_in.name,
        class_id=student_in.class_id,
        roll_number=student_in.roll_number,
        photo_url=student_in.photo_url,
        face_embedding=student_in.face_embedding
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Generate ID card image
    card_url = generate_student_id_card(student, classroom.name)

    return StudentResponse(
        id=student.id,
        student_id=student.student_id,
        name=student.name,
        class_id=student.class_id,
        roll_number=student.roll_number,
        photo_url=student.photo_url,
        has_face_enrolled=bool(student.face_embedding),
        class_name=classroom.name,
        created_at=student.created_at
    )


@router.post("/{student_id_pk}/enroll-face")
async def enroll_student_face(
    student_id_pk: int,
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    student = db.query(Student).filter(Student.id == student_id_pk).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    img_np = None
    file_path_str = None

    if file:
        contents = await file.read()
        filename = f"student_{student.student_id}_{file.filename}"
        save_path = UPLOADS_DIR / filename
        with open(save_path, "wb") as f:
            f.write(contents)

        import cv2
        import numpy as np
        nparr = np.frombuffer(contents, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        file_path_str = f"/uploads/{filename}"
    elif image_base64:
        img_np = decode_base64_image(image_base64)
        filename = f"student_{student.student_id}_captured.jpg"
        save_path = UPLOADS_DIR / filename
        import cv2
        cv2.imwrite(str(save_path), img_np)
        file_path_str = f"/uploads/{filename}"
    else:
        raise HTTPException(status_code=400, detail="Must provide photo file or image_base64 string")

    # Generate local face embedding
    embedding = generate_face_embedding(img_np)
    if not embedding:
        raise HTTPException(status_code=400, detail="No face detected in photo. Please upload a clear face image.")

    student.photo_url = file_path_str
    student.face_embedding = json.dumps(embedding)
    db.commit()
    db.refresh(student)

    classroom = db.query(ClassRoom).filter(ClassRoom.id == student.class_id).first()
    class_name = classroom.name if classroom else "Class"
    generate_student_id_card(student, class_name)

    return {
        "message": f"Face successfully enrolled for {student.name}",
        "photo_url": student.photo_url,
        "has_face_enrolled": True
    }


@router.get("/{student_id_pk}/id-card")
def get_id_card(student_id_pk: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id_pk).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    classroom = db.query(ClassRoom).filter(ClassRoom.id == student.class_id).first()
    class_name = classroom.name if classroom else "Class"
    card_url = generate_student_id_card(student, class_name)

    return {"card_url": card_url, "student_id": student.student_id, "name": student.name}


@router.delete("/{student_id_pk}")
def delete_student(
    student_id_pk: int,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    student = db.query(Student).filter(Student.id == student_id_pk).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}
