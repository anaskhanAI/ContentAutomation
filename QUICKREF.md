# Quick Reference Guide

## Common Commands

```bash
# Test all connections
python main.py test

# Check system status (now shows quota, quality distribution, top items)
python main.py status

# Run scraping once
python main.py scrape

# Process existing content (default: 15 items with intelligent selection)
python main.py process

# Process with custom settings
python main.py process --min-relevance 0.6 --max-items 10

# Run complete pipeline once (scrape + intelligent processing)
python main.py run

# Start automated scheduler
python main.py schedule

# View help
python main.py --help
```

## Configuration Quick Check

```bash
# Required environment variables
OPUS_API_KEY          # From Opus → My Organization → API Keys
OPUS_WORKFLOW_ID      # From workflow URL
FIRECRAWL_API_KEY     # From firecrawl.dev
SUPABASE_URL          # From Supabase → Settings → API
SUPABASE_KEY          # From Supabase → Settings → API (anon key)

# Processing configuration (new in v1.1)
MAX_ITEMS_PER_RUN=15         # Items per processing run (default: 15)
MIN_RELEVANCE_SCORE=0.5      # Quality threshold (default: 0.5)
DAILY_POST_LIMIT=30          # Safety limit (default: 30)
ENABLE_CONTENT_DIVERSITY=true    # Intelligent selection (default: true)
IMMEDIATE_PROCESSING=true        # Auto-process mode (default: true)
```

## Database Quick Queries

```sql
-- Check recent jobs
SELECT job_execution_id, status, initiated_at 
FROM opus_jobs 
ORDER BY initiated_at DESC 
LIMIT 10;

-- High-relevance content waiting
SELECT title, relevance_score, url 
FROM scraped_content 
WHERE is_processed = false AND relevance_score > 0.5
ORDER BY relevance_score DESC;

-- Recent system events
SELECT * FROM system_logs 
ORDER BY created_at DESC 
LIMIT 20;

-- Published posts
SELECT post_text, published_at, platform, post_url
FROM published_posts
ORDER BY published_at DESC;
```

## Troubleshooting Quick Fixes

### Connection Issues
```bash
# Test connections
python main.py test

# Check logs
tail -f logs/content_automation.log

# Enable debug mode
# In .env: LOG_LEVEL=DEBUG
```

### No Content Scraped
1. Check source URLs are accessible
2. Verify Firecrawl API quota
3. Check logs for errors

### Opus Job Failures
1. Verify workflow ID is correct
2. Check workflow input schema matches
3. Review audit log in Opus

### Database Errors
1. Verify Supabase credentials
2. Check project isn't paused
3. Verify schema is deployed

## File Structure

```
src/
├── config.py          # Configuration & environment variables
├── logger.py          # Logging setup
├── models.py          # Data models (Pydantic)
├── database.py        # Supabase client & queries
├── scraper.py         # Firecrawl web scraping
├── processor.py       # Content scoring & categorization
├── opus_client.py     # Opus API integration
├── orchestrator.py    # Pipeline orchestration
└── scheduler.py       # Automated scheduling

database/
└── schema.sql         # Database schema (run in Supabase)

main.py               # CLI entry point
```

## Key Metrics

### Relevance Score Components
- Keywords: 40%
- Title: 30%
- Content Quality: 20%
- Freshness: 10%

### Quality Tiers (New in v1.1)
- Tier 1 (Excellence): ≥ 0.8 - Always prioritized
- Tier 2 (Quality): 0.6 - 0.8 - Selected with diversity
- Tier 3 (Good): 0.5 - 0.6 - Fill to quota

### Default Thresholds
- Minimum relevance for processing: 0.5
- Default scraping interval: 60 minutes
- Max items per processing run: **15** (updated)
- Max pages per source crawl: 10
- Daily post limit: **30** (new safety feature)

## API Endpoints Reference

### Opus API
```
GET  /workflow/{id}              # Get workflow schema
POST /job/initiate               # Create job
POST /job/execute                # Execute job
GET  /job/{id}/status            # Check status
GET  /job/{id}/results           # Get results
GET  /job/{id}/audit             # Get audit log
```

## Scheduler Modes

```bash
# Full pipeline (default) - scrape + process together
python main.py schedule --mode full_pipeline

# Separate - scrape and process independently
python main.py schedule --mode separate

# Scraping only
python main.py schedule --mode scraping

# Processing only
python main.py schedule --mode processing
```

## Environment Variables

```bash
# Required
OPUS_API_KEY
OPUS_WORKFLOW_ID
FIRECRAWL_API_KEY
SUPABASE_URL
SUPABASE_KEY

# Optional
OPUS_BASE_URL=https://operator.opus.com
ENVIRONMENT=development
LOG_LEVEL=INFO
SCRAPING_INTERVAL_MINUTES=60
MAX_RETRIES=3
RETRY_DELAY_SECONDS=5
CONTENT_SOURCES=url1,url2
TARGET_AUDIENCE=B2B_decision_makers
```

## Logs Location

- Application logs: `logs/content_automation.log`
- Database logs: `system_logs` table in Supabase
- Scheduler output: stdout (or redirected file)

## Content Types

- `industry_news`: News articles and updates
- `thought_leadership`: Insights and analysis
- `case_study`: Success stories and implementations

## Quick Workflow Test

```bash
# 1. Test connections
python main.py test

# 2. Scrape some content
python main.py scrape

# 3. Check what was scraped
python main.py status

# 4. Process and send to Opus
python main.py process --max-items 1

# 5. Check Opus dashboard for job
# Go to Opus → Jobs → Review → Approve → Publish
```
