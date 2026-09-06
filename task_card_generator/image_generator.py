"""Image generation for task cards."""

import tempfile
import textwrap
from datetime import datetime

from .config import PIL_AVAILABLE, Image, ImageDraw, ImageFont


def wrap_text_to_width(text, font, max_width, draw):
    """
    Wrap text to fit within a specified pixel width.
    
    Args:
        text (str): The text to wrap
        font: The PIL font object
        max_width (int): Maximum width in pixels
        draw: PIL ImageDraw object for measuring text
    
    Returns:
        list: List of text lines that fit within max_width
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Test if adding this word would exceed the width
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            # If current_line is empty, the single word is too long
            if not current_line:
                # Break the word itself if it's too long
                for i in range(len(word), 0, -1):
                    partial_word = word[:i]
                    bbox = draw.textbbox((0, 0), partial_word, font=font)
                    if bbox[2] - bbox[0] <= max_width:
                        lines.append(partial_word)
                        remaining = word[i:]
                        if remaining:
                            # Recursively wrap the remaining part
                            remaining_lines = wrap_text_to_width(remaining, font, max_width, draw)
                            lines.extend(remaining_lines)
                        break
            else:
                lines.append(current_line)
                current_line = word
                # Check if the new current_line fits
                bbox = draw.textbbox((0, 0), current_line, font=font)
                if bbox[2] - bbox[0] > max_width:
                    # If even the single word doesn't fit, break it
                    lines.extend(wrap_text_to_width(current_line, font, max_width, draw))
                    current_line = ""
    
    if current_line:
        lines.append(current_line)
    
    return lines



def create_task_image(task_data):
    """Create task card image with hand-drawn lightning bolts."""
    if not PIL_AVAILABLE:
        print("PIL not available - skipping image generation")
        return None

    try:
        # Image dimensions (optimized for thermal printer)
        width = 576  # 72mm thermal printer width
        
        # Load fonts first to calculate sizes
        # Try Linux-compatible fonts
        title_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # DejaVu Sans Bold
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Liberation Sans Bold
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # DejaVu Sans
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Liberation Sans
            "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",  # Lato Bold
            "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",  # Lato Regular
        ]
        
        date_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # DejaVu Sans
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Liberation Sans
            "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",  # Lato Regular
        ]
        
        # Load title font (slightly bigger)
        title_font = None
        for font_path in title_font_paths:
            try:
                title_font = ImageFont.truetype(font_path, 56)  # Increased from 48 to 56
                break
            except:
                continue
        
        if title_font is None:
            title_font = ImageFont.load_default()
        
        # Load date font (slightly bigger)
        date_font = None
        for font_path in date_font_paths:
            try:
                date_font = ImageFont.truetype(font_path, 28)  # Increased from 24 to 28
                break
            except:
                continue
        
        if date_font is None:
            date_font = ImageFont.load_default()

        # Create a temporary draw object to measure text
        temp_img = Image.new("RGB", (width, 100), "white")
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate content height with proper text wrapping
        # Leave some margin on both sides (50px each side = 100px total)
        text_max_width = width - 100
        title_lines = wrap_text_to_width(task_data["title"], title_font, text_max_width, temp_draw)
        
        # Calculate heights (adjusted for slightly bigger text)
        creation_date_height = 35  # Increased from 30 to 35
        title_height = len(title_lines) * 68 + 10  # Increased line height from 58 to 68
        separator_height = 20
        due_date_height = 35  # Increased from 30 to 35
        priority_height = 35   # Increased from 30 to 35
        total_padding = 60
        
        # Calculate initial height (removed emoji_height)
        initial_height = creation_date_height + title_height + (separator_height * 2) + due_date_height + priority_height + total_padding

        # Create image with white background
        img = Image.new("RGB", (width, initial_height), "white")
        draw = ImageDraw.Draw(img)

        # Draw creation date at the top
        current_y = 10
        
        # Format creation date as dd-mm-yyyy
        if isinstance(task_data["creation_date"], datetime):
            creation_date = task_data["creation_date"]
        else:
            creation_date = datetime.now()
        
        creation_date_text = f"Created: {creation_date.strftime('%d-%m-%Y')}"
        creation_date_bbox = draw.textbbox((0, 0), creation_date_text, font=date_font)
        creation_date_width = creation_date_bbox[2] - creation_date_bbox[0]
        creation_date_x = (width - creation_date_width) // 2
        draw.text((creation_date_x, current_y), creation_date_text, fill="black", font=date_font)
        
        current_y += creation_date_height

        # Draw title with proper text wrapping
        title_y = current_y
        
        # Recalculate title lines with the actual draw object for precise measurements
        title_lines = wrap_text_to_width(task_data["title"], title_font, text_max_width, draw)
        
        # Update height if needed (in case the actual wrapped lines differ)
        actual_title_height = len(title_lines) * 68 + 10  # Updated line height to 68
        if actual_title_height != title_height:
            height = creation_date_height + actual_title_height + (separator_height * 2) + due_date_height + priority_height + total_padding
            # Recreate image with correct height
            img = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(img)
            
            # Redraw creation date
            draw.text((creation_date_x, 10), creation_date_text, fill="black", font=date_font)
        
        for i, line in enumerate(title_lines):
            line_bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            draw.text((line_x, title_y + i * 68), line, fill="black", font=title_font)  # Updated line height to 68

        current_y = title_y + len(title_lines) * 68 + 20

        # Draw due date with dotted separator (removed lightning bolt section)
        separator_y = current_y
        
        # Draw dotted line separator
        separator_line_y = separator_y + 10
        dot_spacing = 20
        for x in range(50, width - 50, dot_spacing):
            draw.ellipse([x-2, separator_line_y-2, x+2, separator_line_y+2], fill="black")
        
        # Draw due date with "DUE:" label in dd-mm-yyyy format
        date_y = separator_y + 30
        
        # Use the actual task due date and format as dd-mm-yyyy
        if isinstance(task_data["due_date"], datetime):
            task_due_date = task_data["due_date"]
        else:
            # Handle string dates if needed (fallback)
            task_due_date = datetime.now()
            
        due_date_text = f"DUE: {task_due_date.strftime('%d-%m-%Y')}"
        date_bbox = draw.textbbox((0, 0), due_date_text, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = (width - date_width) // 2
        draw.text((date_x, date_y), due_date_text, fill="black", font=date_font)

        # Draw another dotted line separator
        priority_separator_y = date_y + 40  # Reduced spacing
        for x in range(50, width - 50, dot_spacing):
            draw.ellipse([x-2, priority_separator_y-2, x+2, priority_separator_y+2], fill="black")
        
        # Draw priority with "Priority:" label
        priority_y = priority_separator_y + 20
        priority_text = f"Priority: {task_data['priority']}"
        priority_bbox = draw.textbbox((0, 0), priority_text, font=date_font)
        priority_width = priority_bbox[2] - priority_bbox[0]
        priority_x = (width - priority_width) // 2
        draw.text((priority_x, priority_y), priority_text, fill="black", font=date_font)

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_file.name, "PNG")
        temp_file.close()

        print(f"Task card image created: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"Error creating task card image: {str(e)}")
        return None
