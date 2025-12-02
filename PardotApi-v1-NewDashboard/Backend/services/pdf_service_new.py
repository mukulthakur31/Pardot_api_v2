from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
from datetime import datetime

# Import section functions
try:
    from .pdf_service_sections import (
        create_detailed_email_section, create_detailed_form_section, 
        create_detailed_prospect_section, create_detailed_landing_page_section,
        create_detailed_engagement_section, create_detailed_utm_section,
        create_recommendations_section, create_appendix_section
    )
except ImportError:
    # Fallback for direct execution
    from pdf_service_sections import (
        create_detailed_email_section, create_detailed_form_section, 
        create_detailed_prospect_section, create_detailed_landing_page_section,
        create_detailed_engagement_section, create_detailed_utm_section,
        create_recommendations_section, create_appendix_section
    )

def create_comprehensive_summary_pdf(email_stats, form_stats, prospect_health, landing_page_stats=None, engagement_programs=None, utm_analysis=None):
    """Generate professional audit-quality Pardot report with comprehensive analysis"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        content = []
        styles = getSampleStyleSheet()
        
        # Professional styling
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=1, textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=18, spaceAfter=20, textColor=colors.HexColor('#374151'), fontName='Helvetica-Bold')
        subsection_style = ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'), fontName='Helvetica-Bold')
        
        # PROFESSIONAL COVER PAGE
        content.extend(create_professional_cover_page())
        content.append(PageBreak())
        
        # TABLE OF CONTENTS
        content.extend(create_table_of_contents())
        content.append(PageBreak())
        
        # EXECUTIVE SUMMARY
        content.extend(create_executive_summary(email_stats, form_stats, prospect_health, landing_page_stats, engagement_programs, utm_analysis))
        content.append(PageBreak())
        
        # EMAIL CAMPAIGNS SECTION
        if email_stats:
            content.extend(create_detailed_email_section(email_stats))
            content.append(PageBreak())
        
        # FORMS SECTION
        if form_stats:
            content.extend(create_detailed_form_section(form_stats))
            content.append(PageBreak())
        
        # LANDING PAGES SECTION
        if landing_page_stats:
            content.extend(create_detailed_landing_page_section(landing_page_stats))
            content.append(PageBreak())
        
        # PROSPECTS SECTION
        if prospect_health:
            content.extend(create_detailed_prospect_section(prospect_health))
            content.append(PageBreak())
        
        # ENGAGEMENT PROGRAMS SECTION
        if engagement_programs:
            content.extend(create_detailed_engagement_section(engagement_programs))
            content.append(PageBreak())
        
        # UTM ANALYSIS SECTION
        if utm_analysis:
            content.extend(create_detailed_utm_section(utm_analysis))
            content.append(PageBreak())
        
        # RECOMMENDATIONS SECTION
        content.extend(create_recommendations_section(email_stats, form_stats, prospect_health, landing_page_stats))
        
        # APPENDIX
        content.extend(create_appendix_section())
        
        doc.build(content)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating report: {str(e)}")
        return create_error_pdf(str(e))

def create_professional_cover_page():
    """Create professional cover page"""
    styles = getSampleStyleSheet()
    content = []
    
    # Company Logo Area
    content.append(Spacer(1, 1*inch))
    
    # Main Title
    title_style = ParagraphStyle('CoverTitle', parent=styles['Heading1'], 
                               fontSize=28, spaceAfter=30, alignment=1, 
                               textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("PARDOT MARKETING AUTOMATION", title_style))
    content.append(Paragraph("COMPREHENSIVE AUDIT REPORT", title_style))
    
    content.append(Spacer(1, 0.5*inch))
    
    # Subtitle
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Normal'], 
                                  fontSize=16, spaceAfter=40, alignment=1, 
                                  textColor=colors.HexColor('#4b5563'), fontName='Helvetica')
    
    content.append(Paragraph("Performance Analysis & Strategic Recommendations", subtitle_style))
    
    content.append(Spacer(1, 1*inch))
    
    # Report Details Box
    report_details = f"""
    <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
    <b>Report Period:</b> Comprehensive Analysis<br/>
    <b>Document Version:</b> 1.0<br/>
    <b>Confidentiality:</b> Internal Use Only
    """
    
    details_style = ParagraphStyle('ReportDetails', parent=styles['Normal'], 
                                 fontSize=12, spaceAfter=20, alignment=1, 
                                 textColor=colors.HexColor('#374151'), leading=18)
    
    details_para = Paragraph(report_details, details_style)
    
    details_table = Table([[details_para]], colWidths=[5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BORDER', (0, 0), (-1, -1), 2, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    
    content.append(details_table)
    
    content.append(Spacer(1, 1*inch))
    
    # Footer
    footer_style = ParagraphStyle('CoverFooter', parent=styles['Normal'], 
                                fontSize=10, alignment=1, 
                                textColor=colors.HexColor('#6b7280'))
    
    content.append(Paragraph("Prepared by Pardot Analytics Platform", footer_style))
    
    return content

def create_table_of_contents():
    """Create table of contents"""
    styles = getSampleStyleSheet()
    content = []
    
    # Title
    toc_title = ParagraphStyle('TOCTitle', parent=styles['Heading1'], 
                             fontSize=20, spaceAfter=30, alignment=1, 
                             textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("TABLE OF CONTENTS", toc_title))
    
    # TOC Items
    toc_data = [
        ['SECTION', 'PAGE'],
        ['Executive Summary', '3'],
        ['1. Email Campaign Analysis', '4'],
        ['2. Form Performance Analysis', '6'],
        ['3. Landing Page Analysis', '8'],
        ['4. Prospect Database Health', '10'],
        ['5. Engagement Programs', '12'],
        ['6. UTM Tracking Analysis', '14'],
        ['7. Strategic Recommendations', '16'],
        ['Appendix', '18']
    ]
    
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15)
    ]))
    
    content.append(toc_table)
    
    return content

def create_executive_summary(email_stats, form_stats, prospect_health, landing_page_stats, engagement_programs, utm_analysis):
    """Create executive summary section"""
    styles = getSampleStyleSheet()
    content = []
    
    # Title
    summary_title = ParagraphStyle('SummaryTitle', parent=styles['Heading1'], 
                                 fontSize=20, spaceAfter=25, alignment=1, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("EXECUTIVE SUMMARY", summary_title))
    
    # Key Metrics Overview
    content.append(Paragraph("Key Performance Indicators", 
                           ParagraphStyle('SectionHeader', parent=styles['Heading2'], 
                                        fontSize=16, spaceAfter=15, textColor=colors.HexColor('#374151'))))
    
    # Calculate key metrics
    total_campaigns = len(email_stats) if email_stats else 0
    total_forms = len(form_stats) if form_stats else 0
    total_prospects = prospect_health.get('total_prospects', 0) if prospect_health else 0
    
    # Email metrics
    if email_stats:
        total_sent = sum(email.get('stats', {}).get('sent', 0) for email in email_stats)
        total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats)
        total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
        open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
    else:
        total_sent = 0
        open_rate = 0
    
    # Form metrics
    if form_stats:
        total_form_views = sum(form.get('views', 0) for form in form_stats)
        total_submissions = sum(form.get('submissions', 0) for form in form_stats)
        conversion_rate = (total_submissions / total_form_views * 100) if total_form_views > 0 else 0
    else:
        total_form_views = 0
        conversion_rate = 0
    
    # Prospect health
    if prospect_health:
        duplicates = prospect_health.get('duplicates', {}).get('count', 0)
        inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
        health_score = ((total_prospects - duplicates - inactive) / total_prospects * 100) if total_prospects > 0 else 100
    else:
        health_score = 100
    
    # KPI Table
    kpi_data = [
        ['METRIC', 'VALUE', 'STATUS'],
        ['Email Campaigns', f"{total_campaigns:,}", 'Active'],
        ['Email Open Rate', f"{open_rate:.1f}%", 'Good' if open_rate > 20 else 'Needs Improvement'],
        ['Active Forms', f"{total_forms:,}", 'Deployed'],
        ['Form Conversion Rate', f"{conversion_rate:.1f}%", 'Good' if conversion_rate > 15 else 'Needs Improvement'],
        ['Total Prospects', f"{total_prospects:,}", 'Database'],
        ['Database Health Score', f"{health_score:.1f}%", 'Healthy' if health_score > 80 else 'Needs Attention']
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(kpi_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Executive Summary Text
    summary_text = f"""
    This comprehensive audit of your Pardot marketing automation platform reveals both strengths and opportunities for optimization. 
    Your platform currently manages {total_campaigns} email campaigns, {total_forms} forms, and {total_prospects:,} prospects.
    
    <b>Key Findings:</b>
    • Email performance shows {open_rate:.1f}% open rate across {total_sent:,} emails sent
    • Form conversion rate of {conversion_rate:.1f}% indicates {'strong' if conversion_rate > 20 else 'moderate' if conversion_rate > 10 else 'weak'} lead capture effectiveness
    • Database health score of {health_score:.1f}% {'meets' if health_score > 80 else 'falls below'} industry standards
    
    <b>Priority Actions:</b>
    • Optimize email subject lines and send times to improve engagement
    • Streamline form fields to increase conversion rates
    • Implement database cleanup procedures for duplicate and inactive records
    • Enhance lead scoring and grading processes for better qualification
    """
    
    summary_para = Paragraph(summary_text, 
                           ParagraphStyle('SummaryText', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16, alignment=0))
    
    content.append(summary_para)
    
    return content

def create_error_pdf(error_message):
    """Create simple error PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    content = [
        Paragraph("Report Generation Error", styles['Title']),
        Spacer(1, 0.2*inch),
        Paragraph(f"Error: {error_message}", styles['Normal']),
        Spacer(1, 0.2*inch),
        Paragraph("Please try again or contact support if the issue persists.", styles['Normal'])
    ]
    
    doc.build(content)
    buffer.seek(0)
    return buffer