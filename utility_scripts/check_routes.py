import sys
sys.path.insert(0, 'C:\\Users\\mnban\\Documents\\kids\\backend')

with open('C:\\Users\\mnban\\Documents\\kids\\backend\\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
print("Found product_detail definitions at:")
for i, line in enumerate(lines, 1):
    if 'def product_detail' in line:
        print(f"\nLine {i}: {line.rstrip()}")
        # Show context (5 lines before and after)
        start = max(0, i-6)
        end = min(len(lines), i+5)
        print("Context:")
        for j in range(start, end):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1}: {lines[j].rstrip()}")
