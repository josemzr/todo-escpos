"""PDF generation for task cards."""

import tempfile
from datetime import datetime

from .config import (
    REPORTLAB_AVAILABLE,
    TA_CENTER,
    Paragraph,
    ParagraphStyle,
    SimpleDocTemplate,
    Spacer,
    colors,
    getSampleStyleSheet,
)

# Try to register emoji-supporting fonts with ReportLab
if REPORTLAB_AVAILABLE:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    
    # Try to register Windows emoji fonts
    emoji_font_registered = False
    for font_name, font_path in [
        ("SegoeUIEmoji", "C:/Windows/Fonts/seguiemj.ttf"),
        ("SegoeUIEmoji", "C:/Windows/Fonts/segoeuiemoji.ttf"),
        ("SegoeUISymbol", "C:/Windows/Fonts/seguisym.ttf"),
    ]:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                emoji_font_registered = True
                break
        except:
            pass

# Import additional ReportLab components for drawing
if REPORTLAB_AVAILABLE:
    from reportlab.lib.units import inch
    from reportlab.platypus import Flowable
else:
    # Define dummy values if ReportLab not available
    inch = 1

    class Flowable:
        def __init__(self):
            pass



def create_task_pdf(task_data):
    """Create a PDF with task card layout optimized for thermal printer."""
    if not REPORTLAB_AVAILABLE:
        print("Reportlab not available - cannot create PDF")
        return None

    try:
        # Create temporary PDF file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_filename = temp_pdf.name
        temp_pdf.close()

        # Custom page size for thermal printer (72mm width ≈ 2.83 inches)
        # Height will auto-adjust based on content
        pagesize = (2.83 * inch, 4.5 * inch)  # 72mm x ~114mm, more room for text

        # Create PDF document with minimal margins
        doc = SimpleDocTemplate(pdf_filename, pagesize=pagesize, topMargin=0.15*inch, bottomMargin=0.15*inch, leftMargin=0.25*inch, rightMargin=0.25*inch)
        styles = getSampleStyleSheet()
        story = []

        # Custom styles with smaller fonts for receipt printer
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=32,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=36,
        )

        date_style = ParagraphStyle(
            "CustomDate",
            parent=styles["Normal"],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.black,
        )

        # Add title
        story.append(Paragraph(task_data["title"], title_style))
        story.append(Spacer(1, 0.1 * inch))

        # Add lightning bolt emoji based on priority
        bolt_style = ParagraphStyle(
            "BoltStyle",
            parent=styles["Normal"],
            fontSize=48,
            alignment=TA_CENTER,
            leading=56,
        )
        
        # Try to use an emoji font if available
        if emoji_font_registered and "SegoeUIEmoji" in pdfmetrics.getRegisteredFontNames():
            bolt_style.fontName = "SegoeUIEmoji"
        elif emoji_font_registered and "SegoeUISymbol" in pdfmetrics.getRegisteredFontNames():
            bolt_style.fontName = "SegoeUISymbol"
        
        if task_data["priority"].upper() == "HIGH":
            # Three lightning bolt emojis for high priority
            story.append(Paragraph("⚡ ⚡ ⚡", bolt_style))
        else:
            # Single lightning bolt emoji
            story.append(Paragraph("⚡", bolt_style))

        story.append(Spacer(1, 0.1 * inch))

        # Add due date with clock emoji
        due_date = datetime.now().strftime("%B %d")
        # Add ordinal suffix
        day = int(datetime.now().strftime("%d"))
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        due_date_text = f"{datetime.now().strftime('%B %d')}{suffix}"
        story.append(Paragraph(due_date_text, date_style))

        # Build PDF
        doc.build(story)

        print(f"PDF created: {pdf_filename}")
        return pdf_filename

    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        return None


def pdf_to_image(pdf_path):
    """Convert PDF to image for thermal printer."""
    from .config import PDF2IMAGE_AVAILABLE, convert_from_path

    if not PDF2IMAGE_AVAILABLE:
        print("pdf2image not available - cannot convert PDF to image")
        return None

    try:
        # Convert PDF to images (DPI adjusted for thermal printer)
        images = convert_from_path(
            pdf_path, dpi=203
        )  # 203 DPI is common for thermal printers

        if images:
            # Get the first page
            img = images[0]

            # Save as temporary image file
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(temp_img.name, "PNG")
            temp_img.close()

            print(f"PDF converted to image: {temp_img.name}")
            return temp_img.name
        else:
            print("No images generated from PDF")
            return None

    except Exception as e:
        print(f"Error converting PDF to image: {str(e)}")
        return None
