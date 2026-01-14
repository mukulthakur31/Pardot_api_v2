from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def create_safe_comprehensive_pdf(email_stats, form_stats, prospect_health, landing_page_stats=None, engagement_programs=None, utm_analysis=None, database_health=None):
    """Generate a completely safe PDF that handles all None values"""
    try:
        print("🛡️ Creating safe PDF with bulletproof null handling...")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        content = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, spaceAfter=20, alignment=1, textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
        content.append(Paragraph("📊 PARDOT COMPREHENSIVE REPORT", title_style))
        content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ParagraphStyle('Date', parent=styles['Normal'], fontSize=12, spaceAfter=30, alignment=1, textColor=colors.HexColor('#6b7280'))))
        
        # Safe data extraction
        def safe_len(data):
            if data is None:
                return 0
            if isinstance(data, list):
                return len(data)
            return 0
        
        def safe_get(data, key, default=0):
            if data is None:
                return default
            if isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # Calculate metrics safely
        total_emails = safe_len(email_stats)
        total_forms = safe_len(form_stats)
        
        # Email metrics
        total_sent = 0
        total_opens = 0
        total_clicks = 0
        total_delivered = 0
        
        if email_stats and isinstance(email_stats, list):
            for email in email_stats:
                if isinstance(email, dict):
                    stats = email.get('stats', {})
                    if isinstance(stats, dict):
                        total_sent += stats.get('sent', 0) or 0
                        total_opens += stats.get('opens', 0) or 0
                        total_clicks += stats.get('clicks', 0) or 0
                        total_delivered += stats.get('delivered', 0) or 0
        
        open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
        click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
        
        # Form metrics
        total_form_views = 0
        total_form_submissions = 0
        
        if form_stats and isinstance(form_stats, list):
            for form in form_stats:
                if isinstance(form, dict):
                    total_form_views += form.get('views', 0) or 0
                    total_form_submissions += form.get('submissions', 0) or 0
        
        form_conversion_rate = (total_form_submissions / total_form_views * 100) if total_form_views > 0 else 0
        
        # Prospect metrics
        total_prospects = 0
        if database_health and isinstance(database_health, dict):
            summary = database_health.get('summary', {})
            if isinstance(summary, dict):
                total_prospects = summary.get('total_database', 0) or 0
        elif prospect_health and isinstance(prospect_health, dict):
            total_prospects = prospect_health.get('total_prospects', 0) or 0
        
        # Executive Summary
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')
        content.append(Paragraph("📋 EXECUTIVE SUMMARY", section_style))
        
        summary_data = [
            ['METRIC', 'VALUE', 'STATUS'],
            ['Total Prospects', f'{total_prospects:,}', '👥 Database'],
            ['Email Campaigns', f'{total_emails:,}', '📧 Active'],
            ['Email Open Rate', f'{open_rate:.1f}%', '✅ Good' if open_rate > 20 else '⚠️ Review'],
            ['Email Click Rate', f'{click_rate:.1f}%', '✅ Good' if click_rate > 2.5 else '⚠️ Review'],
            ['Active Forms', f'{total_forms:,}', '📝 Deployed'],
            ['Form Conversion Rate', f'{form_conversion_rate:.1f}%', '✅ Good' if form_conversion_rate > 15 else '⚠️ Optimize']
        ]
        
        summary_table = Table(summary_data, colWidths=[2.2*inch, 1.3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        content.append(summary_table)
        content.append(Spacer(1, 0.3*inch))
        
        # Email Section
        content.append(Paragraph("📧 EMAIL CAMPAIGN PERFORMANCE", section_style))
        content.append(Paragraph(f"Total Campaigns: {total_emails}", styles['Normal']))
        content.append(Paragraph(f"Total Sent: {total_sent:,}", styles['Normal']))
        content.append(Paragraph(f"Total Opens: {total_opens:,} ({open_rate:.1f}%)", styles['Normal']))
        content.append(Paragraph(f"Total Clicks: {total_clicks:,} ({click_rate:.1f}%)", styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Form Section
        content.append(Paragraph("📝 FORM PERFORMANCE", section_style))
        content.append(Paragraph(f"Total Forms: {total_forms}", styles['Normal']))
        content.append(Paragraph(f"Total Views: {total_form_views:,}", styles['Normal']))
        content.append(Paragraph(f"Total Submissions: {total_form_submissions:,} ({form_conversion_rate:.1f}%)", styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Database Section
        content.append(Paragraph("👥 DATABASE HEALTH", section_style))
        content.append(Paragraph(f"Total Prospects: {total_prospects:,}", styles['Normal']))
        
        if database_health and isinstance(database_health, dict):
            content.append(Paragraph("✅ Comprehensive database health data available", styles['Normal']))
        elif prospect_health and isinstance(prospect_health, dict):
            content.append(Paragraph("⚠️ Legacy prospect health data available", styles['Normal']))
        else:
            content.append(Paragraph("❌ No database health data available", styles['Normal']))
        
        content.append(Spacer(1, 0.2*inch))
        
        # Engagement Programs
        content.append(Paragraph("🎯 ENGAGEMENT PROGRAMS", section_style))
        if engagement_programs and isinstance(engagement_programs, dict):
            summary = engagement_programs.get('summary', {})
            if isinstance(summary, dict):
                total_programs = summary.get('total_programs', 0) or 0
                active_count = summary.get('active_count', 0) or 0
                content.append(Paragraph(f"Total Programs: {total_programs}", styles['Normal']))
                content.append(Paragraph(f"Active Programs: {active_count}", styles['Normal']))
            else:
                content.append(Paragraph("Engagement program data structure invalid", styles['Normal']))
        else:
            content.append(Paragraph("No engagement program data available", styles['Normal']))
        
        content.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        content.append(Paragraph("💡 RECOMMENDATIONS", section_style))
        recommendations = [
            "• Review email campaigns with low open rates",
            "• Optimize forms with poor conversion rates", 
            "• Clean up database duplicates and inactive records",
            "• Implement A/B testing for better performance",
            "• Regular monitoring and maintenance recommended"
        ]
        
        for rec in recommendations:
            content.append(Paragraph(rec, ParagraphStyle('Rec', parent=styles['Normal'], fontSize=10, spaceAfter=4, leftIndent=20)))
        
        # Footer
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph("📈 Report generated by Pardot Analytics Platform", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#6b7280'))))
        
        print("✅ Safe PDF content created successfully")
        doc.build(content)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"❌ Error in safe PDF generation: {str(e)}")
        # Create minimal error PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        content = [
            Paragraph("Report Generation Error", styles['Title']),
            Spacer(1, 0.2*inch),
            Paragraph(f"Error: {str(e)}", styles['Normal']),
            Spacer(1, 0.2*inch),
            Paragraph("Please contact support.", styles['Normal'])
        ]
        
        doc.build(content)
        buffer.seek(0)
        return buffer