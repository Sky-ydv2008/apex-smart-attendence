from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

# Teacher Schemas
class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = "Computer Science"

class TeacherCreate(TeacherBase):
    password: str

class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    teacher: TeacherResponse

# Class Schemas
class ClassCreate(BaseModel):
    name: str
    section: str
    department: Optional[str] = "Computer Science"

class ClassResponse(BaseModel):
    id: int
    name: str
    section: str
    department: str
    student_count: Optional[int] = 0
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Subject Schemas
class SubjectCreate(BaseModel):
    code: str
    name: str
    department: Optional[str] = "Computer Science"

class SubjectResponse(BaseModel):
    id: int
    code: str
    name: str
    department: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Student Schemas
class StudentCreate(BaseModel):
    student_id: str
    name: str
    class_id: int
    roll_number: str
    photo_url: Optional[str] = None
    face_embedding: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    student_id: str
    name: str
    class_id: int
    roll_number: str
    photo_url: Optional[str] = None
    has_face_enrolled: bool = False
    class_name: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Attendance Session Schemas
class SessionCreate(BaseModel):
    class_id: int
    subject_id: int
    date: str
    start_time: str
    end_time: str
    late_threshold_minutes: Optional[int] = 5
    verification_mode: Optional[str] = "ocr_face"

class SessionResponse(BaseModel):
    id: int
    class_id: int
    subject_id: int
    teacher_id: int
    date: str
    start_time: str
    end_time: str
    status: str
    late_threshold_minutes: int
    verification_mode: str
    class_name: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    total_students: Optional[int] = 0
    present_count: Optional[int] = 0
    late_count: Optional[int] = 0
    absent_count: Optional[int] = 0
    attendance_rate: Optional[float] = 0.0
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Attendance Record Schemas
class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    status: str
    timestamp: datetime.datetime
    verification_method: str
    face_confidence: float
    id_card_confidence: float
    override_reason: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class AttendanceOverrideRequest(BaseModel):
    record_id: int
    new_status: str  # present, late, absent
    reason: str

# Scan Request and Response Schemas
class ScanRequest(BaseModel):
    session_id: int
    image_base64: str  # Camera frame image in base64 format

class ScanResponse(BaseModel):
    success: bool
    message: str
    card_verified: bool
    face_matched: bool
    overall_confidence: float
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    status: Optional[str] = None  # PRESENT, LATE, REJECTED
    details: Optional[dict] = None
