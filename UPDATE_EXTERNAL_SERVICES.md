# Step 1: Update External Service Configurations

This guide will help you update Google OAuth and Stripe webhook URLs to use your new custom domain `elevance.art`.

## Part 1: Update Google OAuth Redirect URIs

### Step 1.1: Access Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Sign in with your Google account

2. **Navigate to APIs & Services**
   - Click on **"APIs & Services"** in the left sidebar
   - Click on **"Credentials"**

3. **Find Your OAuth 2.0 Client**
   - Look for your OAuth 2.0 Client ID (the one you're using for this app)
   - Click on the **pencil icon** (Edit) next to it

### Step 1.2: Add New Redirect URIs

1. **Find "Authorized redirect URIs" section**
   - Scroll down to the **"Authorized redirect URIs"** section

2. **Add the new domain URIs**
   - Click **"+ ADD URI"** button
   - Add: `https://elevance.art/auth/google/callback`
   - Click **"+ ADD URI"** again
   - Add: `https://www.elevance.art/auth/google/callback`

3. **Keep existing URIs (if any)**
   - Don't delete your existing `onrender.com` URIs
   - Keep both old and new URIs active
   - This ensures the app works on both domains during transition

4. **Save Changes**
   - Click **"SAVE"** at the bottom of the page
   - Wait for confirmation that changes are saved

### Step 1.3: Verify JavaScript Origins (if applicable)

1. **Check "Authorized JavaScript origins"**
   - In the same OAuth client settings
   - Find **"Authorized JavaScript origins"** section

2. **Add new origins** (if needed)
   - Click **"+ ADD URI"**
   - Add: `https://elevance.art`
   - Click **"+ ADD URI"** again
   - Add: `https://www.elevance.art`

3. **Save Changes**
   - Click **"SAVE"**

### Step 1.4: Test Google OAuth

1. **Visit your site**: `https://elevance.art`
2. **Try signing in with Google**
3. **Verify it redirects correctly** and logs you in

---

## Part 2: Update Stripe Webhook URL

### Step 2.1: Access Stripe Dashboard

1. **Go to Stripe Dashboard**
   - Visit: https://dashboard.stripe.com
   - Sign in to your Stripe account

2. **Navigate to Webhooks**
   - Click on **"Developers"** in the left sidebar
   - Click on **"Webhooks"**

### Step 2.2: Find Your Existing Webhook

1. **Locate your webhook**
   - Look for the webhook pointing to your Render domain
   - It should be something like: `https://airbnb-photo-enhancer.onrender.com/api/payment/webhook`
   - Click on it to edit

### Step 2.3: Update Webhook URL

**Option A: Update Existing Webhook (Recommended)**

1. **Click "Edit" or the webhook URL**
2. **Update the endpoint URL**:
   - Change from: `https://airbnb-photo-enhancer.onrender.com/api/payment/webhook`
   - Change to: `https://elevance.art/api/payment/webhook`
3. **Click "Update" or "Save"**

**Option B: Create New Webhook (Alternative)**

If you want to keep both webhooks active:

1. **Click "+ Add endpoint"**
2. **Enter endpoint URL**: `https://elevance.art/api/payment/webhook`
3. **Select events to listen to**:
   - `checkout.session.completed`
   - Any other events you're currently using
4. **Click "Add endpoint"**

### Step 2.4: Update Webhook Secret (if you created new webhook)

**⚠️ Important**: If you created a NEW webhook, you need to update the secret in Render!

1. **Get the new webhook signing secret**
   - In Stripe Dashboard → Webhooks → Your new webhook
   - Click **"Reveal"** next to "Signing secret"
   - Copy the secret (starts with `whsec_`)

2. **Update in Render**
   - Go to Render Dashboard → Your service → Environment
   - Find `STRIPE_WEBHOOK_SECRET` environment variable
   - Update it with the new secret
   - Click **"Save Changes"**
   - **Redeploy** your service (or it will auto-redeploy)

### Step 2.5: Test Stripe Webhook

1. **Make a test payment** on your site
2. **Check Stripe Dashboard** → Webhooks → Your webhook
3. **Verify events are being received** successfully
4. **Check Render logs** to ensure webhook is processing correctly

---

## Part 3: Verification Checklist

After completing both updates, verify everything works:

### Google OAuth Verification:
- [ ] Added `https://elevance.art/auth/google/callback` to Google OAuth
- [ ] Added `https://www.elevance.art/auth/google/callback` to Google OAuth
- [ ] Added JavaScript origins (if needed)
- [ ] Tested Google sign-in on `https://elevance.art`
- [ ] Tested Google sign-in on `https://www.elevance.art`

### Stripe Webhook Verification:
- [ ] Updated webhook URL to `https://elevance.art/api/payment/webhook`
- [ ] Updated `STRIPE_WEBHOOK_SECRET` in Render (if created new webhook)
- [ ] Tested payment flow on `https://elevance.art`
- [ ] Verified webhook events are received in Stripe Dashboard
- [ ] Verified payment completion works correctly

### General Testing:
- [ ] User registration works
- [ ] User login works (email/password)
- [ ] Google OAuth works
- [ ] Photo upload works
- [ ] Photo enhancement works
- [ ] Payment flow works
- [ ] Photo download after payment works

---

## Troubleshooting

### Google OAuth Issues:

**Error: "redirect_uri_mismatch"**
- Double-check the redirect URI in Google Cloud Console matches exactly
- Make sure you're using `https://` (not `http://`)
- Verify there are no trailing slashes
- Wait a few minutes after saving - changes can take time to propagate

**Error: "invalid_client"**
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct in Render
- Check that you're using the correct OAuth client (not a different project's)

### Stripe Webhook Issues:

**Webhook not receiving events**
- Verify the webhook URL is correct in Stripe Dashboard
- Check that `STRIPE_WEBHOOK_SECRET` matches in Render
- Check Render logs for webhook errors
- Test webhook in Stripe Dashboard → Webhooks → Send test webhook

**Payment completes but doesn't process**
- Check Render logs for webhook processing errors
- Verify webhook secret is correct
- Make sure webhook endpoint is accessible (not blocked by firewall)

---

## Summary

✅ **Google OAuth**: Add redirect URIs for `elevance.art` and `www.elevance.art`
✅ **Stripe Webhook**: Update webhook URL to `https://elevance.art/api/payment/webhook`
✅ **Test Everything**: Verify all functionality works on the new domain

Once both are updated and tested, your application will be fully functional on `elevance.art`! 🚀




