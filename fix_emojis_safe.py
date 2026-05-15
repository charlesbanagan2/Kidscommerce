#!/usr/bin/env python3
# Binary-safe emoji fix script

file_path = r'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py'

with open(file_path, 'rb') as f:
    content = f.read()

print(f"File size before: {len(content)} bytes")

# Use byte sequences instead of strings
fixes = [
    # (old_bytes, new_bytes)
    (b'\xc3\xb0\xc2\x9f\xc2\xbb\xc2\xaf\xc2\xb8', b'\xf0\x9f\x9b\x92'),  # shopping cart
    (b'\xc3\xb0\xc2\x9f\xc2\xa2\xc2\xb3', b'\xf0\x9f\x92\xb3'),           # credit card
    (b'\xc3\xb0\xc2\x9f\xc2\x92\xc2\xa6', b'\xf0\x9f\x93\xa6'),           # package
    (b'\xc3\xb0\xc2\x9f\xc2\xa2\xc2\xb6', b'\xf0\x9f\x91\xb6'),           # baby
    (b'\xc3\xb0\xc2\x9f\xc2\xa2\xc2\xa7', b'\xf0\x9f\x91\xa7'),           # girl
    (b'\xc3\xb0\xc2\x9f\xc2\xa2\xc2\xa6', b'\xf0\x9f\x91\xa6'),           # boy
    (b'\xc3\xb0\xc2\x9f\xc2\x92\xc2\xa7', b'\xf0\x9f\x93\xa7'),           # email
    (b'\xc3\xb0\xc2\x9f\xc2\x92\xc2\x9e', b'\xf0\x9f\x93\x9e'),           # phone
    (b'\xc3\xb0\xc2\x9f\xc2\x92\xc2\x8b', b'\xf0\x9f\x93\x8b'),           # clipboard
    (b'\xc3\xb0\xc2\x9f\xc2\xa2\xc2\xa1', b'\xf0\x9f\x92\xa1'),           # lightbulb
    (b'\xc3\xb0\xc2\x9f\xc2\x8e', b'\xf0\x9f\x8e\x81'),                   # gift
    (b'\xc3\xa2\xc2\x9c\xc2\xa8', b'\xe2\x9c\xa8'),                       # sparkles
    (b'\xc3\xa2\xc2\xad', b'\xe2\xad\x90'),                               # star
    (b'\xc3\xa2\xc2\x86\xc2\x92', b'\xe2\x86\x92'),                       # arrow
]

count = 0
for old_bytes, new_bytes in fixes:
    matches = content.count(old_bytes)
    if matches > 0:
        content = content.replace(old_bytes, new_bytes)
        count += matches
        print(f"  Fixed {matches} occurrences")

with open(file_path, 'wb') as f:
    f.write(content)

print(f"File size after: {len(content)} bytes")
print(f"✅ Applied {count} fixes total!")
