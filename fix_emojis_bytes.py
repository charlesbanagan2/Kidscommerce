#!/usr/bin/env python3
import re

# Read the file as bytes
with open(r'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py', 'rb') as f:
    content = f.read()

print(f"Original file size: {len(content)} bytes")

# Create a series of byte-level replacements
replacements = [
    # Corrupted emoji bytes to proper emoji bytes
    (b'ðŸ›ï¸', '🛒'.encode('utf-8')),      # shopping cart
    (b'ðŸ\x92³', '💳'.encode('utf-8')),       # credit card (different encoding)
    (b'ðŸ'³', '💳'.encode('utf-8')),       # credit card
    (b'ðŸ"¦', '📦'.encode('utf-8')),       # package
    (b'ðŸŽ', '🎁'.encode('utf-8')),        # gift  
    (b'ðŸ'¶', '👶'.encode('utf-8')),       # baby
    (b'ðŸ'§', '👧'.encode('utf-8')),       # girl
    (b'ðŸ'¦', '👦'.encode('utf-8')),       # boy
    (b'ðŸ"§', '📧'.encode('utf-8')),       # email
    (b'ðŸ"ž', '📞'.encode('utf-8')),       # phone
    (b'ðŸ"‹', '📋'.encode('utf-8')),       # clipboard
    (b'ðŸ'¡', '💡'.encode('utf-8')),       # lightbulb
    (b'âœ¨', '✨'.encode('utf-8')),        # sparkles
    (b'â­', '⭐'.encode('utf-8')),         # star
    (b'â†'', '→'.encode('utf-8')),         # arrow
]

count = 0
for old_bytes, new_bytes in replacements:
    old_count = content.count(old_bytes)
    if old_count > 0:
        content = content.replace(old_bytes, new_bytes)
        count += old_count
        print(f"Replaced {old_count} occurrences")

# Write back
with open(r'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py', 'wb') as f:
    f.write(content)

print(f"\n✅ Fixed {count} corrupted characters!")
print(f"New file size: {len(content)} bytes")
