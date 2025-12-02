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

# Import chart functions
try:
    from .pdf_charts import create_landing_page_chart, create_engagement_chart, create_utm_quality_chart
except ImportError:
    from pdf_charts import create_landing_page_chart, create_engagement_chart, create_utm_quality_chart

def create_detailed_email_section(email_stats):
    """Create detailed email analytics section"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section Title
    section_title = ParagraphStyle('EmailSectionTitle', parent=styles['Heading1'], 
                                 fontSize=18, spaceAfter=20, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("1. EMAIL CAMPAIGN ANALYSIS", section_title))
    
    # Section Overview
    overview_text = f"""
    This section analyzes the performance of {len(email_stats)} email campaigns in your Pardot system. 
    Email marketing remains a cornerstone of digital marketing with an average ROI of $42 for every $1 spent. 
    Our analysis examines delivery rates, engagement metrics, and campaign effectiveness.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    # Calculate metrics
    total_sent = sum(email.get('stats', {}).get('sent', 0) for email in email_stats)
    total_delivered = sum(email.get('stats', {}).get('delivered', 0) for email in email_stats)
    total_opens = sum(email.get('stats', {}).get('opens', 0) for email in email_stats)
    total_clicks = sum(email.get('stats', {}).get('clicks', 0) for email in email_stats)
    total_bounces = sum(email.get('stats', {}).get('bounces', 0) for email in email_stats)
    
    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (total_opens / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
    bounce_rate = (total_bounces / total_sent * 100) if total_sent > 0 else 0
    
    # Performance Metrics Table
    content.append(Paragraph("1.1 Campaign Performance Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    performance_data = [
        ['METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Total Campaigns', f"{len(email_stats):,}", 'N/A', '✓ Active'],
        ['Emails Sent', f"{total_sent:,}", 'N/A', '✓ Volume High'],
        ['Delivery Rate', f"{delivery_rate:.1f}%", '95%+', 
         '✓ Excellent' if delivery_rate >= 95 else '⚠ Good' if delivery_rate >= 90 else '✗ Needs Improvement'],
        ['Open Rate', f"{open_rate:.1f}%", '21-25%', 
         '✓ Excellent' if open_rate >= 25 else '⚠ Average' if open_rate >= 20 else '✗ Below Average'],
        ['Click Rate', f"{click_rate:.1f}%", '2.5-4%', 
         '✓ Excellent' if click_rate >= 4 else '⚠ Average' if click_rate >= 2.5 else '✗ Below Average'],
        ['Bounce Rate', f"{bounce_rate:.1f}%", '<2%', 
         '✓ Excellent' if bounce_rate <= 2 else '⚠ Acceptable' if bounce_rate <= 5 else '✗ High']
    ]
    
    performance_table = Table(performance_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
    performance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(performance_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Top Performing Campaigns
    content.append(Paragraph("1.2 Top Performing Campaigns", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    # Sort campaigns by engagement
    sorted_campaigns = sorted(email_stats, 
                            key=lambda x: x.get('stats', {}).get('opens', 0) + x.get('stats', {}).get('clicks', 0), 
                            reverse=True)[:10]
    
    campaigns_data = [['CAMPAIGN NAME', 'SENT', 'OPENS', 'CLICKS', 'OPEN %', 'CTR %']]
    
    for campaign in sorted_campaigns:
        stats = campaign.get('stats', {})
        name = campaign.get('name', 'Unknown')[:25] + '...' if len(campaign.get('name', '')) > 25 else campaign.get('name', 'Unknown')
        sent = stats.get('sent', 0)
        delivered = stats.get('delivered', 0)
        opens = stats.get('opens', 0)
        clicks = stats.get('clicks', 0)
        
        camp_open_rate = (opens / delivered * 100) if delivered > 0 else 0
        camp_click_rate = (clicks / delivered * 100) if delivered > 0 else 0
        
        campaigns_data.append([
            name,
            f"{sent:,}",
            f"{opens:,}",
            f"{clicks:,}",
            f"{camp_open_rate:.1f}%",
            f"{camp_click_rate:.1f}%"
        ])
    
    campaigns_table = Table(campaigns_data, colWidths=[2.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
    campaigns_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(campaigns_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Email Performance Chart
    content.append(Paragraph("1.3 Email Performance Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_email_performance_chart(total_sent, total_delivered, total_opens, total_clicks))
    
    # Key Insights
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("1.4 Key Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    insights = [
        f"• Campaign Volume: {len(email_stats)} campaigns sent {total_sent:,} emails with {delivery_rate:.1f}% delivery success",
        f"• Engagement Performance: {open_rate:.1f}% open rate {'exceeds' if open_rate > 21 else 'meets' if open_rate >= 18 else 'falls below'} industry standards",
        f"• Click-through Effectiveness: {click_rate:.1f}% CTR indicates {'strong' if click_rate > 3 else 'moderate' if click_rate >= 2 else 'weak'} content relevance",
        f"• List Health: {bounce_rate:.1f}% bounce rate {'indicates healthy' if bounce_rate < 3 else 'suggests list cleanup needed for'} subscriber database"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], 
                                                       fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_detailed_form_section(form_stats):
    """Create detailed form analytics section"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section Title
    section_title = ParagraphStyle('FormSectionTitle', parent=styles['Heading1'], 
                                 fontSize=18, spaceAfter=20, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("2. FORM PERFORMANCE ANALYSIS", section_title))
    
    # Section Overview
    overview_text = f"""
    This section analyzes {len(form_stats)} marketing forms deployed across your Pardot platform. 
    Forms are critical conversion points in the customer journey, serving as the primary mechanism for lead capture and qualification. 
    Our analysis examines form performance, user engagement patterns, and conversion optimization opportunities.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    # Calculate metrics
    total_views = sum(form.get('views', 0) for form in form_stats)
    total_submissions = sum(form.get('submissions', 0) for form in form_stats)
    overall_conversion_rate = (total_submissions / total_views * 100) if total_views > 0 else 0
    
    # Form Conversion Analysis
    content.append(Paragraph("2.1 Form Conversion Analysis", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    conversion_data = [
        ['CONVERSION METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Total Forms Active', f"{len(form_stats):,}", 'N/A', '✓ Deployed'],
        ['Total Form Views', f"{total_views:,}", 'N/A', '✓ High Traffic'],
        ['Total Submissions', f"{total_submissions:,}", 'N/A', '✓ Active Conversion'],
        ['Overall Conversion Rate', f"{overall_conversion_rate:.1f}%", '15-25%', 
         '✓ Excellent' if overall_conversion_rate >= 25 else '⚠ Good' if overall_conversion_rate >= 15 else '✗ Needs Improvement']
    ]
    
    conversion_table = Table(conversion_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
    conversion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#d1fae5')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(conversion_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Top Performing Forms
    content.append(Paragraph("2.2 Top Performing Forms", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    # Sort forms by conversion rate
    sorted_forms = sorted([f for f in form_stats if f.get('views', 0) > 0], 
                         key=lambda x: (x.get('submissions', 0) / x.get('views', 1) * 100), 
                         reverse=True)[:10]
    
    forms_data = [['FORM NAME', 'VIEWS', 'SUBMISSIONS', 'CONVERSION %']]
    
    for form in sorted_forms:
        name = form.get('name', 'Unknown')[:30] + '...' if len(form.get('name', '')) > 30 else form.get('name', 'Unknown')
        views = form.get('views', 0)
        submissions = form.get('submissions', 0)
        conv_rate = (submissions / views * 100) if views > 0 else 0
        
        forms_data.append([
            name,
            f"{views:,}",
            f"{submissions:,}",
            f"{conv_rate:.1f}%"
        ])
    
    forms_table = Table(forms_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
    forms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    content.append(forms_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Form Performance Chart
    content.append(Paragraph("2.3 Form Performance Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_form_performance_chart(total_views, total_submissions))
    
    return content

def create_detailed_prospect_section(prospect_health):
    """Create detailed prospect health section"""
    styles = getSampleStyleSheet()
    content = []
    
    # Section Title
    section_title = ParagraphStyle('ProspectSectionTitle', parent=styles['Heading1'], 
                                 fontSize=18, spaceAfter=20, 
                                 textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')
    
    content.append(Paragraph("4. PROSPECT DATABASE HEALTH", section_title))
    
    total_prospects = prospect_health.get('total_prospects', 0)
    
    # Section Overview
    overview_text = f"""
    This section provides a comprehensive health assessment of your {total_prospects:,} prospect database records. 
    Database quality directly impacts marketing effectiveness, sales productivity, and customer experience. 
    Our analysis identifies data quality issues, segmentation opportunities, and database optimization strategies.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    # Calculate metrics
    duplicates = prospect_health.get('duplicates', {}).get('count', 0)
    inactive = prospect_health.get('inactive_prospects', {}).get('count', 0)
    missing_fields = prospect_health.get('missing_fields', {}).get('count', 0)
    scoring_issues = prospect_health.get('scoring_issues', {}).get('count', 0)
    
    healthy_prospects = total_prospects - duplicates - inactive - missing_fields - scoring_issues
    database_health_score = (healthy_prospects / total_prospects * 100) if total_prospects > 0 else 0
    
    # Data Quality Assessment
    content.append(Paragraph("4.1 Data Quality Assessment", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    quality_data = [
        ['DATA QUALITY METRIC', 'COUNT', 'PERCENTAGE', 'IMPACT'],
        ['Total Prospect Records', f"{total_prospects:,}", '100%', '✓ Baseline'],
        ['Healthy Records', f"{healthy_prospects:,}", f"{database_health_score:.1f}%", 
         '✓ Excellent' if database_health_score >= 85 else '⚠ Good' if database_health_score >= 70 else '✗ Critical'],
        ['Duplicate Records', f"{duplicates:,}", f"{(duplicates/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '✓ Low' if duplicates/total_prospects < 0.05 else '⚠ Medium' if duplicates/total_prospects < 0.15 else '✗ High'],
        ['Inactive Prospects (90+ days)', f"{inactive:,}", f"{(inactive/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '✓ Low' if inactive/total_prospects < 0.20 else '⚠ Medium' if inactive/total_prospects < 0.40 else '✗ High'],
        ['Incomplete Profiles', f"{missing_fields:,}", f"{(missing_fields/total_prospects*100):.1f}%" if total_prospects > 0 else '0%', 
         '✓ Low' if missing_fields/total_prospects < 0.10 else '⚠ Medium' if missing_fields/total_prospects < 0.25 else '✗ High']
    ]
    
    quality_table = Table(quality_data, colWidths=[2.2*inch, 1*inch, 1*inch, 1.3*inch])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(quality_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Database Health Chart
    content.append(Paragraph("4.2 Database Health Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_prospect_health_chart(healthy_prospects, duplicates, inactive, missing_fields, scoring_issues))
    
    return content

def create_email_performance_chart(sent, delivered, opens, clicks):
    """Create email performance bar chart"""
    drawing = Drawing(500, 300)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 80
    chart.height = 180
    chart.width = 380
    
    chart.data = [[sent, delivered, opens, clicks]]
    chart.categoryAxis.categoryNames = ['Sent', 'Delivered', 'Opens', 'Clicks']
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(sent, 1) * 1.2
    chart.valueAxis.labels.fontSize = 9
    
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    chart.bars.strokeColor = colors.HexColor('#1e40af')
    chart.bars.strokeWidth = 1
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'Email Campaign Performance Metrics', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(chart)
    drawing.add(title)
    return drawing

def create_form_performance_chart(views, submissions):
    """Create form performance pie chart"""
    drawing = Drawing(500, 300)
    pie = Pie()
    pie.x = 200
    pie.y = 100
    pie.width = 120
    pie.height = 120
    
    abandoned = views - submissions if views > submissions else 0
    conversion_rate = (submissions / views * 100) if views > 0 else 0
    
    pie.data = [submissions, abandoned]
    pie.labels = [f'Conversions\n{submissions:,}\n({conversion_rate:.1f}%)', 
                  f'Abandoned\n{abandoned:,}\n({100-conversion_rate:.1f}%)']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices.fontSize = 9
    pie.slices.fontName = 'Helvetica-Bold'
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'Form Conversion Performance', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_prospect_health_chart(healthy, duplicates, inactive, missing_fields, scoring_issues):
    """Create prospect health pie chart"""
    drawing = Drawing(500, 300)
    pie = Pie()
    pie.x = 200
    pie.y = 100
    pie.width = 120
    pie.height = 120
    
    total = healthy + duplicates + inactive + missing_fields + scoring_issues
    
    pie.data = [healthy, duplicates, inactive, missing_fields, scoring_issues]
    pie.labels = [
        f'Healthy\n{healthy:,}\n({healthy/total*100:.1f}%)',
        f'Duplicates\n{duplicates:,}',
        f'Inactive\n{inactive:,}',
        f'Missing Fields\n{missing_fields:,}',
        f'Scoring Issues\n{scoring_issues:,}'
    ]
    
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices[2].fillColor = colors.HexColor('#dc2626')
    pie.slices[3].fillColor = colors.HexColor('#8b5cf6')
    pie.slices[4].fillColor = colors.HexColor('#f97316')
    pie.slices.fontSize = 8
    pie.slices.fontName = 'Helvetica-Bold'
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'Prospect Database Health Distribution', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_detailed_landing_page_section(landing_page_stats):
    """Create detailed landing page section"""
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("3. LANDING PAGE ANALYSIS", 
                           ParagraphStyle('LandingPageTitle', parent=styles['Heading1'], 
                                        fontSize=18, spaceAfter=20, 
                                        textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
    
    if not landing_page_stats:
        content.append(Paragraph("No landing page data available for analysis.", 
                               ParagraphStyle('NoData', parent=styles['Normal'], 
                                            fontSize=11, textColor=colors.HexColor('#6b7280'))))
        return content
    
    summary = landing_page_stats.get('summary', {})
    total_pages = summary.get('total_pages', 0)
    active_pages = landing_page_stats.get('active_pages', {}).get('count', 0)
    inactive_pages = landing_page_stats.get('inactive_pages', {}).get('count', 0)
    
    overview_text = f"""
    This section analyzes {total_pages} landing pages in your Pardot system, examining page performance, 
    field mapping configurations, and conversion optimization opportunities. Landing pages serve as critical 
    conversion points in your marketing funnel.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    # Landing Page Performance Overview
    content.append(Paragraph("3.1 Page Performance Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    performance_data = [
        ['METRIC', 'VALUE', 'STATUS'],
        ['Total Landing Pages', f"{total_pages:,}", '✓ Active'],
        ['Active Pages (30 days)', f"{active_pages:,}", f"✓ {(active_pages/total_pages*100):.1f}%" if total_pages > 0 else '0%'],
        ['Inactive Pages', f"{inactive_pages:,}", f"⚠ {(inactive_pages/total_pages*100):.1f}%" if total_pages > 0 else '0%'],
        ['Total Activities', f"{summary.get('total_activities', 0):,}", '✓ Tracked']
    ]
    
    performance_table = Table(performance_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    performance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(performance_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Landing Page Chart
    content.append(Paragraph("3.2 Landing Page Activity Distribution", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_landing_page_chart(active_pages, inactive_pages))
    
    # Key Insights
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("3.3 Key Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    insights = [
        f"• Page Portfolio: {total_pages} total landing pages with {active_pages} showing recent activity",
        f"• Activity Rate: {(active_pages/total_pages*100):.1f}% of pages are actively generating traffic" if total_pages > 0 else "• No activity data available",
        f"• Optimization Opportunity: {inactive_pages} pages may need content refresh or URL promotion",
        f"• Total Engagement: {summary.get('total_activities', 0):,} tracked activities across all pages"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], 
                                                       fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_detailed_engagement_section(engagement_programs):
    """Create detailed engagement programs section"""
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("5. ENGAGEMENT PROGRAMS", 
                           ParagraphStyle('EngagementTitle', parent=styles['Heading1'], 
                                        fontSize=18, spaceAfter=20, 
                                        textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
    
    if not engagement_programs:
        content.append(Paragraph("No engagement program data available for analysis.", 
                               ParagraphStyle('NoData', parent=styles['Normal'], 
                                            fontSize=11, textColor=colors.HexColor('#6b7280'))))
        return content
    
    overview_text = """
    This section analyzes your Pardot engagement programs, which are automated marketing workflows designed to nurture 
    prospects through personalized, multi-touch campaigns. Engagement programs help maintain consistent communication 
    and guide prospects through the sales funnel.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    summary = engagement_programs.get('summary', {})
    active_programs = engagement_programs.get('active_programs', [])
    
    # Program Overview
    content.append(Paragraph("5.1 Program Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    program_data = [
        ['METRIC', 'VALUE', 'STATUS'],
        ['Total Programs', f"{summary.get('total_programs', 0):,}", '✓ Configured'],
        ['Active Programs', f"{summary.get('active_count', 0):,}", '✓ Running'],
        ['Paused Programs', f"{summary.get('paused_count', 0):,}", '⚠ On Hold'],
        ['Inactive Programs', f"{summary.get('inactive_count', 0):,}", '⚠ Stopped']
    ]
    
    program_table = Table(program_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    program_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3e8ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(program_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Active Programs List
    if active_programs:
        content.append(Paragraph("5.2 Active Programs", 
                               ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                            fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
        
        programs_data = [['PROGRAM NAME', 'STATUS', 'CREATED DATE']]
        
        for program in active_programs[:10]:  # Show top 10
            name = program.get('name', 'Unknown')[:35] + '...' if len(program.get('name', '')) > 35 else program.get('name', 'Unknown')
            status = program.get('status', 'Unknown')
            created_date = program.get('createdAt', '')
            if created_date:
                try:
                    created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except:
                    created_date = 'Unknown'
            
            programs_data.append([name, status, created_date])
        
        programs_table = Table(programs_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        programs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(programs_table)
        content.append(Spacer(1, 0.3*inch))
    
    # Engagement Chart
    content.append(Paragraph("5.3 Program Status Distribution", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_engagement_chart(summary.get('active_count', 0), 
                                         summary.get('paused_count', 0), 
                                         summary.get('inactive_count', 0)))
    
    return content

def create_detailed_utm_section(utm_analysis):
    """Create detailed UTM analysis section"""
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("6. UTM TRACKING ANALYSIS", 
                           ParagraphStyle('UTMTitle', parent=styles['Heading1'], 
                                        fontSize=18, spaceAfter=20, 
                                        textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
    
    if not utm_analysis:
        content.append(Paragraph("No UTM tracking data available for analysis.", 
                               ParagraphStyle('NoData', parent=styles['Normal'], 
                                            fontSize=11, textColor=colors.HexColor('#6b7280'))))
        return content
    
    overview_text = """
    This section analyzes UTM (Urchin Tracking Module) parameters in your Pardot system. UTM tracking enables 
    precise campaign attribution by tagging URLs with source, medium, campaign, and other parameters. 
    Proper UTM implementation is crucial for accurate marketing ROI measurement.
    """
    
    content.append(Paragraph(overview_text, 
                           ParagraphStyle('Overview', parent=styles['Normal'], 
                                        fontSize=11, spaceAfter=20, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=16)))
    
    utm_data = utm_analysis.get('utm_analysis', {})
    
    # UTM Overview
    content.append(Paragraph("6.1 UTM Tracking Overview", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    total_analyzed = utm_data.get('total_prospects_analyzed', 0)
    utm_coverage = utm_data.get('utm_coverage_percentage', 0)
    utm_issues = utm_data.get('prospects_with_utm_issues', 0)
    quality_score = utm_data.get('data_quality_score', 0)
    
    utm_overview_data = [
        ['UTM METRIC', 'VALUE', 'BENCHMARK', 'STATUS'],
        ['Prospects Analyzed', f"{total_analyzed:,}", 'N/A', '✓ Complete'],
        ['UTM Coverage', f"{utm_coverage:.1f}%", '80%+', 
         '✓ Excellent' if utm_coverage >= 80 else '⚠ Good' if utm_coverage >= 60 else '✗ Needs Improvement'],
        ['Data Quality Score', f"{quality_score:.1f}%", '90%+', 
         '✓ Excellent' if quality_score >= 90 else '⚠ Good' if quality_score >= 75 else '✗ Needs Improvement'],
        ['UTM Issues Found', f"{utm_issues:,}", '<5%', 
         '✓ Low' if utm_issues/total_analyzed < 0.05 else '⚠ Medium' if utm_issues/total_analyzed < 0.15 else '✗ High']
    ]
    
    utm_table = Table(utm_overview_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.3*inch])
    utm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e0f2fe')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    
    content.append(utm_table)
    content.append(Spacer(1, 0.3*inch))
    
    # UTM Parameters Analysis
    utm_parameters = utm_analysis.get('utm_parameters_analysis', {})
    if utm_parameters:
        content.append(Paragraph("6.2 UTM Parameters Usage", 
                               ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                            fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
        
        param_data = [['PARAMETER', 'USAGE COUNT', 'COVERAGE %']]
        
        for param, data in utm_parameters.items():
            if isinstance(data, dict):
                usage = data.get('usage_count', 0)
                coverage = data.get('coverage_percentage', 0)
                param_data.append([param.upper(), f"{usage:,}", f"{coverage:.1f}%"])
        
        param_table = Table(param_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(param_table)
        content.append(Spacer(1, 0.3*inch))
    
    # UTM Quality Chart
    content.append(Paragraph("6.3 UTM Data Quality Visualization", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    content.append(create_utm_quality_chart(total_analyzed - utm_issues, utm_issues))
    
    # Key Insights
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("6.4 Key Insights", 
                           ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                        fontSize=14, spaceAfter=15, textColor=colors.HexColor('#4b5563'))))
    
    insights = [
        f"• UTM Implementation: {utm_coverage:.1f}% of prospects have UTM tracking data",
        f"• Data Quality: {quality_score:.1f}% quality score indicates {'excellent' if quality_score >= 90 else 'good' if quality_score >= 75 else 'poor'} UTM hygiene",
        f"• Issues Identified: {utm_issues:,} prospects have UTM parameter inconsistencies",
        f"• Campaign Attribution: Proper UTM tracking enables accurate ROI measurement across {len(utm_parameters)} parameters"
    ]
    
    for insight in insights:
        content.append(Paragraph(insight, ParagraphStyle('Insight', parent=styles['Normal'], 
                                                       fontSize=10, spaceAfter=8, leftIndent=20)))
    
    return content

def create_recommendations_section(email_stats, form_stats, prospect_health, landing_page_stats):
    """Create recommendations section"""
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("7. STRATEGIC RECOMMENDATIONS", 
                           ParagraphStyle('RecommendationsTitle', parent=styles['Heading1'], 
                                        fontSize=18, spaceAfter=20, 
                                        textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
    
    recommendations = [
        "• Implement A/B testing for email subject lines to improve open rates by 15-25%",
        "• Reduce form fields to essential information only to increase conversion rates",
        "• Clean up duplicate prospects to improve data accuracy and campaign effectiveness",
        "• Implement progressive profiling to gather additional data over time",
        "• Review and optimize lead scoring criteria based on conversion data"
    ]
    
    for rec in recommendations:
        content.append(Paragraph(rec, ParagraphStyle('Recommendation', parent=styles['Normal'], 
                                                   fontSize=11, spaceAfter=10, leftIndent=20)))
    
    return content

def create_appendix_section():
    """Create appendix section"""
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("APPENDIX", 
                           ParagraphStyle('AppendixTitle', parent=styles['Heading1'], 
                                        fontSize=18, spaceAfter=20, 
                                        textColor=colors.HexColor('#1f2937'), fontName='Helvetica-Bold')))
    
    content.append(Paragraph("Methodology and Data Sources", 
                           ParagraphStyle('AppendixSubtitle', parent=styles['Heading2'], 
                                        fontSize=14, spaceAfter=15, 
                                        textColor=colors.HexColor('#4b5563'), fontName='Helvetica-Bold')))
    
    methodology_text = """
    This report was generated using data extracted from your Pardot marketing automation platform via API integration. 
    All metrics and calculations are based on real-time data as of the report generation date. 
    Industry benchmarks are sourced from leading marketing research organizations including HubSpot, Mailchimp, and Salesforce.
    """
    
    content.append(Paragraph(methodology_text, 
                           ParagraphStyle('AppendixText', parent=styles['Normal'], 
                                        fontSize=10, spaceAfter=15, 
                                        textColor=colors.HexColor('#374151'), 
                                        leading=14)))
    
    return content