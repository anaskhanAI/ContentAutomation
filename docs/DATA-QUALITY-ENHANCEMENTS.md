# Data Quality Enhancements

## 🎯 Overview

This document details the comprehensive data quality improvements implemented to ensure fresh, diverse, high-quality content from all 12 configured sources.

---

## 🚨 Problems Identified

### 1. **Archive/Category Page Pollution**
- **Issue**: System was scraping pagination, category, and archive listing pages instead of actual articles
- **Examples**: 
  - `techcrunch.com/category/artificial-intelligence/page/79/`
  - `techcrunch.com/category/artificial-intelligence/page/187/`
  - Archive pages with "Page X of Y" titles
- **Impact**: 90%+ of scraped content was listing pages, not articles

### 2. **Single-Source Dominance**
- **Issue**: TechCrunch dominated 90% of all content
- **Root Cause**: 
  - Old crawl data still in database
  - No fresh scrapes from new 12 sources
  - No diversity enforcement

### 3. **Low Content Quality**
- **Issue**: Very short content (< 500 chars), link-heavy listing pages
- **Impact**: Content unsuitable for AI content generation

### 4. **Stale Data**
- **Issue**: Using old scraped data, not leveraging RSS for fresh content
- **Impact**: Generated posts about outdated news

---

## ✅ Solutions Implemented

### 1. **Intelligent URL Filtering**

**New Method**: `_is_valid_article_url(url, title)`

**Filters out:**
- `/page/` - Pagination pages
- `/category/` - Category listing pages
- `/archives/` or `/archive/` - Archive pages
- `/tag/` or `/tags/` - Tag listing pages
- `/author/` - Author pages
- `/feed/` or `/rss` - Feed endpoints

**Title validation:**
- Rejects titles with multiple invalid patterns
- Examples: "Page 79 of 453", "Archives", "Category: AI"

**Location**: `src/scraper.py:37-89`

```python
def _is_valid_article_url(self, url: str, title: str = "") -> bool:
    """Validate if URL is an actual article."""
    invalid_patterns = ['/page/', '/category/', '/archives/', ...]
    # Checks URL and title for invalid patterns
    return True if valid else False
```

---

### 2. **Content Quality Validation**

**New Method**: `_is_quality_content(content, title, url)`

**Validates:**
- **Minimum length**: 500 characters (meaningful articles)
- **Link density**: Rejects link-heavy listing pages (>20 links with <2000 chars)
- **Paragraph count**: At least 3 substantial paragraphs (>50 chars each)
- **Not empty**: Has actual content

**Location**: `src/scraper.py:91-147`

```python
def _is_quality_content(self, content: str, title: str = "", url: str = "") -> bool:
    """Validate content meets quality standards."""
    # Checks length, link density, paragraph count
    return True if quality content else False
```

---

### 3. **Quality Checks in All Scraping Methods**

**Updated Methods:**

1. **`scrape_url()`** (Line 91-206)
   - ✅ URL validation before storing
   - ✅ Content quality check before storing
   - ✅ Early rejection with logging

2. **`scrape_from_rss()`** (Line 238-373)
   - ✅ URL validation for each RSS entry
   - ✅ Skips archive/category links from RSS
   - ✅ Still benefits from RSS metadata (dates, authors)

3. **`crawl_website()`** (Line 439-613)
   - ✅ URL validation for each crawled page
   - ✅ Content quality check for each page
   - ✅ Prevents storing listing pages from crawls

---

### 4. **Enhanced Source Diversity Tracking**

**Updated**: `src/orchestrator.py:scrape_from_sources()`

**New Features:**
- Per-source result tracking
- Detailed logging by source type
- Visual source summary with icons
- Credit tracking per source
- Method tracking (RSS vs Crawl)

**Output Format:**
```
📊 SCRAPING SUMMARY BY SOURCE
═══════════════════════════════════════════════════════

📁 RESEARCH PAPERS
  ✅ 📰 Hugging Face Papers: 3 articles stored (scraped: 3, credits: 3)
  ✅ 🌐 Papers with Code: 2 articles stored (scraped: 2, credits: 10)

📁 NEWS AGGREGATOR
  ✅ 📰 Alpha Signal: 3 articles stored (scraped: 3, credits: 3)
  ✅ 📰 The Rundown AI: 3 articles stored (scraped: 3, credits: 3)
  ...

═══════════════════════════════════════════════════════
TOTALS: 32 articles stored from 11/12 sources
═══════════════════════════════════════════════════════
```

**Icons:**
- ✅ = Successfully scraped content
- ❌ = No content scraped
- 📰 = RSS method
- 🌐 = Web crawl method
- ⏭️ = Skipped

---

## 🛠️ New Tools & Scripts

### 1. **Diagnostic Script**

**File**: `scripts/diagnose_data_quality.py`

**Purpose**: Comprehensive analysis of database content quality

**Features:**
- Per-source content analysis
- Quality issue detection (archive pages, short content, etc.)
- Source diversity analysis with visual bars
- Freshness analysis (24h, 7d, 30d, older)
- Actionable recommendations

**Usage:**
```bash
python scripts/diagnose_data_quality.py
```

**Sample Output:**
```
🔍 DATA QUALITY DIAGNOSTIC REPORT
═══════════════════════════════════════════════════════

📊 SOURCES OVERVIEW
  Total sources configured: 12
  Active sources: 12
  Inactive sources: 0

📁 CONTENT BY SOURCE

✅ 📰 VentureBeat AI
    Type: tech_news
    URL: https://venturebeat.com/category/ai/
    Total scraped: 3
    └─ Processed: 0
    └─ Unprocessed: 3

❌ 🌐 TechCrunch AI
    Type: tech_news
    URL: https://techcrunch.com/category/artificial-intelligence/
    Total scraped: 45
    └─ Processed: 0
    └─ Unprocessed: 45
    ⚠️  Quality Issues:
       └─ Category URLs: 20
       └─ Pagination URLs: 25

...

🗑️  Quality Issues Found:
    ├─ Archive pages (marked): 0
    ├─ Category URLs: 20
    ├─ Pagination URLs: 25
    ├─ Archive URLs: 5
    └─ Short content (<500 chars): 10

  ⚠️  TOTAL QUALITY ISSUES: 60 items (40% of all content)

🌈 SOURCE DIVERSITY
═══════════════════════════════════════════════════════

  Content distribution:
    TechCrunch AI              45 (30%) ███████████████
    VentureBeat AI              3 (2%)  █
    Alpha Signal                3 (2%)  █
    ...

  ❌ Sources with NO content scraped:
    • Google Research Blog
    • OpenAI News

💡 RECOMMENDATIONS
═══════════════════════════════════════════════════════

  ⚠️  HIGH PERCENTAGE OF LOW-QUALITY DATA (40%)
      Action: Run scripts/clean_bad_data.sql in Supabase

  ⚠️  2 SOURCES HAVE NO CONTENT
      Action: Run 'python main.py scrape' to scrape fresh content

  ⚠️  SINGLE SOURCE DOMINANCE: TechCrunch AI has 30% of all content
      Action: Run fresh scrape to diversify content sources
```

---

### 2. **Clean Bad Data SQL Script**

**File**: `scripts/clean_bad_data.sql`

**Purpose**: Mark archive/category pages as processed in Supabase

**Targets:**
- URLs with `/page/`, `/category/`, `/archives/`
- Titles with "Page X of Y", "Archives", "Category:"
- Content shorter than 500 characters

**Usage:**
1. Open Supabase SQL Editor
2. Copy/paste the script
3. Execute
4. Verifies how many rows were marked

---

## 📋 Testing & Verification

### Step 1: Run Diagnostic (Before)

```bash
python scripts/diagnose_data_quality.py
```

**Expected Issues:**
- High percentage of archive pages
- Single-source dominance (TechCrunch)
- Missing content from new sources
- Stale data

---

### Step 2: Clean Bad Data

```sql
-- In Supabase SQL Editor
-- Run scripts/clean_bad_data.sql
```

**Expected Results:**
- 30-60 items marked as processed (archive pages)
- Quality issues reduced

---

### Step 3: Run Fresh Scrape

```bash
python main.py scrape
```

**Expected Results:**
```
📊 SCRAPING SUMMARY BY SOURCE
═══════════════════════════════════════════════════════

📁 RESEARCH PAPERS
  ✅ 📰 Hugging Face Papers: 3 articles stored
  ✅ 🌐 Papers with Code: 2 articles stored

📁 NEWS AGGREGATOR
  ✅ 📰 Alpha Signal: 3 articles stored
  ✅ 📰 The Rundown AI: 3 articles stored
  ✅ 📰 Ben's Bites: 3 articles stored
  ✅ 📰 TLDR AI: 3 articles stored

📁 COMPANY BLOG
  ✅ 🌐 OpenAI News: 3 articles stored
  ✅ 🌐 Google Research Blog: 3 articles stored
  ✅ 📰 Anthropic News: 3 articles stored
  ✅ 📰 Microsoft Research Blog: 3 articles stored

📁 TECH NEWS
  ✅ 📰 TechCrunch AI: 3 articles stored
  ✅ 🌐 VentureBeat AI: 3 articles stored

═══════════════════════════════════════════════════════
TOTALS: 33 articles stored from 12/12 sources
═══════════════════════════════════════════════════════

💰 CREDIT USAGE SUMMARY
  Credits this run: 48
  Monthly projection (daily): 1,440
  Sources (RSS): 8
  Sources (Crawl): 4
  Credit limit (monthly): 3000
```

**Quality Indicators:**
- ✅ All 12 sources represented
- ✅ Balanced distribution (~3 per source)
- ✅ No archive/category URLs
- ✅ RSS used where available (lower credits)
- ✅ Within credit budget (1,440 < 3,000)

---

### Step 4: Run Diagnostic (After)

```bash
python scripts/diagnose_data_quality.py
```

**Expected Improvements:**
- ✅ Low quality issues (< 5%)
- ✅ Good source diversity (11-12/12 sources)
- ✅ Fresh content (last 24h)
- ✅ Balanced distribution

---

### Step 5: Process Content

```bash
python main.py process --max-items 5
```

**Expected Results:**
- Diverse content types (research, news, company blogs)
- Various sources represented
- Quality titles and content
- Recent articles (last 7 days)

---

## 🎯 Key Benefits

### 1. **Quality**
- ✅ Real articles, not listing pages
- ✅ Minimum 500 characters of actual content
- ✅ Meaningful paragraphs, not just links
- ✅ Proper article structure

### 2. **Freshness**
- ✅ RSS feeds prioritized for latest content
- ✅ 7-day freshness filter
- ✅ Content from last 24-48 hours
- ✅ Up-to-date news and research

### 3. **Diversity**
- ✅ 12 sources across 4 categories
- ✅ Balanced distribution (~3 per source)
- ✅ Multiple content types
- ✅ Different perspectives

### 4. **Credit Efficiency**
- ✅ RSS uses minimal credits (1 per article)
- ✅ Crawl limited to 3 pages
- ✅ URL deduplication prevents re-scraping
- ✅ Monthly projection: ~1,000-1,400 credits (well under 3,000 limit)

---

## 🔧 Configuration

All settings in `.env`:

```bash
# RSS Configuration (ensures fresh content)
USE_RSS_FEEDS=true
RSS_FRESHNESS_DAYS=7
RSS_FALLBACK_TO_CRAWL=true

# Credit Optimization (ensures quality + efficiency)
MAX_ARTICLES_PER_SOURCE=3
MAX_CRAWL_PAGES=3
ENABLE_URL_DEDUPLICATION=true
TRACK_CREDIT_USAGE=true
```

---

## 🚀 Best Practices

### Daily Workflow

1. **Morning**: Run fresh scrape
   ```bash
   python main.py scrape
   ```

2. **Review**: Check logs for quality
   - Look for ✅ icons (all sources scraped)
   - Verify credit usage (< 100 per run)
   - Check for balanced distribution

3. **Process**: Send to Opus
   ```bash
   python main.py process --max-items 15
   ```

4. **Approve**: Review jobs in Opus platform
   - Content should be diverse
   - Titles should be specific articles
   - Content should be recent

---

### Weekly Maintenance

1. **Run diagnostic**
   ```bash
   python scripts/diagnose_data_quality.py
   ```

2. **Check for issues**
   - Source diversity (all 12 sources active?)
   - Quality issues (< 10% bad data?)
   - Freshness (content from last 7 days?)

3. **Clean if needed**
   ```sql
   -- Run scripts/clean_bad_data.sql if quality issues found
   ```

---

## 📊 Expected Metrics

### After Fresh Scrape (Daily)
- **Items scraped**: 30-36 articles
- **Sources represented**: 11-12/12
- **Firecrawl credits**: 40-100
- **Archive pages**: 0
- **Average content length**: 1,500-5,000 characters

### After Processing (Daily)
- **Items sent to Opus**: 15
- **Source diversity**: 8-12 different sources
- **Content types**: Mix of news, research, blogs
- **Quality score**: 0.6-0.9 relevance

---

## 🐛 Troubleshooting

### Problem: Some sources return 0 items

**Diagnosis:**
```bash
python scripts/diagnose_data_quality.py
```

**Possible Causes:**
1. RSS feed unavailable → Fallback to crawl enabled?
2. All URLs filtered as invalid → Check source URL
3. Content too short → Source has short summaries
4. Network issues → Check Firecrawl status

**Solutions:**
- Verify RSS feed URL in `scripts/insert_sources.py`
- Check source is active in Supabase
- Review Firecrawl logs for errors
- Try manual scrape: `python -c "from src.scraper import scraper; print(scraper.scrape_url('URL'))"`

---

### Problem: Too many archive pages still getting through

**Check validation logic:**
1. Look at URLs in database
2. Identify patterns not caught
3. Add patterns to `_is_valid_article_url()`
4. Re-scrape

**Quick fix:**
```sql
-- In Supabase, manually mark specific patterns
UPDATE scraped_content 
SET is_processed = true
WHERE url LIKE '%your-new-pattern%';
```

---

### Problem: Credit usage too high

**Diagnosis:**
```bash
# Check last scrape logs for credit summary
# Look for "💰 CREDIT USAGE SUMMARY"
```

**Adjustments:**
```bash
# In .env
MAX_ARTICLES_PER_SOURCE=2  # Reduce from 3
MAX_CRAWL_PAGES=2          # Reduce from 3
```

---

## 📚 Related Documentation

- `RSS-AND-SOURCES.md` - RSS integration details
- `CREDIT-OPTIMIZATION.md` - Credit optimization strategies
- `WORKFLOW-INPUT-FIX.md` - Opus workflow input fixes
- `README.md` - General setup and usage

---

## ✅ Summary

The data quality enhancements ensure:

1. **Only real articles** are scraped (no archive/category pages)
2. **Fresh content** from last 7 days via RSS
3. **Diverse sources** - all 12 sources contribute equally
4. **Quality content** - minimum 500 chars, proper structure
5. **Credit efficient** - ~1,000-1,400 credits/month (under 3,000 limit)
6. **Easy diagnostics** - comprehensive tools for monitoring

**Result**: High-quality, diverse, fresh content ready for AI-powered social media post generation! 🎉
