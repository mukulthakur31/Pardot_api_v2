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

def create_professional_pdf_report(stats_list, filterType=None, startDate=None, endDate=None):
    """Generate a modern, compact professional PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    content = []
    
    # 1. HEADER & SUMMARY (Single Page)
    content.extend(create_modern_header_and_summary(stats_list, filterType, startDate, endDate))
    
    # 2. EMAIL PERFORMANCE TABLE (Compact)
    if stats_list:
        content.append(Spacer(1, 0.3*inch))
        content.extend(create_compact_email_table(stats_list))
        
        # 3. KEY INSIGHTS & RECOMMENDATIONS
        content.append(Spacer(1, 0.3*inch))
        content.extend(create_insights_section(stats_list))
    else:
        content.append(Paragraph("No email data available for the selected period.", getSampleStyleSheet()['Normal']))
    
    doc.build(content)
    buffer.seek(0)
    return buffer

def create_form_pdf_report(form_stats):
    """Generate PDF report for form statistics"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    content = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('FormHeader', parent=styles['Heading1'], 
                                fontSize=20, spaceAfter=16, alignment=1, 
                                textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("📝 FORM PERFORMANCE REPORT", header_style))
    content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                           ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, spaceAfter=16, alignment=1, textColor=colors.HexColor('#6b7280'))))
    
    # Summary
    total_views = sum(form.get('views', 0) for form in form_stats)
    total_submissions = sum(form.get('submissions', 0) for form in form_stats)
    avg_conversion = (total_submissions / total_views * 100) if total_views > 0 else 0
    
    summary_data = [
        ['📊 FORM SUMMARY', 'VALUE'],
        ['Total Forms', f"{len(form_stats):,}"],
        ['Total Views', f"{total_views:,}"],
        ['Total Submissions', f"{total_submissions:,}"],
        ['Average Conversion Rate', f"{avg_conversion:.1f}%"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3.2*inch, 1.8*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Form details table
    if form_stats:
        table_data = [['Form Name', 'Views', 'Submissions', 'Conversion Rate']]
        
        for form in form_stats[:20]:  # Limit to first 20 forms
            name = form.get('name', 'Unknown')[:30] + '...' if len(form.get('name', '')) > 30 else form.get('name', 'Unknown')
            views = form.get('views', 0)
            submissions = form.get('submissions', 0)
            conversion_rate = (submissions / views * 100) if views > 0 else 0
            
            table_data.append([
                name,
                f"{views:,}",
                f"{submissions:,}",
                f"{conversion_rate:.1f}%"
            ])
        
        form_table = Table(table_data, colWidths=[3.2*inch, 0.9*inch, 1*inch, 1.1*inch])
        form_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4)
        ]))
        
        content.append(Paragraph("📋 FORM PERFORMANCE DETAILS", 
                               ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
        content.append(form_table)
    
    doc.build(content)
    buffer.seek(0)
    return buffer

def create_prospect_pdf_report(health_data):
    """Generate PDF report for prospect health analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    content = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('ProspectHeader', parent=styles['Heading1'], 
                                fontSize=20, spaceAfter=16, alignment=1, 
                                textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("🏥 PROSPECT DATABASE HEALTH REPORT", header_style))
    content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                           ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, spaceAfter=16, alignment=1, textColor=colors.HexColor('#6b7280'))))
    
    # Health summary
    summary_data = [
        ['📊 DATABASE HEALTH SUMMARY', 'COUNT', 'PERCENTAGE'],
        ['Total Prospects', f"{health_data['total_prospects']:,}", '100%'],
        ['Duplicate Prospects', f"{health_data['duplicates']['count']:,}", f"{(health_data['duplicates']['count']/health_data['total_prospects']*100):.1f}%"],
        ['Inactive Prospects (90+ days)', f"{health_data['inactive_prospects']['count']:,}", f"{(health_data['inactive_prospects']['count']/health_data['total_prospects']*100):.1f}%"],
        ['Missing Critical Fields', f"{health_data['missing_fields']['count']:,}", f"{(health_data['missing_fields']['count']/health_data['total_prospects']*100):.1f}%"],
        ['Scoring Issues', f"{health_data['scoring_issues']['count']:,}", f"{(health_data['scoring_issues']['count']/health_data['total_prospects']*100):.1f}%"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Grading analysis
    grading = health_data.get('grading_analysis', {})
    if grading:
        content.append(Paragraph("📊 GRADING ANALYSIS", 
                               ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
        
        grading_data = [
            ['Grading Metric', 'Value'],
            ['Grading Coverage', f"{grading.get('grading_coverage', 0):.1f}%"],
            ['Graded Prospects', f"{grading.get('graded_prospects', 0):,}"],
            ['Ungraded Prospects', f"{grading.get('ungraded_prospects', 0):,}"]
        ]
        
        grading_table = Table(grading_data, colWidths=[3.2*inch, 1.8*inch])
        grading_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4)
        ]))
        
        content.append(grading_table)
    
    doc.build(content)
    buffer.seek(0)
    return buffer

# Helper functions for email PDF report
def create_modern_header_and_summary(stats_list, filterType, startDate, endDate):
    """Create modern header with integrated summary"""
    styles = getSampleStyleSheet()
    content = []
    
    # Modern Header
    header_style = ParagraphStyle('ModernHeader', parent=styles['Heading1'], 
                                fontSize=20, spaceAfter=8, alignment=1, 
                                textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    subtitle_style = ParagraphStyle('ModernSubtitle', parent=styles['Normal'], 
                                  fontSize=12, spaceAfter=16, alignment=1, 
                                  textColor=colors.HexColor('#6b7280'))
    
    content.append(Paragraph("📊 EMAIL CAMPAIGN PERFORMANCE REPORT", header_style))
    
    # Date and generation info
    if filterType and filterType != "":
        if filterType == "custom" and startDate and endDate:
            date_str = f"Custom Date Range: {startDate} to {endDate} • Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        else:
            filter_display = filterType.replace('_', ' ').title()
            date_str = f"Filter: {filter_display} • Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    else:
        date_str = f"All Campaign Data • Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    
    content.append(Paragraph(date_str, subtitle_style))
    
    return content

def create_compact_email_table(stats_list):
    """Create a compact table showing all email performance"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section header
    section_style = ParagraphStyle('CompactSection', parent=styles['Heading2'], 
                                 fontSize=16, spaceAfter=12, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph(f"📈 CAMPAIGN PERFORMANCE BREAKDOWN ({len(stats_list)} Campaigns)", section_style))
    
    # Prepare table data
    table_data = [['Campaign Name', 'Sent', 'Opens', 'Clicks', 'Open Rate', 'CTR']]
    
    for email_data in stats_list[:25]:  # Limit to first 25 campaigns
        stats = email_data.get('stats', {})
        name = email_data.get('name', 'Unknown')[:30] + '...' if len(email_data.get('name', '')) > 30 else email_data.get('name', 'Unknown')
        sent = stats.get('sent', 0)
        delivered = stats.get('delivered', 0)
        opens = stats.get('opens', 0)
        clicks = stats.get('clicks', 0)
        
        open_rate = (opens / delivered * 100) if delivered > 0 else 0
        click_rate = (clicks / delivered * 100) if delivered > 0 else 0
        
        table_data.append([
            name,
            f"{sent:,}",
            f"{opens:,}",
            f"{clicks:,}",
            f"{open_rate:.1f}%",
            f"{click_rate:.1f}%"
        ])
    
    # Create table with proper column alignment
    email_table = Table(table_data, colWidths=[2.2*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch])
    email_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Campaign name column (left align)
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(email_table)
    return content

def create_insights_section(stats_list):
    """Create insights and recommendations section"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section header
    section_style = ParagraphStyle('InsightsSection', parent=styles['Heading2'], 
                                 fontSize=16, spaceAfter=12, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("🎯 KEY INSIGHTS & RECOMMENDATIONS", section_style))
    
    # Calculate totals
    total_sent = sum(email.get('stats', {}).get('sent', 0) for email in stats_list)
    total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in stats_list)
    total_opens = sum(email.get('stats', {}).get('opens', 0) for email in stats_list)
    total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in stats_list)
    
    open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
    
    # Create insights table
    insights_data = [
        ['📊 PERFORMANCE ANALYSIS', 'VALUE'],
        ['Overall Open Rate', f"{open_rate:.1f}%"],
        ['Overall Click Rate', f"{click_rate:.1f}%"],
        ['Total Campaigns', f"{len(stats_list):,}"],
        ['Total Emails Sent', f"{total_sent:,}"],
        ['Total Engagement', f"{((total_opens + total_clicks) / total_delivered * 100):.1f}%" if total_delivered > 0 else '0%']
    ]
    
    insights_table = Table(insights_data, colWidths=[3.2*inch, 1.8*inch])
    insights_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(insights_table)
    return content

def create_comprehensive_summary_pdf(email_stats, form_stats, prospect_health, landing_page_stats=None, engagement_programs=None, utm_analysis=None):
    """Generate sectioned Pardot report with individual data summaries"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        content = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1, textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=18, spaceAfter=15, textColor=colors.HexColor('#3b82f6'), fontName='Helvetica-Bold')
        metric_style = ParagraphStyle('Metric', parent=styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#059669'), fontName='Helvetica-Bold')
        
        # COVER PAGE
        content.append(Spacer(1, 1.5*inch))
        content.append(Paragraph("📊 PARDOT PERFORMANCE REPORT", title_style))
        content.append(Spacer(1, 0.3*inch))
        content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('Date', parent=styles['Normal'], fontSize=14, alignment=1, textColor=colors.HexColor('#6b7280'))))
        content.append(PageBreak())
        
        # EMAIL CAMPAIGNS SECTION
        if email_stats:
            content.append(Paragraph("📧 EMAIL CAMPAIGNS", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            email_metrics = calculate_email_metrics(email_stats)
            content.append(Paragraph(f"Total Campaigns: {email_metrics['total_campaigns']:,}", metric_style))
            content.append(Paragraph(f"Emails Sent: {email_metrics['total_sent']:,}", metric_style))
            content.append(Paragraph(f"Open Rate: {email_metrics['open_rate']:.1f}%", metric_style))
            content.append(Paragraph(f"Click Rate: {email_metrics['click_rate']:.1f}%", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_email_chart(email_metrics['total_sent'], email_metrics['total_opens'], email_metrics['total_clicks']))
            content.append(PageBreak())
        
        # FORMS SECTION
        if form_stats:
            content.append(Paragraph("📝 FORMS", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            form_metrics = calculate_form_metrics(form_stats)
            content.append(Paragraph(f"Total Forms: {form_metrics['total_forms']:,}", metric_style))
            content.append(Paragraph(f"Form Views: {form_metrics['total_views']:,}", metric_style))
            content.append(Paragraph(f"Submissions: {form_metrics['total_submissions']:,}", metric_style))
            content.append(Paragraph(f"Conversion Rate: {form_metrics['conversion_rate']:.1f}%", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_form_chart(form_metrics['total_views'], form_metrics['total_submissions']))
            content.append(PageBreak())
        
        # LANDING PAGES SECTION
        if landing_page_stats:
            content.append(Paragraph("🚀 LANDING PAGES", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            summary = landing_page_stats.get('summary', {})
            active_count = landing_page_stats.get('active_pages', {}).get('count', 0)
            inactive_count = landing_page_stats.get('inactive_pages', {}).get('count', 0)
            
            content.append(Paragraph(f"Total Pages: {summary.get('total_pages', 0):,}", metric_style))
            content.append(Paragraph(f"Active Pages (3 months): {active_count:,}", metric_style))
            content.append(Paragraph(f"Inactive Pages: {inactive_count:,}", metric_style))
            content.append(Paragraph(f"Total Activities: {summary.get('total_activities', 0):,}", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_landing_chart(active_count, inactive_count))
            content.append(PageBreak())
        
        # PROSPECTS SECTION
        if prospect_health:
            content.append(Paragraph("👥 PROSPECTS", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            prospect_metrics = calculate_prospect_metrics(prospect_health)
            content.append(Paragraph(f"Total Prospects: {prospect_metrics['total_prospects']:,}", metric_style))
            content.append(Paragraph(f"Healthy Records: {prospect_metrics['healthy']:,}", metric_style))
            content.append(Paragraph(f"Issues Found: {prospect_metrics['issues_count']:,}", metric_style))
            content.append(Paragraph(f"Health Score: {prospect_metrics['health_score']:.1f}%", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_prospect_chart(prospect_metrics['healthy'], prospect_metrics['issues_count']))
            content.append(PageBreak())
        
        # ENGAGEMENT PROGRAMS SECTION
        if engagement_programs:
            content.append(Paragraph("🎯 ENGAGEMENT PROGRAMS", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            summary = engagement_programs.get('summary', {})
            content.append(Paragraph(f"Total Programs: {summary.get('total_programs', 0):,}", metric_style))
            content.append(Paragraph(f"Active Programs: {summary.get('active_count', 0):,}", metric_style))
            content.append(Paragraph(f"Paused Programs: {summary.get('paused_count', 0):,}", metric_style))
            content.append(Paragraph(f"Completed Programs: {summary.get('completed_count', 0):,}", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_engagement_chart(summary.get('active_count', 0), summary.get('paused_count', 0), summary.get('completed_count', 0)))
            content.append(PageBreak())
        
        # UTM ANALYSIS SECTION
        if utm_analysis:
            content.append(Paragraph("📊 UTM TRACKING", section_style))
            content.append(Spacer(1, 0.2*inch))
            
            utm_data = utm_analysis.get('utm_analysis', {})
            total_analyzed = utm_data.get('total_prospects_analyzed', 0)
            utm_issues = utm_data.get('prospects_with_utm_issues', 0)
            quality_score = ((total_analyzed - utm_issues) / max(total_analyzed, 1) * 100)
            
            content.append(Paragraph(f"Prospects Analyzed: {total_analyzed:,}", metric_style))
            content.append(Paragraph(f"UTM Issues Found: {utm_issues:,}", metric_style))
            content.append(Paragraph(f"Data Quality Score: {quality_score:.1f}%", metric_style))
            
            content.append(Spacer(1, 0.2*inch))
            content.append(create_fast_utm_chart(total_analyzed - utm_issues, utm_issues))
            content.append(PageBreak())
        
        # RECOMMENDATIONS SECTION
        content.append(Paragraph("💡 RECOMMENDATIONS", section_style))
        content.append(Spacer(1, 0.2*inch))
        
        recommendations = [
            "📧 Implement A/B testing for email subject lines",
            "📝 Optimize form fields to increase conversions", 
            "🏥 Clean up duplicate and inactive prospect records",
            "🚀 Review landing page performance and optimize",
            "📊 Standardize UTM parameter usage",
            "🎯 Restart paused engagement programs"
        ]
        
        for rec in recommendations:
            content.append(Paragraph(rec, ParagraphStyle('Rec', parent=styles['Normal'], fontSize=12, spaceAfter=8, leftIndent=20)))
        
        doc.build(content)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating report: {str(e)}")
        return create_error_pdf(str(e))

# OPTIMIZED HELPER FUNCTIONS FOR FAST PDF GENERATION

def calculate_email_metrics(email_stats):
    """Fast calculation of email metrics"""
    if not email_stats:
        return {'total_campaigns': 0, 'total_sent': 0, 'total_opens': 0, 'total_clicks': 0, 'open_rate': 0, 'click_rate': 0}
    
    # Sample large datasets for performance
    sample_stats = email_stats[:100] if len(email_stats) > 100 else email_stats
    
    total_sent = sum(email.get('stats', {}).get('sent', 0) for email in sample_stats)
    total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in sample_stats)
    total_opens = sum(email.get('stats', {}).get('opens', 0) for email in sample_stats)
    total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in sample_stats)
    
    return {
        'total_campaigns': len(email_stats),
        'total_sent': total_sent,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'open_rate': (total_opens / total_delivered * 100) if total_delivered > 0 else 0,
        'click_rate': (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
    }

def calculate_form_metrics(form_stats):
    """Fast calculation of form metrics"""
    if not form_stats:
        return {'total_forms': 0, 'total_views': 0, 'total_submissions': 0, 'conversion_rate': 0}
    
    # Sample large datasets for performance
    sample_stats = form_stats[:50] if len(form_stats) > 50 else form_stats
    
    total_views = sum(form.get('views', 0) for form in sample_stats)
    total_submissions = sum(form.get('submissions', 0) for form in sample_stats)
    
    return {
        'total_forms': len(form_stats),
        'total_views': total_views,
        'total_submissions': total_submissions,
        'conversion_rate': (total_submissions / total_views * 100) if total_views > 0 else 0
    }

def calculate_prospect_metrics(prospect_health):
    """Fast calculation of prospect metrics"""
    if not prospect_health:
        return {'total_prospects': 0, 'healthy': 0, 'issues_count': 0, 'health_score': 100}
    
    total_prospects = prospect_health.get('total_prospects', 0)
    duplicates = prospect_health.get('duplicates', {}).get('count', 0)
    inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
    missing_fields = prospect_health.get('missing_fields', {}).get('count', 0)
    scoring_issues = prospect_health.get('scoring_issues', {}).get('count', 0)
    
    issues_count = duplicates + inactive + missing_fields + scoring_issues
    healthy = total_prospects - issues_count
    health_score = (healthy / total_prospects * 100) if total_prospects > 0 else 100
    
    return {
        'total_prospects': total_prospects,
        'healthy': healthy,
        'issues_count': issues_count,
        'health_score': health_score
    }

def create_executive_metrics_table(email_stats, form_stats, prospect_health, landing_page_stats):
    """Create executive summary metrics table"""
    email_metrics = calculate_email_metrics(email_stats)
    form_metrics = calculate_form_metrics(form_stats)
    prospect_metrics = calculate_prospect_metrics(prospect_health)
    
    # Create summary table
    summary_data = [
        ['METRIC', 'VALUE', 'STATUS'],
        ['Email Campaigns', f"{email_metrics['total_campaigns']:,}", '📧 Active'],
        ['Email Open Rate', f"{email_metrics['open_rate']:.1f}%", '✅ Good' if email_metrics['open_rate'] > 20 else '⚠️ Review'],
        ['Forms Active', f"{form_metrics['total_forms']:,}", '📝 Deployed'],
        ['Form Conversion', f"{form_metrics['conversion_rate']:.1f}%", '✅ Good' if form_metrics['conversion_rate'] > 15 else '⚠️ Optimize'],
        ['Total Prospects', f"{prospect_metrics['total_prospects']:,}", '👥 Database'],
        ['Database Health', f"{prospect_metrics['health_score']:.1f}%", '✅ Healthy' if prospect_metrics['health_score'] > 70 else '🔴 Critical']
    ]
    
    summary_table = Table(summary_data, colWidths=[2.2*inch, 1.3*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    return summary_table

def create_fast_email_chart(sent, opens, clicks):
    """Create simplified email performance chart"""
    drawing = Drawing(500, 200)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 50
    chart.height = 120
    chart.width = 380
    
    chart.data = [[sent, opens, clicks]]
    chart.categoryAxis.categoryNames = ['Sent', 'Opens', 'Clicks']
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(sent, 1) * 1.1
    chart.valueAxis.labels.fontSize = 9
    
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'Email Performance Metrics', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_fast_form_chart(views, submissions):
    """Create simplified form conversion chart"""
    drawing = Drawing(500, 200)
    
    pie = Pie()
    pie.x = 200
    pie.y = 60
    pie.width = 100
    pie.height = 100
    
    abandoned = views - submissions if views > submissions else 0
    conversion_rate = (submissions / views * 100) if views > 0 else 0
    
    pie.data = [submissions, abandoned]
    pie.labels = [f'Converted\n{submissions:,}\n({conversion_rate:.1f}%)', f'Views Only\n{abandoned:,}']
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices.fontSize = 9
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'Form Conversion Analysis', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_fast_prospect_chart(healthy, issues):
    """Create simplified prospect health chart"""
    drawing = Drawing(500, 200)
    
    pie = Pie()
    pie.x = 200
    pie.y = 60
    pie.width = 100
    pie.height = 100
    
    total = healthy + issues
    health_percentage = (healthy / total * 100) if total > 0 else 100
    
    pie.data = [healthy, issues]
    pie.labels = [f'Healthy\n{healthy:,}\n({health_percentage:.1f}%)', f'Issues\n{issues:,}']
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#ef4444')
    pie.slices.fontSize = 9
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'Database Health Status', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def generate_smart_recommendations(email_metrics, form_metrics, prospect_metrics):
    """Generate intelligent recommendations based on data"""
    recommendations = []
    
    # Email recommendations
    if email_metrics['open_rate'] < 20:
        recommendations.append("📧 Implement A/B testing for email subject lines - potential 15-25% open rate improvement")
    if email_metrics['click_rate'] < 2.5:
        recommendations.append("🎯 Optimize email content and CTAs - current click rate below industry average")
    
    # Form recommendations
    if form_metrics['conversion_rate'] < 15:
        recommendations.append("📝 Reduce form fields to essential information only - can increase conversions by 20-30%")
    if form_metrics['total_forms'] > 0:
        recommendations.append("📊 Implement progressive profiling to gather data over multiple interactions")
    
    # Database recommendations
    if prospect_metrics['health_score'] < 70:
        recommendations.append("🏥 Priority database cleanup - remove duplicates and inactive records immediately")
    if prospect_metrics['issues_count'] > prospect_metrics['total_prospects'] * 0.2:
        recommendations.append("🔧 Implement automated data quality monitoring and validation rules")
    
    # Default recommendations if none triggered
    if not recommendations:
        recommendations = [
            "📈 Continue monitoring performance metrics and maintain current optimization efforts",
            "🎯 Explore advanced segmentation strategies for improved targeting",
            "📊 Consider implementing marketing attribution modeling for better ROI tracking"
        ]
    
    return recommendations

def create_fast_landing_chart(active, inactive):
    """Create landing page status chart"""
    drawing = Drawing(500, 200)
    pie = Pie()
    pie.x = 200
    pie.y = 60
    pie.width = 100
    pie.height = 100
    
    total = active + inactive
    active_pct = (active / total * 100) if total > 0 else 0
    
    pie.data = [active, inactive]
    pie.labels = [f'Active\n{active:,}\n({active_pct:.1f}%)', f'Inactive\n{inactive:,}']
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#ef4444')
    pie.slices.fontSize = 9
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'Landing Page Activity Status', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_fast_engagement_chart(active, paused, completed):
    """Create engagement programs chart"""
    drawing = Drawing(500, 200)
    chart = VerticalBarChart()
    chart.x = 100
    chart.y = 50
    chart.height = 120
    chart.width = 300
    
    chart.data = [[active, paused, completed]]
    chart.categoryAxis.categoryNames = ['Active', 'Paused', 'Completed']
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(active, paused, completed, 1) * 1.1
    chart.valueAxis.labels.fontSize = 9
    
    chart.bars[0].fillColor = colors.HexColor('#8b5cf6')
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'Engagement Program Status', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_fast_utm_chart(clean, issues):
    """Create UTM data quality chart"""
    drawing = Drawing(500, 200)
    pie = Pie()
    pie.x = 200
    pie.y = 60
    pie.width = 100
    pie.height = 100
    
    total = clean + issues
    quality_pct = (clean / total * 100) if total > 0 else 100
    
    pie.data = [clean, issues]
    pie.labels = [f'Clean Data\n{clean:,}\n({quality_pct:.1f}%)', f'Issues\n{issues:,}']
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices.fontSize = 9
    
    from reportlab.graphics.shapes import String
    title = String(250, 175, 'UTM Data Quality Analysis', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    
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

def create_enhanced_email_chart(sent, delivered, opens, clicks):
    """Create enhanced email performance chart with better design"""
    drawing = Drawing(500, 280)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 80
    chart.height = 160
    chart.width = 380
    
    # Enhanced data with gradient colors
    chart.data = [[sent, delivered, opens, clicks]]
    chart.categoryAxis.categoryNames = ['Emails Sent', 'Delivered', 'Opened', 'Clicked']
    chart.categoryAxis.labels.fontSize = 10
    chart.categoryAxis.labels.fontName = 'Helvetica-Bold'
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(sent, delivered, opens, clicks, 1) * 1.2
    chart.valueAxis.labels.fontSize = 9
    chart.valueAxis.labels.fontName = 'Helvetica'
    
    # Enhanced bar styling with gradients
    chart.bars[0].fillColor = colors.HexColor('#1e40af')
    chart.bars.strokeColor = colors.HexColor('#1e3a8a')
    chart.bars.strokeWidth = 1
    
    # Add background grid
    chart.categoryAxis.visibleGrid = 1
    chart.valueAxis.visibleGrid = 1
    chart.categoryAxis.gridStrokeColor = colors.HexColor('#f3f4f6')
    chart.valueAxis.gridStrokeColor = colors.HexColor('#f3f4f6')
    
    from reportlab.graphics.shapes import String, Rect
    
    # Add background
    bg_rect = Rect(0, 0, 500, 280, fillColor=colors.white, strokeColor=colors.HexColor('#e5e7eb'))
    drawing.add(bg_rect)
    
    # Enhanced title with background
    title_bg = Rect(50, 250, 400, 25, fillColor=colors.HexColor('#1f2937'), strokeColor=None)
    drawing.add(title_bg)
    
    title = String(250, 260, 'Email Campaign Performance Metrics', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.white
    
    # Add value labels on bars
    bar_width = 380 / 4
    for i, (label, value) in enumerate(zip(['Sent', 'Delivered', 'Opens', 'Clicks'], [sent, delivered, opens, clicks])):
        x_pos = 60 + (i * bar_width) + (bar_width / 2)
        y_pos = 80 + (value / max(sent, delivered, opens, clicks, 1) * 160) + 10
        
        value_label = String(x_pos, y_pos, f'{value:,}', textAnchor='middle')
        value_label.fontSize = 8
        value_label.fontName = 'Helvetica-Bold'
        value_label.fillColor = colors.HexColor('#1f2937')
        drawing.add(value_label)
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_enhanced_form_chart(views, submissions, abandoned):
    """Create enhanced form conversion chart with better design"""
    drawing = Drawing(500, 280)
    
    # Add background
    from reportlab.graphics.shapes import Rect
    bg_rect = Rect(0, 0, 500, 280, fillColor=colors.white, strokeColor=colors.HexColor('#e5e7eb'))
    drawing.add(bg_rect)
    
    # Enhanced pie chart
    pie = Pie()
    pie.x = 175
    pie.y = 90
    pie.width = 150
    pie.height = 150
    
    # Ensure we have valid data
    if submissions + abandoned == 0:
        submissions = 1
        abandoned = 0
    
    conversion_rate = (submissions / (submissions + abandoned) * 100) if (submissions + abandoned) > 0 else 0
    
    pie.data = [submissions, abandoned]
    pie.labels = [f'Conversions\n{submissions:,} ({conversion_rate:.1f}%)', f'Abandoned\n{abandoned:,} ({100-conversion_rate:.1f}%)']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#059669')
    pie.slices[1].fillColor = colors.HexColor('#dc2626')
    
    # Enhanced styling with dark text for visibility
    pie.slices.fontName = 'Helvetica-Bold'
    pie.slices.fontSize = 9
    pie.slices.fontColor = colors.HexColor('#1f2937')
    
    from reportlab.graphics.shapes import String
    
    # Enhanced title with background
    title_bg = Rect(50, 250, 400, 25, fillColor=colors.HexColor('#059669'), strokeColor=None)
    drawing.add(title_bg)
    
    title = String(250, 260, 'Form Conversion Performance Analysis', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.white
    
    # Add summary statistics
    stats_text = String(250, 60, f'Total Views: {views:,} | Conversion Rate: {conversion_rate:.1f}%', textAnchor='middle')
    stats_text.fontSize = 10
    stats_text.fontName = 'Helvetica-Bold'
    stats_text.fillColor = colors.HexColor('#374151')
    
    drawing.add(pie)
    drawing.add(title)
    drawing.add(stats_text)
    return drawing

def create_enhanced_prospect_chart(healthy, duplicates, inactive, missing_fields, scoring_issues):
    """Create enhanced prospect health chart with better design"""
    drawing = Drawing(500, 280)
    
    # Add background
    from reportlab.graphics.shapes import Rect
    bg_rect = Rect(0, 0, 500, 280, fillColor=colors.white, strokeColor=colors.HexColor('#e5e7eb'))
    drawing.add(bg_rect)
    
    # Enhanced pie chart
    pie = Pie()
    pie.x = 175
    pie.y = 90
    pie.width = 150
    pie.height = 150
    
    # Ensure we have valid data
    total = healthy + duplicates + inactive + missing_fields + scoring_issues
    if total == 0:
        healthy = 1
        total = 1
    
    health_score = (healthy / total * 100) if total > 0 else 100
    
    pie.data = [healthy, duplicates, inactive, missing_fields, scoring_issues]
    pie.labels = [
        f'Healthy\n{healthy:,}\n({healthy/total*100:.1f}%)',
        f'Duplicates\n{duplicates:,}\n({duplicates/total*100:.1f}%)',
        f'Inactive\n{inactive:,}\n({inactive/total*100:.1f}%)',
        f'Missing Fields\n{missing_fields:,}\n({missing_fields/total*100:.1f}%)',
        f'Scoring Issues\n{scoring_issues:,}\n({scoring_issues/total*100:.1f}%)'
    ]
    
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#059669')
    pie.slices[1].fillColor = colors.HexColor('#dc6803')
    pie.slices[2].fillColor = colors.HexColor('#dc2626')
    pie.slices[3].fillColor = colors.HexColor('#7c2d12')
    pie.slices[4].fillColor = colors.HexColor('#ea580c')
    
    # Enhanced styling with dark text for visibility
    pie.slices.fontName = 'Helvetica-Bold'
    pie.slices.fontSize = 8
    pie.slices.fontColor = colors.HexColor('#1f2937')
    
    from reportlab.graphics.shapes import String
    
    # Enhanced title with background
    title_bg = Rect(50, 250, 400, 25, fillColor=colors.HexColor('#dc2626'), strokeColor=None)
    drawing.add(title_bg)
    
    title = String(250, 260, 'Prospect Database Health Analysis', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.white
    
    # Add health score
    health_text = String(250, 60, f'Database Health Score: {health_score:.1f}% | Total Records: {total:,}', textAnchor='middle')
    health_text.fontSize = 10
    health_text.fontName = 'Helvetica-Bold'
    health_text.fillColor = colors.HexColor('#374151')
    
    drawing.add(pie)
    drawing.add(title)
    drawing.add(health_text)
    return drawing

def create_executive_summary_paragraph(email_stats, form_stats, prospect_health, landing_page_stats=None):
    """Create executive summary paragraph with key highlights"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section header
    summary_style = ParagraphStyle('ExecSummary', parent=styles['Heading2'], 
                                 fontSize=18, spaceAfter=16, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("📊 EXECUTIVE SUMMARY", summary_style))
    
    # Calculate key metrics
    total_emails = len(email_stats) if email_stats else 0
    total_forms = len(form_stats) if form_stats else 0
    total_prospects = prospect_health.get('total_prospects', 0) if prospect_health else 0
    
    # Email metrics
    total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats) if email_stats else 0
    total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats) if email_stats else 0
    total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats) if email_stats else 0
    total_bounces = sum(email.get('stats', {}).get('bounces', 0) for email in email_stats) if email_stats else 0
    
    open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
    bounce_rate = (total_bounces / total_delivered * 100) if total_delivered > 0 else 0
    
    # Form metrics
    total_form_views = sum(form.get('views', 0) for form in form_stats) if form_stats else 0
    total_form_submissions = sum(form.get('submissions', 0) for form in form_stats) if form_stats else 0
    form_conversion_rate = (total_form_submissions / total_form_views * 100) if total_form_views > 0 else 0
    
    # Prospect issues
    duplicates = prospect_health.get('duplicates', {}).get('count', 0) if prospect_health else 0
    inactive = prospect_health.get('inactive_prospects', {}).get('count', 0) if prospect_health else 0
    missing_fields = prospect_health.get('missing_fields', {}).get('count', 0) if prospect_health else 0
    
    # Landing page issues
    field_issues = len(landing_page_stats.get('field_mapping_issues', [])) if landing_page_stats else 0
    
    # Create executive summary paragraph
    summary_text = f"""Your Pardot platform currently manages <b>{total_emails:,} email campaigns</b>, <b>{total_forms:,} forms</b>, and <b>{total_prospects:,} prospects</b>. 
    
    <b>Key Performance Metrics:</b> Email campaigns achieve a <b>{open_rate:.1f}% open rate</b> and <b>{click_rate:.1f}% click-through rate</b> with a <b>{bounce_rate:.1f}% bounce rate</b>. Forms maintain a <b>{form_conversion_rate:.1f}% conversion rate</b> across <b>{total_form_views:,} total views</b>.
    
    <b>Top 3 Critical Issues Identified:</b>
    • <b>Database Quality:</b> {duplicates:,} duplicate prospects and {inactive:,} inactive records requiring cleanup
    • <b>Data Completeness:</b> {missing_fields:,} prospects missing critical profile information
    • <b>Configuration Issues:</b> {field_issues:,} landing pages with field mapping problems affecting lead capture
    
    This audit reveals significant opportunities for optimization across email engagement, form conversion, and database health management."""
    
    summary_paragraph_style = ParagraphStyle('SummaryText', parent=styles['Normal'], 
                                           fontSize=11, spaceAfter=16, 
                                           textColor=colors.HexColor('#374151'), 
                                           leading=16, alignment=0)
    
    content.append(Paragraph(summary_text, summary_paragraph_style))
    
    return content

def create_critical_issues_section(email_stats, form_stats, prospect_health, landing_page_stats=None):
    """Create critical issues section with urgent findings"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section header
    critical_style = ParagraphStyle('CriticalIssues', parent=styles['Heading2'], 
                                  fontSize=18, spaceAfter=16, 
                                  textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("⚠️ CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION", critical_style))
    
    # Identify critical issues
    critical_issues = []
    
    # Email issues
    if email_stats:
        total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
        total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats)
        click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
        
        if click_rate == 0:
            critical_issues.append("• 📧 **0% Click-Through Rate**: No email engagement indicates content relevance issues")
        elif click_rate < 1:
            critical_issues.append(f"• 📧 **Low CTR ({click_rate:.1f}%)**: Email content failing to drive action")
    
    # Form issues
    if form_stats:
        zero_conversion_forms = [f for f in form_stats if f.get('submissions', 0) == 0 and f.get('views', 0) > 0]
        if zero_conversion_forms:
            critical_issues.append(f"• 📝 **{len(zero_conversion_forms)} Forms with 0% Conversion**: Forms receiving traffic but no submissions")
    
    # Prospect issues
    if prospect_health:
        total_prospects = prospect_health.get('total_prospects', 0)
        duplicates = prospect_health.get('duplicates', {}).get('count', 0)
        inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
        
        if duplicates > total_prospects * 0.15:
            critical_issues.append(f"• 👥 **High Duplicate Rate ({duplicates:,} records)**: {(duplicates/total_prospects*100):.1f}% of database contains duplicates")
        
        if inactive > total_prospects * 0.30:
            critical_issues.append(f"• 📊 **Inactive Prospect Crisis ({inactive:,} records)**: {(inactive/total_prospects*100):.1f}% of database inactive for 90+ days")
    
    # Landing page issues
    if landing_page_stats:
        field_issues = landing_page_stats.get('field_mapping_issues', [])
        critical_field_issues = [i for i in field_issues if i.get('severity') == 'critical']
        
        if critical_field_issues:
            critical_issues.append(f"• 🚀 **Field Mapping Failures ({len(critical_field_issues)} critical)**: Landing pages not capturing lead data properly")
    
    # Add default issues if none found
    if not critical_issues:
        critical_issues = [
            "• 📈 **Performance Optimization Needed**: Review engagement metrics for improvement opportunities",
            "• 📊 **Database Maintenance Required**: Regular cleanup and optimization recommended",
            "• ⚙️ **Configuration Review**: Audit system settings for optimal performance"
        ]
    
    # Display critical issues
    issue_style = ParagraphStyle('IssueText', parent=styles['Normal'], 
                               fontSize=11, spaceAfter=12, 
                               textColor=colors.HexColor('#dc2626'), 
                               leading=16, leftIndent=20)
    
    for issue in critical_issues[:5]:  # Limit to top 5 issues
        content.append(Paragraph(issue, issue_style))
    
    return content

def create_detailed_email_section(email_stats):
    """Create detailed email analytics section with comprehensive analysis"""
    styles = getSampleStyleSheet()
    content = []
    
    section_style = ParagraphStyle('EmailSection', parent=styles['Heading2'], 
                                 fontSize=20, spaceAfter=16, 
                                 textColor=colors.HexColor('#3b82f6'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("📧 2. EMAIL CAMPAIGN ANALYTICS", section_style))
    
    if not email_stats:
        content.append(Paragraph("No email data available for analysis.", styles['Normal']))
        return content
    
    # Section overview
    overview_style = ParagraphStyle('EmailOverview', parent=styles['Normal'], 
                                  fontSize=11, spaceAfter=16, 
                                  textColor=colors.HexColor('#374151'), 
                                  leading=16, alignment=0)
    
    content.append(Paragraph(
        f"This section analyzes the performance of {len(email_stats)} email campaigns in your Pardot system. "
        "Email marketing remains one of the highest ROI marketing channels, with an average return of $42 for every $1 spent. "
        "Our analysis examines delivery rates, engagement metrics, and campaign effectiveness to identify optimization opportunities.", 
        overview_style
    ))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Calculate comprehensive email metrics
    total_sent = sum(email.get('stats', {}).get('sent', 0) for email in email_stats)
    total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
    total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats)
    total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats)
    total_bounces = sum(email.get('stats', {}).get('bounces', 0) for email in email_stats)
    total_unsubscribes = sum(email.get('stats', {}).get('unsubscribes', 0) for email in email_stats)
    
    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
    bounce_rate = (total_bounces / total_sent * 100) if total_sent > 0 else 0
    unsubscribe_rate = (total_unsubscribes / total_delivered * 100) if total_delivered > 0 else 0
    
    # 2.1 Campaign Performance Overview
    content.append(Paragraph("📈 2.1 Campaign Performance Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    performance_data = [
        ['METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Total Campaigns', f"{len(email_stats):,}", 'N/A', '🟢 Active'],
        ['Emails Sent', f"{total_sent:,}", 'N/A', '🟢 Volume High'],
        ['Delivery Rate', f"{delivery_rate:.1f}%", '95%+', 
         '🟢 Excellent' if delivery_rate >= 95 else '🟡 Good' if delivery_rate >= 90 else '🔴 Needs Improvement'],
        ['Open Rate', f"{open_rate:.1f}%", '21-25%', 
         '🟢 Excellent' if open_rate >= 25 else '🟡 Average' if open_rate >= 20 else '🔴 Below Average'],
        ['Click Rate', f"{click_rate:.1f}%", '2.5-4%', 
         '🟢 Excellent' if click_rate >= 4 else '🟡 Average' if click_rate >= 2.5 else '🔴 Below Average'],
        ['Bounce Rate', f"{bounce_rate:.1f}%", '<2%', 
         '🟢 Excellent' if bounce_rate <= 2 else '🟡 Acceptable' if bounce_rate <= 5 else '🔴 High'],
        ['Unsubscribe Rate', f"{unsubscribe_rate:.1f}%", '<0.5%', 
         '🟢 Excellent' if unsubscribe_rate <= 0.5 else '🟡 Acceptable' if unsubscribe_rate <= 1 else '🔴 High']
    ]
    
    performance_table = Table(performance_data, colWidths=[1.8*inch, 0.9*inch, 1*inch, 1.3*inch])
    performance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(performance_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 2.2 Top Performing Campaigns
    content.append(Paragraph("🏆 2.2 Top Performing Campaigns", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    # Sort campaigns by engagement (opens + clicks)
    sorted_campaigns = sorted(email_stats, 
                            key=lambda x: x.get('stats', {}).get('opens', 0) + x.get('stats', {}).get('clicks', 0), 
                            reverse=True)[:10]
    
    top_campaigns_data = [['CAMPAIGN NAME', 'SENT', 'OPENS', 'CLICKS', 'OPEN %', 'CTR %']]
    
    for campaign in sorted_campaigns:
        stats = campaign.get('stats', {})
        name = campaign.get('name', 'Unknown')[:20] + '...' if len(campaign.get('name', '')) > 20 else campaign.get('name', 'Unknown')
        sent = stats.get('sent', 0)
        delivered = stats.get('delivered', 0)
        opens = stats.get('opens', 0)
        clicks = stats.get('clicks', 0)
        
        camp_open_rate = (opens / delivered * 100) if delivered > 0 else 0
        camp_click_rate = (clicks / delivered * 100) if delivered > 0 else 0
        
        top_campaigns_data.append([
            name,
            f"{sent:,}",
            f"{opens:,}",
            f"{clicks:,}",
            f"{camp_open_rate:.1f}%",
            f"{camp_click_rate:.1f}%"
        ])
    
    campaigns_table = Table(top_campaigns_data, colWidths=[1.9*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch])
    campaigns_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    
    content.append(campaigns_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 2.3 Engagement Analysis Chart
    content.append(Paragraph("📉 2.3 Engagement Metrics Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    content.append(create_detailed_email_chart(total_sent, total_delivered, total_opens, total_clicks, total_bounces))
    
    # 2.4 Key Insights and Recommendations
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("🔍 2.4 Email Marketing Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    insights = [
        f"• Campaign Volume: {len(email_stats)} campaigns sent {total_sent:,} emails with {delivery_rate:.1f}% delivery success",
        f"• Engagement Performance: {open_rate:.1f}% open rate {'exceeds' if open_rate > 21 else 'meets' if open_rate >= 18 else 'falls below'} industry standards",
        f"• Click-through Effectiveness: {click_rate:.1f}% CTR indicates {'strong' if click_rate > 3 else 'moderate' if click_rate >= 2 else 'weak'} content relevance",
        f"• List Health: {bounce_rate:.1f}% bounce rate {'indicates healthy' if bounce_rate < 3 else 'suggests list cleanup needed for'} subscriber database",
        f"• Subscriber Retention: {unsubscribe_rate:.1f}% unsubscribe rate {'shows good' if unsubscribe_rate < 0.5 else 'indicates potential'} content-audience alignment"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_detailed_email_chart(sent, delivered, opens, clicks, bounces):
    """Create detailed email performance chart with proper spacing"""
    drawing = Drawing(500, 280)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 70  # Increased bottom margin
    chart.height = 150
    chart.width = 400
    
    # Prepare data
    chart.data = [[sent, delivered, opens, clicks, bounces]]
    chart.categoryAxis.categoryNames = ['Sent', 'Delivered', 'Opens', 'Clicks', 'Bounces']
    chart.categoryAxis.labels.fontSize = 9
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(sent, 1) * 1.2  # Extra space at top
    chart.valueAxis.labels.fontSize = 8
    
    # Color bars with gradient effect
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    
    # Add title with more space
    from reportlab.graphics.shapes import String
    title = String(250, 240, 'Email Campaign Performance Metrics', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_detailed_form_section(form_stats):
    """Create detailed form analytics section with comprehensive analysis"""
    styles = getSampleStyleSheet()
    content = []
    
    section_style = ParagraphStyle('FormSection', parent=styles['Heading2'], 
                                 fontSize=20, spaceAfter=16, 
                                 textColor=colors.HexColor('#10b981'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("📝 3. FORM PERFORMANCE ANALYTICS", section_style))
    
    if not form_stats:
        content.append(Paragraph("No form data available for analysis.", styles['Normal']))
        return content
    
    # Section overview
    overview_style = ParagraphStyle('FormOverview', parent=styles['Normal'], 
                                  fontSize=11, spaceAfter=16, 
                                  textColor=colors.HexColor('#374151'), 
                                  leading=16, alignment=0)
    
    content.append(Paragraph(
        f"This section provides a comprehensive analysis of {len(form_stats)} marketing forms deployed across your Pardot platform. "
        "Forms are critical conversion points in the customer journey, serving as the primary mechanism for lead capture and qualification. "
        "Our analysis examines form performance, user engagement patterns, and conversion optimization opportunities.", 
        overview_style
    ))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Calculate comprehensive form metrics
    total_views = sum(form.get('views', 0) for form in form_stats)
    total_submissions = sum(form.get('submissions', 0) for form in form_stats)
    total_unique_views = sum(form.get('unique_views', 0) for form in form_stats)
    total_unique_submissions = sum(form.get('unique_submissions', 0) for form in form_stats)
    total_conversions = sum(form.get('conversions', 0) for form in form_stats)
    total_clicks = sum(form.get('clicks', 0) for form in form_stats)
    
    overall_conversion_rate = (total_submissions / total_views * 100) if total_views > 0 else 0
    unique_conversion_rate = (total_unique_submissions / total_unique_views * 100) if total_unique_views > 0 else 0
    qualified_conversion_rate = (total_conversions / total_submissions * 100) if total_submissions > 0 else 0
    
    # 3.1 Form Conversion Analysis
    content.append(Paragraph("🎯 3.1 Form Conversion Analysis", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    conversion_data = [
        ['CONVERSION METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Total Forms Active', f"{len(form_stats):,}", 'N/A', '🟢 Deployed'],
        ['Total Form Views', f"{total_views:,}", 'N/A', '🟢 High Traffic'],
        ['Total Submissions', f"{total_submissions:,}", 'N/A', '🟢 Active Conversion'],
        ['Overall Conversion Rate', f"{overall_conversion_rate:.1f}%", '15-25%', 
         '🟢 Excellent' if overall_conversion_rate >= 25 else '🟡 Good' if overall_conversion_rate >= 15 else '🔴 Needs Improvement'],
        ['Unique Visitor Conversion', f"{unique_conversion_rate:.1f}%", '10-20%', 
         '🟢 Excellent' if unique_conversion_rate >= 20 else '🟡 Good' if unique_conversion_rate >= 10 else '🔴 Below Average'],
        ['Lead Qualification Rate', f"{qualified_conversion_rate:.1f}%", '60-80%', 
         '🟢 Excellent' if qualified_conversion_rate >= 80 else '🟡 Good' if qualified_conversion_rate >= 60 else '🔴 Needs Review']
    ]
    
    conversion_table = Table(conversion_data, colWidths=[2*inch, 0.9*inch, 1*inch, 1.1*inch])
    conversion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#d1fae5')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(conversion_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 3.2 Top Performing Forms
    content.append(Paragraph("🏆 3.2 Top Performing Forms", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    # Sort forms by conversion rate
    sorted_forms = sorted([f for f in form_stats if f.get('views', 0) > 0], 
                         key=lambda x: (x.get('submissions', 0) / x.get('views', 1) * 100), 
                         reverse=True)[:10]
    
    top_forms_data = [['FORM NAME', 'VIEWS', 'SUBMITS', 'CONVERTS', 'CONV %', 'QUAL %']]
    
    for form in sorted_forms:
        name = form.get('name', 'Unknown')[:15] + '...' if len(form.get('name', '')) > 15 else form.get('name', 'Unknown')
        views = form.get('views', 0)
        submissions = form.get('submissions', 0)
        conversions = form.get('conversions', 0)
        
        conv_rate = (submissions / views * 100) if views > 0 else 0
        qual_rate = (conversions / submissions * 100) if submissions > 0 else 0
        
        top_forms_data.append([
            name,
            f"{views:,}",
            f"{submissions:,}",
            f"{conversions:,}",
            f"{conv_rate:.1f}%",
            f"{qual_rate:.1f}%"
        ])
    
    forms_table = Table(top_forms_data, colWidths=[1.7*inch, 0.65*inch, 0.7*inch, 0.7*inch, 0.65*inch, 0.65*inch])
    forms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    
    content.append(forms_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 3.3 Form Performance Visualization
    content.append(Paragraph("📉 3.3 Form Performance Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    content.append(create_detailed_form_chart(total_views, total_submissions, total_conversions, total_clicks))
    
    # 3.4 Form Optimization Insights
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("🔍 3.4 Form Optimization Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    # Calculate additional insights
    avg_views_per_form = total_views / len(form_stats) if form_stats else 0
    avg_submissions_per_form = total_submissions / len(form_stats) if form_stats else 0
    high_performing_forms = len([f for f in form_stats if (f.get('submissions', 0) / max(f.get('views', 1), 1) * 100) > 20])
    
    insights = [
        f"• Form Portfolio: {len(form_stats)} active forms generating {total_views:,} total views and {total_submissions:,} submissions",
        f"• Conversion Performance: {overall_conversion_rate:.1f}% overall conversion rate {'exceeds' if overall_conversion_rate > 20 else 'meets' if overall_conversion_rate >= 15 else 'falls below'} industry benchmarks",
        f"• Form Efficiency: Average {avg_views_per_form:.0f} views and {avg_submissions_per_form:.0f} submissions per form",
        f"• High Performers: {high_performing_forms} forms ({high_performing_forms/len(form_stats)*100:.1f}%) achieve >20% conversion rates",
        f"• Lead Quality: {qualified_conversion_rate:.1f}% of submissions convert to qualified prospects",
        f"• User Engagement: {total_clicks:,} total form interactions indicate {'strong' if total_clicks > total_views else 'moderate'} user engagement"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_detailed_form_chart(views, submissions, conversions, clicks):
    """Create detailed form performance chart with proper spacing"""
    drawing = Drawing(500, 280)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 70  # Increased bottom margin
    chart.height = 150
    chart.width = 400
    
    # Prepare data
    chart.data = [[views, submissions, conversions, clicks]]
    chart.categoryAxis.categoryNames = ['Views', 'Submissions', 'Conversions', 'Clicks']
    chart.categoryAxis.labels.fontSize = 9
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(views, 1) * 1.2  # Extra space at top
    chart.valueAxis.labels.fontSize = 8
    
    # Color bars
    chart.bars[0].fillColor = colors.HexColor('#10b981')
    
    # Add title with more space
    from reportlab.graphics.shapes import String
    title = String(250, 240, 'Form Engagement and Conversion Metrics', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_detailed_prospect_section(prospect_health):
    """Create detailed prospect health section with comprehensive analysis"""
    styles = getSampleStyleSheet()
    content = []
    
    section_style = ParagraphStyle('ProspectSection', parent=styles['Heading2'], 
                                 fontSize=20, spaceAfter=16, 
                                 textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("🏥 4. PROSPECT DATABASE HEALTH", section_style))
    
    if not prospect_health:
        content.append(Paragraph("No prospect data available for analysis.", styles['Normal']))
        return content
    
    # Section overview
    overview_style = ParagraphStyle('ProspectOverview', parent=styles['Normal'], 
                                  fontSize=11, spaceAfter=16, 
                                  textColor=colors.HexColor('#374151'), 
                                  leading=16, alignment=0)
    
    total_prospects = prospect_health.get('total_prospects', 0)
    content.append(Paragraph(
        f"This section provides a comprehensive health assessment of your {total_prospects:,} prospect database records. "
        "Database quality directly impacts marketing effectiveness, sales productivity, and customer experience. "
        "Our analysis identifies data quality issues, segmentation opportunities, and database optimization strategies "
        "to maximize your marketing automation ROI.", 
        overview_style
    ))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Calculate comprehensive prospect metrics
    duplicates = prospect_health.get('duplicates', {}).get('count', 0)
    inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
    missing_fields = prospect_health.get('missing_fields', {}).get('count', 0)
    scoring_issues = prospect_health.get('scoring_issues', {}).get('count', 0)
    grading_analysis = prospect_health.get('grading_analysis', {})
    
    healthy_prospects = total_prospects - duplicates - inactive - missing_fields - scoring_issues
    database_health_score = (healthy_prospects / total_prospects * 100) if total_prospects > 0 else 0
    
    # 4.1 Data Quality Assessment
    content.append(Paragraph("🔍 4.1 Data Quality Assessment", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    quality_data = [
        ['DATA QUALITY METRIC', 'COUNT', '%', 'IMPACT'],
        ['Total Prospect Records', f"{total_prospects:,}", '100%', '🟢 Baseline'],
        ['Healthy Records', f"{healthy_prospects:,}", f"{database_health_score:.1f}%", 
         '🟢 Excellent' if database_health_score >= 85 else '🟡 Good' if database_health_score >= 70 else '🔴 Critical'],
        ['Duplicate Records', f"{duplicates:,}", f"{(duplicates/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '🟢 Low' if duplicates/total_prospects < 0.05 else '🟡 Medium' if duplicates/total_prospects < 0.15 else '🔴 High'],
        ['Inactive Prospects (90+ days)', f"{inactive:,}", f"{(inactive/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '🟢 Low' if inactive/total_prospects < 0.20 else '🟡 Medium' if inactive/total_prospects < 0.40 else '🔴 High'],
        ['Incomplete Profiles', f"{missing_fields:,}", f"{(missing_fields/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '🟢 Low' if missing_fields/total_prospects < 0.10 else '🟡 Medium' if missing_fields/total_prospects < 0.25 else '🔴 High'],
        ['Scoring Inconsistencies', f"{scoring_issues:,}", f"{(scoring_issues/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '🟢 Low' if scoring_issues/total_prospects < 0.05 else '🟡 Medium' if scoring_issues/total_prospects < 0.15 else '🔴 High']
    ]
    
    quality_table = Table(quality_data, colWidths=[2*inch, 0.9*inch, 0.8*inch, 1.3*inch])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(quality_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 4.2 Prospect Grading Analysis
    content.append(Paragraph("🎯 4.2 Prospect Grading and Scoring Analysis", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    graded_prospects = grading_analysis.get('graded_prospects', 0)
    ungraded_prospects = grading_analysis.get('ungraded_prospects', 0)
    grading_coverage = grading_analysis.get('grading_coverage', 0)
    grade_distribution = grading_analysis.get('grade_distribution', {})
    
    grading_data = [
        ['GRADING METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Grading Coverage', f"{grading_coverage:.1f}%", '80%+', 
         '🟢 Excellent' if grading_coverage >= 80 else '🟡 Good' if grading_coverage >= 60 else '🔴 Needs Improvement'],
        ['Graded Prospects', f"{graded_prospects:,}", 'N/A', '🟢 Tracked'],
        ['Ungraded Prospects', f"{ungraded_prospects:,}", '<20%', 
         '🟢 Low' if ungraded_prospects/total_prospects < 0.20 else '🟡 Medium' if ungraded_prospects/total_prospects < 0.40 else '🔴 High'],
        ['Grade Categories', f"{len(grade_distribution)}", '4-6', 
         '🟢 Optimal' if 4 <= len(grade_distribution) <= 6 else '🟡 Acceptable']
    ]
    
    grading_table = Table(grading_data, colWidths=[1.9*inch, 1.1*inch, 1*inch, 1*inch])
    grading_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c2d12')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef7ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(grading_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 4.3 Database Health Visualization
    content.append(Paragraph("📉 4.3 Database Health Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    content.append(create_detailed_prospect_chart(healthy_prospects, duplicates, inactive, missing_fields, scoring_issues))
    
    # 4.4 Database Optimization Insights
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("🔍 4.4 Database Optimization Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    insights = [
        f"• Database Scale: {total_prospects:,} total prospects with {database_health_score:.1f}% overall health score",
        f"• Data Quality Issues: {duplicates + inactive + missing_fields + scoring_issues:,} records ({((duplicates + inactive + missing_fields + scoring_issues)/total_prospects*100):.1f}%) require attention",
        f"• Duplicate Management: {duplicates:,} duplicate records impact data accuracy and campaign effectiveness",
        f"• Engagement Health: {inactive:,} prospects inactive for 90+ days may need re-engagement campaigns",
        f"• Profile Completeness: {missing_fields:,} prospects missing critical fields limit segmentation capabilities",
        f"• Scoring Accuracy: {scoring_issues:,} prospects show scoring inconsistencies requiring model review",
        f"• Grading Implementation: {grading_coverage:.1f}% coverage {'meets' if grading_coverage >= 70 else 'falls below'} best practice standards"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_detailed_prospect_chart(healthy, duplicates, inactive, missing_fields, scoring_issues):
    """Create detailed prospect health chart with proper spacing"""
    drawing = Drawing(500, 280)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 70  # Increased bottom margin
    chart.height = 150
    chart.width = 400
    
    # Prepare data
    chart.data = [[healthy, duplicates, inactive, missing_fields, scoring_issues]]
    chart.categoryAxis.categoryNames = ['Healthy', 'Duplicates', 'Inactive', 'Missing Fields', 'Scoring Issues']
    chart.categoryAxis.labels.fontSize = 8
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(healthy, duplicates, inactive, missing_fields, scoring_issues, 1) * 1.2  # Extra space at top
    chart.valueAxis.labels.fontSize = 8
    
    # Color bars
    chart.bars[0].fillColor = colors.HexColor('#dc2626')
    
    # Add title with more space
    from reportlab.graphics.shapes import String
    title = String(250, 240, 'Prospect Database Health Distribution', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_detailed_landing_page_section(landing_page_stats):
    """Create detailed landing page analytics section"""
    styles = getSampleStyleSheet()
    content = []
    
    section_style = ParagraphStyle('LandingPageSection', parent=styles['Heading2'], 
                                 fontSize=20, spaceAfter=16, 
                                 textColor=colors.HexColor('#f59e0b'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("🚀 5. LANDING PAGE ANALYTICS", section_style))
    
    if not landing_page_stats:
        content.append(Paragraph("No landing page data available for analysis.", styles['Normal']))
        return content
    
    # Section overview
    overview_style = ParagraphStyle('LandingPageOverview', parent=styles['Normal'], 
                                  fontSize=11, spaceAfter=16, 
                                  textColor=colors.HexColor('#374151'), 
                                  leading=16, alignment=0)
    
    total_pages = landing_page_stats.get('total_landing_pages', 0)
    active_pages = len(landing_page_stats.get('active_forms', []))
    inactive_pages = len(landing_page_stats.get('inactive_forms', []))
    field_issues = len(landing_page_stats.get('field_mapping_issues', []))
    
    content.append(Paragraph(
        f"This section analyzes {total_pages} landing pages in your Pardot system, examining page performance, "
        f"field mapping configurations, and conversion optimization opportunities. Landing pages serve as critical "
        f"conversion points in your marketing funnel, and proper configuration is essential for lead capture effectiveness.", 
        overview_style
    ))
    
    content.append(Spacer(1, 0.2*inch))
    
    # 5.1 Page Performance Overview
    content.append(Paragraph("📊 5.1 Page Performance Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    performance_data = [
        ['LANDING PAGE METRIC', 'VALUE', 'STATUS'],
        ['Total Landing Pages', f"{total_pages:,}", '🟢 Active'],
        ['Active Pages (30 days)', f"{active_pages:,}", f"🟢 {(active_pages/total_pages*100):.1f}%" if total_pages > 0 else '0%'],
        ['Inactive Pages', f"{inactive_pages:,}", f"🟡 {(inactive_pages/total_pages*100):.1f}%" if total_pages > 0 else '0%'],
        ['Field Mapping Issues', f"{field_issues:,}", '🔴 Critical' if field_issues > total_pages * 0.2 else '🟡 Medium' if field_issues > 0 else '🟢 Clean']
    ]
    
    performance_table = Table(performance_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch])
    performance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(performance_table)
    content.append(Spacer(1, 0.3*inch))
    
    # 5.2 Field Mapping Issues Analysis
    if field_issues > 0:
        content.append(Paragraph("⚠️ 5.2 Field Mapping Issues Analysis", 
                               ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
        
        # Categorize issues by severity
        issues = landing_page_stats.get('field_mapping_issues', [])
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        high_issues = [i for i in issues if i.get('severity') == 'high']
        medium_issues = [i for i in issues if i.get('severity') == 'medium']
        
        issues_data = [
            ['ISSUE SEVERITY', 'COUNT', 'IMPACT'],
            ['Critical Issues', f"{len(critical_issues):,}", '🔴 Immediate Action Required'],
            ['High Priority Issues', f"{len(high_issues):,}", '🟡 Address Soon'],
            ['Medium Priority Issues', f"{len(medium_issues):,}", '🟠 Plan Resolution']
        ]
        
        issues_table = Table(issues_data, colWidths=[2*inch, 1*inch, 2*inch])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(issues_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Top issues list
        content.append(Paragraph("🔍 Critical Issues Requiring Immediate Attention:", 
                               ParagraphStyle('IssuesHeader', parent=styles['Normal'], fontSize=11, spaceAfter=8, fontName='Helvetica-Bold')))
        
        for issue in critical_issues[:5]:  # Show top 5 critical issues
            content.append(Paragraph(f"• {issue.get('field_name', 'Unknown')}: {issue.get('issue', 'No description')}", 
                                   ParagraphStyle('Issue', parent=styles['Normal'], fontSize=9, spaceAfter=4, leftIndent=20)))
    
    return content

def create_recommendations_section(email_stats, form_stats, prospect_health, landing_page_stats=None):
    """Create strategic recommendations section"""
    styles = getSampleStyleSheet()
    content = []
    
    section_style = ParagraphStyle('RecommendationsSection', parent=styles['Heading2'], 
                                 fontSize=20, spaceAfter=16, 
                                 textColor=colors.HexColor('#7c3aed'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("💡 6. STRATEGIC RECOMMENDATIONS", section_style))
    
    # Section overview
    overview_style = ParagraphStyle('RecommendationsOverview', parent=styles['Normal'], 
                                  fontSize=11, spaceAfter=20, 
                                  textColor=colors.HexColor('#374151'), 
                                  leading=16, alignment=0)
    
    content.append(Paragraph(
        "Based on our comprehensive analysis of your Pardot platform performance, we have identified key optimization "
        "opportunities across email marketing, form conversion, and database management. These strategic recommendations "
        "are prioritized by potential impact and implementation complexity to maximize your marketing automation ROI.", 
        overview_style
    ))
    
    # 5.1 Email Marketing Optimization
    content.append(Paragraph("📧 5.1 Email Marketing Optimization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    email_recommendations = [
        "• Subject Line Testing: Implement A/B testing for subject lines to improve open rates by 15-25%",
        "• Send Time Optimization: Analyze recipient time zones and engagement patterns for optimal delivery timing",
        "• List Segmentation: Create targeted segments based on engagement history and demographic data",
        "• Mobile Optimization: Ensure all email templates are mobile-responsive for 60%+ mobile opens",
        "• Personalization Strategy: Implement dynamic content based on prospect behavior and preferences"
    ]
    
    for rec in email_recommendations:
        content.append(Paragraph(rec, ParagraphStyle('Recommendation', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    content.append(Spacer(1, 0.2*inch))
    
    # 5.2 Form Conversion Improvement
    content.append(Paragraph("📝 5.2 Form Conversion Improvement", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    form_recommendations = [
        "• Form Field Optimization: Reduce form fields to essential information only to increase conversion rates",
        "• Progressive Profiling: Implement progressive profiling to gather additional data over time",
        "• Social Proof Integration: Add testimonials and trust indicators near form submission buttons",
        "• Multi-Step Forms: Consider breaking long forms into multiple steps to reduce abandonment",
        "• Thank You Page Optimization: Create compelling thank you pages with next-step calls-to-action"
    ]
    
    for rec in form_recommendations:
        content.append(Paragraph(rec, ParagraphStyle('Recommendation', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    content.append(Spacer(1, 0.2*inch))
    
    # 5.3 Landing Page Optimization (if data available)
    if landing_page_stats:
        content.append(Paragraph("🚀 5.3 Landing Page Optimization", 
                               ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
        
        landing_recommendations = [
            "• Field Mapping Audit: Review and fix CRM field connections to ensure proper lead data capture",
            "• Form Integration: Ensure all landing pages have properly configured forms for lead generation",
            "• URL Configuration: Verify all pages have accessible URLs and proper vanity URL setup",
            "• Mobile Responsiveness: Test landing page performance across all device types",
            "• Conversion Tracking: Implement proper analytics to measure page performance and ROI"
        ]
        
        for rec in landing_recommendations:
            content.append(Paragraph(rec, ParagraphStyle('Recommendation', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
        
        content.append(Spacer(1, 0.2*inch))
    
    # 5.4 Database Management Strategy
    content.append(Paragraph("🏥 5.4 Database Management Strategy", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    database_recommendations = [
        "• Duplicate Cleanup: Implement automated duplicate detection and merging processes",
        "• Re-engagement Campaigns: Create targeted campaigns for inactive prospects before removal",
        "• Data Enrichment: Use third-party data sources to complete missing prospect information",
        "• Scoring Model Review: Audit and optimize lead scoring criteria based on conversion data",
        "• Grading System Enhancement: Expand grading coverage to improve lead qualification accuracy"
    ]
    
    for rec in database_recommendations:
        content.append(Paragraph(rec, ParagraphStyle('Recommendation', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Implementation Priority Matrix
    content.append(Paragraph("🎯 Implementation Priority Matrix", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1f2937'))))
    
    priority_data = [
        ['RECOMMENDATION', 'IMPACT', 'EFFORT', 'PRIORITY'],
        ['Email Subject Line Testing', 'High', 'Low', '🔴 Immediate'],
        ['Form Field Optimization', 'High', 'Medium', '🟡 Short-term'],
        ['Database Duplicate Cleanup', 'Medium', 'High', '🟡 Short-term'],
        ['Mobile Email Optimization', 'High', 'Medium', '🔴 Immediate'],
        ['Lead Scoring Model Review', 'Medium', 'High', '🟠 Long-term']
    ]
    
    priority_table = Table(priority_data, colWidths=[2.1*inch, 0.8*inch, 0.8*inch, 1.3*inch])
    priority_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    content.append(priority_table)
    
    return content

def create_performance_overview_chart(email_stats, form_stats, prospect_health):
    """Create overview performance bar chart with proper spacing"""
    drawing = Drawing(500, 230)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50  # Increased bottom margin
    chart.height = 140
    chart.width = 400
    
    # Prepare data
    email_count = len(email_stats) if email_stats else 0
    form_count = len(form_stats) if form_stats else 0
    prospect_count = prospect_health.get('total_prospects', 0) if prospect_health else 0
    
    chart.data = [[email_count, form_count, prospect_count]]
    chart.categoryAxis.categoryNames = ['Email Campaigns', 'Forms', 'Prospects']
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(email_count, form_count, prospect_count, 1) * 1.2  # Extra space at top
    chart.valueAxis.labels.fontSize = 9
    
    # Color bars
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    
    # Add title with more space
    from reportlab.graphics.shapes import String
    title = String(250, 200, 'Platform Overview - Total Counts', textAnchor='middle')
    title.fontSize = 12
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_email_performance_pie_chart(opens, clicks, delivered):
    """Create email performance pie chart"""
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 100
    pie.height = 100
    
    # Calculate data
    no_engagement = delivered - opens - clicks if delivered > opens + clicks else 0
    
    pie.data = [opens, clicks, no_engagement]
    pie.labels = ['Opens', 'Clicks', 'No Engagement']
    pie.slices.strokeWidth = 0.5
    pie.slices[0].fillColor = colors.HexColor('#3b82f6')
    pie.slices[1].fillColor = colors.HexColor('#10b981')
    pie.slices[2].fillColor = colors.HexColor('#6b7280')
    
    # Add title
    from reportlab.graphics.shapes import String
    title = String(200, 160, 'Email Engagement Distribution', textAnchor='middle')
    title.fontSize = 11
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_form_conversion_chart(views, submissions):
    """Create form conversion pie chart"""
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 100
    pie.height = 100
    
    # Calculate data
    no_conversion = views - submissions if views > submissions else 0
    
    pie.data = [submissions, no_conversion]
    pie.labels = ['Conversions', 'Views Only']
    pie.slices.strokeWidth = 0.5
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    
    # Add title
    from reportlab.graphics.shapes import String
    title = String(200, 160, 'Form Conversion Rate', textAnchor='middle')
    title.fontSize = 11
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_prospect_health_pie_chart(duplicates, inactive, missing_fields, scoring_issues, total):
    """Create prospect health pie chart"""
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 100
    pie.height = 100
    
    # Calculate healthy prospects
    issues = duplicates + inactive + missing_fields + scoring_issues
    healthy = total - issues if total > issues else 0
    
    pie.data = [healthy, duplicates, inactive, missing_fields, scoring_issues]
    pie.labels = ['Healthy', 'Duplicates', 'Inactive', 'Missing Fields', 'Scoring Issues']
    pie.slices.strokeWidth = 0.5
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices[2].fillColor = colors.HexColor('#ef4444')
    pie.slices[3].fillColor = colors.HexColor('#8b5cf6')
    pie.slices[4].fillColor = colors.HexColor('#f97316')
    
    # Add title
    from reportlab.graphics.shapes import String
    title = String(200, 160, 'Prospect Database Health', textAnchor='middle')
    title.fontSize = 11
    title.fontName = 'Helvetica-Bold'
    
    drawing.add(pie)
    drawing.add(title)
    return drawing