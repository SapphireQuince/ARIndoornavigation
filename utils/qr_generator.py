import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

def generate_qr_codes(base_url, entrance_count=5, output_dir='qr_codes'):
    """Generate QR codes for all entrances"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    qr_codes = {}
    
    for i in range(1, entrance_count + 1):
        # Create URL for each entrance
        entrance_url = f"{base_url}/?entrance={i}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(entrance_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create a larger image with label
        final_img = Image.new('RGB', (400, 500), 'white')
        
        # Paste QR code
        qr_resized = qr_img.resize((300, 300))
        final_img.paste(qr_resized, (50, 50))
        
        # Add text label
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a nice font
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add title
        title = f"Entrance {i}"
        bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = bbox[2] - bbox[0]
        draw.text(((400 - title_width) // 2, 370), title, fill="black", font=font_large)
        
        # Add instructions
        instruction = "Scan to Start Navigation"
        bbox = draw.textbbox((0, 0), instruction, font=font_small)
        inst_width = bbox[2] - bbox[0]
        draw.text(((400 - inst_width) // 2, 410), instruction, fill="gray", font=font_small)
        
        # Add URL for reference
        url_text = entrance_url
        bbox = draw.textbbox((0, 0), url_text, font=font_small)
        url_width = bbox[2] - bbox[0]
        if url_width > 380:  # If URL is too long, truncate it
            url_text = url_text[:40] + "..."
            bbox = draw.textbbox((0, 0), url_text, font=font_small)
            url_width = bbox[2] - bbox[0]
        draw.text(((400 - url_width) // 2, 440), url_text, fill="gray", font=font_small)
        
        # Save the image
        filename = f"entrance_{i}.png"
        filepath = os.path.join(output_dir, filename)
        final_img.save(filepath)
        
        qr_codes[i] = {
            'url': entrance_url,
            'filename': filename,
            'filepath': filepath
        }
        
        print(f"Generated QR code for Entrance {i}: {filepath}")
    
    return qr_codes

def generate_qr_code_html(qr_codes, output_dir='qr_codes'):
    """Generate an HTML file to display all QR codes for printing"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Indoor Navigation QR Codes</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .qr-container { 
                display: flex; 
                flex-wrap: wrap; 
                gap: 20px; 
                justify-content: center;
            }
            .qr-card { 
                border: 2px solid #333; 
                padding: 20px; 
                text-align: center;
                margin: 10px;
                page-break-inside: avoid;
            }
            .qr-card img { 
                max-width: 300px; 
                height: auto;
            }
            .qr-title { 
                font-size: 24px; 
                font-weight: bold; 
                margin: 10px 0;
            }
            .qr-url { 
                font-size: 12px; 
                color: #666; 
                word-break: break-all;
            }
            @media print {
                .qr-card { page-break-inside: avoid; }
            }
        </style>
    </head>
    <body>
        <h1>Indoor Navigation System - QR Codes</h1>
        <p>Print and place these QR codes at the respective entrances</p>
        <div class="qr-container">
    """
    
    for entrance_id, qr_info in qr_codes.items():
        html_content += f"""
            <div class="qr-card">
                <div class="qr-title">Entrance {entrance_id}</div>
                <img src="{qr_info['filename']}" alt="QR Code for Entrance {entrance_id}">
                <div class="qr-url">{qr_info['url']}</div>
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    html_filepath = os.path.join(output_dir, 'qr_codes_print.html')
    with open(html_filepath, 'w') as f:
        f.write(html_content)
    
    print(f"Generated QR codes HTML file: {html_filepath}")
    return html_filepath

if __name__ == "__main__":
    # Test QR code generation
    base_url = "http://192.168.1.100:5000"
    qr_codes = generate_qr_codes(base_url)
    generate_qr_code_html(qr_codes)