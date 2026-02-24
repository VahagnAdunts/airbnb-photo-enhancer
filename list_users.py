#!/usr/bin/env python3
"""
Script to list all registered users from the database.
Usage: python list_users.py
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def list_users():
    """List all registered users with their details"""
    with app.app_context():
        try:
            # Query all users
            users = User.query.order_by(User.created_at.desc()).all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print(f"\n{'='*80}")
            print(f"Total Registered Users: {len(users)}")
            print(f"{'='*80}\n")
            
            # Print header
            print(f"{'ID':<5} {'Username':<25} {'Email':<35} {'Created At':<20} {'Photos':<8} {'Free Access':<12}")
            print("-" * 80)
            
            # Print each user
            for user in users:
                created_str = user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A'
                free_access = 'Yes' if user.has_free_access else 'No'
                print(f"{user.id:<5} {user.username:<25} {user.email:<35} {created_str:<20} {user.images_processed:<8} {free_access:<12}")
            
            print(f"\n{'='*80}")
            print("\nSummary:")
            print(f"  - Total users: {len(users)}")
            print(f"  - Users with free access: {sum(1 for u in users if u.has_free_access)}")
            print(f"  - Total photos processed: {sum(u.images_processed for u in users)}")
            
            # Count users by signup method
            email_users = sum(1 for u in users if u.google_id is None)
            google_users = sum(1 for u in users if u.google_id is not None)
            print(f"  - Email signups: {email_users}")
            print(f"  - Google signups: {google_users}")
            
        except Exception as e:
            print(f"Error querying database: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    exit_code = list_users()
    sys.exit(exit_code)
