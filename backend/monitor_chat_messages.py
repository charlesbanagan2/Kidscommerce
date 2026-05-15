"""
Real-time Chat Message Monitor
Shows messages as they are saved to the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
import time

print("="*70)
print("  REAL-TIME CHAT MESSAGE MONITOR")
print("  Press Ctrl+C to stop")
print("="*70)

with app.app_context():
    # Get initial count
    result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
    last_count = result.scalar()
    print(f"\n[INFO] Starting monitor... Current messages: {last_count}\n")
    
    try:
        while True:
            # Check for new messages
            result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
            current_count = result.scalar()
            
            if current_count > last_count:
                # New messages detected!
                new_messages = current_count - last_count
                print(f"\n[NEW] {new_messages} new message(s) detected!")
                
                # Get the new messages
                result = db.session.execute(text("""
                    SELECT 
                        cm.id,
                        cm.message,
                        cm.product_id,
                        cm.order_id,
                        cm.created_at,
                        u1.first_name || ' ' || u1.last_name as sender_name,
                        u1.role as sender_role,
                        u2.first_name || ' ' || u2.last_name as receiver_name,
                        u2.role as receiver_role,
                        p.name as product_name
                    FROM chat_message cm
                    JOIN "user" u1 ON cm.sender_id = u1.id
                    JOIN "user" u2 ON cm.receiver_id = u2.id
                    LEFT JOIN product p ON cm.product_id = p.id
                    ORDER BY cm.created_at DESC
                    LIMIT :limit
                """), {'limit': new_messages})
                
                messages = result.fetchall()
                for msg in messages:
                    msg_type = "PRODUCT" if msg[2] else ("ORDER" if msg[3] else "DIRECT")
                    timestamp = msg[4].strftime("%H:%M:%S") if msg[4] else "Unknown"
                    
                    print(f"\n  [{msg_type}] Message ID: {msg[0]}")
                    print(f"  Time: {timestamp}")
                    print(f"  From: {msg[5]} ({msg[6]})")
                    print(f"  To: {msg[7]} ({msg[8]})")
                    if msg[9]:
                        print(f"  Product: {msg[9]}")
                    print(f"  Message: {msg[1][:100]}{'...' if len(msg[1]) > 100 else ''}")
                    print(f"  " + "-"*60)
                
                last_count = current_count
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Monitor stopped")
        print(f"[INFO] Final message count: {current_count}")
        print("="*70)
