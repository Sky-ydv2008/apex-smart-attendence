from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import datetime

from app.database import get_db
from app.models import Teacher
from app.schemas import TeacherCreate, TeacherResponse, Token
from app.auth import verify_password, get_password_hash, create_access_token, get_current_teacher

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def register_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    existing = db.query(Teacher).filter(Teacher.email == teacher_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    teacher = Teacher(
        name=teacher_in.name,
        email=teacher_in.email,
        password_hash=get_password_hash(teacher_in.password),
        department=teacher_in.department or "Computer Science"
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == form_data.username).first()
    if not teacher or not verify_password(form_data.password, teacher.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": teacher.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "teacher": teacher
    }


@router.get("/me", response_model=TeacherResponse)
def get_me(current_teacher: Teacher = Depends(get_current_teacher)):
    return current_teacher
