# Setting Up Admin Access in Render

## Method 1: Using Render Dashboard (Easiest)

1. **Go to your Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Log in to your account

2. **Find your PostgreSQL Database**
   - Click on "Databases" in the left sidebar
   - Find your PostgreSQL database (the one connected to your app)
   - Click on it to open the database details

3. **Open the Database Shell**
   - In the database page, look for the "Connect" or "Shell" button
   - Click on it to open a database shell/terminal

4. **Run the SQL Command**
   ```sql
   UPDATE "user" 
   SET is_admin = TRUE 
   WHERE email = 'elevance.art@gmail.com';
   ```

5. **Verify the Update**
   ```sql
   SELECT id, username, email, is_admin 
   FROM "user" 
   WHERE email = 'elevance.art@gmail.com';
   ```
   You should see `is_admin = t` (true) for your user.

## Method 2: Using psql Command Line

If you have `psql` installed locally:

1. **Get your Database Connection String**
   - In Render dashboard, go to your PostgreSQL database
   - Find the "Internal Database URL" or "Connection String"
   - It will look like: `postgresql://user:password@hostname:port/dbname`

2. **Connect to the Database**
   ```bash
   psql "postgresql://user:password@hostname:port/dbname"
   ```

3. **Run the SQL Command**
   ```sql
   UPDATE "user" 
   SET is_admin = TRUE 
   WHERE email = 'elevance.art@gmail.com';
   ```

4. **Verify and Exit**
   ```sql
   SELECT id, username, email, is_admin FROM "user" WHERE email = 'elevance.art@gmail.com';
   \q
   ```

## Method 3: Using Python Script (Alternative)

Create a temporary script `set_admin.py`:

```python
import os
from app import app, db
from models import User

# Admin email
YOUR_EMAIL = 'elevance.art@gmail.com'

with app.app_context():
    user = User.query.filter_by(email=YOUR_EMAIL).first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"✅ Admin access granted to {user.email} (ID: {user.id})")
    else:
        print(f"❌ User with email {YOUR_EMAIL} not found")
```

Then run it:
```bash
python set_admin.py
```

## Method 4: Using Render Shell (Recommended)

1. **Go to your Web Service** (not the database)
   - In Render dashboard, click on your web service
   - Click on "Shell" tab (or look for a terminal/shell option)

2. **Run Python Command**
   ```bash
   python3 -c "
   from app import app, db
   from models import User
   with app.app_context():
       user = User.query.filter_by(email='elevance.art@gmail.com').first()
       if user:
           user.is_admin = True
           db.session.commit()
           print(f'Admin granted to {user.email}')
       else:
           print('User not found')
   "
   ```

## Quick Reference

**Important Notes:**
- ✅ Admin email configured: `elevance.art@gmail.com`
- The table name is `"user"` (with quotes) because `user` is a reserved keyword in PostgreSQL
- After setting `is_admin = TRUE`, you need to **log out and log back in** for the change to take effect
- You can verify admin status by checking the database or trying to access `/admin`

## Troubleshooting

### "relation 'user' does not exist"
- Make sure you're connected to the correct database
- The table might be named differently - check with: `\dt` (list tables)

### "permission denied"
- Make sure you're using the correct database user credentials
- Check that you have write permissions

### Changes not taking effect
- Log out and log back in to your account (elevance.art@gmail.com)
- Clear your browser cache/cookies
- Restart your Render service (if needed)

## Verify Admin Access

After setting `is_admin = TRUE`:

1. **Log out** of your account
2. **Log back in**
3. **Visit**: `https://your-domain.com/admin`
4. You should see the admin dashboard with all users

If you see "Access Denied", double-check:
- Your email matches exactly (case-insensitive)
- You logged out and back in
- The database update was successful
