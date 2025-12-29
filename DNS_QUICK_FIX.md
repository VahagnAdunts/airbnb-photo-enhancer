# DNS Quick Fix for elevance.art

## The Problems You Had:

1. ❌ Using **CNAME** for root domain (`@`) - GoDaddy doesn't support this
2. ❌ Value had `https://` - DNS records don't use protocols
3. ❌ Value was incomplete: `airbnb-photo-enhancer.onrender.` (missing `.com`)
4. ❌ **CONFLICTING A RECORD**: You have TWO A records for root domain (`@`):
   - ✅ One pointing to `216.24.57.1` (CORRECT - keep this!)
   - ❌ One pointing to `WebsiteBuilder Site` (WRONG - DELETE THIS!)
   
   **The "WebsiteBuilder Site" A record is preventing verification!**

## The Correct Configuration:

### For Root Domain (`elevance.art`):

1. **Delete** the incorrect CNAME record you tried to add
2. **Add a new A Record**:
   - **Type**: `A` (NOT CNAME!)
   - **Name**: `@` (or leave blank)
   - **Value**: `216.24.57.1` (just the IP, no `https://`)
   - **TTL**: `1/2 Hour` (or default)
   - Click **"Save"**

### For WWW Subdomain (`www.elevance.art`):

1. **Add a CNAME Record**:
   - **Type**: `CNAME`
   - **Name**: `www` (just "www", not the full domain)
   - **Value**: `airbnb-photo-enhancer.onrender.com` (NO `https://`, complete with `.com`)
   - **TTL**: `1/2 Hour` (or default)
   - Click **"Save"**

## Step-by-Step in GoDaddy:

### Step 1: Fix Root Domain (elevance.art) - CRITICAL!

**You currently have TWO A records for `@` - this is the problem!**

1. **DELETE the A record with value `WebsiteBuilder Site`**
   - Find the A record where Value = `WebsiteBuilder Site`
   - Click the **Delete icon** (trash can) next to it
   - Confirm deletion
   
2. **KEEP the A record with value `216.24.57.1`**
   - This one is correct - DO NOT delete it!
   
3. **Verify you only have ONE A record for `@`**
   - It should be: Type `A`, Name `@`, Value `216.24.57.1`
   - If you don't have this record, add it:
     - Click **"Add"** or **"Add Record"**
     - **Type**: `A`
     - **Name**: `@`
     - **Value**: `216.24.57.1`
     - **TTL**: `1/2 Hour`
     - Click **"Save"**

### Step 2: Add WWW Subdomain

1. Click **"Add"** or **"Add Record"**
2. Select **Type**: `CNAME`
3. **Name**: `www`
4. **Value**: `airbnb-photo-enhancer.onrender.com` (make sure it's complete!)
5. **TTL**: `1/2 Hour`
6. Click **"Save"**

## Verify Your Records:

After saving, you should have **EXACTLY**:

```
Type: A
Name: @
Value: 216.24.57.1
(ONLY ONE A record for @ - NO "WebsiteBuilder Site" record!)

Type: CNAME
Name: www
Value: airbnb-photo-enhancer.onrender.com
(Note: The trailing dot in GoDaddy's display is normal, but the actual value should be without trailing dot)
```

**IMPORTANT**: 
- You must have ONLY ONE A record for `@` pointing to `216.24.57.1`
- DELETE the A record with value `WebsiteBuilder Site`
- The CNAME for `www` should point to `airbnb-photo-enhancer.onrender.com` (without trailing dot when editing)

## Important Notes:

- ✅ **A Record** for root domain (`@`)
- ✅ **CNAME** for `www` subdomain
- ✅ **No `https://`** in any DNS record value
- ✅ **Complete hostname** with `.com` at the end
- ✅ **IP address** for A record (not a domain name)

## After Saving:

1. Go back to Render dashboard
2. Click **"Verify"** button next to each domain
3. Wait 5-10 minutes for DNS to propagate
4. You should see **"Domain Verified"** (green checkmark)
5. **Certificate Error is Normal**: If you see "Certificate Error" after "Domain Verified", this is usually temporary
   - Wait 30-60 minutes for SSL certificate to provision automatically
   - See `SSL_CERTIFICATE_FIX.md` for detailed troubleshooting

## Still Having Issues?

### Most Common Problem: Multiple A Records

**If verification still fails, check:**
1. ✅ You have ONLY ONE A record for `@` (root domain)
2. ✅ That A record points to `216.24.57.1` (NOT "WebsiteBuilder Site")
3. ✅ You deleted the "WebsiteBuilder Site" A record
4. ✅ The CNAME for `www` points to `airbnb-photo-enhancer.onrender.com` (no trailing dot)

### Other Things to Check:

- Wait 5-10 minutes after deleting records - DNS changes take time to propagate
- Double-check the IP address in Render dashboard (it might be different from `216.24.57.1`)
- Make sure you're not editing the NS (nameserver) records - those should stay as-is
- Try clicking "Verify" in Render dashboard again after waiting a few minutes
- Check if GoDaddy has any "parked page" or "website builder" settings that might be interfering

### If Still Not Working:

1. **Check DNS propagation**: Visit https://dnschecker.org and search for `elevance.art`
   - Should show A record pointing to `216.24.57.1`
2. **Verify in Render**: The IP address might have changed - check your Render dashboard for the exact IP
3. **Contact Render Support**: If DNS is correct but verification still fails, Render support can help

