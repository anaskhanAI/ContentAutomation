# RSS Feed Integration & Content Source Management

## Overview

This document describes the RSS feed integration and enhanced content source management features added to the Content Automation System.

## 🎯 **Key Features**

### 1. **RSS Feed Support**
- Efficient content discovery using RSS/Atom feeds
- Built-in date filtering (last 7 days by default)
- Hybrid approach: RSS for discovery + web scraping for full content
- Automatic fallback to web crawling if RSS unavailable

### 2. **Database-Driven Source Management**
- All content sources stored in Supabase `content_sources` table
- Support for RSS feed URLs in source metadata
- Source categorization by type (research_papers, news_aggregator, company_blog, tech_news)
- Dynamic source activation/deactivation

### 3. **Intelligent Scraping Strategy**
```
For each source:
  IF has RSS feed AND RSS enabled:
    1. Fetch RSS feed
    2. Filter entries by date (last N days)
    3. Scrape full content from article URLs
  ELSE:
    1. Use web crawling (existing Firecrawl method)
```

---

## 📋 **Content Sources**

### Research Papers (2 sources)
- **Hugging Face Papers**: https://huggingface.co/papers
- **Papers with Code**: https://paperswithcode.com/

### AI News Aggregators (4 sources)
- **Alpha Signal**: https://alphasignal.ai/
- **The Rundown AI**: https://www.therundown.ai/archive (has RSS)
- **Ben's Bites**: https://bensbites.beehiiv.com/archive (has RSS)
- **TLDR AI**: https://tldr.tech/ai/archives (has RSS)

### Company Research Blogs (4 sources)
- **OpenAI News**: https://openai.com/news/ (has RSS)
- **Google Research Blog**: https://research.google/blog/ (has RSS)
- **Anthropic News**: https://www.anthropic.com/news (may have RSS)
- **Microsoft Research Blog**: https://www.microsoft.com/en-us/research/blog/ (has RSS)

### Tech News (2 sources)
- **TechCrunch AI**: https://techcrunch.com/category/artificial-intelligence/ (has RSS)
- **VentureBeat AI**: https://venturebeat.com/category/ai/ (has RSS)

**Total: 12 sources** (9 with RSS feeds)

---

## 🚀 **Setup Instructions**

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependency added:
- `feedparser>=6.0.11` - RSS/Atom feed parsing

### 2. Populate Content Sources

Run the source insertion script:

```bash
python scripts/insert_sources.py
```

This will:
- Insert all 12 content sources into Supabase
- Skip sources that already exist
- Verify insertion was successful
- Display summary of active sources

### 3. Configure RSS Settings

Update your `.env` file:

```env
# RSS Feed Configuration
USE_RSS_FEEDS=true                 # Enable/disable RSS feeds
RSS_FRESHNESS_DAYS=7               # Only fetch entries from last N days
RSS_FALLBACK_TO_CRAWL=true         # Fallback to web crawling if RSS fails
```

---

## 📊 **Configuration Options**

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_RSS_FEEDS` | `true` | Enable RSS feed usage |
| `RSS_FRESHNESS_DAYS` | `7` | Only fetch RSS entries from last N days |
| `RSS_FALLBACK_TO_CRAWL` | `true` | Fall back to web crawling if RSS unavailable |

### Source Metadata Fields

Sources in the database have an optional `metadata` field (JSONB) that can contain:

```json
{
  "has_rss": true,
  "rss_feed_url": "https://example.com/feed/",
  "description": "Source description",
  "priority": "high",
  "language": "en"
}
```

---

## 🔧 **How It Works**

### RSS Scraping Flow

```python
# 1. Fetch RSS feed
entries = rss_reader.fetch_feed(rss_feed_url, only_recent=True)

# 2. Filter by date (last 7 days)
# This happens inside fetch_feed() automatically

# 3. For each entry:
for entry in entries:
    # Get article URL from RSS
    article_url = entry['link']
    
    # Scrape full content
    full_content = scraper.scrape_url(article_url)
    
    # Enhance with RSS metadata
    full_content.published_at = entry['published_at']
    full_content.author = entry['author']
```

### Date Filtering

The RSS reader automatically filters content based on `RSS_FRESHNESS_DAYS`:

```python
# Content age calculation
cutoff = datetime.now() - timedelta(days=settings.rss_freshness_days)

# Only include recent content
if published_date >= cutoff:
    # Include in results
```

### Freshness Scoring

The content processor already has freshness scoring built-in:

```python
# Freshness component (10% of relevance score)
if age < 1 day:    freshness = 1.0
if age < 7 days:   freshness = 0.8
if age < 30 days:  freshness = 0.6
if age < 90 days:  freshness = 0.4
else:              freshness = 0.2
```

---

## 🛠️ **New Modules**

### `src/rss_reader.py`

RSS/Atom feed parsing module:

```python
from src.rss_reader import rss_reader

# Fetch recent articles
entries = rss_reader.fetch_feed('https://example.com/feed/')

# Get just the URLs
urls = rss_reader.get_recent_articles('https://example.com/feed/')

# Check if feed is valid
is_valid = rss_reader.check_feed_availability('https://example.com/feed/')
```

### `scripts/insert_sources.py`

Source ingestion script:

```bash
# Insert all sources
python scripts/insert_sources.py

# Output shows:
# - Sources inserted
# - Sources skipped (already exist)
# - Errors if any
# - Verification of active sources
```

---

## 📈 **Benefits**

### 1. **Recency Guarantee**
- Only content from last 7 days (configurable)
- RSS provides accurate publish dates
- Better freshness scores

### 2. **Efficiency**
- RSS fetches faster than full web crawling
- Less Firecrawl API credits used
- Only scrape full content for recent articles

### 3. **Scalability**
- Easy to add new sources (just insert into database)
- No code changes needed for new sources
- Sources can be enabled/disabled dynamically

### 4. **Quality**
- Authoritative sources (OpenAI, Google, Microsoft, etc.)
- Diverse content types
- Better relevance through date filtering

---

## 🧪 **Testing**

### Test RSS Feed

```bash
python -c "
from src.rss_reader import rss_reader

# Test a feed
entries = rss_reader.fetch_feed('https://openai.com/news/rss/')
print(f'Found {len(entries)} recent entries')

for entry in entries[:3]:
    print(f\"  - {entry['title']}\")
    print(f\"    Published: {entry['published_at']}\")
"
```

### Test Source Scraping

```bash
# Run scraping with RSS enabled
python main.py scrape

# Check logs for RSS usage:
# "Using RSS feed for source..."
# "RSS scraping successful..."
```

### Verify in Database

```bash
python -c "
from src.database import db

sources = db.get_active_sources()
rss_count = sum(1 for s in sources if s.metadata.get('has_rss'))

print(f'Total sources: {len(sources)}')
print(f'Sources with RSS: {rss_count}')
"
```

---

## 🐛 **Troubleshooting**

### RSS Feed Not Found

```
WARNING: No recent entries found in RSS feed
```

**Solutions:**
- Check if RSS URL is correct
- Verify feed is publicly accessible
- Try increasing `RSS_FRESHNESS_DAYS`

### Fallback to Web Crawling

```
WARNING: RSS scraping failed, falling back to web crawling
```

**This is normal behavior when:**
- RSS feed is temporarily unavailable
- Feed format is invalid
- Network issues

**The system will automatically use web crawling instead.**

### Source Not Scraped

**Check:**
1. Is source active? `is_active = true` in database
2. Is RSS URL correct in metadata?
3. Are RSS settings enabled in `.env`?

---

## 📝 **Database Schema**

### content_sources Table

```sql
CREATE TABLE content_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    scraping_frequency_minutes INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT true,
    reliability_score FLOAT DEFAULT 1.0,
    last_scraped_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Example Source Record

```json
{
  "id": "uuid-here",
  "url": "https://openai.com/news/",
  "name": "OpenAI News",
  "source_type": "company_blog",
  "scraping_frequency_minutes": 240,
  "is_active": true,
  "metadata": {
    "has_rss": true,
    "rss_feed_url": "https://openai.com/news/rss/",
    "description": "Official OpenAI news and research",
    "priority": "very_high",
    "language": "en"
  }
}
```

---

## 🎓 **Best Practices**

1. **Always run `scripts/insert_sources.py` first** before scraping
2. **Monitor RSS availability** - some feeds may change URLs
3. **Adjust `RSS_FRESHNESS_DAYS`** based on source update frequency
4. **Enable fallback** to ensure continuous operation
5. **Check `python main.py status`** to verify sources and RSS config

---

## 🔄 **Migration from Old System**

If you were using the old `CONTENT_SOURCES` environment variable:

1. **Run the insertion script** to populate database
2. **Old env var still works** as fallback
3. **Database sources take priority** over env var
4. **Recommended:** Remove env var after confirming database sources work

---

## 📚 **Related Documentation**

- [15-Item Workflow](./15-ITEM-WORKFLOW.md) - Content selection strategy
- [Firecrawl SDK Update](./FIRECRAWL-SDK-UPDATE.md) - Web scraping details
- [Setup Guide](../SETUP.md) - Initial setup instructions

---

## ✅ **Verification Checklist**

After setup, verify everything works:

- [ ] Dependencies installed (`feedparser` present)
- [ ] Sources inserted (12 total in database)
- [ ] RSS settings configured in `.env`
- [ ] `python main.py status` shows RSS info
- [ ] Test scraping: `python main.py scrape`
- [ ] Check logs for RSS usage
- [ ] Verify content in database has recent dates

---

**Last Updated:** 2026-01-19
