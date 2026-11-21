"""
Generates a realistic, purely synthetic routine lab report PDF for educational demonstration.
Contains no real patient information or clinical records.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def create_synthetic_lab_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title & Disclaimer Header
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f2b48'),
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#b91c1c'),
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
    )

    story.append(Paragraph("SYNTHETIC DEMO LABORATORY REPORT", title_style))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "<b>NOTICE:</b> FOR EDUCATIONAL DEMONSTRATION PURPOSES ONLY. "
            "CONTAINS 100% SYNTHETIC DATA. NOT A REAL PATIENT MEDICAL RECORD.",
            disclaimer_style
        )
    )
    story.append(Spacer(1, 14))

    # Patient Demographic Header (Synthetic)
    demo_data = [
        ["Patient Name:", "Demo Patient (Synthetic)", "Ordering Provider:", "Dr. Alex Taylor, MD (Simulated)"],
        ["Patient ID:", "SYN-98241", "Specimen Collection:", "2026-11-15 08:30 AM"],
        ["Date of Birth:", "1988-04-12", "Report Date:", "2026-11-15 02:45 PM"],
    ]
    t_demo = Table(demo_data, colWidths=[100, 170, 110, 160])
    t_demo.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 16))

    # Lab Section 1: Complete Blood Count (CBC)
    story.append(Paragraph("<b>1. Complete Blood Count (CBC) with Differential</b>", styles['Heading3']))
    cbc_data = [
        ["Test Name", "Result", "Standard Range", "Units", "Flag"],
        ["White Blood Cells (WBC)", "6.8", "4.5 - 11.0", "x10^3/uL", "Normal"],
        ["Red Blood Cells (RBC)", "4.75", "4.30 - 5.90", "x10^6/uL", "Normal"],
        ["Hemoglobin (Hgb)", "14.2", "13.5 - 17.5", "g/dL", "Normal"],
        ["Hematocrit (Hct)", "42.1", "38.8 - 50.0", "%", "Normal"],
        ["Platelets", "245", "150 - 450", "x10^3/uL", "Normal"],
    ]
    t_cbc = Table(cbc_data, colWidths=[180, 80, 120, 80, 80])
    t_cbc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cbc)
    story.append(Spacer(1, 16))

    # Lab Section 2: Comprehensive Metabolic Panel (CMP)
    story.append(Paragraph("<b>2. Comprehensive Metabolic Panel (CMP)</b>", styles['Heading3']))
    cmp_data = [
        ["Test Name", "Result", "Standard Range", "Units", "Flag"],
        ["Glucose (Fasting)", "94", "70 - 99", "mg/dL", "Normal"],
        ["BUN (Blood Urea Nitrogen)", "14", "7 - 20", "mg/dL", "Normal"],
        ["Creatinine", "0.92", "0.60 - 1.20", "mg/dL", "Normal"],
        ["eGFR (Non-African American)", ">60", ">60", "mL/min/1.73m2", "Normal"],
        ["Sodium", "139", "135 - 145", "mmol/L", "Normal"],
        ["Potassium", "4.2", "3.5 - 5.0", "mmol/L", "Normal"],
    ]
    t_cmp = Table(cmp_data, colWidths=[180, 80, 120, 80, 80])
    t_cmp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cmp)
    story.append(Spacer(1, 16))

    # Lab Section 3: Lipid Profile
    story.append(Paragraph("<b>3. Fasting Lipid Panel</b>", styles['Heading3']))
    lipid_data = [
        ["Test Name", "Result", "Standard Range", "Units", "Flag"],
        ["Total Cholesterol", "208", "<200 (Desirable)", "mg/dL", "Borderline"],
        ["Triglycerides", "145", "<150 (Normal)", "mg/dL", "Normal"],
        ["HDL Cholesterol (Good)", "52", ">40", "mg/dL", "Normal"],
        ["LDL Cholesterol (Calc)", "127", "<100 (Optimal)", "mg/dL", "Above Optimal"],
    ]
    t_lipid = Table(lipid_data, colWidths=[180, 80, 120, 80, 80])
    t_lipid.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_lipid)
    story.append(Spacer(1, 18))

    # Note
    story.append(Paragraph(
        "<b>Physician Review Note:</b> Results must be correlated clinically with physical examination "
        "and medical history. Mild elevations in LDL cholesterol should be reviewed in the context of "
        "lifestyle, family history, and 10-year ASCVD risk calculations.",
        normal_style
    ))

    doc.build(story)
    print(f"Successfully generated synthetic PDF at: {output_path}")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(out_dir, "synthetic_blood_work_report.pdf")
    create_synthetic_lab_pdf(target_path)
