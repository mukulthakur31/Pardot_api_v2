from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors

def create_landing_page_chart(active, inactive):
    """Create landing page activity chart"""
    drawing = Drawing(500, 300)
    pie = Pie()
    pie.x = 200
    pie.y = 100
    pie.width = 120
    pie.height = 120
    
    total = active + inactive
    active_pct = (active / total * 100) if total > 0 else 0
    
    pie.data = [active, inactive]
    pie.labels = [f'Active\n{active:,}\n({active_pct:.1f}%)', 
                  f'Inactive\n{inactive:,}\n({100-active_pct:.1f}%)']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices.fontSize = 9
    pie.slices.fontName = 'Helvetica-Bold'
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'Landing Page Activity Status', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_engagement_chart(active, paused, inactive):
    """Create engagement programs status chart"""
    drawing = Drawing(500, 300)
    pie = Pie()
    pie.x = 200
    pie.y = 100
    pie.width = 120
    pie.height = 120
    
    total = active + paused + inactive
    if total == 0:
        total = 1
        active = 1
    
    pie.data = [active, paused, inactive]
    pie.labels = [f'Active\n{active:,}', f'Paused\n{paused:,}', f'Inactive\n{inactive:,}']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices[2].fillColor = colors.HexColor('#dc2626')
    pie.slices.fontSize = 9
    pie.slices.fontName = 'Helvetica-Bold'
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'Engagement Program Status Distribution', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_utm_quality_chart(clean_data, issues):
    """Create UTM data quality chart"""
    drawing = Drawing(500, 300)
    pie = Pie()
    pie.x = 200
    pie.y = 100
    pie.width = 120
    pie.height = 120
    
    total = clean_data + issues
    quality_pct = (clean_data / total * 100) if total > 0 else 100
    
    pie.data = [clean_data, issues]
    pie.labels = [f'Clean Data\n{clean_data:,}\n({quality_pct:.1f}%)', 
                  f'Issues\n{issues:,}\n({100-quality_pct:.1f}%)']
    pie.slices.strokeWidth = 2
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor('#10b981')
    pie.slices[1].fillColor = colors.HexColor('#f59e0b')
    pie.slices.fontSize = 9
    pie.slices.fontName = 'Helvetica-Bold'
    
    from reportlab.graphics.shapes import String
    title = String(250, 270, 'UTM Data Quality Analysis', textAnchor='middle')
    title.fontSize = 14
    title.fontName = 'Helvetica-Bold'
    title.fillColor = colors.HexColor('#1f2937')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing