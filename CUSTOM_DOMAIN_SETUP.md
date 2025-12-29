# Custom Domain Setup Guide - elevance.art

This guide will help you connect your GoDaddy domain (elevance.art) to your Render deployment.

## Step 1: Add Custom Domain on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Log in to your account

2. **Navigate to Your Web Service**
   - Click on your web service (airbnb-photo-enhancer or similar)
   - Go to the **"Settings"** tab

3. **Add Custom Domain**
   - Scroll down to **"Custom Domains"** section
   - Click **"Add Custom Domain"**
   - Enter: `elevance.art`
   - Click **"Save"**

4. **Add WWW Subdomain (Optional but Recommended)**
   - Also add: `www.elevance.art`
   - This allows users to access your site with or without "www"

5. **Get DNS Configuration**
   - Render will show you DNS records to add
   - You'll see something like:
     - **Type**: `CNAME`
     - **Name**: `@` (or blank for root domain)
     - **Value**: `your-app.onrender.com`
     - **Type**: `CNAME`
     - **Name**: `www`
     - **Value**: `your-app.onrender.com`

## Step 2: Configure DNS on GoDaddy

1. **Log in to GoDaddy**
   - Visit: https://www.godaddy.com
   - Log in to your account

2. **Go to Domain Management**
   - Click on **"My Products"** or **"Domains"**
   - Find `elevance.art` in your domain list
   - Click on **"DNS"** or **"Manage DNS"**

3. **Add A Record for Root Domain (`elevance.art`)**
   
   **IMPORTANT**: Render requires an **A record** (or ANAME/ALIAS) for the root domain, NOT a CNAME.
   
   - Click **"Add"** or **"Add Record"**
   - **Type**: Select `A` (not CNAME!)
   - **Name**: `@` (or leave blank, or use `elevance.art`)
   - **Value**: `216.24.57.1` (this is the IP address from Render - check your Render dashboard for the exact IP)
   - **TTL**: `600` (or default)
   - Click **"Save"**
   
   **Note**: 
   - Do NOT use `https://` in the value field - DNS records don't use protocols
   - Do NOT use CNAME for root domain - GoDaddy and most DNS providers don't support it
   - The value should be just the IP address: `216.24.57.1` (verify this IP in your Render dashboard)

4. **Add CNAME Record for WWW Subdomain (`www.elevance.art`)**
   - Click **"Add"** or **"Add Record"**
   - **Type**: Select `CNAME`
   - **Name**: `www` (just "www", not "www.elevance.art")
   - **Value**: `airbnb-photo-enhancer.onrender.com` (NO `https://`, just the hostname)
   - **TTL**: `600` (or default)
   - Click **"Save"**
   
   **Important**: 
   - Remove `https://` from the value - DNS records only need the hostname
   - Make sure the value is complete: `airbnb-photo-enhancer.onrender.com` (not missing `.com`)

5. **Remove Conflicting Records**
   - Remove any existing A or CNAME records for `@` or `www` that conflict
   - Keep only the new records you just added

## Step 3: Wait for DNS Propagation

1. **DNS Propagation Time**
   - DNS changes can take 24-48 hours to propagate globally
   - Usually works within 1-2 hours
   - You can check propagation status at: https://www.whatsmydns.net

2. **Verify DNS Settings**
   - Use command line: `nslookup elevance.art`
   - Or use online tools: https://dnschecker.org
   - Should show your Render service

## Step 4: SSL Certificate (Automatic)

1. **Render Automatically Provisions SSL**
   - Once DNS is configured correctly, Render will automatically:
     - Detect your custom domain
     - Provision a free SSL certificate (Let's Encrypt)
     - Enable HTTPS

2. **Wait for SSL**
   - SSL certificate provisioning usually takes 5-10 minutes after DNS is correct
   - Check Render dashboard → Your service → Settings → Custom Domains
   - Status should show "Active" with SSL enabled

## Step 5: Update Application Configuration

### Update Environment Variables (if needed)

Some services might need to know about the custom domain. Check if you need to update:

1. **Google OAuth Redirect URIs**
   - Go to Google Cloud Console
   - Update authorized redirect URIs:
     - `https://elevance.art/auth/google/callback`
     - `https://www.elevance.art/auth/google/callback`

2. **Stripe Webhook URL**
   - Go to Stripe Dashboard → Webhooks
   - Update webhook URL:
     - `https://elevance.art/api/payment/webhook`

3. **Google Tag Manager** (if used)
   - Update any domain-specific configurations

### Update Code (if needed)

Your Flask app should automatically work with the custom domain. However, check:

1. **Hardcoded URLs**
   - Search for any hardcoded `onrender.com` URLs
   - Update to use `elevance.art` or use relative URLs

2. **CORS Settings**
   - If you have CORS restrictions, add `elevance.art` to allowed origins

## Step 6: Test Your Domain

1. **Test HTTP**
   - Visit: `http://elevance.art`
   - Should redirect to HTTPS automatically

2. **Test HTTPS**
   - Visit: `https://elevance.art`
   - Should show your application
   - Check SSL certificate is valid (lock icon in browser)

3. **Test WWW**
   - Visit: `https://www.elevance.art`
   - Should also work

4. **Test All Features**
   - User registration/login
   - Photo upload and enhancement
   - Payment flow
   - OAuth (Google sign-in)

## Troubleshooting

### Issue: Domain not resolving

**Solution:**
- Wait longer (DNS can take up to 48 hours)
- Verify DNS records are correct in GoDaddy
- Check DNS propagation: https://dnschecker.org
- Make sure you're using the correct Render service URL

### Issue: SSL certificate not provisioning

**Solution:**
- Ensure DNS is correctly configured and propagated
- Wait 10-15 minutes after DNS is correct
- Check Render dashboard for SSL status
- Contact Render support if it doesn't provision after 24 hours

### Issue: "Site can't be reached" or "Connection refused"

**Solution:**
- Verify your Render service is running
- Check DNS records point to correct Render service
- Ensure custom domain is added in Render dashboard
- Check Render logs for errors

### Issue: Mixed content warnings

**Solution:**
- Ensure all resources (images, scripts) use HTTPS
- Update any hardcoded HTTP URLs to HTTPS
- Check browser console for mixed content errors

### Issue: OAuth/Stripe not working

**Solution:**
- Update redirect URIs in Google Cloud Console
- Update webhook URL in Stripe Dashboard
- Clear browser cache and cookies
- Test in incognito/private browsing mode

## GoDaddy-Specific Notes

### If CNAME for Root Domain Doesn't Work

GoDaddy sometimes doesn't support CNAME for root domain (@). Options:

1. **Use A Records** (if Render provides IPs)
   - Render may provide IP addresses for A records
   - Create A records pointing to those IPs

2. **Use GoDaddy Forwarding**
   - Set up domain forwarding in GoDaddy
   - Forward `elevance.art` → `www.elevance.art`
   - Use CNAME for `www` subdomain only

3. **Contact Render Support**
   - They may have specific instructions for GoDaddy
   - Some domains work better with A records

## DNS Record Examples

### For Root Domain (elevance.art)

**Use A Record (Required by Render)**
```
Type: A
Name: @
Value: 216.24.57.1
TTL: 600
```

**Note**: Check your Render dashboard for the exact IP address. It may be different from `216.24.57.1`.

### For WWW Subdomain (www.elevance.art)

```
Type: CNAME
Name: www
Value: airbnb-photo-enhancer.onrender.com
TTL: 600
```

**Important**: 
- No `https://` prefix
- Complete hostname with `.com` at the end

## Verification Checklist

After setup, verify:

- [ ] Custom domain added in Render dashboard
- [ ] DNS records added in GoDaddy
- [ ] DNS propagated (check with dnschecker.org)
- [ ] `https://elevance.art` works
- [ ] `https://www.elevance.art` works
- [ ] SSL certificate is active (green lock icon)
- [ ] All features work (login, upload, payment)
- [ ] OAuth redirects work correctly
- [ ] Stripe webhooks work correctly

## Next Steps

1. **Update Marketing Materials**
   - Update any links to use `elevance.art`
   - Update social media profiles
   - Update email signatures

2. **Set Up Email** (Optional)
   - Consider setting up email with your domain
   - Use services like SendGrid, Mailgun, or AWS SES
   - Configure SPF/DKIM records in GoDaddy DNS

3. **Monitor**
   - Check Render dashboard regularly
   - Monitor SSL certificate expiration (auto-renewed by Render)
   - Set up uptime monitoring

## Support

If you encounter issues:

1. **Render Support**: https://render.com/docs
2. **GoDaddy Support**: https://www.godaddy.com/help
3. **Check Render Logs**: Dashboard → Your Service → Logs
4. **DNS Checker**: https://dnschecker.org

## Summary

✅ **Add custom domain in Render dashboard**
✅ **Configure DNS records in GoDaddy**
✅ **Wait for DNS propagation (1-48 hours)**
✅ **SSL certificate auto-provisions**
✅ **Update OAuth and Stripe URLs**
✅ **Test everything**

Your domain `elevance.art` will be live once DNS propagates! 🚀

