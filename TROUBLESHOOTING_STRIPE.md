# Troubleshooting Stripe Payment Issues

## Issue: Environment Variables Set But Still Getting Errors

If you've added the Stripe keys to Render but still getting errors, try these steps:

### Step 1: Verify Environment Variables Are Saved

1. Go to Render Dashboard → Your Service → Environment tab
2. Make sure all three variables are there:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`
3. Check that values don't have extra spaces or quotes

### Step 2: Manual Redeploy

Sometimes Render doesn't pick up new environment variables automatically:

1. Go to Render Dashboard → Your Service
2. Click **"Manual Deploy"** button (top right)
3. Select **"Deploy latest commit"**
4. Wait for deployment to complete

### Step 3: Check Logs

1. Go to Render Dashboard → Your Service → **"Logs"** tab
2. Look for these messages:
   - ✅ `"Stripe initialized successfully"` - Good!
   - ❌ `"STRIPE_SECRET_KEY not set"` - Variable not loaded

### Step 4: Verify Stripe Keys Are Correct

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Make sure you're copying the **correct keys**:
   - **Secret key** starts with `sk_live_` (live) or `sk_test_` (test)
   - **Publishable key** starts with `pk_live_` (live) or `pk_test_` (test)
3. Make sure you're using **live keys** if you want real payments
4. Make sure you're using **test keys** if you want to test

### Step 5: Check Webhook Secret

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click on your webhook: `https://airbnb-photo-enhancer.onrender.com/api/payment/webhook`
3. Click **"Reveal"** next to "Signing secret"
4. Copy the value (starts with `whsec_`)
5. Make sure it matches what's in Render's `STRIPE_WEBHOOK_SECRET`

### Step 6: Test Payment Flow

1. Go to your app: `https://airbnb-photo-enhancer.onrender.com`
2. Upload a photo
3. Try to download it
4. Should redirect to Stripe Checkout

### Common Issues

**Issue: "NoneType object has no attribute 'Session'"**
- **Cause**: Stripe not initialized
- **Fix**: Make sure `STRIPE_SECRET_KEY` is set and service is redeployed

**Issue: "Payment system not configured"**
- **Cause**: Environment variable not loaded
- **Fix**: Manual redeploy after adding variables

**Issue: Webhook not receiving events**
- **Cause**: `STRIPE_WEBHOOK_SECRET` doesn't match
- **Fix**: Update webhook secret in Render to match Stripe

**Issue: Payment succeeds but download doesn't work**
- **Cause**: Webhook not processing correctly
- **Fix**: Check webhook logs in Stripe Dashboard

### Still Not Working?

1. **Check Render Logs** for specific error messages
2. **Check Stripe Dashboard** → Logs for API errors
3. **Verify** all three environment variables are set correctly
4. **Try manual redeploy** one more time

### Quick Test

After setting variables and redeploying, check the logs for:
```
Stripe initialized successfully (key starts with: sk_live_...)
```

If you see this, Stripe is working! If not, the variable isn't being read.

