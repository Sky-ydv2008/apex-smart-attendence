import json
import datetime
import numpy as np
from PIL import Image, ImageDraw
from app.database import SessionLocal, engine, Base
from app.models import Teacher, ClassRoom, Subject, Student, AttendanceSession, AttendanceRecord
from app.auth import get_password_hash
from app.config import UPLOADS_DIR, CARDS_DIR
from app.ai.face_engine import generate_face_embedding
from app.utils.card_generator import generate_student_id_card

def create_synthetic_face_image(name: str, color: tuple) -> tuple[str, list]:
    """Generates a synthetic face image file and returns (photo_url, embedding)."""
    img = Image.new("RGB", (200, 200), color=color)
    draw = ImageDraw.Draw(img)

    # Draw face oval
    draw.ellipse([30, 30, 170, 170], fill="#FCD34D", outline="#F59E0B", width=3) # Skin tone
    # Eyes
    draw.ellipse([65, 75, 85, 95], fill="#1F2937")
    draw.ellipse([115, 75, 135, 95], fill="#1F2937")
    # Smile
    draw.arc([65, 110, 135, 145], start=0, end=180, fill="#1F2937", width=3)

    filename = f"seed_{name.lower().replace(' ', '_')}.jpg"
    path = UPLOADS_DIR / filename
    img.save(path)

    import cv2
    img_cv = cv2.imread(str(path))
    embedding = generate_face_embedding(img_cv)
    if not embedding:
        # Fallback 128-dim normalized random seed embedding
        np.random.seed(abs(hash(name)) % 10000)
        rand_vec = np.random.randn(128)
        embedding = (rand_vec / np.linalg.norm(rand_vec)).tolist()

    return f"/uploads/{filename}", embedding


def seed_database():
    print("Seeding database with AttendAI demo data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Teacher
    teacher = db.query(Teacher).filter(Teacher.email == "teacher@apex.edu").first()
    if not teacher:
        teacher = Teacher(
            name="Dr. Rahul Sharma",
            email="teacher@apex.edu",
            password_hash=get_password_hash("admin123"),
            department="Computer Science"
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        print("Created Teacher: teacher@apex.edu / admin123")

    # 2. Classes
    class_csea = db.query(ClassRoom).filter(ClassRoom.name == "CSE-A").first()
    if not class_csea:
        class_csea = ClassRoom(name="CSE-A", section="A", department="Computer Science")
        db.add(class_csea)

    class_cseb = db.query(ClassRoom).filter(ClassRoom.name == "CSE-B").first()
    if not class_cseb:
        class_cseb = ClassRoom(name="CSE-B", section="B", department="Computer Science")
        db.add(class_cseb)

    class_ece = db.query(ClassRoom).filter(ClassRoom.name == "ECE-1").first()
    if not class_ece:
        class_ece = ClassRoom(name="ECE-1", section="1", department="Electronics")
        db.add(class_ece)

    db.commit()
    db.refresh(class_csea)
    db.refresh(class_cseb)

    # 3. Subjects
    sub_ds = db.query(Subject).filter(Subject.code == "CS201").first()
    if not sub_ds:
        sub_ds = Subject(code="CS201", name="Data Structures & Algorithms", department="Computer Science")
        db.add(sub_ds)

    sub_ai = db.query(Subject).filter(Subject.code == "CS302").first()
    if not sub_ai:
        sub_ai = Subject(code="CS302", name="AI & Machine Learning", department="Computer Science")
        db.add(sub_ai)

    db.commit()
    db.refresh(sub_ds)

    # 4. Students
    sample_students = [
        {"student_id": "CS20260142", "name": "Rahul Patel", "class_id": class_csea.id, "roll_number": "42", "color": (30, 58, 138)},
        {"student_id": "CS20260143", "name": "Ananya Sharma", "class_id": class_csea.id, "roll_number": "43", "color": (131, 24, 67)},
        {"student_id": "CS20260144", "name": "Vikram Singh", "class_id": class_csea.id, "roll_number": "44", "color": (6, 78, 59)},
        {"student_id": "CS20260145", "name": "Priya Nair", "class_id": class_csea.id, "roll_number": "45", "color": (120, 53, 15)},
        {"student_id": "CS20260146", "name": "Amit Verma", "class_id": class_cseb.id, "roll_number": "01", "color": (88, 28, 135)},
        {"student_id": "CS20260147", "name": "Sneha Reddy", "class_id": class_cseb.id, "roll_number": "02", "color": (15, 118, 110)},
    ]

    for s in sample_students:
        existing = db.query(Student).filter(Student.student_id == s["student_id"]).first()
        if not existing:
            photo_url, embedding = create_synthetic_face_image(s["name"], s["color"])
            student = Student(
                student_id=s["student_id"],
                name=s["name"],
                class_id=s["class_id"],
                roll_number=s["roll_number"],
                photo_url=photo_url,
                face_embedding=json.dumps(embedding)
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            # Generate student ID card PNG
            c_name = "CSE-A" if s["class_id"] == class_csea.id else "CSE-B"
            generate_student_id_card(student, c_name)
            print(f"Enrolled student & generated ID card for: {s['name']} ({s['student_id']})")

    # 5. Active Attendance Session for Demo
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    start_time_str = (now - datetime.timedelta(minutes=10)).strftime("%H:%M")
    end_time_str = (now + datetime.timedelta(minutes=50)).strftime("%H:%M")

    active_session = db.query(AttendanceSession).filter(
        AttendanceSession.class_id == class_csea.id,
        AttendanceSession.date == today_str,
        AttendanceSession.status == "active"
    ).first()

    if not active_session:
        active_session = AttendanceSession(
            class_id=class_csea.id,
            subject_id=sub_ds.id,
            teacher_id=teacher.id,
            date=today_str,
            start_time=start_time_str,
            end_time=end_time_str,
            status="active",
            late_threshold_minutes=15,
            verification_mode="ocr_face"
        )
        db.add(active_session)
        db.commit()
        db.refresh(active_session)
        print(f"Created Active Demo Attendance Session #{active_session.id} for CSE-A - Data Structures")

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
