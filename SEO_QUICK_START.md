# SEO Quick Start Checklist

This is a prioritized checklist for implementing SEO improvements. Start from the top and work your way down.

---

## 🔴 Critical - Do These First (1-2 hours)

### 1. Meta Descriptions
- [ ] Add unique meta description to `home.html` (150-160 chars)
- [ ] Add meta description to `pricing.html`
- [ ] Add meta description to `features.html`
- [ ] Add meta description to `about.html`
- [ ] Add meta description to `contact.html`

**Example for home.html:**
```html
<meta name="description" content="Transform your Airbnb and real estate photos with AI-powered enhancement. Professional quality results in seconds. Try free, no credit card required.">
```

### 2. Open Graph Tags
- [ ] Add Open Graph tags to `home.html`
- [ ] Add Open Graph tags to `pricing.html`
- [ ] Add Open Graph tags to `features.html`

**Minimum required OG tags:**
```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://elevance.art/">
<meta property="og:title" content="Elevance AI - AI-Powered Photo Enhancement">
<meta property="og:description" content="Transform your Airbnb and real estate photos with AI-powered enhancement.">
<meta property="og:image" content="https://elevance.art/static/images/og-image.jpg">
```

### 3. Canonical URLs
- [ ] Add canonical tag to `home.html`: `<link rel="canonical" href="https://elevance.art/">`
- [ ] Add canonical tag to `pricing.html`: `<link rel="canonical" href="https://elevance.art/pricing">`
- [ ] Add canonical tag to all other pages

### 4. Sitemap.xml
- [ ] Add `/sitemap.xml` route to `app.py` (see SEO_IMPLEMENTATION_GUIDE.md)
- [ ] Create `sitemap.xml` template
- [ ] Test: Visit `https://elevance.art/sitemap.xml`

### 5. Robots.txt
- [ ] Add `/robots.txt` route to `app.py` (see SEO_IMPLEMENTATION_GUIDE.md)
- [ ] Test: Visit `https://elevance.art/robots.txt`

---

## 🟡 High Priority - Do Next (2-3 hours)

### 6. Structured Data (Schema.org)
- [ ] Add Organization schema to `home.html`
- [ ] Add WebApplication schema to `home.html`
- [ ] Add FAQPage schema to FAQ section in `home.html`

**Test:** Use https://search.google.com/test/rich-results

### 7. Image Alt Text
- [ ] Add alt text to hero image in `home.html`
- [ ] Add alt text to feature images
- [ ] Add alt text to all other images

**Example:**
```html
<img src="image.jpg" alt="Before and after comparison of Airbnb bedroom photo enhanced with AI">
```

### 8. Google Search Console Setup
- [ ] Create Google Search Console account
- [ ] Verify domain ownership (DNS or HTML file)
- [ ] Submit sitemap: `https://elevance.art/sitemap.xml`
- [ ] Request indexing for homepage

---

## 🟢 Medium Priority - Do When You Have Time (3-4 hours)

### 9. Twitter Cards
- [ ] Add Twitter Card meta tags to all pages
- [ ] Test with: https://cards-dev.twitter.com/validator

### 10. Image Optimization
- [ ] Compress existing images (use TinyPNG or similar)
- [ ] Convert to WebP format where possible
- [ ] Implement lazy loading: `<img loading="lazy">`

### 11. Page Titles Optimization
- [ ] Ensure each page has unique, descriptive title
- [ ] Include primary keyword in title
- [ ] Keep titles under 60 characters

**Current titles to review:**
- Home: "Elevance AI - Photo Enhancement" → "Elevance AI - AI-Powered Photo Enhancement for Airbnb & Real Estate"
- Pricing: "Pricing - Elevance AI" → "Pricing - Elevance AI Photo Enhancement | $0.55 per Photo"

### 12. Internal Linking
- [ ] Add links from homepage to key pages (pricing, features)
- [ ] Add links from features page to pricing
- [ ] Add footer links (already have some, verify they're working)

---

## ⚪ Nice to Have - Do Later (Ongoing)

### 13. Content Expansion
- [ ] Expand FAQ section with more questions
- [ ] Add blog section (future)
- [ ] Create use-case specific landing pages

### 14. Performance
- [ ] Run PageSpeed Insights test
- [ ] Optimize CSS/JS (minify)
- [ ] Enable browser caching headers

### 15. Analytics
- [ ] Set up conversion goals in Google Analytics
- [ ] Track organic traffic sources
- [ ] Monitor keyword rankings

---

## Quick Wins (5 minutes each)

These can be done immediately:

1. **Update page titles** - Make them more descriptive
2. **Add meta descriptions** - Copy from current content, make 150-160 chars
3. **Add canonical URLs** - One line per page
4. **Create robots.txt** - Simple route in app.py
5. **Create sitemap.xml** - Simple route in app.py

---

## Testing Checklist

After implementing, test:

- [ ] **Rich Results Test**: https://search.google.com/test/rich-results
  - Enter your homepage URL
  - Check for structured data errors

- [ ] **Facebook Debugger**: https://developers.facebook.com/tools/debug/
  - Enter your homepage URL
  - Check Open Graph tags

- [ ] **Twitter Card Validator**: https://cards-dev.twitter.com/validator
  - Enter your homepage URL
  - Check Twitter cards

- [ ] **PageSpeed Insights**: https://pagespeed.web.dev/
  - Enter your homepage URL
  - Check performance score

- [ ] **Mobile-Friendly Test**: https://search.google.com/test/mobile-friendly
  - Enter your homepage URL
  - Verify mobile compatibility

- [ ] **Sitemap**: Visit `https://elevance.art/sitemap.xml`
  - Should see XML with all pages listed

- [ ] **Robots.txt**: Visit `https://elevance.art/robots.txt`
  - Should see text file with crawl rules

---

## Expected Results Timeline

- **Week 1**: Technical SEO implemented, sitemap submitted
- **Week 2-4**: Google starts indexing pages with new meta tags
- **Month 2-3**: See improvements in search impressions
- **Month 3-6**: Organic traffic increases (20-50%)
- **Month 6+**: Established rankings for target keywords

---

## Resources

- **Full Plan**: See `SEO_IMPROVEMENT_PLAN.md`
- **Implementation Details**: See `SEO_IMPLEMENTATION_GUIDE.md`
- **Google Search Console**: https://search.google.com/search-console
- **Schema.org**: https://schema.org/
- **Open Graph Protocol**: https://ogp.me/

---

**Start with the Critical items (🔴) - they provide the biggest impact with minimal effort!**

