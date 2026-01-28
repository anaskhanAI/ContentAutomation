# Setup Guide

Complete step-by-step setup instructions for the Content Automation System.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] pip package manager
- [ ] Git (optional, for version control)
- [ ] Supabase account ([sign up here](https://supabase.com))
- [ ] Firecrawl API key ([get one here](https://firecrawl.dev))
- [ ] Opus account with API access
- [ ] Twitter/X integration configured in Opus workflow

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Navigate to project directory
cd "/Users/anas/Documents/Ops on Opus/Content Automation"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Supabase Database Setup

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and create project
4. Wait for project to be ready (~2 minutes)

### 2.2 Get Supabase Credentials

1. In your Supabase project, go to Settings → API
2. Copy the following:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

### 2.3 Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Open `database/schema.sql` from this project
4. Copy all the SQL content
5. Paste into the Supabase SQL Editor
6. Click "Run" or press Cmd/Ctrl + Enter
7. Verify tables are created by going to **Table Editor**

You should see these tables:
- content_sources
- scraped_content
- opus_jobs
- generated_content
- published_posts
- content_templates
- system_logs

## Step 3: Firecrawl Setup

### 3.1 Get Firecrawl API Key

1. Go to [firecrawl.dev](https://firecrawl.dev)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the API key (starts with `fc-...`)

## Step 4: Opus Setup

### 4.1 Get Opus API Key

1. Log in to your Opus account
2. Navigate to **My Organization** → Settings
3. Click **API Keys** in the left sidebar
4. Click **+ Generate API Key**
5. Give it a name (e.g., "Content Automation")
6. Click **Generate Key**
7. **IMPORTANT**: Copy the key immediately (you can't see it again!)

### 4.2 Find Your Workflow ID

1. In Opus, go to the **Workflows** tab
2. Find or create your content generation workflow
3. Click on the workflow to open it
4. Look at the URL in your browser
5. The workflow ID is the part after `/workflow/`
   - Example: In `app.opus.com/app/workflow/B9uGJfZ3CFwOdMKH`
   - The ID is: `B9uGJfZ3CFwOdMKH`

### 4.3 Configure Opus Workflow

Your Opus workflow should have these nodes:

**Required Input Variables:**
- Scraped content data (object)
- Content type (string)
- Target audience (string)

**Workflow Nodes:**
1. **Input nodes** to receive data
2. **Agent node** with:
   - LLM model (GPT-4, Claude, etc.)
   - System prompt for content generation
   - User prompt template
   - Temperature (0.6-0.8)
3. **Validation nodes** (optional):
   - Character count check
   - Format validation
4. **Human approval node**
5. **Twitter integration node** to post

## Step 5: Environment Configuration

### 5.1 Create .env File

```bash
# Copy the example file
cp env.example .env

# Open .env in your text editor
# On macOS:
open .env

# On Windows:
notepad .env

# On Linux:
nano .env
```

### 5.2 Fill in Your Credentials

Edit `.env` and replace all placeholder values:

```bash
# Opus API Configuration
OPUS_API_KEY=your_actual_opus_api_key_here
OPUS_BASE_URL=https://operator.opus.com
OPUS_WORKFLOW_ID=your_actual_workflow_id_here

# Firecrawl Configuration
FIRECRAWL_API_KEY=your_actual_firecrawl_api_key_here

# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_actual_supabase_anon_key_here

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
SCRAPING_INTERVAL_MINUTES=60
MAX_RETRIES=3
RETRY_DELAY_SECONDS=5

# Content Sources (comma-separated URLs)
CONTENT_SOURCES=https://techcrunch.com/category/artificial-intelligence/,https://www.theverge.com/ai-artificial-intelligence

# Content Strategy
CONTENT_TYPES=industry_news,thought_leadership,case_study
TARGET_AUDIENCE=B2B_decision_makers
```

### 5.3 Verify .env File

**Important**: Make sure:
- No spaces around the `=` sign
- No quotes around values (unless they contain spaces)
- All keys are present
- No typos in variable names

## Step 6: Test Installation

### 6.1 Test Connections

```bash
python main.py test
```

Expected output:
```
🔍 Testing Connections

✅ Supabase: Connected (found X sources)
✅ Opus API: Connected (workflow: Your Workflow Name)
✅ Firecrawl: Connected and working

✅ All connections successful!
```

If you see errors:
- **Supabase**: Check SUPABASE_URL and SUPABASE_KEY
- **Opus API**: Check OPUS_API_KEY and OPUS_WORKFLOW_ID
- **Firecrawl**: Check FIRECRAWL_API_KEY

### 6.2 Check System Status

```bash
python main.py status
```

This shows:
- Current configuration
- Active sources
- Unprocessed content count

## Step 7: First Run

### 7.1 Run a Test Scrape

```bash
python main.py scrape
```

This will:
1. Fetch active sources from database
2. Scrape content from each source
3. Store content in Supabase
4. Display results

### 7.2 Run Full Pipeline

```bash
python main.py run
```

This will:
1. Scrape content
2. Process and score content
3. Send high-relevance items to Opus
4. Display job execution results

### 7.3 Monitor in Opus

1. Go to your Opus dashboard
2. Navigate to Jobs
3. You should see new job executions
4. Review generated content in approval nodes
5. Approve to post to Twitter/X

## Step 8: Production Setup (Optional)

### 8.1 Start Automated Scheduler

```bash
# Run in foreground (for testing)
python main.py schedule

# Run in background (production)
nohup python main.py schedule > scheduler.log 2>&1 &
```

### 8.2 Set Up as System Service

Create a systemd service (Linux) or launchd service (macOS) for automatic startup.

**Linux (systemd)**:

Create `/etc/systemd/system/content-automation.service`:

```ini
[Unit]
Description=Content Automation System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Content Automation
Environment="PATH=/path/to/Content Automation/venv/bin"
ExecStart=/path/to/Content Automation/venv/bin/python main.py schedule
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable content-automation
sudo systemctl start content-automation
sudo systemctl status content-automation
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Supabase connection fails

**Solution**: 
1. Check SUPABASE_URL format (should include https://)
2. Verify SUPABASE_KEY is the anon/public key, not service_role key
3. Check project is not paused in Supabase dashboard

### Issue: Opus API authentication fails

**Solution**:
1. Verify OPUS_API_KEY is correct
2. Check key hasn't expired
3. Ensure you have API access enabled in Opus

### Issue: No content scraped

**Solution**:
1. Check source URLs are accessible
2. Verify Firecrawl API key and quota
3. Check logs in `logs/content_automation.log`

### Issue: Firecrawl rate limit errors

**Solution**:
1. Check your Firecrawl plan limits
2. Reduce scraping frequency
3. Limit max_pages in scraper settings

## Getting Help

1. **Check Logs**: `tail -f logs/content_automation.log`
2. **Debug Mode**: Set `LOG_LEVEL=DEBUG` in `.env`
3. **Database Logs**: Query `system_logs` table in Supabase
4. **Test Mode**: Run `python main.py test`

## Next Steps

Once everything is working:

1. **Customize Sources**: Add more content sources in Supabase
2. **Tune Relevance**: Adjust relevance scoring weights
3. **Customize Prompts**: Update content templates in Supabase
4. **Set Schedule**: Configure automation schedule
5. **Monitor Performance**: Review published posts and engagement

## Security Reminders

- [ ] `.env` file is in `.gitignore`
- [ ] API keys are not committed to version control
- [ ] Supabase RLS (Row Level Security) is configured if needed
- [ ] API keys are rotated regularly
- [ ] Logs don't contain sensitive information

---

**Setup complete! 🎉**

Run `python main.py --help` to see all available commands.
