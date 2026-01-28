# 💰 Firecrawl Credit Optimization Guide

## Overview

This system is optimized for **sustainable usage** within the **3,000 credits/month** Firecrawl API limit.

**Option B: Balanced Approach** is implemented by default.

---

## 📊 Credit Costs

| Method | Cost | Use Case |
|--------|------|----------|
| **RSS Feed Parsing** | 0 credits | Free content discovery |
| **Scrape (per article)** | 1 credit | Get full article content |
| **Crawl (per site)** | 10+ credits | Discover pages on site |

---

## ⚙️ Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Credit Optimization (Firecrawl API - 3000 credits/month limit)
MAX_ARTICLES_PER_SOURCE=3          # Max articles to scrape per source
MAX_CRAWL_PAGES=3                  # Max pages to crawl when no RSS
ENABLE_URL_DEDUPLICATION=true      # Skip already-scraped URLs
TRACK_CREDIT_USAGE=true            # Log credit usage
```

### Preset Options

**Current: Option B - Balanced Approach ✅**
- Top 3 articles per source with full scrape
- ~60 credits/run, run 3-4x/week
- **~800-1,000 credits/month** (well within limit!)

**Other Available Options:**

**Option A: Maximum Quality** (uses more credits)
```bash
MAX_ARTICLES_PER_SOURCE=5
MAX_CRAWL_PAGES=5
```
- ~100 credits/run, run 2-3x/week
- ~1,200-1,500 credits/month

**Option C: Maximum Efficiency** (uses fewer credits)
```bash
MAX_ARTICLES_PER_SOURCE=2
MAX_CRAWL_PAGES=2
```
- ~40 credits/run, run 5-6x/week
- ~800-1,000 credits/month

---

## 🎯 Optimization Features

### 1. **Article Limit Per Source**
- Limits RSS articles scraped to `MAX_ARTICLES_PER_SOURCE` (default: 3)
- Processes most recent articles first
- Saves: **67% reduction** in credits vs unlimited

### 2. **URL Deduplication**
- Checks if URL already exists in database before scraping
- Skips duplicate URLs automatically
- Saves: **30-50% reduction** on subsequent runs

### 3. **Reduced Crawl Pages**
- Limits web crawling to `MAX_CRAWL_PAGES` (default: 3)
- Only used for sources without RSS feeds
- Saves: **97% reduction** vs unlimited crawling (100+ pages)

### 4. **RSS-First Strategy**
- Uses free RSS feed parsing for content discovery
- Only uses Firecrawl API to scrape full article content
- Saves: **100% on discovery**, only 1 credit per article

---

## 📈 Credit Usage Tracking

### Real-Time Monitoring

When scraping, you'll see detailed credit logs:

```
💰 Firecrawl Credits Used
   source=VentureBeat AI
   credits_used=3
   articles_scraped=3
   duplicates_skipped=2
```

### Summary Report

After each scrape run:

```
📊 CREDIT USAGE SUMMARY
   credits_this_run=45
   monthly_projection_daily=1350
   sources_total=12
   sources_rss=9
   sources_crawl=3
   articles_scraped=36
   credit_limit_monthly=3000
```

### Warning System

Automatic warnings when approaching limits:

```
⚠️  CREDIT CAUTION: Approaching 80% of monthly limit
   projected=2400
   limit=3000
   usage_percent=80
```

---

## 🚀 Expected Usage (Option B)

### Per Scrape Run

```
9 sources WITH RSS:
  - 3 articles each × 9 = 27 articles
  - 1 credit per article = 27 credits
  
3 sources WITHOUT RSS:
  - Crawl 3 pages each × 3 = 9 pages
  - ~10 credits per source = 30 credits
  
TOTAL PER RUN: ~60 credits
```

### Monthly Projection

```
Scraping 3-4 times per week:
  - 60 credits/run × 15 runs/month
  - = 900 credits/month
  
WELL WITHIN 3,000 LIMIT! ✅
REMAINING: 2,100 credits (70% buffer)
```

---

## 🔍 Monitoring Your Usage

### Check Credit Usage

```bash
# Run a scrape and monitor credits
python main.py scrape

# Look for these log lines:
# 💰 Firecrawl Credits Used (per source)
# 📊 CREDIT USAGE SUMMARY (end of run)
```

### View in Database

Credits used are stored in metadata:

```sql
SELECT 
  url,
  title,
  metadata->>'firecrawl_credits_used' as credits
FROM scraped_content
WHERE metadata->>'firecrawl_credits_used' IS NOT NULL
ORDER BY scraped_at DESC
LIMIT 20;
```

---

## ⚡ Performance Tips

### 1. **Scrape Less Frequently**
- Run 3-4x per week instead of daily
- AI news doesn't change that drastically
- Saves 50% on credits

### 2. **Prioritize RSS Sources**
- Add RSS feeds for all sources when possible
- Check `/rss`, `/feed`, or `/atom` endpoints
- Saves 90% on credits vs crawling

### 3. **Clean Old Data**
- Periodically archive processed content
- Keeps deduplication checks fast
- Prevents re-scraping

### 4. **Monitor Projections**
- Check the summary report after each run
- Adjust `MAX_ARTICLES_PER_SOURCE` if needed
- Stay proactive about credit usage

---

## 🛠️ Troubleshooting

### "Monthly projection exceeds limit"

**Solution 1:** Reduce articles per source
```bash
MAX_ARTICLES_PER_SOURCE=2  # Down from 3
```

**Solution 2:** Scrape less frequently
```bash
# Run 2x per week instead of 4x
```

**Solution 3:** Disable some sources
```sql
-- In Supabase
UPDATE content_sources 
SET is_active = false 
WHERE reliability_score < 0.7;
```

### "Too many duplicates skipped"

**Good thing!** Deduplication is saving you credits.

To see fresh content:
- Wait longer between scrapes
- Or clear old processed content

### "Crawl using too many credits"

**Solution:** Add RSS feed for that source
```sql
-- In Supabase
UPDATE content_sources 
SET metadata = metadata || '{"rss_feed_url": "https://example.com/feed", "has_rss": true}'
WHERE url = 'https://example.com';
```

---

## 📝 Best Practices

1. ✅ **Always enable URL deduplication**
2. ✅ **Use RSS feeds whenever possible**
3. ✅ **Monitor credit usage after each run**
4. ✅ **Adjust limits based on your needs**
5. ✅ **Keep `MAX_ARTICLES_PER_SOURCE` at 2-5**
6. ✅ **Keep `MAX_CRAWL_PAGES` at 2-3**
7. ✅ **Run scrapes 2-4 times per week**

---

## 🎯 Summary

With **Option B (Balanced Approach)**:

- ✅ **~900 credits/month** (30% of limit)
- ✅ **70% buffer** for occasional extra runs
- ✅ **High-quality content** (full articles)
- ✅ **Sustainable** for long-term use
- ✅ **Automatic monitoring** and warnings

**You're all set for sustainable, credit-efficient scraping!** 🚀
