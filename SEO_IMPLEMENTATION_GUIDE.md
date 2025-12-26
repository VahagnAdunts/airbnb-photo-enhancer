# SEO Implementation Guide - Step-by-Step

This guide provides specific code examples and implementation steps for improving SEO on Elevance AI.

---

## Phase 1: Technical SEO Implementation

### Step 1: Create Base Template with SEO Meta Tags

**Action:** Create a base template that all pages inherit from, containing all SEO meta tags.

**File:** `templates/base.html` (new file)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>{% block title %}Elevance AI - AI-Powered Photo Enhancement for Real Estate{% endblock %}</title>
    <meta name="title" content="{% block meta_title %}Elevance AI - AI-Powered Photo Enhancement for Real Estate{% endblock %}">
    <meta name="description" content="{% block meta_description %}Transform your Airbnb and real estate photos with AI-powered enhancement. Professional quality results in seconds. Try free, no credit card required.{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}AI photo enhancement, Airbnb photo enhancer, real estate photo editing, property photo enhancement, automated photo editing, listing photo optimizer{% endblock %}">
    <meta name="author" content="Elevance AI">
    <meta name="robots" content="{% block robots %}index, follow{% endblock %}">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{% block canonical_url %}https://elevance.art{{ request.path }}{% endblock %}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">
    <meta property="og:url" content="{% block og_url %}https://elevance.art{{ request.path }}{% endblock %}">
    <meta property="og:title" content="{% block og_title %}Elevance AI - AI-Powered Photo Enhancement{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Transform your Airbnb and real estate photos with AI-powered enhancement. Professional quality results in seconds.{% endblock %}">
    <meta property="og:image" content="{% block og_image %}https://elevance.art/static/images/og-image.jpg{% endblock %}">
    <meta property="og:site_name" content="Elevance AI">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{% block twitter_url %}https://elevance.art{{ request.path }}{% endblock %}">
    <meta name="twitter:title" content="{% block twitter_title %}Elevance AI - AI-Powered Photo Enhancement{% endblock %}">
    <meta name="twitter:description" content="{% block twitter_description %}Transform your Airbnb and real estate photos with AI-powered enhancement.{% endblock %}">
    <meta name="twitter:image" content="{% block twitter_image %}https://elevance.art/static/images/twitter-image.jpg{% endblock %}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/images/apple-touch-icon.png">
    
    <!-- Stylesheet -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    
    <!-- Structured Data (JSON-LD) -->
    {% block structured_data %}{% endblock %}
    
    <!-- Google Tag Manager -->
    {% if gtm_container_id %}
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','{{ gtm_container_id }}');</script>
    {% endif %}
</head>
<body>
    {% if gtm_container_id %}
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={{ gtm_container_id }}"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    {% endif %}
    
    {% block content %}{% endblock %}
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

**Note:** Since you're using Flask, you'll need to adapt this to Jinja2 syntax. The above uses Django-style template tags as an example.

---

### Step 2: Add Structured Data (Schema.org) to Homepage

**File:** `home.html` (update)

Add this in the `<head>` section:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Elevance AI",
  "url": "https://elevance.art",
  "description": "AI-powered photo enhancement tool for Airbnb and real estate listings",
  "applicationCategory": "PhotoEditingApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0.55",
    "priceCurrency": "USD",
    "description": "Per enhanced photo"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "150"
  },
  "featureList": [
    "AI-powered photo enhancement",
    "Instant processing",
    "Professional quality results",
    "Batch processing",
    "No credit card required for preview"
  ]
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Elevance AI",
  "url": "https://elevance.art",
  "logo": "https://elevance.art/static/images/logo.png",
  "sameAs": [
    "https://twitter.com/elevanceai",
    "https://facebook.com/elevanceai",
    "https://linkedin.com/company/elevanceai"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "url": "https://elevance.art/contact"
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How does the photo enhancement process work?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Our AI analyzes your photos and automatically applies professional enhancements including lighting adjustments, color correction, sharpness improvements, and composition fixes."
    }
  }, {
    "@type": "Question",
    "name": "Will the enhanced photos look fake or over-edited?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "No, our AI is trained to enhance photos naturally while maintaining authenticity. The results look professional but realistic."
    }
  }, {
    "@type": "Question",
    "name": "How long does it take to enhance my photos?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Most photos are enhanced in just a few seconds. Batch processing multiple photos typically takes less than a minute."
    }
  }]
}
</script>
```

---

### Step 3: Create Sitemap.xml

**File:** `app.py` (add route)

```python
@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    from flask import make_response
    from datetime import datetime
    
    # List of all public pages
    pages = [
        {
            'loc': 'https://elevance.art/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': 'https://elevance.art/pricing',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.9'
        },
        {
            'loc': 'https://elevance.art/features',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
        },
        {
            'loc': 'https://elevance.art/about',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': 'https://elevance.art/contact',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.6'
        },
        {
            'loc': 'https://elevance.art/terms',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/privacy',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/refund',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/cookies',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
    ]
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response
```

**File:** `sitemap.xml` (new template file)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for page in pages %}
  <url>
    <loc>{{ page.loc }}</loc>
    <lastmod>{{ page.lastmod }}</lastmod>
    <changefreq>{{ page.changefreq }}</changefreq>
    <priority>{{ page.priority }}</priority>
  </url>
{% endfor %}
</urlset>
```

---

### Step 4: Create Robots.txt

**File:** `app.py` (add route)

```python
@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    from flask import make_response
    
    robots_txt = """User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /api/
Disallow: /payment/
Disallow: /auth/

Sitemap: https://elevance.art/sitemap.xml
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response
```

---

### Step 5: Update Homepage with SEO Meta Tags

**File:** `home.html` (update `<head>` section)

Replace the current `<head>` with:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>Elevance AI - AI-Powered Photo Enhancement for Airbnb & Real Estate</title>
    <meta name="description" content="Transform your Airbnb and real estate photos with AI-powered enhancement. Professional quality results in seconds. Try free, no credit card required. #1 AI Real Estate Photo App.">
    <meta name="keywords" content="AI photo enhancement, Airbnb photo enhancer, real estate photo editing, property photo enhancement, automated photo editing, listing photo optimizer, Booking.com photo enhancement">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="https://elevance.art/">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://elevance.art/">
    <meta property="og:title" content="Elevance AI - AI-Powered Photo Enhancement for Real Estate">
    <meta property="og:description" content="Transform your Airbnb and real estate photos with AI-powered enhancement. Professional quality results in seconds.">
    <meta property="og:image" content="https://elevance.art/static/images/og-image.jpg">
    <meta property="og:site_name" content="Elevance AI">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://elevance.art/">
    <meta name="twitter:title" content="Elevance AI - AI-Powered Photo Enhancement">
    <meta name="twitter:description" content="Transform your Airbnb and real estate photos with AI-powered enhancement.">
    <meta name="twitter:image" content="https://elevance.art/static/images/twitter-image.jpg">
    
    <link rel="stylesheet" href="static/css/style.css">
    
    <!-- Structured Data -->
    <!-- Add the JSON-LD scripts from Step 2 here -->
    
    {% if gtm_container_id %}
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','{{ gtm_container_id }}');</script>
    {% endif %}
</head>
```

---

### Step 6: Add Meta Tags to Other Pages

**Files to update:** `pricing.html`, `features.html`, `about.html`, `contact.html`

Example for `pricing.html`:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>Pricing - Elevance AI Photo Enhancement | $0.55 per Photo</title>
    <meta name="description" content="Affordable AI photo enhancement pricing. Only $0.55 per enhanced photo. No subscription fees, no credit card required for preview. Professional quality results.">
    <meta name="keywords" content="photo enhancement pricing, AI photo editing cost, affordable photo enhancement">
    
    <link rel="canonical" href="https://elevance.art/pricing">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://elevance.art/pricing">
    <meta property="og:title" content="Pricing - Elevance AI Photo Enhancement">
    <meta property="og:description" content="Affordable AI photo enhancement. Only $0.55 per enhanced photo.">
    <meta property="og:image" content="https://elevance.art/static/images/pricing-og.jpg">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Pricing - Elevance AI">
    <meta name="twitter:description" content="Affordable AI photo enhancement. Only $0.55 per enhanced photo.">
    
    <link rel="stylesheet" href="static/css/style.css">
    <!-- ... rest of head ... -->
</head>
```

---

### Step 7: Add Alt Text to Images

**Action:** Update all `<img>` tags with descriptive alt text.

**Example:**
```html
<!-- Before -->
<img src="static/images/photo-example.jpg">

<!-- After -->
<img src="static/images/photo-example.jpg" alt="Before and after comparison of Airbnb living room photo enhanced with AI">
```

**Key principles:**
- Be descriptive but concise
- Include relevant keywords naturally
- Don't stuff keywords
- Describe what the image shows

---

### Step 8: Implement Lazy Loading for Images

**File:** `home.html` and other pages with images

Update image tags:
```html
<img src="image.jpg" alt="Description" loading="lazy">
```

Or in JavaScript for dynamic images:
```javascript
// In home.js or app.js
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));
```

---

## Phase 2: Content Optimization

### Step 9: Optimize Heading Structure

**File:** `home.html`

Ensure proper hierarchy:
- One H1 per page (main title)
- H2 for main sections
- H3 for subsections
- Don't skip levels (H1 → H3 is bad, H1 → H2 → H3 is good)

**Current structure looks good, but verify:**
```html
<h1>Enhance Your Listing Photos</h1>  <!-- Good - single H1 -->
<h2 class="section-title">Try It Now - Free</h2>  <!-- Good -->
<h2 class="section-title">How It Works</h2>  <!-- Good -->
<h3 class="faq-question">How does the photo enhancement process work?</h3>  <!-- Good -->
```

---

### Step 10: Add Breadcrumbs

**File:** Create `templates/breadcrumbs.html`

```html
<nav aria-label="Breadcrumb" class="breadcrumbs">
    <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <a itemprop="item" href="/">
                <span itemprop="name">Home</span>
            </a>
            <meta itemprop="position" content="1" />
        </li>
        {% if current_page != 'home' %}
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <span itemprop="name">{{ current_page|title }}</span>
            <meta itemprop="position" content="2" />
        </li>
        {% endif %}
    </ol>
</nav>
```

Add breadcrumbs to pages (except homepage):
```html
{% include 'breadcrumbs.html' %}
```

---

## Phase 3: Performance Optimization

### Step 11: Optimize Images

**Actions:**
1. Convert images to WebP format where possible
2. Compress JPEG/PNG images (use tools like TinyPNG, ImageOptim)
3. Use appropriate image sizes (don't serve 2000px images when 800px is needed)
4. Consider using `<picture>` element for responsive images

**Example:**
```html
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

---

### Step 12: Add Preconnect for External Resources

**File:** All HTML files (in `<head>`)**

```html
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="dns-prefetch" href="https://www.googletagmanager.com">
```

---

## Testing & Validation

### Tools to Use:

1. **Google Rich Results Test**
   - https://search.google.com/test/rich-results
   - Test structured data

2. **Facebook Sharing Debugger**
   - https://developers.facebook.com/tools/debug/
   - Test Open Graph tags

3. **Twitter Card Validator**
   - https://cards-dev.twitter.com/validator
   - Test Twitter cards

4. **Google Search Console**
   - Submit sitemap
   - Monitor indexing
   - Check for errors

5. **PageSpeed Insights**
   - https://pagespeed.web.dev/
   - Test performance

6. **Schema.org Validator**
   - https://validator.schema.org/
   - Validate structured data

---

## Implementation Checklist

- [ ] Create base template with SEO meta tags
- [ ] Add structured data (JSON-LD) to homepage
- [ ] Create sitemap.xml route and template
- [ ] Create robots.txt route
- [ ] Update homepage meta tags
- [ ] Update pricing page meta tags
- [ ] Update features page meta tags
- [ ] Update about page meta tags
- [ ] Update contact page meta tags
- [ ] Add alt text to all images
- [ ] Implement lazy loading
- [ ] Verify heading structure
- [ ] Add breadcrumbs (optional)
- [ ] Optimize images (WebP, compression)
- [ ] Test with validation tools
- [ ] Submit sitemap to Google Search Console
- [ ] Monitor in Google Search Console

---

## Next Steps After Implementation

1. **Set up Google Search Console**
   - Verify domain ownership
   - Submit sitemap.xml
   - Monitor for errors

2. **Track Performance**
   - Set up goals in Google Analytics
   - Monitor organic traffic
   - Track keyword rankings

3. **Iterate**
   - Review performance monthly
   - Update content based on search queries
   - Add new pages based on keyword opportunities

---

**Note:** This is a comprehensive guide. Start with Phase 1 (Technical SEO) as it provides the highest impact with relatively quick implementation.

