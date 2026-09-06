import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    department = Column(String(100), default="Computer Science")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("AttendanceSession", back_populates="teacher")


class ClassRoom(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # e.g. CSE-A
    section = Column(String(20), nullable=False)  # e.g. A
    department = Column(String(100), default="Computer Science")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    students = relationship("Student", back_populates="classroom", cascade="all, delete-orphan")
    sessions = relationship("AttendanceSession", back_populates="classroom")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)  # e.g. CS201
    name = Column(String(100), nullable=False)  # e.g. Data Structures
    department = Column(String(100), default="Computer Science")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("AttendanceSession", back_populates="subject")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. CS20260142
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    roll_number = Column(String(20), nullable=False)
    photo_url = Column(String(255), nullable=True)
    face_embedding = Column(Text, nullable=True)  # Stored as JSON string
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classroom = relationship("ClassRoom", back_populates="students")
    attendance_records = relationship("AttendanceRecord", back_populates="student")


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    date = Column(String(20), nullable=False)  # YYYY-MM-DD
    start_time = Column(String(20), nullable=False)  # HH:MM
    end_time = Column(String(20), nullable=False)  # HH:MM
    status = Column(String(20), default="active")  # scheduled, active, closed
    late_threshold_minutes = Column(Integer, default=5)
    verification_mode = Column(String(50), default="ocr_face")  # ocr_face, face_only, ocr_only
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classroom = relationship("ClassRoom", back_populates="sessions")
    subject = relationship("Subject", back_populates="sessions")
    teacher = relationship("Teacher", back_populates="sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")


class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(20), nullable=False)  # present, late, absent
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    verification_method = Column(String(50), default="ocr_face")  # ocr_face, manual_override, demo_simulation
    face_confidence = Column(Float, default=0.0)
    id_card_confidence = Column(Float, default=0.0)
    override_reason = Column(Text, nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    user_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text, nullable=True)
