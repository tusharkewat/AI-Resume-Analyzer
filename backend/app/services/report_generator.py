import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.analysis import Analysis
from app.models.resume import Resume


class PDFReportGenerator:
    """Generates professional, presentation-ready PDF reports from analysis results."""

    @staticmethod
    def generate_pdf(analysis: Analysis, resume: Resume) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        primary_color = colors.HexColor("#4338ca")  # Indigo 700
        dark_neutral = colors.HexColor("#1e293b")   # Slate 800
        muted_neutral = colors.HexColor("#64748b")  # Slate 500
        accent_color = colors.HexColor("#4f46e5")   # Indigo 600
        success_color = colors.HexColor("#16a34a")  # Green 600
        warning_color = colors.HexColor("#ea580c")  # Orange 600

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=primary_color,
            fontName="Helvetica-Bold",
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=muted_neutral,
            fontName="Helvetica",
            spaceAfter=15
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=dark_neutral,
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=dark_neutral,
            fontName="Helvetica"
        )

        bold_body = ParagraphStyle(
            'BoldBody',
            parent=body_style,
            fontName="Helvetica-Bold"
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=muted_neutral,
            fontName="Helvetica-Oblique"
        )

        story = []

        # Header
        story.append(Paragraph("AI Resume Analyzer & Job Matcher", title_style))
        gen_date = analysis.created_at.strftime("%B %d, %Y") if analysis.created_at else datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Executive Candidate Evaluation Report • Generated on {gen_date}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=15))

        # Overview Table
        candidate_name = resume.structured_data.get("contact", {}).get("full_name") or "Candidate"
        overview_data = [
            [Paragraph("Target Role:", bold_body), Paragraph(analysis.job_title, body_style),
             Paragraph("Candidate:", bold_body), Paragraph(candidate_name, body_style)],
            [Paragraph("Resume File:", bold_body), Paragraph(resume.original_filename, body_style),
             Paragraph("Overall Match:", bold_body), Paragraph(f"<b><font size='12' color='#4338ca'>{analysis.overall_score}%</font></b>", body_style)],
            [Paragraph("Analysis Mode:", bold_body), Paragraph(analysis.analysis_method.replace('_', ' ').title(), body_style),
             Paragraph("Evaluation ID:", bold_body), Paragraph(f"#{analysis.id}", body_style)]
        ]
        t_overview = Table(overview_data, colWidths=[85, 180, 85, 180])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 15))

        # Score Breakdown Section
        story.append(Paragraph("Explainable Scoring Breakdown", section_heading))
        sb = analysis.score_breakdown or {}
        breakdown_rows = [
            [Paragraph("Evaluation Component", bold_body), Paragraph("Score", bold_body), Paragraph("Weight", bold_body), Paragraph("Contribution", bold_body)],
            [Paragraph("Skills & Technical Competencies", body_style),
             Paragraph(f"{sb.get('skills_score', 0)}%", body_style),
             Paragraph(f"{int(sb.get('skills_weight', 0.5)*100)}%", body_style),
             Paragraph(f"{round(sb.get('skills_score', 0) * sb.get('skills_weight', 0.5), 1)} pts", body_style)],
            [Paragraph("Semantic Text & Context Similarity", body_style),
             Paragraph(f"{sb.get('text_similarity_score', 0)}%", body_style),
             Paragraph(f"{int(sb.get('text_similarity_weight', 0.25)*100)}%", body_style),
             Paragraph(f"{round(sb.get('text_similarity_score', 0) * sb.get('text_similarity_weight', 0.25), 1)} pts", body_style)],
            [Paragraph("Relevant Experience & Seniority", body_style),
             Paragraph(f"{sb.get('experience_score', 0)}%", body_style),
             Paragraph(f"{int(sb.get('experience_weight', 0.15)*100)}%", body_style),
             Paragraph(f"{round(sb.get('experience_score', 0) * sb.get('experience_weight', 0.15), 1)} pts", body_style)],
            [Paragraph("Education & Credentials Alignment", body_style),
             Paragraph(f"{sb.get('education_score', 0)}%", body_style),
             Paragraph(f"{int(sb.get('education_weight', 0.1)*100)}%", body_style),
             Paragraph(f"{round(sb.get('education_score', 0) * sb.get('education_weight', 0.1), 1)} pts", body_style)],
            [Paragraph("<b>Composite Match Total</b>", bold_body),
             Paragraph(f"<b>{analysis.overall_score}%</b>", bold_body),
             Paragraph("100%", bold_body),
             Paragraph(f"<b>{analysis.overall_score} pts</b>", bold_body)]
        ]
        t_breakdown = Table(breakdown_rows, colWidths=[230, 100, 100, 100])
        t_breakdown.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_breakdown)
        story.append(Spacer(1, 15))

        # Matching Skills Section
        matching = analysis.matching_skills or []
        story.append(Paragraph(f"Verified Matching Skills ({len(matching)})", section_heading))
        if matching:
            matched_text = ", ".join([f"<b>{m.get('skill', '')}</b>" for m in matching])
            story.append(Paragraph(matched_text, body_style))
        else:
            story.append(Paragraph("No direct matching technical competencies detected.", body_style))
        story.append(Spacer(1, 10))

        # Missing / Unverified Skills
        missing = analysis.missing_or_unverified_skills or []
        story.append(Paragraph(f"Missing or Unverified Target Qualifications ({len(missing)})", section_heading))
        if missing:
            missing_text = ", ".join([f"<b><font color='#ea580c'>{m.get('skill', '')}</font></b>" for m in missing])
            story.append(Paragraph(missing_text, body_style))
        else:
            story.append(Paragraph("Excellent coverage: All evaluated target skills were found in the resume.", body_style))
        story.append(Spacer(1, 15))

        # Recommendations & Actionable Rewrites
        recs = analysis.recommendations or {}
        story.append(Paragraph("Actionable Improvement Recommendations", section_heading))
        
        # Strengths
        for s in recs.get("strengths", []):
            story.append(Paragraph(f"• <b>Strength:</b> {s}", body_style))
            story.append(Spacer(1, 3))

        # Weaknesses
        for w in recs.get("weaknesses", []):
            story.append(Paragraph(f"• <b>Growth Area:</b> {w}", body_style))
            story.append(Spacer(1, 3))

        # Sample Rewrites
        rewrites = recs.get("bullet_point_rewrites", [])
        if rewrites:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Targeted Bullet-Point Enhancement (XYZ Formula)", section_heading))
            for item in rewrites[:2]:
                orig = item.get("original", "")
                rw = item.get("rewritten", "")
                story.append(Paragraph(f"<b>Original:</b> <i>\"{orig}\"</i>", body_style))
                story.append(Paragraph(f"<b>Enhanced:</b> <font color='#16a34a'>\"{rw}\"</font>", body_style))
                story.append(Spacer(1, 5))

        # Disclaimer Section
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))
        story.append(Paragraph(
            "<b>Disclaimer:</b> This report is generated algorithmically for coaching and career guidance purposes. "
            "Scores represent estimates calculated via natural language processing and deterministic skill ontology comparison. "
            "They do not guarantee employment, selection, or interview outcomes.",
            disclaimer_style
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
