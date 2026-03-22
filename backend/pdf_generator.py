from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_soil_report_pdf(history_record, user_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Smart Agriculture Soil Analysis Report", title_style))
    elements.append(Spacer(1, 12))
    
    # User Info
    elements.append(Paragraph(f"<b>Prepared for:</b> {user_name}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {history_record.timestamp.strftime('%Y-%m-%d %H:%M')}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Soil Profile
    elements.append(Paragraph("Soil Profile", subtitle_style))
    data = [
        ["Nitrogen (N)", f"{history_record.N} mg/kg", "Temperature", f"{history_record.temperature} °C"],
        ["Phosphorus (P)", f"{history_record.P} mg/kg", "Humidity", f"{history_record.humidity} %"],
        ["Potassium (K)", f"{history_record.K} mg/kg", "pH Level", f"{history_record.ph}"],
        ["Rainfall", f"{history_record.rainfall} mm", "Health Status", f"{history_record.health.get('prediction', 'Unknown')}"]
    ]
    
    t = Table(data, colWidths=[120, 100, 120, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.silver),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))
    
    # Top Recommendation
    elements.append(Paragraph("Top Crop Recommendation", subtitle_style))
    if history_record.top_crops:
        top_crop = history_record.top_crops[0]
        elements.append(Paragraph(f"<b>{top_crop['name']}</b> ({top_crop['probability']}% Match)", normal_style))
        elements.append(Spacer(1, 6))
        
        # Economics
        econ = top_crop['economics']
        econ_data = [
            ["Estimated Cost", f"Rs. {econ['cost']:,}"],
            ["Expected Yield", f"{econ['yield']:,} kg/acre"],
            ["Market Price", f"Rs. {econ['price']}/kg"],
            ["Expected Profit", f"Rs. {econ['profit']:,}"]
        ]
        
        econ_table = Table(econ_data, colWidths=[200, 200])
        econ_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
            ('BACKGROUND', (0,0), (0,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(econ_table)
        elements.append(Spacer(1, 12))
        
        # Schedules
        elements.append(Paragraph("Fertilizer Master Plan", styles['Heading3']))
        fert = top_crop['fertilizer_schedule']
        fert_data = [["Phase", "Details"], ["Basal", fert['Basal']], ["Vegetative", fert['Vegetative']], ["Flowering", fert['Flowering']]]
        fert_table = Table(fert_data, colWidths=[100, 300])
        fert_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgreen),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(fert_table)
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Irrigation Schedule", styles['Heading3']))
        water = top_crop['water_schedule']
        water_data = [["Frequency", water['Frequency']], ["Critical Stages", water['Stages']]]
        water_table = Table(water_data, colWidths=[100, 300])
        water_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(water_table)
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
