from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ClassRoom, Student, Teacher
from app.schemas import ClassCreate, ClassResponse
from app.auth import get_current_teacher

router = APIRouter(prefix="/api/classes", tags=["Classes"])

@router.get("", response_model=List[ClassResponse])
def get_classes(db: Session = Depends(get_db)):
    classes = db.query(ClassRoom).all()
    results = []
    for c in classes:
        student_count = db.query(Student).filter(Student.class_id == c.id).count()
        res = ClassResponse(
            id=c.id,
            name=c.name,
            section=c.section,
            department=c.department,
            student_count=student_count,
            created_at=c.created_at
        )
        results.append(res)
    return results


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    existing = db.query(ClassRoom).filter(
        ClassRoom.name == class_in.name,
        ClassRoom.section == class_in.section
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Classroom with this name and section already exists")

    classroom = ClassRoom(
        name=class_in.name,
        section=class_in.section,
        department=class_in.department or "Computer Science"
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return ClassResponse(
        id=classroom.id,
        name=classroom.name,
        section=classroom.section,
        department=classroom.department,
        student_count=0,
        created_at=classroom.created_at
    )


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    db.delete(classroom)
    db.commit()
    return {"message": "Classroom deleted successfully"}
