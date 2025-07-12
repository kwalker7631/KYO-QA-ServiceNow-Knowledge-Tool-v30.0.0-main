# auto_icon_system.py - Automatically creates all required UI icons.
# This module is called by run.py before the main application starts.

from pathlib import Path

def check_and_create_icons():
    """
    Checks if the 'assets' folder and all required icons exist.
    If not, it attempts to create them using the Pillow library.
    Returns True if all assets are ready, False otherwise.
    """
    assets_dir = Path("assets")
    required_icons = [
        "start.png", "pause.png", "stop.png", "rerun.png",
        "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"
    ]

    # Check if everything already exists
    if assets_dir.is_dir() and all((assets_dir / icon).exists() for icon in required_icons):
        return True

    print("🎨 UI assets are missing. Attempting to generate them...")
    assets_dir.mkdir(exist_ok=True)

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("❌ ERROR: The 'Pillow' library is required to generate icons.")
        print("   Please ensure it is listed in your requirements.txt file.")
        return False

    # Icon definitions: {filename: {color, shape}}
    icon_defs = {
        "start.png": {"c": (40, 167, 69), "s": "triangle"},
        "pause.png": {"c": (255, 193, 7), "s": "bars"},
        "stop.png": {"c": (220, 53, 69), "s": "square"},
        "rerun.png": {"c": (0, 123, 255), "s": "circle"},
        "open.png": {"c": (111, 66, 193), "s": "diamond"},
        "browse.png": {"c": (23, 162, 184), "s": "folder"},
        "patterns.png": {"c": (253, 126, 20), "s": "grid"},
        "exit.png": {"c": (108, 117, 125), "s": "x"},
        "fullscreen.png": {"c": (32, 201, 151), "s": "corners"},
    }

    created_count = 0
    for filename, config in icon_defs.items():
        file_path = assets_dir / filename
        if file_path.exists():
            created_count += 1
            continue
        try:
            img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            color, shape = config["c"], config["s"]

            # Draw shapes based on config
            if shape == "triangle":
                draw.polygon([(3, 3), (3, 13), (13, 8)], fill=color)
            elif shape == "bars":
                draw.rectangle([4, 3, 6, 13], fill=color)
                draw.rectangle([10, 3, 12, 13], fill=color)
            elif shape == "square":
                draw.rectangle([4, 4, 12, 12], fill=color)
            elif shape == "circle":
                draw.ellipse([2, 2, 14, 14], outline=color, width=2)
                draw.polygon([(12, 4), (12, 8), (14, 6)], fill=color)
            elif shape == "diamond":
                draw.polygon([(8, 2), (13, 7), (8, 14), (3, 7)], outline=color, width=2)
            elif shape == "folder":
                draw.rectangle([2, 6, 14, 13], fill=color)
                draw.polygon([(2, 6), (2, 4), (6, 4), (8, 6)], fill=color)
            elif shape == "grid":
                for i in range(3):
                    for j in range(3):
                        draw.rectangle([3 + i * 4, 3 + j * 4, 5 + i * 4, 5 + j * 4], fill=color)
            elif shape == "x":
                draw.line([(4, 4), (12, 12)], fill=color, width=2)
                draw.line([(12, 4), (4, 12)], fill=color, width=2)
            elif shape == "corners":
                draw.line([(2, 2), (2, 5), (5, 2)], fill=color, width=2)
                draw.line([(14, 2), (14, 5), (11, 2)], fill=color, width=2)
                draw.line([(2, 14), (2, 11), (5, 14)], fill=color, width=2)
                draw.line([(14, 14), (14, 11), (11, 14)], fill=color, width=2)

            img.save(file_path, 'PNG')
            created_count += 1
        except Exception as e:
            print(f"⚠️ Failed to create icon '{filename}': {e}")

    if created_count == len(required_icons):
        print(f"✅ Successfully created {created_count} icons.")
        return True
    else:
        print(f"❌ Failed to create all icons. {created_count}/{len(required_icons)} are ready.")
        return False

if __name__ == '__main__':
    check_and_create_icons()
