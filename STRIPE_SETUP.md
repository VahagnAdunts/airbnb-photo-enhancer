# Stripe Payment Integration Setup Guide

## Overview

Your application now requires payment ($0.55 per photo) before users can download enhanced photos. The payment is processed through Stripe Checkout.

## Setup Instructions

### Step 1: Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Sign in or create an account
3. Make sure you're in **Test Mode** for development (toggle in top right)
4. Go to **Developers** → **API keys**
5. Copy your keys:
   - **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - **Secret key** (starts with `sk_test_` or `sk_live_`)

### Step 2: Set Up Webhook (Important!)

Webhooks are required to confirm payments automatically.

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. Enter your webhook URL:
   - **Development**: `http://localhost:5000/api/payment/webhook` (use ngrok for local testing)
   - **Production**: `https://yourdomain.com/api/payment/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `checkout.session.async_payment_failed`
5. Click **"Add endpoint"**
6. Copy the **Signing secret** (starts with `whsec_`)

### Step 3: Configure Environment Variables

Add these to your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Important**: 
- Use `pk_test_` and `sk_test_` for development
- Use `pk_live_` and `sk_live_` for production
- Never commit your secret keys to version control

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `stripe==7.8.0`

### Step 5: Run Database Migration

The payment system requires a new `Payment` table. Run:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Or restart your Flask app - it will create the table automatically.

### Step 6: Test the Integration

1. **Start your Flask app**:
   ```bash
   python app.py
   ```

2. **For local webhook testing**, use [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 5000
   ```
   Then use the ngrok URL in your Stripe webhook endpoint.

3. **Test the flow**:
   - Log in to your app
   - Upload and enhance some photos
   - Try to download - you should be redirected to Stripe Checkout
   - Use Stripe test card: `4242 4242 4242 4242`
   - Complete payment
   - You should be redirected back and able to download

## How It Works

1. **User clicks download** → System checks if payment is required
2. **Payment required** → Creates Stripe Checkout Session
3. **User redirected** → To Stripe Checkout page
4. **User pays** → Stripe processes payment
5. **Webhook received** → Payment status updated in database
6. **User redirected back** → Can now download photos

## Pricing

- **Price per photo**: $0.55 (55 cents)
- **Minimum**: 1 photo
- **Currency**: USD

## Payment Flow

### For Authenticated Users (Dashboard)

1. User selects photos to download
2. Clicks "Download X Photos - $X.XX"
3. If not paid, redirected to Stripe Checkout
4. After payment, redirected to success page
5. Can then download photos

### For Guest Users (Home Page)

- Photos are free to preview
- Payment only required when downloading saved photos after signup

## Stripe Test Cards

Use these cards for testing (in Test Mode):

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires authentication**: `4000 0025 0000 3155`

Use any future expiry date, any 3-digit CVC, and any ZIP code.

## Production Checklist

Before going live:

- [ ] Switch to **Live Mode** in Stripe Dashboard
- [ ] Update `.env` with live keys (`pk_live_` and `sk_live_`)
- [ ] Set up production webhook endpoint
- [ ] Test with real payment (small amount)
- [ ] Verify webhook is receiving events
- [ ] Set up email notifications for payments
- [ ] Review Stripe Dashboard for security settings

## Troubleshooting

### Payment not processing?

1. Check Stripe API keys are correct in `.env`
2. Verify webhook endpoint is accessible
3. Check Stripe Dashboard → **Logs** for errors
4. Check Flask server logs for errors

### Webhook not working?

1. Use ngrok for local testing
2. Verify webhook secret is correct
3. Check webhook events are selected correctly
4. Test webhook in Stripe Dashboard → **Webhooks** → **Send test webhook**

### Photos not downloading after payment?

1. Check payment status in database
2. Verify webhook processed successfully
3. Check browser console for errors
4. Verify photo IDs match payment record

## Security Notes

- ✅ Never expose secret keys in frontend code
- ✅ Always verify webhook signatures
- ✅ Use HTTPS in production
- ✅ Validate payment status before allowing downloads
- ✅ Check user ownership of photos before payment

## Support

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Testing Guide](https://stripe.com/docs/testing)


