from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('SUPABASE_DB_URL'))

with engine.connect() as conn:
    # Check total messages
    result = conn.execute(text('SELECT COUNT(*) FROM chat_message'))
    total = result.fetchone()[0]
    print(f'Total messages in database: {total}')
    
    # Check last 10 messages
    result = conn.execute(text('''
        SELECT id, sender_id, receiver_id, message, created_at 
        FROM chat_message 
        ORDER BY created_at DESC 
        LIMIT 10
    '''))
    
    print('\nLast 10 messages:')
    print('-' * 80)
    for row in result:
        msg_preview = row[3][:50] if len(row[3]) > 50 else row[3]
        print(f'ID: {row[0]}, From: {row[1]} to To: {row[2]}')
        print(f'Message: {msg_preview}')
        print(f'Time: {row[4]}')
        print('-' * 80)
    
    # Check if there are any messages between specific users
    print('\nChecking for messages between users...')
    result = conn.execute(text('''
        SELECT DISTINCT sender_id, receiver_id, COUNT(*) as msg_count
        FROM chat_message
        GROUP BY sender_id, receiver_id
        ORDER BY msg_count DESC
        LIMIT 10
    '''))
    
    print('\nConversations (sender to receiver):')
    for row in result:
        print(f'User {row[0]} to User {row[1]}: {row[2]} messages')
