from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

app = Flask(__name__)
CORS(app)

def clean_text(text):
    if not text: return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

@app.route('/')
def home():
    return jsonify({'status': 'online', 'service': 'PDF Generator API'})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, 
            textColor=colors.HexColor('#1565c0'), alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=15, 
            textColor=colors.HexColor('#283593'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold')
        subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=11, 
            textColor=colors.HexColor('#1565c0'), spaceAfter=6, spaceBefore=10, fontName='Helvetica-Bold')
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY)
        
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph(clean_text(data.get('title', 'Document')), title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())
        
        if data.get('executive_summary'):
            story.append(Paragraph('Overview', heading_style))
            story.append(Paragraph(clean_text(data['executive_summary']), body_style))
            story.append(Spacer(1, 20))
        
        for section in data.get('sections', []):
            story.append(Paragraph(clean_text(section.get('heading', 'Section')), heading_style))
            story.append(Spacer(1, 8))
            
            for idx, item in enumerate(section.get('items', []), 1):
                term = clean_text(item.get('term', ''))
                term_header = f"{idx}. <b>{term}</b>"
                story.append(Paragraph(term_header, subheading_style))
                
                if item.get('definition'):
                    story.append(Paragraph(f"<b>Definition:</b> {clean_text(item['definition'])}", body_style))
                if item.get('translation'):
                    story.append(Paragraph(f"<b>Vietnamese:</b> <i>{clean_text(item['translation'])}</i>", body_style))
                if item.get('example'):
                    story.append(Paragraph(f'<b>Example:</b> "{clean_text(item["example"])}"', body_style))
                story.append(Spacer(1, 10))
            
            story.append(Spacer(1, 15))
        
        if data.get('conclusion'):
            story.append(PageBreak())
            story.append(Paragraph('Conclusion', heading_style))
            story.append(Paragraph(clean_text(data['conclusion']), body_style))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(buffer, mimetype='application/pdf', as_attachment=True,
            download_name=f"{data.get('title', 'document').replace(' ', '_')}.pdf")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
