#!/usr/bin/env python3
import os

# Change to backend directory
os.chdir(r'c:\Users\mnban\OneDrive\Desktop\kids\backend')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix corrupted emojis
replacements = {
    'ðŸ›ï¸': '🛒',      # shopping cart
    'ðŸ'³': '💳',       # credit card
    'ðŸ"¦': '📦',       # package
    'ðŸ'¶': '👶',       # baby
    'ðŸ'§': '👧',       # girl
    'ðŸ'¦': '👦',       # boy
    'ðŸ"§': '📧',       # email
    'ðŸ"ž': '📞',       # phone
    'ðŸ"‹': '📋',       # clipboard
    'ðŸ'¡': '💡',       # lightbulb
    'ðŸŽ': '🎁',        # gift
    'âœ¨': '✨',        # sparkles
    'â­': '⭐',         # star
    'â†'': '→',         # arrow
}

count = 0
for old, new in replacements.items():
    occurrences = content.count(old)
    if occurrences > 0:
        content = content.replace(old, new)
        count += occurrences
        print(f"  Replaced '{old}' → '{new}' ({occurrences} times)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Successfully fixed {count} corrupted emoji characters in app.py!")
