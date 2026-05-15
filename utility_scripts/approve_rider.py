#!/usr/bin/env python3
"""Approve a rider account by updating user status"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import update_data_by_id, get_data

def approve_rider(email):
    """Approve a rider account by email"""
    # Find user by email
    users = get_data('user', filters={'email': email})
    
    if not users:
        print(f"User with email {email} not found")
        return False
    
    user = users[0]
    user_id = user.get('id')
    
    print(f"Found user: {user.get('first_name')} {user.get('last_name')} (ID: {user_id})")
    print(f"Current status: {user.get('status')}")
    
    # Update status to approved
    update_data = {
        'status': 'approved'
    }
    
    success = update_data_by_id('user', user_id, update_data)
    
    if success:
        print(f"✅ User {email} has been approved!")
        return True
    else:
        print(f"❌ Failed to approve user {email}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python approve_rider.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    approve_rider(email)
