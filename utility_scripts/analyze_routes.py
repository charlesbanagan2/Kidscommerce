with open('C:\\Users\\mnban\\Documents\\kids\\backend\\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines in app.py: {total_lines}")
print("\n" + "="*80)

# Find all product_detail definitions
print("\nAll 'def product_detail' occurrences:")
for i, line in enumerate(lines, 1):
    if 'def product_detail' in line:
        print(f"  Line {i}: {line.strip()}")

print("\n" + "="*80)
print("\nContext around line 7874 (where error occurred):")
start = max(0, 7864)
end = min(len(lines), 7884)
for i in range(start, end):
    marker = ">>>" if i == 7873 else "   "
    print(f"{marker} {i+1}: {lines[i].rstrip()}")

# Write output to file
with open('C:\\Users\\mnban\\Documents\\kids\\route_analysis.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total lines: {total_lines}\n\n")
    out.write("All 'def product_detail' occurrences:\n")
    for i, line in enumerate(lines, 1):
        if 'def product_detail' in line:
            out.write(f"Line {i}: {line.strip()}\n")
            # Show 20 lines of context
            ctx_start = max(0, i-5)
            ctx_end = min(len(lines), i+15)
            out.write("Context:\n")
            for j in range(ctx_start, ctx_end):
                out.write(f"  {j+1}: {lines[j].rstrip()}\n")
            out.write("\n" + "-"*80 + "\n\n")

print("\nFull analysis written to route_analysis.txt")
