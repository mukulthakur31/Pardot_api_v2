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

def create_comprehensive_audit_pdf(email_stats, form_stats, prospect_health, landing_page_stats=None, engagement_programs=None, utm_analysis=None, database_health=None):
    """Generate comprehensive full audit report with ALL details"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.6*inch, rightMargin=0.6*inch)
        
        content = []
        styles = getSampleStyleSheet()
        
        # PROFESSIONAL COVER PAGE
        content.extend(create_cover_page())
        content.append(PageBreak())
        
        # TABLE OF CONTENTS
        content.extend(create_table_of_contents())
        content.append(PageBreak())
        
        # EXECUTIVE SUMMARY
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')
        content.append(Paragraph("📋 EXECUTIVE SUMMARY", section_style))
        
        # Use database health data (new comprehensive prospect health) instead of old prospect health
        total_prospects = 0
        if database_health and database_health.get('summary', {}).get('total_database'):
            total_prospects = database_health.get('summary', {}).get('total_database', 0)
        elif prospect_health:
            # Fallback to old prospect health if database health not available
            total_prospects = prospect_health.get('total_prospects', 0)
        
        total_emails = len(email_stats) if email_stats and isinstance(email_stats, list) else 0
        total_forms = len(form_stats) if form_stats and isinstance(form_stats, list) else 0
        
        # Email metrics
        if email_stats and isinstance(email_stats, list):
            total_sent = sum(email.get('stats', {}).get('sent', 0) for email in email_stats)
            total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats)
            total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats)
            total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
            open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
            click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
        else:
            total_sent = total_opens = total_clicks = open_rate = click_rate = 0
        
        # Form metrics
        if form_stats and isinstance(form_stats, list):
            total_form_views = sum(form.get('views', 0) for form in form_stats)
            total_form_submissions = sum(form.get('submissions', 0) for form in form_stats)
            form_conversion_rate = (total_form_submissions / total_form_views * 100) if total_form_views > 0 else 0
        else:
            total_form_views = total_form_submissions = form_conversion_rate = 0
        
        # Executive summary table
        exec_data = [
            ['METRIC', 'VALUE', 'STATUS'],
            ['Total Prospects', f'{total_prospects:,}', '👥 Database'],
            ['Email Campaigns', f'{total_emails:,}', '📧 Active'],
            ['Email Open Rate', f'{open_rate:.1f}%', '✅ Good' if open_rate > 20 else '⚠️ Review'],
            ['Email Click Rate', f'{click_rate:.1f}%', '✅ Good' if click_rate > 2.5 else '⚠️ Review'],
            ['Active Forms', f'{total_forms:,}', '📝 Deployed'],
            ['Form Conversion Rate', f'{form_conversion_rate:.1f}%', '✅ Good' if form_conversion_rate > 15 else '⚠️ Optimize']
        ]
        
        exec_table = Table(exec_data, colWidths=[2.2*inch, 1.3*inch, 1.5*inch])
        exec_table.setStyle(TableStyle([
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
        content.append(exec_table)
        content.append(PageBreak())
        
        # ENGAGEMENT PROGRAMS ANALYSIS - ALL PROGRAMS
        if engagement_programs:
            content.append(Paragraph("🎯 ENGAGEMENT PROGRAMS", section_style))
            
            summary = engagement_programs.get('summary', {})
            active_programs = engagement_programs.get('active_programs', []) or []
            inactive_programs = engagement_programs.get('inactive_programs', []) or []
            paused_programs = engagement_programs.get('paused_programs', []) or []
            deleted_programs = engagement_programs.get('deleted_programs', []) or []
            all_programs = active_programs + inactive_programs + paused_programs + deleted_programs
            
            # Summary table
            summary_data = [
                ['ENGAGEMENT PROGRAMS SUMMARY', 'COUNT'],
                ['Total Programs', f"{summary.get('total_programs', len(all_programs)):,}"],
                ['Active Programs', f"{len(active_programs):,}"],
                ['Inactive Programs', f"{len(inactive_programs):,}"],
                ['Paused Programs', f"{len(paused_programs):,}"],
                ['Deleted Programs', f"{len(deleted_programs):,}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            content.append(summary_table)
            content.append(Spacer(1, 0.2*inch))
            
            if all_programs:
                content.append(Paragraph("📋 ALL ENGAGEMENT PROGRAMS DETAILS", ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
                
                program_data = [['PROGRAM NAME', 'STATUS', 'CREATED DATE', 'DESCRIPTION']]
                
                for i, program in enumerate(all_programs, 1):
                    name = program.get('name', f'Program {i}')[:30] + '...' if len(program.get('name', '')) > 30 else program.get('name', f'Program {i}')
                    status = program.get('status', 'Unknown')
                    created_date = program.get('createdAt', '')
                    if created_date:
                        try:
                            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                        except:
                            created_date = 'Unknown'
                    description = program.get('description', 'No description')[:35] + '...' if len(program.get('description', '')) > 35 else program.get('description', 'No description')
                    
                    program_data.append([name, status, created_date, description])
                
                program_table = Table(program_data, colWidths=[2.2*inch, 0.8*inch, 1*inch, 2*inch])
                program_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('ALIGN', (3, 1), (3, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
                ]))
                content.append(program_table)
            else:
                content.append(Paragraph("No engagement program data available.", ParagraphStyle('NoData', parent=styles['Normal'], fontSize=11, spaceAfter=10, textColor=colors.HexColor('#6b7280'))))
            
            content.append(PageBreak())
        else:
            content.append(Paragraph("🎯 ENGAGEMENT PROGRAMS", section_style))
            content.append(Paragraph("No engagement program data available for analysis.", ParagraphStyle('NoData', parent=styles['Normal'], fontSize=11, spaceAfter=10, textColor=colors.HexColor('#6b7280'))))
            content.append(PageBreak())
        
        # STRATEGIC RECOMMENDATIONS
        content.append(Paragraph("💡 STRATEGIC RECOMMENDATIONS", section_style))
        
        recommendations = [
            "🔥 IMMEDIATE ACTIONS:",
            "• Clean up duplicate prospect records to improve data accuracy",
            "• Re-engage inactive prospects with targeted campaigns",
            "• Implement A/B testing for email subject lines to increase open rates",
            "• Optimize forms with low conversion rates to capture more leads",
            "",
            "📊 STRATEGIC IMPROVEMENTS:",
            "• Complete missing fields for prospects to improve segmentation",
            "• Review scoring model for prospects with inconsistencies",
            "• Implement progressive profiling to gather prospect data over time",
            "• Create targeted email segments based on engagement history",
            "• Establish regular database maintenance and quality monitoring procedures",
            "• Optimize landing page performance and fix field mapping issues"
        ]
        
        for rec in recommendations:
            if rec.startswith(('🔥', '📊')):
                content.append(Paragraph(rec, ParagraphStyle('RecHeader', parent=styles['Normal'], fontSize=12, spaceAfter=8, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626'))))
            elif rec.startswith('•'):
                content.append(Paragraph(rec, ParagraphStyle('RecItem', parent=styles['Normal'], fontSize=10, spaceAfter=4, leftIndent=20)))
            elif rec == "":
                content.append(Spacer(1, 0.1*inch))
        
        # Footer
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph("📈 Report generated by Pardot Analytics Platform", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#6b7280'))))
        
        doc.build(content)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating comprehensive report: {str(e)}")
        return create_error_pdf(str(e))

def create_cover_page():
    """Create professional cover page"""
    styles = getSampleStyleSheet()
    content = []
    
    # Add spacing from top
    content.append(Spacer(1, 1.5*inch))
    
    # Main title
    title_style = ParagraphStyle('CoverTitle', parent=styles['Heading1'], 
                               fontSize=28, spaceAfter=10, alignment=1, 
                               textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    content.append(Paragraph("PARDOT MARKETING", title_style))
    content.append(Paragraph("AUTOMATION", title_style))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Subtitle
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Heading1'], 
                                  fontSize=24, spaceAfter=20, alignment=1, 
                                  textColor=colors.HexColor('#3b82f6'), fontName='Helvetica-Bold')
    content.append(Paragraph("COMPREHENSIVE AUDIT REPORT", subtitle_style))
    
    content.append(Spacer(1, 0.5*inch))
    
    # Description
    desc_style = ParagraphStyle('CoverDesc', parent=styles['Normal'], 
                              fontSize=16, spaceAfter=30, alignment=1, 
                              textColor=colors.HexColor('#6b7280'), fontName='Helvetica-Bold')
    content.append(Paragraph("Performance Analysis & Strategic Recommendations", desc_style))
    
    content.append(Spacer(1, 1*inch))
    
    # Report details
    details_style = ParagraphStyle('CoverDetails', parent=styles['Normal'], 
                                 fontSize=12, spaceAfter=8, alignment=1, 
                                 textColor=colors.HexColor('#374151'))
    
    current_date = datetime.now().strftime('%B %d, %Y')
    content.append(Paragraph(f"Report Generated: {current_date}", details_style))
    content.append(Paragraph("Report Period: Comprehensive Analysis", details_style))
    content.append(Paragraph("Document Version: 1.0", details_style))
    content.append(Paragraph("Confidentiality: Internal Use Only", details_style))
    
    content.append(Spacer(1, 1*inch))
    
    # Footer
    footer_style = ParagraphStyle('CoverFooter', parent=styles['Normal'], 
                                fontSize=14, spaceAfter=0, alignment=1, 
                                textColor=colors.HexColor('#6366f1'), fontName='Helvetica-Bold')
    content.append(Paragraph("Prepared by Pardot Analytics Platform", footer_style))
    
    return content

def create_table_of_contents():
    """Create table of contents"""
    styles = getSampleStyleSheet()
    content = []
    
    # TOC Title
    toc_title_style = ParagraphStyle('TOCTitle', parent=styles['Heading1'], 
                                   fontSize=20, spaceAfter=30, alignment=1, 
                                   textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    content.append(Paragraph("TABLE OF CONTENTS", toc_title_style))
    
    # TOC Table
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
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