# 🚀 Quick Start: Credit Optimization

## ⚡ Get Started in 3 Minutes

### Step 1: Update .env File (30 seconds)

Add these lines to your `.env` file:

```bash
# Credit Optimization (Firecrawl API - 3000 credits/month limit)
MAX_ARTICLES_PER_SOURCE=3
MAX_CRAWL_PAGES=3
ENABLE_URL_DEDUPLICATION=true
TRACK_CREDIT_USAGE=true
```

Or copy the entire file from `env.example`.

---

### Step 2: Run a Test Scrape (2 minutes)

```bash
python main.py scrape
```

**Watch for these log messages:**

```
💰 Firecrawl Credits Used
   source=VentureBeat AI
   credits_used=3
   articles_scraped=3
   duplicates_skipped=0

💰 Firecrawl Credits Used
   source=TechCrunch AI
   credits_used=3
   articles_scraped=3
   duplicates_skipped=1

📊 CREDIT USAGE SUMMARY
   credits_this_run=54
   monthly_projection_daily=1620
   sources_total=12
   sources_rss=9
   sources_crawl=3
   articles_scraped=33
   credit_limit_monthly=3000
```

---

### Step 3: Verify Results (30 seconds)

✅ **Check credits used:**
   - Should be ~50-70 credits for first run
   - Should show ~1,500-2,100 monthly projection

✅ **Check articles scraped:**
   - Should be ~30-40 articles total
   - Max 3 per source

✅ **No warnings:**
   - Should NOT see ⚠️ CREDIT WARNING
   - Should be well within limit

---

## 📊 What You Should See

### **First Run Example:**

```
RSS feed scraping completed
   rss_url=https://venturebeat.com/feed/
   total_entries=3
   scraped=3
   skipped_duplicates=0
   estimated_credits=3

💰 Firecrawl Credits Used
   source=VentureBeat AI
   credits_used=3
   articles_scraped=3
   duplicates_skipped=0
```

### **Second Run Example (30 min later):**

```
RSS feed scraping completed
   rss_url=https://venturebeat.com/feed/
   total_entries=3
   scraped=1
   skipped_duplicates=2  ← Duplicates skipped!
   estimated_credits=1   ← Only 1 credit used!

💰 Firecrawl Credits Used
   source=VentureBeat AI
   credits_used=1        ← Saved 2 credits!
   articles_scraped=1
   duplicates_skipped=2
```

---

## 🎯 Expected Performance

| Metric | Target | Your Result |
|--------|--------|-------------|
| Credits/Run | 50-70 (first), 30-40 (avg) | _____ |
| Articles/Run | 30-40 | _____ |
| Duplicates Skipped | 0 (first), 10-20 (next) | _____ |
| Monthly Projection | 900-1,500 | _____ |
| % of Limit | 30-50% | _____ |

---

## ⚙️ Optional: Adjust Settings

### Use Fewer Credits

```bash
MAX_ARTICLES_PER_SOURCE=2  # Down from 3
MAX_CRAWL_PAGES=2          # Down from 3
```

Expected: ~800-1,000 credits/month

### Get More Content

```bash
MAX_ARTICLES_PER_SOURCE=5  # Up from 3
MAX_CRAWL_PAGES=5          # Up from 3
```

Expected: ~1,500-2,000 credits/month

---

## 🔍 Troubleshooting

### "Monthly projection too high"

**Check:**
- Are you seeing many "crawl" operations?
- Add RSS feeds for those sources (see `docs/RSS-AND-SOURCES.md`)

**Fix:**
```bash
MAX_ARTICLES_PER_SOURCE=2  # Reduce from 3
```

### "Not getting enough content"

**Check:**
- How many duplicates are being skipped?
- Try running less frequently (every 2-3 days)

**Fix:**
```bash
MAX_ARTICLES_PER_SOURCE=5  # Increase from 3
```

### "Can't find the logs"

**Run with visible output:**
```bash
python main.py scrape 2>&1 | grep -E "💰|📊|⚠️"
```

This will show only credit-related logs.

---

## 📚 Learn More

- **[Full Credit Optimization Guide](docs/CREDIT-OPTIMIZATION.md)**
- **[Implementation Summary](CREDIT-OPTIMIZATION-SUMMARY.md)**
- **[RSS and Sources](docs/RSS-AND-SOURCES.md)**

---

## ✅ You're All Set!

Your system is now optimized for:

✅ **Sustainable usage** - Stay within 3,000 credit limit
✅ **Smart deduplication** - Don't pay twice
✅ **Real-time monitoring** - Know what you're using
✅ **Automatic warnings** - Never exceed limits

**Happy scraping!** 🎉
