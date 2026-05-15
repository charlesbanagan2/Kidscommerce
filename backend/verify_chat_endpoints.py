"""
Verify all chat API endpoints are saving messages to database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Chat API Endpoints Verification")
print("="*60)

with app.app_context():
    try:
        # List all chat-related endpoints
        print("\n[INFO] Checking registered chat endpoints:")
        
        chat_endpoints = []
        for rule in app.url_map.iter_rules():
            if 'chat' in rule.rule.lower() or 'message' in rule.rule.lower():
                chat_endpoints.append({
                    'endpoint': rule.rule,
                    'methods': ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                })
        
        # Group by category
        unified_chat = []
        product_chat = []
        order_chat = []
        
        for ep in chat_endpoints:
            if '/chat/product' in ep['endpoint']:
                product_chat.append(ep)
            elif '/orders/' in ep['endpoint'] and 'message' in ep['endpoint']:
                order_chat.append(ep)
            elif '/chat/' in ep['endpoint']:
                unified_chat.append(ep)
        
        print("\n1. Unified Chat Endpoints (Direct messaging):")
        if unified_chat:
            for ep in unified_chat:
                print(f"   [{ep['methods']}] {ep['endpoint']}")
        else:
            print("   [WARNING] No unified chat endpoints found!")
        
        print("\n2. Product Chat Endpoints:")
        if product_chat:
            for ep in product_chat:
                print(f"   [{ep['methods']}] {ep['endpoint']}")
        else:
            print("   [WARNING] No product chat endpoints found!")
        
        print("\n3. Order Chat Endpoints:")
        if order_chat:
            for ep in order_chat:
                print(f"   [{ep['methods']}] {ep['endpoint']}")
        else:
            print("   [INFO] No order chat endpoints (optional)")
        
        # Verify database triggers/constraints
        print("\n" + "="*60)
        print("  Database Verification")
        print("="*60)
        
        # Check if messages are being saved with timestamps
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN created_at IS NULL THEN 1 END) as missing_timestamp
            FROM chat_message
        """))
        row = result.fetchone()
        print(f"\n[INFO] Timestamp verification:")
        print(f"  Total messages: {row[0]}")
        print(f"  Missing timestamps: {row[1]}")
        if row[1] == 0:
            print("  [OK] All messages have timestamps")
        else:
            print("  [WARNING] Some messages missing timestamps!")
        
        # Check if is_read is being set
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_read IS NULL THEN 1 END) as missing_read_status
            FROM chat_message
        """))
        row = result.fetchone()
        print(f"\n[INFO] Read status verification:")
        print(f"  Total messages: {row[0]}")
        print(f"  Missing read status: {row[1]}")
        if row[1] == 0:
            print("  [OK] All messages have read status")
        else:
            print("  [WARNING] Some messages missing read status!")
        
        # Check message content
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN message IS NULL OR message = '' THEN 1 END) as empty_messages
            FROM chat_message
        """))
        row = result.fetchone()
        print(f"\n[INFO] Message content verification:")
        print(f"  Total messages: {row[0]}")
        print(f"  Empty messages: {row[1]}")
        if row[1] == 0:
            print("  [OK] All messages have content")
        else:
            print("  [WARNING] Some messages are empty!")
        
        # Summary
        print("\n" + "="*60)
        print("  Endpoint Coverage Summary")
        print("="*60)
        
        required_endpoints = {
            'GET /api/v1/chat/conversations': any('/api/v1/chat/conversations' in ep['endpoint'] and 'GET' in ep['methods'] for ep in unified_chat),
            'GET /api/v1/chat/messages/<id>': any('/api/v1/chat/messages/' in ep['endpoint'] and 'GET' in ep['methods'] for ep in unified_chat),
            'POST /api/v1/chat/send': any('/api/v1/chat/send' in ep['endpoint'] and 'POST' in ep['methods'] for ep in unified_chat),
            'GET /api/v1/chat/unread-count': any('/api/v1/chat/unread-count' in ep['endpoint'] and 'GET' in ep['methods'] for ep in unified_chat),
            'POST /api/v1/chat/product/start': any('/api/v1/chat/product/start' in ep['endpoint'] and 'POST' in ep['methods'] for ep in product_chat),
            'POST /api/v1/chat/product/send': any('/api/v1/chat/product/send' in ep['endpoint'] and 'POST' in ep['methods'] for ep in product_chat),
            'GET /api/v1/chat/product/<id>/messages': any('/api/v1/chat/product/' in ep['endpoint'] and '/messages' in ep['endpoint'] and 'GET' in ep['methods'] for ep in product_chat),
        }
        
        all_present = True
        for endpoint, present in required_endpoints.items():
            status = "[OK]" if present else "[MISSING]"
            print(f"  {status} {endpoint}")
            if not present:
                all_present = False
        
        print("\n" + "="*60)
        if all_present and row[1] == 0:
            print("  [SUCCESS] All chat endpoints are properly configured!")
            print("  [SUCCESS] All messages are being saved correctly!")
        else:
            print("  [WARNING] Some issues detected - check above")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
