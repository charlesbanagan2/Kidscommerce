from PIL import Image
import os

# Source logo
source_logo = r"C:\Users\mnban\OneDrive\Desktop\kids\backend\static\uploads\logo_ulit.png"

# Android icon sizes
icon_sizes = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192
}

# Base path for Android resources
base_path = r"C:\Users\mnban\OneDrive\Desktop\kids\mobile_app\android\app\src\main\res"

# Open and process the logo
img = Image.open(source_logo)

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Create icons for each size
for folder, size in icon_sizes.items():
    # Resize image
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Output path
    output_path = os.path.join(base_path, folder, 'ic_launcher.png')
    
    # Save the icon
    resized.save(output_path, 'PNG')
    print(f"Created {folder}/ic_launcher.png ({size}x{size})")

print("\n✓ All app icons updated successfully!")
print("Rebuild your Flutter app to see the new icon.")
