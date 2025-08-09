#!/usr/bin/env python3
"""
Simple script to create a basic ICO file for the Whisper Hotkey service
Run this if you need a proper icon file for Windows shortcuts
"""

from PIL import Image, ImageDraw

def create_whisper_icon():
    """Create a simple microphone icon for the service"""
    
    # Create multiple sizes for ICO format
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    images = []
    
    for size in sizes:
        width, height = size
        
        # Create white background
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Scale elements based on size
        scale = width / 64.0
        
        # Draw microphone shape
        # Microphone capsule (ellipse)
        mic_left = int(20 * scale)
        mic_top = int(10 * scale)
        mic_right = int(44 * scale)
        mic_bottom = int(40 * scale)
        draw.ellipse([mic_left, mic_top, mic_right, mic_bottom], fill=(0, 0, 0, 255))
        
        # Microphone stand (rectangle)
        stand_left = int(30 * scale)
        stand_top = int(40 * scale) 
        stand_right = int(34 * scale)
        stand_bottom = int(50 * scale)
        draw.rectangle([stand_left, stand_top, stand_right, stand_bottom], fill=(0, 0, 0, 255))
        
        # Microphone base (rectangle)
        base_left = int(20 * scale)
        base_top = int(50 * scale)
        base_right = int(44 * scale)
        base_bottom = int(54 * scale)
        draw.rectangle([base_left, base_top, base_right, base_bottom], fill=(0, 0, 0, 255))
        
        # Add some sound waves for style
        if width >= 32:
            wave_color = (100, 100, 100, 180)
            # Right side waves
            draw.arc([mic_right + 2, mic_top + 5, mic_right + 8, mic_bottom - 5], 
                    start=270, end=90, fill=wave_color, width=max(1, int(1 * scale)))
            if width >= 48:
                draw.arc([mic_right + 6, mic_top + 2, mic_right + 14, mic_bottom - 2], 
                        start=270, end=90, fill=wave_color, width=max(1, int(1 * scale)))
        
        images.append(image)
    
    # Save as ICO file
    icon_path = "whisper_icon.ico"
    images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    print(f"Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    try:
        create_whisper_icon()
        print("✓ Whisper icon created successfully!")
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("This is optional - the system tray will work without it.")