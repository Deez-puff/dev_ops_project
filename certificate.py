from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_certificate(patient, vitals_df, alerts, suggestions):
    os.makedirs("data/certificates", exist_ok=True)

    patient_id = patient[0]
    name       = patient[1]
    age        = patient[2]
    sex        = patient[3]
    phone      = patient[4]
    email      = patient[5]
    address    = patient[7]

    filename = f"data/certificates/{patient_id}_report.pdf"
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        rightMargin=inch, leftMargin=inch,
        topMargin=inch, bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Title ──────────────────────────────────────────────
    title_style = ParagraphStyle(
        'CustomTitle',
        fontSize=22,
        fontName='Helvetica-Bold',
        alignment=1,
        spaceAfter=6,
        textColor=colors.black
    )
    sub_style = ParagraphStyle(
        'SubTitle',
        fontSize=12,
        fontName='Helvetica',
        alignment=1,
        spaceAfter=4,
        textColor=colors.darkgreen
    )

    elements.append(Paragraph("HEALTH REPORT", title_style))
    elements.append(Paragraph("Vitals AI — Health Prediction System", sub_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # ── Patient Info ───────────────────────────────────────
    elements.append(Paragraph("PATIENT INFORMATION", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))

    patient_data = [
        ["Patient ID", patient_id],
        ["Name",       name],
        ["Age",        str(age)],
        ["Sex",        sex],
        ["Phone",      phone],
        ["Email",      email],
        ["Address",    address],
    ]
    pt = Table(patient_data, colWidths=[2 * inch, 4 * inch])
    pt.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (0, -1), colors.lightgreen),
        ('BACKGROUND',  (1, 0), (1, -1), colors.white),
        ('FONTNAME',    (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 0), (-1, -1), 11),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.black),
        ('PADDING',     (0, 0), (-1, -1), 7),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(pt)
    elements.append(Spacer(1, 0.3 * inch))

    # ── Latest Vitals ──────────────────────────────────────
    elements.append(Paragraph("LATEST VITAL READINGS", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))

    if vitals_df is not None and not vitals_df.empty:
        latest = vitals_df.iloc[-1]

        vitals_data = [
            ["Vital", "Your Reading", "Normal Range", "Status"],
            ["Heart Rate",
             f"{latest['heart_rate']} bpm", "60–100 bpm", ""],
            ["Oxygen Level (SpO2)",
             f"{latest['spo2']}%", "95–100%", ""],
            ["Body Temperature",
             f"{latest['temperature']} °F", "97–99.5 °F", ""],
            ["Blood Pressure (Upper)",
             f"{latest['bp_systolic']} mmHg", "90–120 mmHg", ""],
            ["Blood Pressure (Lower)",
             f"{latest['bp_diastolic']} mmHg", "60–80 mmHg", ""],
        ]

        vital_keys = [
            "heart_rate", "spo2", "temperature",
            "bp_systolic", "bp_diastolic"
        ]
        for i, key in enumerate(vital_keys):
            status = "NORMAL"
            for s, msg in alerts:
                if s != "NORMAL":
                    status = s
                    break
            vitals_data[i + 1][3] = status

        vt = Table(
            vitals_data,
            colWidths=[2.2 * inch, 1.4 * inch, 1.4 * inch, 1 * inch]
        )
        vt.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, -1), 10),
            ('GRID',        (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING',     (0, 0), (-1, -1), 6),
            ('ALIGN',       (1, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND',  (0, 1), (-1, -1), colors.white),
        ]))
        elements.append(vt)
    elements.append(Spacer(1, 0.3 * inch))

    # ── Health Alerts ──────────────────────────────────────
    elements.append(Paragraph("HEALTH ALERTS", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    for status, msg in alerts:
        clean = msg.replace("⚠️", "WARNING:").replace("✅", "OK:")
        elements.append(Paragraph(f"• {clean}", styles['Normal']))
        elements.append(Spacer(1, 0.05 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # ── Medicine Suggestions ───────────────────────────────
    elements.append(Paragraph("MEDICINE SUGGESTIONS", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    for s in suggestions:
        clean = s.replace("💊", "").replace("✅", "").strip()
        elements.append(Paragraph(f"• {clean}", styles['Normal']))
        elements.append(Spacer(1, 0.05 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # ── Important Note ─────────────────────────────────────
    note_style = ParagraphStyle(
        'Note',
        fontSize=10,
        fontName='Helvetica-Oblique',
        textColor=colors.darkgreen,
        borderColor=colors.darkgreen,
        borderWidth=1,
        borderPadding=8,
        leading=16
    )
    elements.append(Paragraph("IMPORTANT NOTE", styles['Heading2']))
    elements.append(Paragraph(
        "This report is created by an AI system and is for reference only. "
        "Please consult a certified doctor before making any medical decisions. "
        "If you have 2 or more abnormal readings, seek medical attention immediately.",
        note_style
    ))

    doc.build(elements)
    return filename