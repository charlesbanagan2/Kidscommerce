with open(r'C:\Users\mnban\Documents\kids\backend\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 7874 area
start = 7860
end = 7930

print("Lines around 7874:")
for i in range(start, min(end, len(lines))):
    marker = ">>> " if i == 7873 else "    "
    print(f"{marker}{i+1}: {lines[i].rstrip()}")

# Save to file for review
with open(r'C:\Users\mnban\Documents\kids\line_7874_context.txt', 'w', encoding='utf-8') as f:
    for i in range(max(0, 7850), min(7950, len(lines))):
        f.write(f"{i+1}: {lines[i]}")

print("\nContext saved to line_7874_context.txt")
