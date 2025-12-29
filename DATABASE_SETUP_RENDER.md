# Database Setup for Render Deployment

## Current Setup

Your app currently uses **SQLite** (`sqlite:///airbnb_enhancer.db`), which works for development but has limitations on Render.

## ⚠️ SQLite on Render - Important Considerations

### Limitations:

1. **Ephemeral Storage**: Render's free tier uses ephemeral storage
   - Data can be lost when the service restarts
   - Database file is stored in the filesystem (not persistent)

2. **Single Instance**: SQLite doesn't work well with multiple instances
   - If you scale to multiple instances, each has its own database
   - Data won't sync between instances

3. **File System**: SQLite is file-based
   - Not ideal for production web applications
   - Can cause issues with concurrent writes

### ✅ SQLite is OK for:
- Testing/development
- Low-traffic personal projects
- Prototyping
- When you're just getting started

### ❌ SQLite is NOT recommended for:
- Production applications
- Applications with multiple users
- Applications that need data persistence
- Applications that might scale

## Option 1: Keep SQLite (Quick Start) ⚡

**For now, SQLite will work**, but be aware of the limitations above.

### Setup:
- **No action needed** - SQLite will work automatically
- Database file will be created in the `instance/` folder
- **Warning**: Data may be lost on service restarts (free tier)

### When to Upgrade:
- When you have real users
- When data persistence is critical
- When you need to scale

## Option 2: Use PostgreSQL (Recommended for Production) 🚀

PostgreSQL is the recommended database for production on Render.

### Step 1: Create PostgreSQL Database on Render

1. In Render Dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name**: `airbnb-enhancer-db`
   - **Database**: `airbnb_enhancer`
   - **User**: (auto-generated)
   - **Region**: Same as your web service
   - **PostgreSQL Version**: Latest (15 or 16)
   - **Plan**: Free (or paid for production)
4. Click **"Create Database"**

### Step 2: Get Database URL

1. After creation, go to your database dashboard
2. Find **"Internal Database URL"** (for Render services)
3. It looks like:
   ```
   postgresql://user:password@host:5432/dbname
   ```

### Step 3: Update Environment Variable

1. Go to your **Web Service** → **Environment** tab
2. Add/Update:
   ```
   Name: DATABASE_URL
   Value: [Paste the Internal Database URL from step 2]
   ```
3. Click **"Save Changes"**
4. Render will automatically redeploy

### Step 4: Database Migration

The app will automatically create tables on first run, but you can also do it manually:

**Option A: Automatic (Recommended)**
- Just restart your service
- Tables will be created automatically when the app starts

**Option B: Manual Migration**
If you need to migrate existing data:
1. Export data from SQLite (if you have any)
2. Import to PostgreSQL
3. Or let the app start fresh (users will need to sign up again)

## Code Changes Needed

**Good news**: Your code already supports PostgreSQL! 

The `DATABASE_URL` environment variable will automatically be used if set. Your code in `app.py` already handles this:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///airbnb_enhancer.db')
```

This means:
- If `DATABASE_URL` is set → Uses PostgreSQL
- If not set → Falls back to SQLite

## Recommendation

### For Now (Getting Started):
✅ **Keep SQLite** - It will work for testing and initial deployment
- No additional setup needed
- Good for testing the deployment
- You can upgrade later

### For Production:
✅ **Switch to PostgreSQL** - When you're ready for production
- More reliable
- Data persistence
- Better performance
- Scalable

## Migration Path

1. **Start with SQLite** (now)
   - Deploy and test everything
   - Make sure the app works

2. **Upgrade to PostgreSQL** (when ready)
   - Create PostgreSQL database on Render
   - Set `DATABASE_URL` environment variable
   - Redeploy (tables created automatically)
   - Users will need to sign up again (or migrate data)

## PostgreSQL Setup Checklist

If you choose PostgreSQL:

- [ ] Create PostgreSQL database on Render
- [ ] Copy Internal Database URL
- [ ] Add `DATABASE_URL` to Web Service environment variables
- [ ] Save and wait for redeploy
- [ ] Verify tables are created (check logs)
- [ ] Test user registration
- [ ] Test photo upload/enhancement
- [ ] Test payment flow

## Cost Comparison

### SQLite:
- ✅ Free (included with web service)
- ❌ Data may be lost
- ❌ Not scalable

### PostgreSQL (Free Tier):
- ✅ Free (750 hours/month)
- ✅ 1 GB storage
- ✅ Data persistence
- ✅ Better for production

### PostgreSQL (Paid):
- $7/month for more storage and better performance

## My Recommendation

**For your first deployment:**
1. ✅ **Start with SQLite** - Get everything working first
2. ✅ Test the full deployment
3. ✅ Make sure payments, uploads, etc. all work
4. ✅ Then upgrade to PostgreSQL when you're ready for production

This way you can:
- Deploy quickly
- Test everything
- Upgrade database later without code changes

## Quick Answer

**Is SQLite OK for now?**
- ✅ **Yes, for testing/initial deployment**
- ⚠️ **But upgrade to PostgreSQL for production**

Your code already supports both - just set `DATABASE_URL` when ready!

