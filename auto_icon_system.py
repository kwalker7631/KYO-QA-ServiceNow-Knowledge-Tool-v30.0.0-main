# auto_icon_generator.py - Automatically creates icons on first run
from pathlib import Path

def check_and_create_icons():
    """Check if icons exist, create them if missing. Returns True if icons are available."""
    assets_dir = Path("assets")
    
    # List of required icons
    required_icons = [
        "start.png", "pause.png", "stop.png", "rerun.png", 
        "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"
    ]
    
    # Check if assets folder exists and has all icons
    if assets_dir.exists():
        missing_icons = [icon for icon in required_icons if not (assets_dir / icon).exists()]
        if not missing_icons:
            print("✅ All icons found")
            return True
        else:
            print(f"⚠️ Missing {len(missing_icons)} icons: {', '.join(missing_icons)}")
    else:
        print("📁 Assets folder not found")
        missing_icons = required_icons
    
    # Create missing icons
    print("🎨 Creating missing icons...")
    return create_simple_icons_auto()

def create_simple_icons_auto():
    """Create simple icons automatically without user interaction."""
    try:
        from PIL import Image, ImageDraw
        print("📦 PIL found, creating quality icons...")
    except ImportError:
        try:
            print("📦 Installing PIL for icon generation...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            from PIL import Image, ImageDraw
            print("✅ PIL installed successfully")
        except Exception as e:
            print(f"⚠️ Could not install PIL: {e}")
            return create_minimal_icons()
    
    # Create assets folder
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Icon definitions
    icons = {
        "start.png": {"color": (40, 167, 69), "shape": "triangle"},
        "pause.png": {"color": (255, 193, 7), "shape": "bars"},
        "stop.png": {"color": (220, 53, 69), "shape": "square"},
        "rerun.png": {"color": (0, 123, 255), "shape": "circle"},
        "open.png": {"color": (111, 66, 193), "shape": "diamond"},
        "browse.png": {"color": (23, 162, 184), "shape": "folder"},
        "patterns.png": {"color": (253, 126, 20), "shape": "grid"},
        "exit.png": {"color": (108, 117, 125), "shape": "x"},
        "fullscreen.png": {"color": (32, 201, 151), "shape": "corners"}
    }
    
    success_count = 0
    
    for filename, config in icons.items():
        try:
            # Create 16x16 image with transparent background
            img = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            color = config["color"]
            shape = config["shape"]
            
            # Draw shapes
            if shape == "triangle":  # Start/Play
                draw.polygon([(3, 3), (3, 13), (13, 8)], fill=color)
            elif shape == "bars":  # Pause
                draw.rectangle([4, 3, 6, 13], fill=color)
                draw.rectangle([10, 3, 12, 13], fill=color)
            elif shape == "square":  # Stop
                draw.rectangle([4, 4, 12, 12], fill=color)
            elif shape == "circle":  # Rerun/Refresh
                draw.ellipse([2, 2, 14, 14], outline=color, width=2)
                draw.polygon([(12, 4), (12, 8), (14, 6)], fill=color)
            elif shape == "diamond":  # Open/File
                draw.polygon([(8, 2), (13, 7), (8, 14), (3, 7)], outline=color, width=2)
                draw.line([(6, 5), (10, 5)], fill=color, width=1)
                draw.line([(6, 8), (10, 8)], fill=color, width=1)
            elif shape == "folder":  # Browse
                draw.rectangle([2, 6, 14, 13], fill=color)
                draw.polygon([(2, 6), (2, 4), (6, 4), (8, 6)], fill=color)
            elif shape == "grid":  # Patterns
                for i in range(3):
                    for j in range(3):
                        x = 3 + i * 4
                        y = 3 + j * 4
                        draw.rectangle([x, y, x+2, y+2], fill=color)
            elif shape == "x":  # Exit
                draw.line([(4, 4), (12, 12)], fill=color, width=2)
                draw.line([(12, 4), (4, 12)], fill=color, width=2)
            elif shape == "corners":  # Fullscreen
                # Four corner brackets
                draw.line([(2, 2), (2, 5)], fill=color, width=2)
                draw.line([(2, 2), (5, 2)], fill=color, width=2)
                draw.line([(14, 2), (14, 5)], fill=color, width=2)
                draw.line([(14, 2), (11, 2)], fill=color, width=2)
                draw.line([(2, 14), (2, 11)], fill=color, width=2)
                draw.line([(2, 14), (5, 14)], fill=color, width=2)
                draw.line([(14, 14), (14, 11)], fill=color, width=2)
                draw.line([(14, 14), (11, 14)], fill=color, width=2)
            
            # Save the image
            file_path = assets_dir / filename
            img.save(file_path, 'PNG')
            success_count += 1
            
        except Exception as e:
            print(f"⚠️ Failed to create {filename}: {e}")
            return create_minimal_icons()
    
    if success_count == len(icons):
        print(f"✅ Created {success_count} quality icons")
        return True
    else:
        return create_minimal_icons()

def create_minimal_icons():
    """Create minimal valid PNG files as fallback."""
    print("🔧 Creating minimal icons as fallback...")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Minimal valid 16x16 PNG file data
    minimal_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x10,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0xF3, 0xFF, 0x61,
        0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54,
        0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01,
        0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00,
        0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    
    icon_files = [
        "start.png", "pause.png", "stop.png", "rerun.png", 
        "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"
    ]
    
    success_count = 0
    for filename in icon_files:
        try:
            file_path = assets_dir / filename
            with open(file_path, 'wb') as f:
                f.write(minimal_png)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    if success_count == len(icon_files):
        print(f"✅ Created {success_count} minimal icons")
        return True
    else:
        print(f"❌ Only created {success_count}/{len(icon_files)} icons")
        return False

if __name__ == "__main__":
    # Test the auto icon system
    success = check_and_create_icons()
    if success:
        print("🎉 Icon system ready!")
    else:
        print("❌ Icon system failed")
