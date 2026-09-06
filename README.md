# AttendAI — Offline Smart Attendance Platform

> **AI-Powered Classroom Attendance. Zero Cloud Dependency. Instant Local Updates.**

AttendAI is a locally hosted, AI-assisted classroom attendance platform designed for offline educational environments. Students present an ID card and face the camera; local AI reads the card, identifies the student, performs face verification against local embeddings, enforces time windows, records attendance in SQLite, and updates the teacher dashboard instantly via WebSockets—without requiring any internet connection.

---

## 🌟 Key MVP Feature: Two-Factor Identity Verification

- **Step 1 (ID Card OCR):** Identifies who the student claims to be by reading Student ID, Name, and Class via OpenCV perspective correction and local OCR.
- **Step 2 (Live Face Verification):** Confirms that the person holding the card matches that student's enrolled 128-dimensional face embedding.

### Verification Verdict Output
```text
ID Card: Verified ✓ | Face: Matched ✓ | Confidence: 96.8% | Attendance: PRESENT
```

---

## 🚀 Architecture & Tech Stack

- **Frontend:** React + Vite + Tailwind CSS + Lucide Icons + Recharts
- **Backend:** Python + FastAPI + Uvicorn + WebSockets
- **Database:** SQLite (SQLAlchemy ORM)
- **Computer Vision & AI:** OpenCV + EasyOCR + Face Vector Cosine Similarity
- **Export & Reports:** OpenPyXL (Excel), ReportLab (PDF), CSV

---

## ⚡ Quick Start

### 1-Click Launch (Windows)
Double-click `START_SMART_ATTENDANCE.bat` or run:
```cmd
START_SMART_ATTENDANCE.bat
```

### Manual Start

1. **Seed Demo Data & Database:**
   ```bash
   cd backend
   python app/seed.py
   ```

2. **Start Backend Server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

3. **Start Frontend Dev Server:**
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 🔑 Demo Teacher Credentials

- **Email:** `teacher@apex.edu`
- **Password:** `admin123`
- *(Includes 1-Click Quick Demo Login on the login screen!)*

---

## 🎯 Hackathon Demo Flow

1. Teacher logs in (or uses Quick Demo Login).
2. Views active attendance session for **CSE-A — Data Structures & Algorithms**.
3. Navigates to **Live AI Scanner Studio**.
4. Demonstrates live camera scan OR uses the **Hackathon Instant Demo Scan Simulator** to select pre-enrolled students (`Rahul Patel`, `Ananya Sharma`, etc.).
5. System displays dual-factor verification verdict: `ID Card: Verified | Face: Matched | Confidence: 96.8% | PRESENT`.
6. Dashboard present count and real-time WebSocket log update immediately without refreshing.
7. Demonstrates **Teacher Override & Audit Logging** for manual corrections with reason recording.
8. Exports daily summary reports in **PDF**, **Excel (.xlsx)**, and **CSV** formats.
9. Disables Wi-Fi/internet to demonstrate 100% offline local AI operation!

---

## 📂 Project Structure

```text
apex-smart-attendance/
├── START_SMART_ATTENDANCE.bat
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── seed.py
│   │   ├── ai/
│   │   │   ├── ocr_engine.py
│   │   │   ├── face_engine.py
│   │   │   └── decision_engine.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── classes.py
│   │   │   ├── students.py
│   │   │   ├── sessions.py
│   │   │   ├── attendance.py
│   │   │   ├── reports.py
│   │   │   └── websockets.py
│   │   └── utils/
│   │       ├── card_generator.py
│   │       └── export.py
│   └── data/
│       ├── attendai.db
│       ├── uploads/
│       └── id_cards/
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── api.js
        ├── components/
        └── pages/
```
