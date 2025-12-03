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
        
        # COVER PAGE
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1, textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
        content.append(Paragraph("📊 COMPREHENSIVE MARKETING AUDIT REPORT", title_style))
        content.append(Paragraph("PARDOT PLATFORM ANALYSIS", ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=16, spaceAfter=30, alignment=1, textColor=colors.HexColor('#6366f1'), fontName='Helvetica-Bold')))
        content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ParagraphStyle('Date', parent=styles['Normal'], fontSize=12, spaceAfter=40, alignment=1, textColor=colors.HexColor('#6b7280'))))
        
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
        
        total_emails = len(email_stats) if email_stats else 0
        total_forms = len(form_stats) if form_stats else 0
        
        # Email metrics
        if email_stats:
            total_sent = sum(email.get('stats', {}).get('sent', 0) for email in email_stats)
            total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats)
            total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats)
            total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
            open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
            click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
        else:
            total_sent = total_opens = total_clicks = open_rate = click_rate = 0
        
        # Form metrics
        if form_stats:
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
        
        # EMAIL CAMPAIGN ANALYSIS - ALL CAMPAIGNS
        content.append(Paragraph("📧 EMAIL CAMPAIGN PERFORMANCE", section_style))
        content.append(Paragraph(f"Total Email Campaigns: {total_emails}", ParagraphStyle('Count', parent=styles['Normal'], fontSize=11, spaceAfter=10, fontName='Helvetica-Bold')))
        
        if email_stats:
            # ALL email campaigns with complete details
            campaign_data = [['CAMPAIGN NAME', 'SENT', 'DELIVERED', 'OPENS', 'CLICKS', 'BOUNCES', 'OPEN %', 'CTR %']]
            
            for i, campaign in enumerate(email_stats, 1):
                stats = campaign.get('stats', {})
                name = campaign.get('name', f'Campaign {i}')[:25] + '...' if len(campaign.get('name', '')) > 25 else campaign.get('name', f'Campaign {i}')
                sent = stats.get('sent', 0)
                delivered = stats.get('delivered', 0)
                opens = stats.get('opens', 0)
                clicks = stats.get('clicks', 0)
                bounces = stats.get('bounces', 0)
                
                open_rate = (opens / delivered * 100) if delivered > 0 else 0
                click_rate = (clicks / delivered * 100) if delivered > 0 else 0
                
                campaign_data.append([
                    name, f'{sent:,}', f'{delivered:,}', f'{opens:,}', f'{clicks:,}', 
                    f'{bounces:,}', f'{open_rate:.1f}%', f'{click_rate:.1f}%'
                ])
            
            # Create table with all campaigns
            campaign_table = Table(campaign_data, colWidths=[2*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch])
            campaign_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            content.append(campaign_table)
            content.append(Spacer(1, 0.2*inch))
            
            # Email performance chart
            content.append(create_email_performance_chart(total_sent, total_opens, total_clicks))
        else:
            content.append(Paragraph("No email campaign data available.", styles['Normal']))
        
        content.append(PageBreak())
        
        # FORM PERFORMANCE ANALYSIS - ALL FORMS
        content.append(Paragraph("📝 FORM PERFORMANCE ANALYSIS", section_style))
        content.append(Paragraph(f"Total Forms: {total_forms}", ParagraphStyle('Count', parent=styles['Normal'], fontSize=11, spaceAfter=10, fontName='Helvetica-Bold')))
        
        if form_stats:
            # ALL forms with complete details
            form_data = [['FORM NAME', 'VIEWS', 'SUBMISSIONS', 'CONVERSIONS', 'CLICKS', 'CONV %']]
            
            for i, form in enumerate(form_stats, 1):
                name = form.get('name', f'Form {i}')[:30] + '...' if len(form.get('name', '')) > 30 else form.get('name', f'Form {i}')
                views = form.get('views', 0)
                submissions = form.get('submissions', 0)
                conversions = form.get('conversions', 0)
                clicks = form.get('clicks', 0)
                
                conv_rate = (submissions / views * 100) if views > 0 else 0
                
                form_data.append([
                    name, f'{views:,}', f'{submissions:,}', f'{conversions:,}', f'{clicks:,}', f'{conv_rate:.1f}%'
                ])
            
            # Create table with all forms
            form_table = Table(form_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch, 0.9*inch])
            form_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
            ]))
            content.append(form_table)
            content.append(Spacer(1, 0.2*inch))
            
            # Form conversion chart
            content.append(create_form_conversion_chart(total_form_views, total_form_submissions))
        else:
            content.append(Paragraph("No form data available.", styles['Normal']))
        
        content.append(PageBreak())
        
        # COMPREHENSIVE DATABASE HEALTH AUDIT (REPLACES OLD PROSPECT HEALTH)
        content.append(Paragraph("📊 COMPREHENSIVE DATABASE HEALTH AUDIT", section_style))
        
        if database_health:
            # Active Contacts Section
            if database_health.get('active_contacts'):
                content.append(Paragraph("✅ ACTIVE CONTACTS ANALYSIS", ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#10b981'), fontName='Helvetica-Bold')))
                
                active_data = database_health.get('active_contacts', {}).get('table_data', [])
                if active_data:
                    table_data = [['Leads Created', '%age', 'Industry Standard', 'Count Till Jan 2025']]
                    for row in active_data:
                        table_data.append([
                            row.get('metric', ''),
                            row.get('percentage', ''),
                            row.get('industry_standard', ''),
                            f"{row.get('count', 0):,}"
                        ])
                    
                    active_table = Table(table_data, colWidths=[2.2*inch, 1*inch, 1.3*inch, 1.5*inch])
                    active_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                    ]))
                    content.append(active_table)
                    content.append(Spacer(1, 0.2*inch))
            
            # Inactive Contacts Section
            if database_health.get('inactive_contacts'):
                content.append(Paragraph("⚠️ INACTIVE CONTACTS ANALYSIS", ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#f59e0b'), fontName='Helvetica-Bold')))
                
                inactive_data = database_health.get('inactive_contacts', {}).get('table_data', [])
                if inactive_data:
                    table_data = [['Leads Created', '%age', 'Count']]
                    for row in inactive_data:
                        table_data.append([
                            row.get('metric', ''),
                            row.get('percentage', ''),
                            f"{row.get('count', 0):,}"
                        ])
                    
                    inactive_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                    inactive_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                    ]))
                    content.append(inactive_table)
                    content.append(Spacer(1, 0.2*inch))
            
            # Data Quality Section
            if database_health.get('empty_details'):
                content.append(Paragraph("🔍 DATA QUALITY ANALYSIS", ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')))
                
                empty_data = database_health.get('empty_details', {}).get('table_data', [])
                if empty_data:
                    table_data = [['Data Quality Metric', 'Count', '%age']]
                    for row in empty_data:
                        table_data.append([
                            row.get('metric', ''),
                            f"{row.get('count', 0):,}",
                            row.get('percentage', '')
                        ])
                    
                    empty_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                    empty_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                    ]))
                    content.append(empty_table)
                    content.append(Spacer(1, 0.2*inch))
            
            # Lead Scoring Section
            if database_health.get('scoring_issues'):
                content.append(Paragraph("⚡ LEAD SCORING ANALYSIS", ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#7c3aed'), fontName='Helvetica-Bold')))
                
                scoring_data = database_health.get('scoring_issues', {}).get('table_data', [])
                if scoring_data:
                    table_data = [['Scoring Issue', 'Count', '%age']]
                    for row in scoring_data:
                        table_data.append([
                            row.get('metric', ''),
                            f"{row.get('count', 0):,}",
                            row.get('percentage', '')
                        ])
                    
                    scoring_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                    scoring_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3e8ff')]),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                    ]))
                    content.append(scoring_table)
                    content.append(Spacer(1, 0.2*inch))
            
            # Charts
            chart_data = database_health.get('chart_data', [])
            if chart_data:
                content.append(create_database_health_charts(chart_data))
                content.append(Spacer(1, 0.2*inch))
        elif prospect_health:
            # Fallback to old prospect health if database health not available
            content.append(Paragraph("⚠️ Using Legacy Prospect Health Data", ParagraphStyle('Warning', parent=styles['Normal'], fontSize=11, spaceAfter=10, textColor=colors.HexColor('#f59e0b'), fontName='Helvetica-Bold')))
            
            duplicates = prospect_health.get('duplicates', {}).get('count', 0)
            inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
            missing_fields = prospect_health.get('missing_fields', {}).get('count', 0)
            scoring_issues = prospect_health.get('scoring_issues', {}).get('count', 0)
            
            legacy_data = [
                ['LEGACY PROSPECT METRIC', 'COUNT', 'PERCENTAGE'],
                ['Total Prospects', f'{total_prospects:,}', '100%'],
                ['Duplicate Records', f'{duplicates:,}', f'{(duplicates/total_prospects*100):.1f}%' if total_prospects > 0 else '0%'],
                ['Inactive Prospects', f'{inactive:,}', f'{(inactive/total_prospects*100):.1f}%' if total_prospects > 0 else '0%'],
                ['Missing Fields', f'{missing_fields:,}', f'{(missing_fields/total_prospects*100):.1f}%' if total_prospects > 0 else '0%'],
                ['Scoring Issues', f'{scoring_issues:,}', f'{(scoring_issues/total_prospects*100):.1f}%' if total_prospects > 0 else '0%']
            ]
            
            legacy_table = Table(legacy_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch])
            legacy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            content.append(legacy_table)
        else:
            content.append(Paragraph("No database health or prospect data available.", styles['Normal']))
        
        content.append(PageBreak())
        
        # LANDING PAGE PERFORMANCE - ALL PAGES
        if landing_page_stats:
            content.append(Paragraph("🚀 LANDING PAGE PERFORMANCE", section_style))
            
            summary = landing_page_stats.get('summary', {})
            active_pages = landing_page_stats.get('active_pages', {}).get('pages', [])
            inactive_pages = landing_page_stats.get('inactive_pages', {}).get('pages', [])
            all_pages = active_pages + inactive_pages
            
            content.append(Paragraph(f"Total Landing Pages: {len(all_pages)}", ParagraphStyle('Count', parent=styles['Normal'], fontSize=11, spaceAfter=10, fontName='Helvetica-Bold')))
            
            if all_pages:
                # ALL landing pages with complete details
                lp_data = [['PAGE NAME', 'STATUS', 'VIEWS', 'SUBMISSIONS', 'CLICKS', 'CONV %']]
                
                for i, page in enumerate(all_pages, 1):
                    name = page.get('name', f'Page {i}')[:35] + '...' if len(page.get('name', '')) > 35 else page.get('name', f'Page {i}')
                    status = 'Active' if page in active_pages else 'Inactive'
                    views = page.get('views', 0)
                    submissions = page.get('submissions', 0)
                    clicks = page.get('clicks', 0)
                    
                    conv_rate = (submissions / views * 100) if views > 0 else 0
                    
                    lp_data.append([
                        name, status, f'{views:,}', f'{submissions:,}', f'{clicks:,}', f'{conv_rate:.1f}%'
                    ])
                
                # Create table with all landing pages
                lp_table = Table(lp_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch, 1.1*inch])
                lp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3e8ff')]),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
                ]))
                content.append(lp_table)
            else:
                content.append(Paragraph("No landing page data available.", styles['Normal']))
            
            content.append(PageBreak())
        
        # ENGAGEMENT PROGRAMS ANALYSIS - ALL PROGRAMS
        if engagement_programs:
            content.append(Paragraph("🎯 ENGAGEMENT PROGRAMS", section_style))
            
            summary = engagement_programs.get('summary', {})
            active_programs = engagement_programs.get('active_programs', [])
            
            content.append(Paragraph(f"Total Programs: {summary.get('total_programs', 0)}", ParagraphStyle('Count', parent=styles['Normal'], fontSize=11, spaceAfter=10, fontName='Helvetica-Bold')))
            
            if active_programs:
                # ALL engagement programs with details
                program_data = [['PROGRAM NAME', 'STATUS', 'CREATED DATE', 'TYPE']]
                
                for i, program in enumerate(active_programs, 1):
                    name = program.get('name', f'Program {i}')[:35] + '...' if len(program.get('name', '')) > 35 else program.get('name', f'Program {i}')
                    status = program.get('status', 'Unknown')
                    created_date = program.get('createdAt', '')
                    if created_date:
                        try:
                            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                        except:
                            created_date = 'Unknown'
                    program_type = program.get('type', 'Standard')
                    
                    program_data.append([name, status, created_date, program_type])
                
                # Create table with all programs
                program_table = Table(program_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
                program_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
                ]))
                content.append(program_table)
            
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

def create_email_performance_chart(sent, opens, clicks):
    """Create email performance chart"""
    drawing = Drawing(500, 250)
    chart = VerticalBarChart()
    chart.x = 80
    chart.y = 60
    chart.height = 140
    chart.width = 340
    
    chart.data = [[sent, opens, clicks]]
    chart.categoryAxis.categoryNames = ['Emails Sent', 'Emails Opened', 'Emails Clicked']
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(sent, 1) * 1.2
    chart.valueAxis.labels.fontSize = 9
    
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    chart.bars.strokeColor = colors.HexColor('#1e40af')
    chart.bars.strokeWidth = 1
    
    from reportlab.graphics.shapes import String
    title = String(250, 220, 'Email Campaign Performance Overview', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_form_conversion_chart(views, submissions):
    """Create form conversion pie chart"""
    drawing = Drawing(500, 250)
    pie = Pie()
    pie.x = 175
    pie.y = 75
    pie.width = 150
    pie.height = 150
    
    abandoned = views - submissions if views > submissions else 0
    conversion_rate = (submissions / views * 100) if views > 0 else 0
    
    pie.data = [submissions, abandoned]
    pie.labels = [f'Conversions\n{submissions:,}\n({conversion_rate:.1f}%)', f'Abandoned\n{abandoned:,}']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    
    pie.slices.fontName = 'Helvetica-Bold'
    pie.slices.fontSize = 9
    pie.slices.fontColor = colors.HexColor('#1f2937')
    
    from reportlab.graphics.shapes import String
    title = String(250, 230, 'Form Conversion Analysis', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_database_health_charts(chart_data):
    """Create comprehensive database health charts"""
    drawing = Drawing(500, 400)
    
    # Find charts by ID in the array
    lead_trend = None
    engagement = None
    
    if isinstance(chart_data, list):
        for chart in chart_data:
            if chart.get('id') == 'lead_creation_trend':
                lead_trend = chart
            elif chart.get('id') == 'engagement_breakdown':
                engagement = chart
    
    # Lead Creation Trend Chart
    if lead_trend:
        chart_info = lead_trend.get('data', {})
        datasets = chart_info.get('datasets', [{}])
        data_values = datasets[0].get('data', [0, 0, 0]) if datasets else [0, 0, 0]
        labels = chart_info.get('labels', ['30 Days', '60 Days', '90 Days'])
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 250
        chart.height = 120
        chart.width = 400
        
        chart.data = [data_values]
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.fontSize = 9
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(max(data_values), 1) * 1.2
        chart.valueAxis.labels.fontSize = 8
        
        chart.bars[0].fillColor = colors.HexColor('#3b82f6')
        chart.bars.strokeColor = colors.HexColor('#1e40af')
        chart.bars.strokeWidth = 1
        
        from reportlab.graphics.shapes import String
        title1 = String(250, 380, 'Lead Creation Trend (30/60/90 Days)', textAnchor='middle')
        title1.fontSize = 11
        title1.fontName = 'Helvetica-Bold'
        title1.fillColor = colors.HexColor('#1f2937')
        
        drawing.add(chart)
        drawing.add(title1)
    
    # Engagement Breakdown Pie Chart
    if engagement:
        chart_info = engagement.get('data', {})
        datasets = chart_info.get('datasets', [{}])
        data_values = datasets[0].get('data', [1, 1, 1]) if datasets else [1, 1, 1]
        labels = chart_info.get('labels', ['Forms', 'Emails', 'Pages'])
        
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 120
        pie.height = 120
        
        pie.data = data_values
        pie.labels = []
        pie.slices.strokeWidth = 2
        pie.slices.strokeColor = colors.white
        
        # Set colors safely
        colors_list = [colors.HexColor('#10b981'), colors.HexColor('#3b82f6'), colors.HexColor('#f59e0b')]
        for i in range(min(len(data_values), len(colors_list))):
            pie.slices[i].fillColor = colors_list[i]
        
        pie.slices.fontName = 'Helvetica-Bold'
        pie.slices.fontSize = 8
        pie.slices.fontColor = colors.HexColor('#1f2937')
        
        title2 = String(110, 180, 'Engagement Activities', textAnchor='middle')
        title2.fontSize = 10
        title2.fontName = 'Helvetica-Bold'
        title2.fillColor = colors.HexColor('#1f2937')
        
        drawing.add(pie)
        drawing.add(title2)
    
    return drawing

def create_database_health_chart(healthy, duplicates, inactive, missing_fields, scoring_issues):
    """Create database health pie chart"""
    drawing = Drawing(500, 250)
    pie = Pie()
    pie.x = 175
    pie.y = 75
    pie.width = 150
    pie.height = 150
    
    total = healthy + duplicates + inactive + missing_fields + scoring_issues
    if total == 0:
        healthy = 1
        total = 1
    
    pie.data = [healthy, duplicates, inactive, missing_fields, scoring_issues]
    pie.labels = [
        f'Healthy\n{healthy:,}',
        f'Duplicates\n{duplicates:,}',
        f'Inactive\n{inactive:,}',
        f'Missing Fields\n{missing_fields:,}',
        f'Scoring Issues\n{scoring_issues:,}'
    ]
    
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices[2].fillColor = colors.HexColor('#ef4444')
    pie.slices[3].fillColor = colors.HexColor('#8b5cf6')
    pie.slices[4].fillColor = colors.HexColor('#f97316')
    
    pie.slices.fontName = 'Helvetica-Bold'
    pie.slices.fontSize = 8
    pie.slices.fontColor = colors.HexColor('#1f2937')
    
    from reportlab.graphics.shapes import String
    title = String(250, 230, 'Database Health Distribution', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

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