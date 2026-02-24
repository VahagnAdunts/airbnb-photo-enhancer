# Anonymous User Tracking Migration

## Overview
This update adds tracking for anonymous (non-registered) users who enhance photos. Each anonymous user is identified by a unique session ID based on their browser session, IP address, and user agent.

## Database Changes
A new column `anonymous_session_id` has been added to the `EnhancedImage` model:

```python
anonymous_session_id = db.Column(db.String(255), nullable=True, index=True)
```

## Migration Steps

### Option 1: Using Flask-Migrate (Recommended)
If you're using Flask-Migrate:

```bash
flask db migrate -m "Add anonymous_session_id to EnhancedImage"
flask db upgrade
```

### Option 2: Manual SQL Migration
If you need to add the column manually:

```sql
ALTER TABLE enhanced_image ADD COLUMN anonymous_session_id VARCHAR(255);
CREATE INDEX ix_enhanced_image_anonymous_session_id ON enhanced_image(anonymous_session_id);
```

### Option 3: Python Script
Run this Python script to add the column if it doesn't exist:

```python
from app import app, db
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('enhanced_image')]
    
    if 'anonymous_session_id' not in columns:
        db.engine.execute(text('ALTER TABLE enhanced_image ADD COLUMN anonymous_session_id VARCHAR(255)'))
        db.engine.execute(text('CREATE INDEX ix_enhanced_image_anonymous_session_id ON enhanced_image(anonymous_session_id)'))
        print("Column added successfully!")
    else:
        print("Column already exists!")
```

## Features Added

1. **Anonymous Session Tracking**: Each anonymous user gets a unique session ID based on:
   - Flask session ID
   - IP address (hashed)
   - User agent (hashed)

2. **Admin Dashboard Updates**:
   - New statistics showing anonymous users and their photo counts
   - List of all anonymous users with their session IDs
   - Click on a session ID to view all photos for that anonymous user

3. **Photo Viewing**: Admins can view photos from anonymous users just like registered users, with before/after comparison.

## Notes

- The `anonymous_session_id` is only set when `user_id` is `None` (user is not authenticated)
- Anonymous session IDs are consistent across requests for the same browser/device
- The session ID is a 32-character hexadecimal string
- All existing photos will have `anonymous_session_id = NULL` (they were created before this feature)
