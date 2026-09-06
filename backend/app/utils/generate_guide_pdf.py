import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_operating_guide_pdf():
    output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "AttendAI_System_Guide.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#4F46E5"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName='Courier',
        textColor=colors.HexColor("#4F46E5"),
        backColor=colors.HexColor("#F1F5F9"),
        borderColor=colors.HexColor("#E2E8F0"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("<b>AttendAI — Offline Smart Attendance Platform</b>", title_style))
    story.append(Paragraph("Full System Operating Guide & 2-Factor AI Architecture Documentation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=15))

    # Section 1: Overview
    story.append(Paragraph("1. System Overview & Core Concept", h2_style))
    story.append(Paragraph(
        "AttendAI is a locally hosted, AI-assisted classroom attendance platform built for offline environments. "
        "Students present an ID card and face the camera; local AI reads the card, verifies student identity, performs "
        "live face embedding verification against local SQLite records, enforces teacher session time windows, "
        "and updates the real-time dashboard instantly via WebSockets — with <b>100% zero cloud dependency</b>.",
        body_style
    ))

    # Section 2: Two-Factor Verification
    story.append(Paragraph("2. Two-Factor Identity Verification Pipeline", h2_style))
    story.append(Paragraph(
        "To prevent fraudulent attendance (such as one student holding another person's card), AttendAI enforces "
        "a strict 2-Factor verification flow:<br/>"
        "• <b>Factor 1 (ID Card OCR):</b> OpenCV contour detection + perspective warp + EasyOCR extracts Student ID.<br/>"
        "• <b>Factor 2 (Face Vector Verification):</b> Generates a 128-dimensional normalized face embedding and "
        "computes cosine similarity against the enrolled reference embedding (threshold >= 65%).",
        body_style
    ))
    story.append(Paragraph("Verdict Output: ID Card: Verified ✓ | Face: Matched ✓ | Confidence: 96.8% | PRESENT", code_style))

    # Section 3: Credentials
    story.append(Paragraph("3. Demo Credentials & Access URLs", h2_style))
    cred_table_data = [
        ["Resource", "URL / Value"],
        ["Web Application UI", "http://localhost:5173"],
        ["Backend API Endpoint", "http://127.0.0.1:8000"],
        ["Teacher Login Email", "teacher@apex.edu"],
        ["Teacher Password", "admin123 (Or click 1-Click Quick Demo Login)"]
    ]
    t_cred = Table(cred_table_data, colWidths=[160, 340])
    t_cred.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cred)

    # Section 4: Operating Steps
    story.append(Paragraph("4. Step-by-Step Teacher Operating Guide", h2_style))
    story.append(Paragraph(
        "<b>1. Launch App:</b> Run <code>START_SMART_ATTENDANCE.bat</code> or open <code>http://localhost:5173</code>.<br/>"
        "<b>2. Login:</b> Log in as teacher or click <i>Quick Demo Login</i>.<br/>"
        "<b>3. Classes & Enrollment:</b> Enroll students, upload face photos to generate local embeddings, and print student ID cards.<br/>"
        "<b>4. Start Session:</b> Create an attendance session for a class (e.g. CSE-A, Data Structures) and set status to ACTIVE.<br/>"
        "<b>5. Live Scanner Studio:</b> Open camera feed or click <i>Simulate Instant 2-Factor AI Verification Scan</i>.<br/>"
        "<b>6. Auto-Absence:</b> Closing a session automatically marks all un-scanned students as ABSENT.<br/>"
        "<b>7. Teacher Override:</b> Perform audit-logged status overrides with mandatory reason recording.<br/>"
        "<b>8. Export Reports:</b> One-click export daily/monthly reports in PDF, Excel (.xlsx), and CSV formats.",
        body_style
    ))

    # Section 5: Direct Download Links
    story.append(Paragraph("5. Direct System Download Endpoints", h2_style))
    links_data = [
        ["Report Type", "Direct Download Link"],
        ["Live Attendance PDF Report", "http://127.0.0.1:8000/api/reports/export/pdf"],
        ["Excel (.xlsx) Attendance Report", "http://127.0.0.1:8000/api/reports/export/excel"],
        ["CSV Attendance Report", "http://127.0.0.1:8000/api/reports/export/csv"],
        ["System Documentation PDF", "http://127.0.0.1:8000/uploads/AttendAI_System_Guide.pdf"]
    ]
    t_links = Table(links_data, colWidths=[180, 320])
    t_links.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_links)

    doc.build(story)
    print(f"Successfully generated PDF System Guide at: {pdf_path}")

if __name__ == "__main__":
    generate_operating_guide_pdf()
