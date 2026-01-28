#!/usr/bin/env python3
"""
Main entry point for the Content Automation System.
Provides CLI interface for running the pipeline.
"""

import sys
import argparse
from typing import Optional

from src.logger import logger
from src.config import settings

# Lazy imports - only import when needed to avoid early database connection
_orchestrator = None
_pipeline_scheduler = None
_db = None

def get_orchestrator():
    """Lazy load orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        from src.orchestrator import orchestrator
        _orchestrator = orchestrator
    return _orchestrator

def get_scheduler():
    """Lazy load scheduler."""
    global _pipeline_scheduler
    if _pipeline_scheduler is None:
        from src.scheduler import pipeline_scheduler
        _pipeline_scheduler = pipeline_scheduler
    return _pipeline_scheduler

def get_db():
    """Lazy load database."""
    global _db
    if _db is None:
        from src.database import db
        _db = db
    return _db


def run_scraping():
    """Run scraping job once."""
    logger.info("Running one-time scraping job")
    orchestrator = get_orchestrator()
    count = orchestrator.scrape_from_sources()
    logger.info("Scraping completed", items_scraped=count)
    print(f"\n✅ Scraped {count} items successfully")


def run_processing(min_relevance: Optional[float] = None, max_items: Optional[int] = None):
    """Run processing job once."""
    logger.info("Running one-time processing job")
    
    orchestrator = get_orchestrator()
    db = get_db()
    
    # Check daily quota before processing
    daily_count = db.get_daily_job_count()
    daily_limit = settings.daily_post_limit
    
    print(f"\n📊 Daily Quota: {daily_count}/{daily_limit} jobs used")
    
    if daily_count >= daily_limit:
        print(f"\n⚠️  Daily limit reached! Cannot process more items today.")
        return
    
    results = orchestrator.process_content_for_opus(
        min_relevance=min_relevance,
        max_items=max_items
    )
    logger.info("Processing completed", items_processed=len(results))
    print(f"\n✅ Processed {len(results)} items successfully")
    
    if results:
        print("\nJob Execution IDs:")
        for result in results:
            job_id = result.get("job_execution_id", "unknown")
            status = result.get("status", "unknown")
            print(f"  - {job_id}: {status}")
    
    # Show updated quota
    new_daily_count = db.get_daily_job_count()
    print(f"\n📊 Updated Daily Quota: {new_daily_count}/{daily_limit} jobs used")


def run_full_pipeline(scrape: bool = True, process: bool = True,
                     min_relevance: Optional[float] = None, max_items: Optional[int] = None):
    """Run complete pipeline once."""
    logger.info("Running one-time full pipeline")
    
    orchestrator = get_orchestrator()
    db = get_db()
    
    # Show daily quota before starting
    daily_count = db.get_daily_job_count()
    daily_limit = settings.daily_post_limit
    print(f"\n📊 Daily Quota: {daily_count}/{daily_limit} jobs used")
    
    summary = orchestrator.run_full_pipeline(
        scrape=scrape,
        process=process,
        min_relevance=min_relevance,
        max_items=max_items
    )
    
    print("\n✅ Pipeline execution completed")
    print(f"\nSummary:")
    print(f"  - Scraped items: {summary.get('scraped_items', 0)}")
    print(f"  - Processed items: {summary.get('processed_items', 0)}")
    
    if summary.get('opus_jobs'):
        print(f"\nOpus Jobs:")
        for job in summary['opus_jobs']:
            job_id = job.get("job_execution_id", "unknown")
            status = job.get("status", "unknown")
            print(f"  - {job_id}: {status}")
    
    # Show updated quota
    new_daily_count = db.get_daily_job_count()
    print(f"\n📊 Updated Daily Quota: {new_daily_count}/{daily_limit} jobs used")


def start_scheduler(mode: str = 'full_pipeline'):
    """Start automated scheduler."""
    logger.info("Starting automated scheduler", mode=mode)
    print(f"\n🚀 Starting scheduler in '{mode}' mode")
    print(f"Scraping interval: {settings.scraping_interval_minutes} minutes")
    print(f"Press Ctrl+C to stop\n")
    
    pipeline_scheduler = get_scheduler()
    pipeline_scheduler.start(mode=mode)


def show_status():
    """Show system status and recent activity."""
    print("\n📊 Content Automation System Status\n")
    print(f"Environment: {settings.environment}")
    print(f"Opus Workflow ID: {settings.opus_workflow_id}")
    
    print(f"\n⚙️  Configuration:")
    print(f"  - Scraping Interval: {settings.scraping_interval_minutes} minutes")
    print(f"  - Max Items Per Run: {settings.max_items_per_run}")
    print(f"  - Min Relevance Score: {settings.min_relevance_score}")
    print(f"  - Daily Post Limit: {settings.daily_post_limit}")
    print(f"  - Content Diversity: {'Enabled' if settings.enable_content_diversity else 'Disabled'}")
    print(f"  - Immediate Processing: {'Enabled' if settings.immediate_processing else 'Disabled'}")
    
    print(f"\n📡 RSS Feed Settings:")
    print(f"  - Use RSS Feeds: {'Enabled' if settings.use_rss_feeds else 'Disabled'}")
    print(f"  - Freshness Threshold: {settings.rss_freshness_days} days")
    print(f"  - Fallback to Crawl: {'Enabled' if settings.rss_fallback_to_crawl else 'Disabled'}")
    
    # Get recent stats from database
    try:
        db = get_db()
        
        # Daily quota
        daily_count = db.get_daily_job_count()
        daily_limit = settings.daily_post_limit
        quota_pct = (daily_count / daily_limit * 100) if daily_limit > 0 else 0
        print(f"\n📊 Daily Quota:")
        print(f"  - Jobs Today: {daily_count}/{daily_limit} ({quota_pct:.1f}%)")
        print(f"  - Remaining: {daily_limit - daily_count}")
        
        # Get active sources
        sources = db.get_active_sources()
        rss_count = sum(1 for s in sources if s.metadata.get('has_rss', False))
        print(f"\n🌐 Active Sources: {len(sources)} ({rss_count} with RSS)")
        
        for source in sources[:10]:  # Show first 10
            rss_indicator = "📡" if source.metadata.get('has_rss', False) else "🌐"
            print(f"  {rss_indicator} {source.name} ({source.source_type})")
        
        if len(sources) > 10:
            print(f"  ... and {len(sources) - 10} more sources")
        if len(sources) > 5:
            print(f"  ... and {len(sources) - 5} more")
        
        # Get unprocessed content count
        unprocessed = db.get_unprocessed_content(limit=100)
        print(f"\n📄 Content Status:")
        print(f"  - Unprocessed: {len(unprocessed)}")
        
        # Show relevance distribution
        high_relevance = [c for c in unprocessed if c.relevance_score and c.relevance_score >= 0.7]
        good_relevance = [c for c in unprocessed if c.relevance_score and 0.5 <= c.relevance_score < 0.7]
        low_relevance = [c for c in unprocessed if c.relevance_score and c.relevance_score < 0.5]
        
        print(f"  - High Quality (≥0.7): {len(high_relevance)}")
        print(f"  - Good Quality (0.5-0.7): {len(good_relevance)}")
        print(f"  - Lower Quality (<0.5): {len(low_relevance)}")
        
        # Show top items
        if high_relevance:
            print(f"\n⭐ Top Unprocessed Items:")
            for i, content in enumerate(sorted(high_relevance, key=lambda x: x.relevance_score, reverse=True)[:3], 1):
                print(f"  {i}. [{content.relevance_score:.2f}] {content.title[:60]}...")
        
    except Exception as e:
        logger.error("Failed to retrieve status", error=str(e))
        print(f"\n❌ Error retrieving status: {str(e)}")


def test_connection():
    """Test connections to external services."""
    print("\n🔍 Testing Connections\n")
    
    errors = []
    
    # Test Supabase
    try:
        db = get_db()
        sources = db.get_active_sources()
        print(f"✅ Supabase: Connected (found {len(sources)} sources)")
    except Exception as e:
        print(f"❌ Supabase: Failed - {str(e)}")
        errors.append("Supabase")
    
    # Test Opus API
    try:
        from src.opus_client import opus_client
        schema = opus_client.get_workflow_schema()
        workflow_name = schema.get("name", "Unknown")
        print(f"✅ Opus API: Connected (workflow: {workflow_name})")
    except Exception as e:
        print(f"❌ Opus API: Failed - {str(e)}")
        errors.append("Opus API")
    
    # Test Firecrawl
    try:
        from src.scraper import scraper
        # Try a simple scrape (use a reliable test URL)
        test_url = "https://example.com"
        result = scraper.scrape_url(test_url)
        if result:
            print(f"✅ Firecrawl: Connected and working")
        else:
            print(f"⚠️  Firecrawl: Connected but returned no result")
    except Exception as e:
        print(f"❌ Firecrawl: Failed - {str(e)}")
        errors.append("Firecrawl")
    
    if errors:
        print(f"\n❌ Failed connections: {', '.join(errors)}")
        print("Please check your configuration in .env file")
        return False
    else:
        print("\n✅ All connections successful!")
        return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Content Automation System for Opus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline once
  python main.py run

  # Run only scraping
  python main.py scrape

  # Run only processing
  python main.py process --min-relevance 0.6 --max-items 3

  # Start automated scheduler
  python main.py schedule --mode full_pipeline

  # Test connections
  python main.py test

  # Show system status
  python main.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run full pipeline once')
    run_parser.add_argument('--no-scrape', action='store_true', help='Skip scraping step')
    run_parser.add_argument('--no-process', action='store_true', help='Skip processing step')
    run_parser.add_argument('--min-relevance', type=float, 
                          help=f'Minimum relevance score (default: {settings.min_relevance_score})')
    run_parser.add_argument('--max-items', type=int,
                          help=f'Maximum items to process (default: {settings.max_items_per_run})')
    
    # Scrape command
    subparsers.add_parser('scrape', help='Run scraping job once')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Run processing job once')
    process_parser.add_argument('--min-relevance', type=float,
                               help=f'Minimum relevance score (default: {settings.min_relevance_score})')
    process_parser.add_argument('--max-items', type=int,
                               help=f'Maximum items to process (default: {settings.max_items_per_run})')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Start automated scheduler')
    schedule_parser.add_argument('--mode', type=str, 
                                choices=['scraping', 'processing', 'full_pipeline', 'separate'],
                                default='full_pipeline',
                                help='Scheduling mode (default: full_pipeline)')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Test command
    subparsers.add_parser('test', help='Test connections to external services')
    
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Log startup
    logger.info("Application started", command=args.command)
    
    try:
        # Execute command
        if args.command == 'run':
            run_full_pipeline(
                scrape=not args.no_scrape,
                process=not args.no_process,
                min_relevance=args.min_relevance,
                max_items=args.max_items
            )
        
        elif args.command == 'scrape':
            run_scraping()
        
        elif args.command == 'process':
            run_processing(
                min_relevance=args.min_relevance,
                max_items=args.max_items
            )
        
        elif args.command == 'schedule':
            start_scheduler(mode=args.mode)
        
        elif args.command == 'status':
            show_status()
        
        elif args.command == 'test':
            success = test_connection()
            sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    
    except Exception as e:
        logger.error("Application error", error=str(e), exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
