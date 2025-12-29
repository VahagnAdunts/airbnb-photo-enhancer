# SSL Certificate Error Fix - elevance.art

## ✅ Good News!

Your domains are **"Domain Verified"** - this means:
- ✅ DNS records are correct
- ✅ Render can see your domain
- ✅ The hard part is done!

## ⚠️ Certificate Error - Usually Temporary

The "Certificate Error" is common and usually resolves automatically. Here's what to do:

## Step 1: Wait (Most Important!)

**SSL certificates can take 10-60 minutes to provision after DNS verification.**

1. **Wait at least 15-30 minutes** after seeing "Domain Verified"
2. Refresh the Render dashboard periodically
3. The certificate should provision automatically

## Step 2: Verify DNS is Fully Propagated

Even though Render shows "Domain Verified", Let's Encrypt (SSL provider) might need DNS to be fully propagated globally.

### Check DNS Propagation:

1. **Visit**: https://dnschecker.org
2. **Search for**: `elevance.art`
3. **Check A Record**: Should show `216.24.57.1` in all/most locations
4. **Search for**: `www.elevance.art`
5. **Check CNAME**: Should show `airbnb-photo-enhancer.onrender.com` in all/most locations

**If DNS is not fully propagated:**
- Wait another 30-60 minutes
- DNS can take up to 48 hours globally (usually 1-2 hours)

## Step 3: Check for Common Issues

### Issue 1: Multiple A Records (Already Fixed)
✅ You've already fixed this - you should only have ONE A record for `@`

### Issue 2: DNS Caching
Sometimes DNS needs to refresh:
- Clear your browser cache
- Try accessing `https://elevance.art` in an incognito/private window
- Wait a few more minutes

### Issue 3: Let's Encrypt Rate Limiting
Let's Encrypt has rate limits. If you've tried multiple times:
- Wait 1 hour before trying again
- Render will automatically retry

## Step 4: Manual Verification Steps

### In GoDaddy (Double-Check):

1. **Verify A Record for Root Domain:**
   - Type: `A`
   - Name: `@`
   - Value: `216.24.57.1`
   - Should be ONLY ONE A record (no "WebsiteBuilder Site")

2. **Verify CNAME for WWW:**
   - Type: `CNAME`
   - Name: `www`
   - Value: `airbnb-photo-enhancer.onrender.com`
   - No trailing dots

### In Render Dashboard:

1. Go to your service → Settings → Custom Domains
2. Click **"Verify"** button again (sometimes helps)
3. Wait 10-15 minutes after clicking verify
4. Check if status changes

## Step 5: If Still Not Working After 1 Hour

### Option 1: Contact Render Support
1. Click **"Contact support"** link in the error message
2. Explain that:
   - Domain is verified
   - DNS records are correct
   - Certificate provisioning is failing
   - Provide your domain: `elevance.art`

### Option 2: Try Removing and Re-adding Domain

**⚠️ Only do this if it's been over 1 hour and support hasn't responded:**

1. In Render dashboard, click **"Delete"** on `elevance.art`
2. Wait 5 minutes
3. Click **"+ Add Custom Domain"**
4. Re-add `elevance.art` and `www.elevance.art`
5. Wait for verification and certificate provisioning

## Step 6: Verify Certificate is Working

Once the certificate is provisioned:

1. **Visit**: `https://elevance.art`
2. **Check browser**: Should show a lock icon (🔒) in the address bar
3. **No warnings**: Should not show "Not Secure" or certificate errors
4. **Test www**: `https://www.elevance.art` should also work

## Common Timeline

- **DNS Verification**: ✅ Done (you see "Domain Verified")
- **DNS Propagation**: 1-2 hours (usually faster)
- **SSL Certificate Provisioning**: 10-60 minutes after DNS verification
- **Total Time**: Usually 30-90 minutes from when DNS is correct

## What's Happening Behind the Scenes

1. ✅ **DNS Verified**: Render confirmed your DNS records are correct
2. ⏳ **Certificate Request**: Render requests SSL certificate from Let's Encrypt
3. ⏳ **Let's Encrypt Validation**: Let's Encrypt verifies domain ownership via DNS
4. ⏳ **Certificate Issued**: Let's Encrypt issues the certificate
5. ⏳ **Certificate Installed**: Render installs the certificate on your service
6. ✅ **HTTPS Active**: Your site becomes accessible via HTTPS

The error you're seeing is likely at step 3 or 4 - Let's Encrypt is having trouble validating or issuing the certificate.

## Troubleshooting Checklist

- [ ] Waited at least 30 minutes after "Domain Verified"
- [ ] Checked DNS propagation at dnschecker.org
- [ ] Verified only ONE A record for `@` in GoDaddy
- [ ] Verified CNAME for `www` is correct
- [ ] Clicked "Verify" again in Render dashboard
- [ ] Waited another 15 minutes
- [ ] If still failing after 1 hour, contacted Render support

## Expected Outcome

After waiting, you should see:
- ✅ **Domain Verified** (green checkmark)
- ✅ **Certificate Active** (green checkmark, no red error)
- ✅ `https://elevance.art` works
- ✅ `https://www.elevance.art` works

## Summary

**This is normal!** Certificate errors are common right after DNS verification. The certificate usually provisions automatically within 30-60 minutes. Just wait and check back - it should resolve on its own.

If it doesn't resolve after 1 hour, contact Render support using the link in the error message.




