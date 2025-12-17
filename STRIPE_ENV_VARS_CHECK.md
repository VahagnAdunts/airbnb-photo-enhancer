# Stripe Environment Variables - Quick Check

## Error You're Seeing

```
AttributeError: 'NoneType' object has no attribute 'Session'
```

This means **Stripe is not initialized** because `STRIPE_SECRET_KEY` is missing.

## Fix: Add Stripe Keys to Render

### Step 1: Go to Render Dashboard

1. Open your Render service dashboard
2. Click on your web service
3. Go to **"Environment"** tab (left sidebar)

### Step 2: Add Missing Variables

Add these three environment variables:

**1. STRIPE_SECRET_KEY**
```
Name: STRIPE_SECRET_KEY
Value: sk_live_xxxxx (your Stripe secret key)
```

**2. STRIPE_PUBLISHABLE_KEY**
```
Name: STRIPE_PUBLISHABLE_KEY
Value: pk_live_xxxxx (your Stripe publishable key)
```

**3. STRIPE_WEBHOOK_SECRET** (optional for now, but needed for production)
```
Name: STRIPE_WEBHOOK_SECRET
Value: whsec_xxxxx (from Stripe webhook settings)
```

### Step 3: Get Your Stripe Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Click **"Developers"** → **"API keys"**
3. Copy:
   - **Secret key** (starts with `sk_live_` or `sk_test_`)
   - **Publishable key** (starts with `pk_live_` or `pk_test_`)

**Important:**
- Use **test keys** (`sk_test_` / `pk_test_`) for testing
- Use **live keys** (`sk_live_` / `pk_live_`) for production

### Step 4: Save and Redeploy

1. Click **"Save Changes"** after adding each variable
2. Render will automatically redeploy
3. Wait for deployment to complete

### Step 5: Test Payment

1. Go to your app
2. Upload a photo
3. Try to download
4. Should redirect to Stripe Checkout

## Quick Checklist

- [ ] `STRIPE_SECRET_KEY` added to Render environment
- [ ] `STRIPE_PUBLISHABLE_KEY` added to Render environment
- [ ] `STRIPE_WEBHOOK_SECRET` added (optional for now)
- [ ] Render service redeployed
- [ ] Payment flow tested

## Where to Find Stripe Keys

**Stripe Dashboard:**
- https://dashboard.stripe.com/test/apikeys (test keys)
- https://dashboard.stripe.com/apikeys (live keys)

**Webhook Secret:**
- https://dashboard.stripe.com/webhooks
- Click on your webhook
- Click "Reveal" next to "Signing secret"

## After Adding Keys

The error should be fixed and payments should work!

