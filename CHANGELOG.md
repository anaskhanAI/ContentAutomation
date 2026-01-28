# Changelog

## Version 1.1.0 - Enhanced 15-Item Workflow

### 🎯 Major Enhancements

#### Intelligent Content Selection
- **Tiered Selection System**: Content is now selected using a 3-tier quality approach
  - Tier 1 (Excellence ≥0.8): Must-include items, up to 40% of batch
  - Tier 2 (Quality 0.6-0.8): High-quality items with diversity, up to 50% of batch
  - Tier 3 (Good 0.5-0.6): Fill remaining slots as needed
- **Content Diversity**: Automatic balancing across content types (industry_news, thought_leadership, case_study)
- **Smart Distribution**: Ensures variety in sources and themes

#### Daily Safety Limits
- **Daily Post Limit**: Configurable cap on Opus jobs per day (default: 30)
- **Quota Tracking**: Real-time monitoring of daily usage
- **Automatic Throttling**: Stops processing when daily limit is reached
- **Quota Visibility**: Status command shows current usage and remaining quota

#### Enhanced Configuration
- **MAX_ITEMS_PER_RUN**: Set to 15 by default (configurable)
- **MIN_RELEVANCE_SCORE**: Quality threshold (default: 0.5)
- **DAILY_POST_LIMIT**: Safety cap (default: 30 jobs/day)
- **ENABLE_CONTENT_DIVERSITY**: Toggle intelligent diversity (default: true)
- **IMMEDIATE_PROCESSING**: Auto-process after scraping (default: true)

### 📊 New Features

#### Processor Enhancements
- `select_diverse_content()`: Intelligent selection with category balancing
- `select_tiered_content()`: Quality-based tiered selection
- Enhanced categorization logic for better content type detection

#### Database Enhancements
- `get_daily_job_count()`: Track Opus jobs initiated today
- Improved daily quota tracking for safety limits

#### CLI Improvements
- Enhanced `status` command with detailed metrics:
  - Daily quota usage and percentage
  - Content quality distribution (high/good/low)
  - Top unprocessed items preview
  - Configuration display
- Real-time quota updates after operations
- Dynamic defaults from configuration

### 🔧 Configuration Changes

#### New Environment Variables
```bash
MAX_ITEMS_PER_RUN=15              # Up from 5
MIN_RELEVANCE_SCORE=0.5           # Configurable threshold
DAILY_POST_LIMIT=30               # Safety limit
ENABLE_CONTENT_DIVERSITY=true    # Intelligent selection
IMMEDIATE_PROCESSING=true         # Auto-process mode
```

### 🎨 User Experience Improvements

#### Better Monitoring
- Daily quota displayed before and after operations
- Quality distribution breakdown in status
- Top items preview for quick assessment
- Clearer configuration visibility

#### Smarter Defaults
- CLI commands now use configuration defaults
- No need to specify common parameters
- Override available when needed

#### Safety Features
- Automatic daily limit enforcement
- Warning when approaching limits
- Graceful handling when quota exhausted

### 🔄 Workflow Changes

#### Recommended Flow
1. **Scraping**: Runs on schedule, collects all content
2. **Scoring**: Automatic relevance calculation
3. **Storage**: All content stored in Supabase
4. **Intelligent Selection**: Top 15 items selected with diversity
5. **Opus Processing**: Batch sent to Opus (respecting daily limits)
6. **Human Approval**: Review ~15 posts in Opus
7. **Publishing**: Approved posts auto-posted to Twitter/X

#### Selection Logic
- Guarantees excellence (tier 1 items always included)
- Ensures diversity (balanced across categories)
- Fills to target volume intelligently
- Respects quality thresholds at all tiers

### 📈 Performance Impact

#### Cost Optimization
- Daily limit prevents runaway costs
- Tiered selection ensures high approval rates
- Reduced waste from low-quality content

#### Quality Improvements
- Diverse content keeps feed interesting
- Tiered approach prioritizes excellence
- Category balancing prevents monotony

#### Operational Efficiency
- Configurable defaults reduce manual intervention
- Automatic quota management prevents overload
- Clear status visibility for quick decisions

### 🐛 Bug Fixes
- None (new feature release)

### ⚠️ Breaking Changes
- Default `max_items` changed from 5 to 15
- `process_content_for_opus()` signature changed (now accepts None for defaults)
- `run_full_pipeline()` signature changed (now accepts None for defaults)

### 🔄 Migration Guide

#### From Previous Version
No migration needed! New features are backwards compatible.

To leverage new features:
1. Copy new settings from `env.example` to your `.env`
2. Adjust `MAX_ITEMS_PER_RUN` and `DAILY_POST_LIMIT` as needed
3. Run `python main.py status` to see enhanced metrics

#### Configuration Update
```bash
# Add to your .env file:
MAX_ITEMS_PER_RUN=15
MIN_RELEVANCE_SCORE=0.5
DAILY_POST_LIMIT=30
ENABLE_CONTENT_DIVERSITY=true
IMMEDIATE_PROCESSING=true
```

### 📚 Documentation Updates
- README updated with 15-item workflow
- QUICKREF updated with new commands and features
- SETUP guide enhanced with new configuration

---

## Version 1.0.0 - Initial Release

### Features
- Firecrawl integration for web scraping
- Supabase database for content storage
- Opus API integration for content generation
- Intelligent relevance scoring
- Human approval workflow
- Twitter/X auto-posting
- Automated scheduling
- Comprehensive CLI interface
- Structured logging
- Error handling and retries
