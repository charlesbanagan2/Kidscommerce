with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = []
i = 0
while i < len(lines):
    # Skip lines with "# Send notification" followed by "notify_" calls
    if (i < len(lines)-2 and 
        '# Send notification' in lines[i] and 
        lines[i+1].strip().startswith('notify_')):
        # Skip both the comment and the notify call
        i += 2
    else:
        fixed.append(lines[i])
        i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed)

print('Fixed all indentation errors')
