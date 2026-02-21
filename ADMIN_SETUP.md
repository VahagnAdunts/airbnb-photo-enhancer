# Admin Dashboard Setup Guide

## Overview

The admin dashboard allows you to view all registered users, their emails, usernames, and statistics. Access is secured and requires admin privileges.

## Setting Up Admin Access

You have two options to grant admin access:

### Option 1: Using Environment Variable (Recommended for Quick Setup)

Add your email(s) to the `ADMIN_EMAILS` environment variable:

```bash
# In your .env file or production environment variables
ADMIN_EMAILS=your-email@example.com,another-admin@example.com
```

**For Render/Heroku:**
- Go to your service dashboard
- Navigate to Environment variables
- Add: `ADMIN_EMAILS` = `your-email@example.com`

### Option 2: Using Database Flag (Permanent Solution)

Set the `is_admin` flag directly in the database:

**For PostgreSQL:**
```sql
UPDATE "user" 
SET is_admin = TRUE 
WHERE email = 'your-email@example.com';
```

**For SQLite:**
```sql
UPDATE user 
SET is_admin = 1 
WHERE email = 'your-email@example.com';
```

Or use Python:
```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(email='your-email@example.com').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"Admin access granted to {user.email}")
```

## Accessing the Admin Dashboard

1. **Log in** to your account (the one with admin privileges)
2. **Navigate** to: `https://your-domain.com/admin`
3. You'll see:
   - Total user statistics
   - Search functionality
   - Paginated list of all users with:
     - User ID
     - Username
     - Email
     - Signup method (Email/Google)
     - Registration date
     - Number of photos processed
     - Free access status

## Security Features

- ✅ Requires user to be logged in (`@login_required`)
- ✅ Checks admin privileges before allowing access
- ✅ Logs unauthorized access attempts
- ✅ Returns 403 error for non-admin users
- ✅ Supports multiple admin emails via environment variable
- ✅ Supports permanent admin flag in database

## Features

- **User Search**: Search by username or email
- **Pagination**: 50 users per page
- **Statistics Dashboard**: 
  - Total users
  - Email vs Google signups
  - Free access users
  - Total photos processed
- **User Details**: View all user information in a clean table format

## Troubleshooting

### "Access Denied" Error

If you see an access denied error:
1. Make sure you're logged in
2. Verify your email is in `ADMIN_EMAILS` environment variable, OR
3. Check that your user has `is_admin = TRUE` in the database

### Database Migration

The `is_admin` column is automatically added when the app starts. If you see errors:
1. Check application logs for migration messages
2. Manually add the column if needed (see Option 2 above)

## Best Practices

1. **Use Environment Variable** for quick setup during development
2. **Use Database Flag** for permanent admin users in production
3. **Limit Admin Emails** - only add trusted email addresses
4. **Monitor Logs** - check for unauthorized access attempts
5. **Change Defaults** - if using environment variable, use a strong, unique value
