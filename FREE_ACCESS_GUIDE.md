# Free Access Account Guide

This guide explains how to enable free access for an account, allowing downloads without payment.

## What is Free Access?

When a user account has `has_free_access` set to `True`, they can download enhanced photos without going through the Stripe payment process. The system will automatically grant download permissions for these users.

## Methods to Enable Free Access

### Method 1: Using the Admin API Endpoint (Recommended)

1. **Set up an admin secret key** in your environment variables:
   ```bash
   export ADMIN_SECRET_KEY='your-secret-key-here'
   ```
   
   Or add it to your Render environment variables:
   - Go to your Render dashboard
   - Select your service
   - Go to Environment tab
   - Add: `ADMIN_SECRET_KEY` = `your-secret-key-here`

2. **Enable free access via API**:
   ```bash
   curl -X POST https://your-domain.com/api/admin/set-free-access \
     -H "Content-Type: application/json" \
     -H "X-Admin-Secret: your-secret-key-here" \
     -d '{
       "email": "user@example.com",
       "has_free_access": true
     }'
   ```

3. **Disable free access**:
   ```bash
   curl -X POST https://your-domain.com/api/admin/set-free-access \
     -H "Content-Type: application/json" \
     -H "X-Admin-Secret: your-secret-key-here" \
     -d '{
       "email": "user@example.com",
       "has_free_access": false
     }'
   ```

### Method 2: Direct Database Update (PostgreSQL)

If you have direct database access:

1. **Connect to your PostgreSQL database** (via Render dashboard or psql)

2. **Update the user**:
   ```sql
   UPDATE "user" 
   SET has_free_access = TRUE 
   WHERE email = 'user@example.com';
   ```

3. **Verify the change**:
   ```sql
   SELECT id, email, has_free_access 
   FROM "user" 
   WHERE email = 'user@example.com';
   ```

### Method 3: Using Python Script

Create a script `enable_free_access.py`:

```python
import os
from app import app, db
from models import User

with app.app_context():
    email = 'user@example.com'  # Change this to your email
    user = User.query.filter_by(email=email).first()
    
    if user:
        user.has_free_access = True
        db.session.commit()
        print(f"Free access enabled for {email}")
    else:
        print(f"User {email} not found")
```

Run it:
```bash
python enable_free_access.py
```

## How It Works

1. **Payment Check**: When a user with free access tries to download photos:
   - The `/api/payment/check-status` endpoint returns `paid: true` immediately
   - No payment record is required

2. **Checkout Session**: When creating a checkout session:
   - If user has free access, the endpoint returns `free_access: true`
   - A payment record with `amount: 0` and `status: 'completed'` is created for tracking
   - The frontend proceeds directly to download

3. **Frontend**: The JavaScript automatically detects free access and skips the payment flow

## Security Notes

- The admin endpoint requires `ADMIN_SECRET_KEY` to be set
- Use a strong, random secret key
- Never commit the secret key to version control
- Consider restricting the admin endpoint by IP in production

## Testing Free Access

1. Enable free access for your test account
2. Upload and enhance photos
3. Try to download - it should work without payment
4. Check the browser console for "Free access granted" messages

## Troubleshooting

- **Migration**: The `has_free_access` column is automatically added on startup if missing
- **Default Value**: New users have `has_free_access = False` by default
- **Database**: If you see errors about missing column, restart the app to trigger migration

