#!/usr/bin/env python3
"""
Icon Generator for FileConverter Application.

This script generates an icon file for the FileConverter application.
It uses the Pillow library to create a simple icon that represents the
file conversion functionality.
"""

import os
import sys
from pathlib import Path

def generate_icon():
    """Generate an icon file for FileConverter application."""
    # Get the directory where this script is located
    current_dir = Path(__file__).parent
    icon_path = current_dir / "icon.ico"
    
    # Ensure the directory exists
    os.makedirs(current_dir, exist_ok=True)
    
    # Skip if the icon already exists
    if icon_path.exists():
        print(f"Icon file already exists at {icon_path}")
        return str(icon_path)
    
    try:
        # Try to import PIL for image creation
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow (PIL) library not installed. Cannot generate detailed icon.")
        print("Icon will be generated when Pillow is installed with 'pip install Pillow'")
        print("Creating a placeholder file instead")
        # Create a simple placeholder file
        with open(icon_path, 'wb') as f:
            # Write minimal .ico file header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00\x28\x01\x00\x00\x16\x00\x00\x00')
            # Write minimal icon data (16x16 px)
            f.write(b'\x00' * 296)
        print(f"Created icon placeholder at {icon_path}")
        return str(icon_path)
    
    # Create icon sizes
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    try:
        for size in sizes:
            # Create a new image with a white background
            img = Image.new('RGBA', (size, size), color=(255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a background circle
            circle_color = (0, 120, 212)  # Blue color
            circle_bounds = (2, 2, size-2, size-2)
            draw.ellipse(circle_bounds, fill=circle_color)
            
            # Draw an arrow pointing right representing conversion
            arrow_color = (255, 255, 255)  # White color
            
            # Draw a stylized arrow based on size
            if size >= 48:
                # More detailed arrow for larger sizes
                arrow_width = int(size * 0.5)
                arrow_height = int(size * 0.25)
                x_center = size // 2
                y_center = size // 2
                
                # Arrow shaft
                shaft_left = x_center - arrow_width // 2
                shaft_right = x_center + arrow_width // 2
                shaft_top = y_center - arrow_height // 4
                shaft_bottom = y_center + arrow_height // 4
                
                # Arrow head
                head_left = shaft_right - arrow_height // 2
                head_top = y_center - arrow_height // 2
                head_bottom = y_center + arrow_height // 2
                
                # Draw the shaft
                draw.rectangle((shaft_left, shaft_top, shaft_right, shaft_bottom), fill=arrow_color)
                
                # Draw the arrowhead
                arrow_head_points = [
                    (shaft_right, y_center),
                    (head_left, head_top),
                    (head_left, head_bottom)
                ]
                draw.polygon(arrow_head_points, fill=arrow_color)
            else:
                # Simpler arrow for smaller sizes
                arrow_points = [
                    (size // 4, size // 3),
                    (size * 3 // 4, size // 2),
                    (size // 4, size * 2 // 3)
                ]
                draw.polygon(arrow_points, fill=arrow_color)
            
            images.append(img)
        
        # Save as .ico file with multiple sizes
        images[0].save(
            icon_path,
            format="ICO",
            sizes=[(size, size) for size in sizes],
            append_images=images[1:]
        )
        
        print(f"Created icon file at {icon_path}")
        return str(icon_path)
    
    except Exception as e:
        print(f"Error generating icon: {e}")
        # Fallback to create a simple placeholder if image generation fails
        with open(icon_path, 'wb') as f:
            # Write minimal .ico file header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00\x28\x01\x00\x00\x16\x00\x00\x00')
            # Write minimal icon data (16x16 px)
            f.write(b'\x00' * 296)
        print(f"Created icon placeholder at {icon_path} due to error")
        return str(icon_path)

if __name__ == "__main__":
    generate_icon()