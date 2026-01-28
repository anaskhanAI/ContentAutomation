# Content Automation System for Opus

An intelligent content automation pipeline that scrapes web content, processes it for relevance, generates social media posts using Opus AI workflows, and publishes them to Twitter/X with human approval.

> **🎉 NEW: Web UI Available!** Beautiful modern web interface now available! Manage sources, trigger scraping, and submit Opus jobs from your browser. See [WEB-UI-COMPLETE-SUMMARY.md](WEB-UI-COMPLETE-SUMMARY.md) to get started!

> **✨ Latest: Data Quality Upgrade** The system ensures fresh, diverse, high-quality content from all 12 sources with smart filtering and validation. See [QUALITY-UPGRADE-COMPLETE.md](QUALITY-UPGRADE-COMPLETE.md) for details.

## 🎯 Overview

This system demonstrates Opus's capabilities by automating your own content marketing workflow:

1. **Multi-Source Scraping**: Scrapes from 12+ AI/tech sources using RSS feeds + Firecrawl
2. **Intelligent Content Discovery**: RSS-first strategy with automatic date filtering (last 7 days)
3. **Intelligence Layer**: Scores content for relevance (with freshness weighting) and categorizes by type
4. **Opus Integration**: Sends high-quality content to Opus workflows for AI-powered post generation
5. **Human Approval**: Content is reviewed and approved within Opus
6. **Auto-Publishing**: Approved posts are automatically published to Twitter/X

## ✨ Key Features

### 🌐 **12 Premium Content Sources**
- **Research Papers**: Hugging Face, Papers with Code
- **News Aggregators**: Alpha Signal, The Rundown AI, Ben's Bites, TLDR AI
- **Company Blogs**: OpenAI, Google Research, Anthropic, Microsoft Research
- **Tech News**: TechCrunch, VentureBeat

### 📡 **RSS Feed Integration**
- **Efficient Discovery**: Uses RSS feeds for 9 sources (75% coverage)
- **Date Filtering**: Only fetches content from last 7 days (configurable)
- **Hybrid Approach**: RSS for URLs + web scraping for full content
- **Auto Fallback**: Seamlessly falls back to web crawling if RSS unavailable

### 🎯 **Intelligent Content Selection**
- **Tiered Quality System**: Excellence (0.8+), Great (0.6-0.8), Good (0.5-0.6)
- **Diversity Algorithm**: Ensures content variety across categories
- **Freshness Scoring**: Recent content gets higher relevance scores
- **Daily Limits**: Safety controls for Opus job execution (30/day default)

### 💰 **Credit Optimization** (NEW!)
- **Sustainable Usage**: Optimized for 3,000 credits/month Firecrawl limit
- **Smart Limits**: Max 3 articles per source (configurable)
- **URL Deduplication**: Skips already-scraped content (30-50% savings)
- **RSS-First**: Free content discovery + 1 credit per article
- **Usage Tracking**: Real-time credit monitoring and monthly projections
- **Auto Warnings**: Alerts when approaching credit limits
- **~900 credits/month**: Option B (Balanced) uses only 30% of limit!

## 🏗️ Architecture

```
┌─────────────────┐
│  Web Sources    │
│  (TechCrunch,   │
│   The Verge)    │
└────────┬────────┘
         │
         │ Firecrawl
         ▼
┌─────────────────┐
│   Scraper       │ ──► Store in Supabase
│   Module        │
└────────┬────────┘
         │
         │ Process & Score
         ▼
┌─────────────────┐
│   Processor     │ ──► Calculate Relevance
│   Module        │     Categorize Content
└────────┬────────┘
         │
         │ High-Relevance Content
         ▼
┌─────────────────┐
│ Opus API Client │ ──► Initiate Job
│                 │     Execute Workflow
│                 │     Poll Status
└────────┬────────┘
         │
         │ Generated Content
         ▼
┌─────────────────┐
│  Opus Workflow  │
│  - Agent Node   │ ──► Generate Post
│  - Validation   │     Human Approval
│  - Approval     │     Post to X
└─────────────────┘
```

## 📋 Features

- **Automated Web Scraping**: Uses Firecrawl to crawl and scrape content from multiple sources
- **Intelligent Filtering**: Calculates relevance scores based on keywords, content quality, and freshness
- **Content Categorization**: Automatically categorizes content as industry news, thought leadership, or case studies
- **Opus Integration**: Complete API integration with job initiation, execution, status polling, and results retrieval
- **Database Tracking**: Full audit trail in Supabase for all scraped content, jobs, and published posts
- **Automated Scheduling**: Built-in scheduler for hands-free operation
- **Error Handling**: Robust retry logic and comprehensive error logging
- **CLI Interface**: Easy-to-use command-line interface for all operations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account and project
- Firecrawl API key
- Opus account with API access
- Twitter/X integration configured in Opus

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd "/Users/anas/Documents/Ops on Opus/Content Automation"
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up Supabase database**:
   - Create a new Supabase project
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste the contents of `database/schema.sql`
   - Execute the SQL to create all tables and indexes

5. **Populate content sources**:
```bash
python scripts/insert_sources.py
```
This inserts all 12 content sources (research papers, news aggregators, company blogs, tech news) into Supabase with RSS feed URLs where available.

6. **Configure environment variables**:
   - Copy `env.example` to `.env`:
     ```bash
     cp env.example .env
     ```
   - Edit `.env` and fill in your credentials:
     ```bash
     # Opus API
     OPUS_API_KEY=your_opus_service_key_here
     OPUS_WORKFLOW_ID=your_workflow_id_here
     
     # Firecrawl
     FIRECRAWL_API_KEY=your_firecrawl_api_key_here
     
     # Supabase
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
     
     # Content Sources
     CONTENT_SOURCES=https://techcrunch.com/category/artificial-intelligence/
     ```

6. **Test connections**:
```bash
python main.py test
```

### First Run

Run the complete pipeline once to test:

```bash
python main.py run
```

This will:
- Scrape content from configured sources
- Process and score the content
- Send high-relevance items to Opus
- Display results

## 📖 Usage

### CLI Commands

#### Run Full Pipeline Once
```bash
# Run complete pipeline (scrape + process with intelligent selection)
python main.py run

# Uses defaults from config: max_items=15, min_relevance=0.5
# Includes daily quota checking and tiered quality selection

# Run with custom settings
python main.py run --min-relevance 0.6 --max-items 10

# Skip scraping (only process existing content)
python main.py run --no-scrape
```

#### Scrape Only
```bash
# Scrape content from all active sources
python main.py scrape
```

#### Process Only
```bash
# Process existing content and send to Opus (default: 15 items)
python main.py process

# Shows daily quota before and after
# Uses intelligent tiered selection for quality

# With custom filters
python main.py process --min-relevance 0.7 --max-items 10
```

#### Start Automated Scheduler
```bash
# Run full pipeline automatically at intervals
python main.py schedule

# Run scraping and processing separately
python main.py schedule --mode separate

# Only scraping
python main.py schedule --mode scraping
```

#### Show System Status
```bash
python main.py status
```

#### Test Connections
```bash
python main.py test
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPUS_API_KEY` | Opus service key | ✅ | - |
| `OPUS_WORKFLOW_ID` | Workflow ID for content generation | ✅ | - |
| `FIRECRAWL_API_KEY` | Firecrawl API key | ✅ | - |
| `SUPABASE_URL` | Supabase project URL | ✅ | - |
| `SUPABASE_KEY` | Supabase anonymous key | ✅ | - |
| `SCRAPING_INTERVAL_MINUTES` | Interval between scraping runs | ❌ | 60 |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | ❌ | INFO |
| `MAX_ITEMS_PER_RUN` | Items to send to Opus per run | ❌ | 15 |
| `MIN_RELEVANCE_SCORE` | Minimum relevance threshold | ❌ | 0.5 |
| `DAILY_POST_LIMIT` | Max Opus jobs per day (safety) | ❌ | 30 |
| `ENABLE_CONTENT_DIVERSITY` | Enable intelligent diversity | ❌ | true |
| `IMMEDIATE_PROCESSING` | Process after scraping | ❌ | true |
| `CONTENT_SOURCES` | Comma-separated URLs to scrape | ❌ | - |

### Content Sources

Add sources in Supabase `content_sources` table or via the `CONTENT_SOURCES` environment variable:

```sql
INSERT INTO content_sources (url, name, source_type)
VALUES 
  ('https://techcrunch.com/category/artificial-intelligence/', 'TechCrunch AI', 'news'),
  ('https://www.theverge.com/ai-artificial-intelligence', 'The Verge AI', 'news');
```

## 🧩 System Components

### 1. Scraper Module (`src/scraper.py`)
- Uses Firecrawl API for web scraping
- Extracts title, content, summary, keywords, author, and metadata
- Generates content hashes for deduplication
- Supports both single URL scraping and website crawling

### 2. Processor Module (`src/processor.py`)
- **Relevance Scoring**: Calculates scores (0.0-1.0) based on:
  - Keyword matching (40%)
  - Title relevance (30%)
  - Content quality (20%)
  - Freshness (10%)
- **Intelligent Selection**: 
  - Tiered quality selection (Tier 1: ≥0.8, Tier 2: 0.6-0.8, Tier 3: 0.5-0.6)
  - Content diversity across categories
  - Smart distribution to ensure variety
- **Categorization**: Auto-categorizes as industry_news, thought_leadership, or case_study
- **Data Preparation**: Formats data for Opus workflows

### 3. Opus Client (`src/opus_client.py`)
- Complete Opus API integration
- Workflow schema retrieval and caching
- Job initiation and execution
- Status polling with timeout handling
- Results retrieval
- Audit log access
- Retry logic with exponential backoff

### 4. Database Client (`src/database.py`)
- Supabase integration
- CRUD operations for all data models
- Efficient querying with filters and sorting
- Comprehensive error handling

### 5. Orchestrator (`src/orchestrator.py`)
- Coordinates the complete pipeline
- Manages data flow between components
- Error handling and recovery
- Job tracking and status updates

### 6. Scheduler (`src/scheduler.py`)
- APScheduler-based automation
- Multiple scheduling modes
- Cron support for custom schedules
- System event logging

## 📊 Database Schema

The system uses the following main tables in Supabase:

- **content_sources**: Web sources to scrape
- **scraped_content**: Raw scraped data with relevance scores
- **opus_jobs**: Job execution tracking
- **generated_content**: AI-generated posts
- **published_posts**: Published social media posts
- **content_templates**: Prompt templates for content generation
- **system_logs**: System-wide audit trail

See `database/schema.sql` for complete schema.

## 🔄 Workflow

### Complete Pipeline Flow

1. **Scraping Phase**:
   - Fetch active sources from database
   - Crawl each source using Firecrawl
   - Extract content, metadata, and keywords
   - Generate content hash for deduplication
   - Store in `scraped_content` table

2. **Processing Phase**:
   - Retrieve unprocessed content
   - Filter by minimum relevance threshold (default: 0.5)
   - **Intelligent Selection** (default: 15 items):
     - Tier 1: Excellence items (≥0.8) prioritized
     - Tier 2: Quality items (0.6-0.8) with diversity
     - Tier 3: Good items (0.5-0.6) to fill quota
   - Check daily posting limit (default: 30/day)
   - Ensure category diversity

3. **Opus Execution Phase**:
   - Prepare data for Opus workflow
   - Initiate job via API
   - Execute job with content payload
   - Poll status until completion
   - Retrieve results
   - Store in database

4. **Human Approval Phase** (in Opus):
   - Content appears in Opus approval node
   - Human reviews and approves/rejects
   - Approved content proceeds to publishing

5. **Publishing Phase** (in Opus):
   - Opus posts to Twitter/X via integration
   - External system polls for completion
   - Retrieves results and logs success

## 🎨 Opus Workflow Setup

Your Opus workflow should have:

1. **Input Nodes**:
   - `scraped_content` (object): Contains url, title, summary, keywords
   - `content_type` (string): Type of content (industry_news, etc.)
   - `target_audience` (string): Target audience identifier

2. **Agent Node**:
   - System prompt from content_templates
   - User prompt with scraped data
   - Temperature setting (0.6-0.8)
   - Model selection (GPT-4, Claude, etc.)

3. **Validation Nodes**:
   - Character count (280 for Twitter)
   - Format validation
   - Hashtag insertion

4. **Human Approval Node**:
   - Review generated content
   - Approve/reject decision

5. **Twitter Integration Node**:
   - Post approved content to X
   - Return post URL and metadata

## 🔐 Security Best Practices

- Never commit `.env` file to version control
- Store API keys securely
- Use environment-specific configurations
- Regularly rotate API keys
- Monitor API usage and rate limits
- Review audit logs regularly

## 📈 Monitoring & Logging

### Log Files

Logs are stored in the `logs/` directory:
- `content_automation.log`: JSON-formatted logs for all operations

### Database Logging

All major events are logged to the `system_logs` table:
```sql
SELECT * FROM system_logs 
ORDER BY created_at DESC 
LIMIT 100;
```

### Check Job Status

```sql
-- Recent Opus jobs
SELECT job_execution_id, status, initiated_at, completed_at
FROM opus_jobs
ORDER BY initiated_at DESC
LIMIT 10;

-- High-relevance unprocessed content
SELECT url, title, relevance_score, scraped_at
FROM scraped_content
WHERE is_processed = false AND relevance_score > 0.5
ORDER BY relevance_score DESC;
```

## 🐛 Troubleshooting

### Connection Issues

```bash
# Test all connections
python main.py test
```

### Check Logs

```bash
# View recent logs
tail -f logs/content_automation.log
```

### Common Issues

1. **Firecrawl API errors**: Check API key and rate limits
2. **Opus job failures**: Check workflow ID and input schema alignment
3. **Supabase connection errors**: Verify URL and key
4. **No content scraped**: Check source URLs are accessible

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## 🔄 Customization

### Adding New Content Sources

```sql
INSERT INTO content_sources (url, name, source_type, scraping_frequency_minutes)
VALUES ('https://example.com/blog', 'Example Blog', 'blog', 120);
```

### Adjusting Relevance Scoring

Edit `src/processor.py` and modify the `calculate_relevance_score` method weights:

```python
weights = {
    'keywords': 0.4,      # Adjust these values
    'title': 0.3,
    'content_quality': 0.2,
    'freshness': 0.1
}
```

### Custom Content Templates

Add templates to Supabase:

```sql
INSERT INTO content_templates (content_type, template_name, system_prompt, user_prompt_template)
VALUES (
  'product_update',
  'Product Update Tweet',
  'You are a product marketing expert...',
  'Create a tweet about this product update: {summary}'
);
```

## 📦 Project Structure

```
Content Automation/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging setup
│   ├── models.py           # Data models
│   ├── database.py         # Supabase client
│   ├── scraper.py          # Firecrawl scraper
│   ├── processor.py        # Content processing
│   ├── opus_client.py      # Opus API client
│   ├── orchestrator.py     # Pipeline orchestration
│   └── scheduler.py        # Automated scheduling
├── database/
│   └── schema.sql          # Database schema
├── logs/                   # Log files
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── .gitignore
└── README.md
```

## 📚 Documentation

### 🚀 Quick Start Guides
- **[WEB-UI-COMPLETE-SUMMARY.md](WEB-UI-COMPLETE-SUMMARY.md)** - 🎯 **NEW!** Web interface setup (20 minutes)
- **[FULL-STACK-DEPLOYMENT.md](FULL-STACK-DEPLOYMENT.md)** - Complete deployment guide (Railway + Vercel)
- [QUALITY-UPGRADE-COMPLETE.md](QUALITY-UPGRADE-COMPLETE.md) - Data quality improvements (3-step setup)
- [ASYNC-JOB-SUBMISSION.md](ASYNC-JOB-SUBMISSION.md) - No timeout job submission
- [WORKFLOW-INPUT-FIX.md](WORKFLOW-INPUT-FIX.md) - Opus workflow troubleshooting

### 📖 Detailed Guides
- **[Data Quality Enhancements](docs/DATA-QUALITY-ENHANCEMENTS.md)** - Quality filtering, validation, source diversity
- [Credit Optimization Guide](docs/CREDIT-OPTIMIZATION.md) - Firecrawl credit management and optimization
- [RSS and Sources Guide](docs/RSS-AND-SOURCES.md) - Multi-source scraping and RSS feed integration
- [WEB-UI-IMPLEMENTATION-GUIDE.md](WEB-UI-IMPLEMENTATION-GUIDE.md) - Web UI technical details
- [Enhancement Summary](ENHANCEMENT-SUMMARY.md) - All implemented features and improvements

## 🚧 Future Enhancements

- [ ] Multi-platform support (LinkedIn, Facebook)
- [ ] A/B testing for content variations
- [ ] Analytics dashboard
- [ ] Performance-based prompt optimization
- [ ] Advanced NLP for keyword extraction
- [ ] Content calendar visualization
- [ ] Webhook support for real-time triggers
- [ ] Admin web UI for management

## 📄 License

This is an internal project for demonstrating Opus capabilities.

## 🤝 Support

For issues or questions:
1. Check logs in `logs/content_automation.log`
2. Review database logs in `system_logs` table
3. Run `python main.py test` to verify connections
4. Check Opus workflow configuration

## 🎓 Learning Resources

- [Opus API Documentation](https://docs.opus.com)
- [Firecrawl Documentation](https://docs.firecrawl.dev)
- [Supabase Documentation](https://supabase.com/docs)
- [APScheduler Documentation](https://apscheduler.readthedocs.io)

---

**Built with ❤️ to showcase Opus's automation capabilities**
