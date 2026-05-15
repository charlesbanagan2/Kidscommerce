with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'def product_detail' in line:
            print(f'Line {i+1}: {line.rstrip()}')
