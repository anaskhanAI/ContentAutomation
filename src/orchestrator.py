"""
Orchestrator for the content automation pipeline.
Coordinates scraping, processing, and Opus workflow execution.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.logger import logger
from src.config import settings
from src.database import db
from src.scraper import scraper
from src.processor import processor
from src.opus_client import opus_client, OpusAPIError
from src.models import ScrapedContent, OpusJob, GeneratedContent


class PipelineOrchestrator:
    """Orchestrates the complete content automation pipeline."""
    
    def __init__(self):
        """Initialize orchestrator."""
        logger.info("Pipeline orchestrator initialized")
    
    def scrape_from_sources(self) -> int:
        """
        Scrape content from all active sources.
        
        Returns:
            Number of items successfully scraped and stored
        """
        logger.info("Starting scraping from all active sources")
        
        # Get active sources from database
        sources = db.get_active_sources()
        
        if not sources:
            logger.warning("No active sources found")
            return 0
        
        total_scraped = 0
        total_credits_used = 0  # Track total Firecrawl credits
        sources_with_rss = 0
        sources_with_crawl = 0
        source_results = []  # Track per-source results for summary
        
        for source in sources:
            try:
                logger.info("Scraping source", source_name=source.name, url=source.url)
                
                # Check if source has RSS feed and RSS is enabled
                rss_feed_url = source.metadata.get('rss_feed_url')
                has_rss = source.metadata.get('has_rss', False)
                
                scraped_contents = []
                stored_count = 0  # Initialize counter
                scrape_method = "none"  # Initialize method
                
                # Strategy 1: Try RSS first if available and enabled
                if settings.use_rss_feeds and has_rss and rss_feed_url:
                    logger.info("Using RSS feed for source",
                               source_name=source.name,
                               rss_url=rss_feed_url)
                    
                    scraped_contents = scraper.scrape_from_rss(
                        rss_feed_url=rss_feed_url,
                        source=source,
                        scrape_full_content=True  # Get full content from article URLs
                    )
                    
                    if scraped_contents:
                        logger.info("RSS scraping successful",
                                   source_name=source.name,
                                   items=len(scraped_contents))
                    elif settings.rss_fallback_to_crawl:
                        logger.warning("RSS scraping failed, falling back to web crawling",
                                     source_name=source.name)
                        # Fall through to web crawling
                    else:
                        logger.warning("RSS scraping failed and fallback disabled",
                                     source_name=source.name)
                        continue
                
                # Strategy 2: Fall back to web crawling (or primary if no RSS)
                if not scraped_contents:
                    # Use config for max_pages to optimize credit usage
                    max_crawl_pages = settings.max_crawl_pages
                    
                    logger.info("Using web crawling for source",
                               source_name=source.name,
                               reason="no_rss" if not has_rss else "rss_failed",
                               max_pages=max_crawl_pages)
                    
                    scraped_contents = scraper.crawl_website(
                        url=source.url,
                        max_pages=max_crawl_pages,
                        source=source
                    )
                
                if scraped_contents:
                    # Track credits used for this source
                    source_credits = 0
                    for content in scraped_contents:
                        credits = content.metadata.get('firecrawl_credits_used', 0)
                        source_credits += credits
                        total_credits_used += credits
                    
                    # Track which method was used
                    scrape_method = "rss" if (has_rss and rss_feed_url) else "crawl"
                    if has_rss and rss_feed_url:
                        sources_with_rss += 1
                    else:
                        sources_with_crawl += 1
                    
                    # Process and store each scraped content
                    stored_count = 0
                    for content in scraped_contents:
                        try:
                            content_id = processor.process_scraped_content(content)
                            if content_id:
                                stored_count += 1
                                total_scraped += 1
                        except Exception as e:
                            logger.error("Failed to process scraped content",
                                       url=content.url,
                                       error=str(e))
                    
                    # Track result for this source
                    source_results.append({
                        'name': source.name,
                        'type': source.source_type,
                        'method': scrape_method,
                        'scraped': len(scraped_contents),
                        'stored': stored_count,
                        'credits': source_credits
                    })
                    
                    # Update source last_scraped_at
                    db.update_source_scraped_time(source.id)
                    
                    logger.info("Source scraping completed",
                               source_name=source.name,
                               items_scraped=len(scraped_contents),
                               items_stored=stored_count,
                               method=scrape_method)
                
                else:
                    # No content scraped from this source
                    source_results.append({
                        'name': source.name,
                        'type': source.source_type,
                        'method': 'none',
                        'scraped': 0,
                        'stored': 0,
                        'credits': 0
                    })
                    logger.warning("No content scraped from source",
                                 source_name=source.name,
                                 url=source.url)
                
            except Exception as e:
                logger.error("Failed to scrape source",
                           source_name=source.name,
                           error=str(e))
                continue
        
        logger.info("Scraping from all sources completed", total_items=total_scraped)
        
        # Log detailed per-source summary
        logger.info("="*80)
        logger.info("📊 SCRAPING SUMMARY BY SOURCE")
        logger.info("="*80)
        
        # Group by source type
        by_type = {}
        for result in source_results:
            src_type = result['type']
            if src_type not in by_type:
                by_type[src_type] = []
            by_type[src_type].append(result)
        
        for src_type, results in by_type.items():
            logger.info(f"\n📁 {src_type.upper().replace('_', ' ')}")
            for result in results:
                status_icon = "✅" if result['stored'] > 0 else "❌"
                method_icon = "📰" if result['method'] == 'rss' else "🌐" if result['method'] == 'crawl' else "⏭️"
                logger.info(f"  {status_icon} {method_icon} {result['name']}: {result['stored']} articles stored (scraped: {result['scraped']}, credits: {result['credits']})")
        
        logger.info("\n" + "="*80)
        logger.info(f"TOTALS: {total_scraped} articles stored from {len([r for r in source_results if r['stored'] > 0])}/{len(sources)} sources")
        logger.info("="*80)
        
        # Log credit usage summary
        if settings.track_credit_usage:
            monthly_projection = total_credits_used * 30  # Assuming daily scraping
            logger.warning("📊 CREDIT USAGE SUMMARY",
                         credits_this_run=total_credits_used,
                         monthly_projection_daily=monthly_projection,
                         sources_total=len(sources),
                         sources_rss=sources_with_rss,
                         sources_crawl=sources_with_crawl,
                         articles_scraped=total_scraped,
                         credit_limit_monthly=3000)
            
            # Warn if approaching limit
            if monthly_projection > 3000:
                logger.error("⚠️  CREDIT WARNING: Monthly projection exceeds 3000 credit limit!",
                           projected=monthly_projection,
                           limit=3000,
                           overage=monthly_projection - 3000)
            elif monthly_projection > 2400:  # 80% of limit
                logger.warning("⚠️  CREDIT CAUTION: Approaching 80% of monthly limit",
                             projected=monthly_projection,
                             limit=3000,
                             usage_percent=int((monthly_projection / 3000) * 100))
        
        return total_scraped
    
    def process_content_for_opus(self, min_relevance: Optional[float] = None,
                                max_items: Optional[int] = None,
                                use_tiered_selection: bool = True) -> List[Dict[str, Any]]:
        """
        Select and process high-relevance content for Opus workflows.
        Uses intelligent selection with diversity and daily limits.
        
        Args:
            min_relevance: Minimum relevance score threshold (uses config default if None)
            max_items: Maximum number of items to process (uses config default if None)
            use_tiered_selection: Use tiered quality selection (recommended)
            
        Returns:
            List of job results
        """
        # Use configuration defaults if not specified
        if min_relevance is None:
            min_relevance = settings.min_relevance_score
        if max_items is None:
            max_items = settings.max_items_per_run
        
        logger.info("Processing content for Opus",
                   min_relevance=min_relevance,
                   max_items=max_items,
                   use_tiered=use_tiered_selection)
        
        # Check daily limit
        daily_count = db.get_daily_job_count()
        daily_limit = settings.daily_post_limit
        
        if daily_count >= daily_limit:
            logger.warning("Daily post limit reached",
                         current_count=daily_count,
                         limit=daily_limit)
            return []
        
        # Adjust max_items based on remaining daily quota
        remaining_quota = daily_limit - daily_count
        max_items = min(max_items, remaining_quota)
        
        logger.info("Daily quota check",
                   jobs_today=daily_count,
                   daily_limit=daily_limit,
                   remaining_quota=remaining_quota,
                   will_process=max_items)
        
        # Get high-relevance unprocessed content
        high_relevance_content = processor.filter_by_relevance(min_score=min_relevance)
        
        if not high_relevance_content:
            logger.info("No high-relevance content found for processing")
            return []
        
        # Intelligent selection
        if use_tiered_selection:
            logger.info("Using tiered selection for quality and diversity")
            content_to_process = processor.select_tiered_content(
                high_relevance_content,
                max_items=max_items
            )
        elif settings.enable_content_diversity:
            logger.info("Using diversity-based selection")
            content_to_process = processor.select_diverse_content(
                high_relevance_content,
                max_items=max_items,
                ensure_diversity=True
            )
        else:
            logger.info("Using simple top-N selection")
            # Simple: just take top N by score
            high_relevance_content.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            content_to_process = high_relevance_content[:max_items]
        
        logger.info("Selected content for Opus processing",
                   available=len(high_relevance_content),
                   selected=len(content_to_process))
        
        results = []
        
        for content in content_to_process:
            try:
                result = self.send_to_opus(content)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error("Failed to send content to Opus",
                           content_id=str(content.id),
                           error=str(e))
                continue
        
        logger.info("Opus processing completed",
                   total_sent=len(content_to_process),
                   successful=len(results),
                   daily_total=daily_count + len(results))
        
        return results
    
    def send_to_opus(self, content: ScrapedContent) -> Optional[Dict[str, Any]]:
        """
        Send single content item to Opus for processing.
        
        Args:
            content: ScrapedContent to process
            
        Returns:
            Job result dictionary or None if failed
        """
        logger.info("Sending content to Opus",
                   content_id=str(content.id),
                   url=content.url)
        
        try:
            # Categorize content
            content_type = processor.categorize_content(content)
            
            # Prepare data for Opus
            opus_input = processor.prepare_for_opus(content, content_type)
            
            # Create job title and description
            job_title = f"Generate {content_type} post: {content.title[:50]}"
            job_description = f"Generate social media content from: {content.url}"
            
            # Create Opus job record in database (before execution)
            opus_job = OpusJob(
                workflow_id=settings.opus_workflow_id,
                scraped_content_id=content.id,
                status="INITIATED",
                job_payload=opus_input
            )
            
            job_db_id = db.insert_opus_job(opus_job)
            
            if not job_db_id:
                logger.error("Failed to create job record in database")
                return None
            
            # Execute Opus job (async - no timeout)
            try:
                job_result = opus_client.run_complete_job_async(
                    scraped_data=opus_input,
                    content_type=content_type,
                    title=job_title,
                    description=job_description
                )
                
                job_execution_id = job_result.get("job_execution_id")
                
                # Update job status in database as SUBMITTED (not COMPLETED)
                db.update_opus_job_status(
                    job_execution_id=job_execution_id,
                    status="SUBMITTED",
                    results={"message": job_result.get("message"), "note": job_result.get("note")}
                )
                
                # Mark content as processed (it's now in Opus queue)
                db.mark_content_processed(content.id)
                
                logger.info("Content successfully sent to Opus (async mode)",
                           content_id=str(content.id),
                           job_execution_id=job_execution_id,
                           status="SUBMITTED",
                           message="Job queued for manual approval in Opus")
                
                return job_result
                
            except OpusAPIError as e:
                # Update job status as failed
                if opus_job.job_execution_id:
                    db.update_opus_job_status(
                        job_execution_id=opus_job.job_execution_id,
                        status="FAILED",
                        error_message=str(e)
                    )
                
                logger.error("Opus job failed",
                           content_id=str(content.id),
                           error=str(e))
                return None
            
        except Exception as e:
            logger.error("Failed to send content to Opus",
                       content_id=str(content.id),
                       error=str(e))
            return None
    
    def _extract_generated_content(self, results: Dict[str, Any]) -> Optional[str]:
        """
        Extract generated content text from Opus job results.
        
        Args:
            results: Opus job results
            
        Returns:
            Generated content text or None
        """
        # This depends on your Opus workflow output structure
        # Adjust based on actual results format
        
        # Try common locations for generated content
        if isinstance(results, dict):
            # Check for common result keys
            for key in ['generated_content', 'content', 'text', 'output', 'summary', 'data']:
                if key in results:
                    value = results[key]
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict) and 'text' in value:
                        return value['text']
        
        # If structure is different, log for debugging
        logger.debug("Could not extract generated content from results",
                    result_keys=list(results.keys()) if isinstance(results, dict) else type(results))
        
        return None
    
    def run_full_pipeline(self, scrape: bool = True,
                         process: bool = True,
                         min_relevance: Optional[float] = None,
                         max_items: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the complete content automation pipeline.
        
        Args:
            scrape: Whether to scrape new content
            process: Whether to process and send to Opus
            min_relevance: Minimum relevance score for processing (uses config default if None)
            max_items: Maximum items to send to Opus (uses config default if None)
            
        Returns:
            Pipeline execution summary
        """
        # Use configuration defaults if not specified
        if min_relevance is None:
            min_relevance = settings.min_relevance_score
        if max_items is None:
            max_items = settings.max_items_per_run
        
        logger.info("Starting full pipeline execution",
                   scrape=scrape,
                   process=process,
                   min_relevance=min_relevance,
                   max_items=max_items,
                   immediate_processing=settings.immediate_processing)
        
        summary = {
            "scraped_items": 0,
            "processed_items": 0,
            "opus_jobs": []
        }
        
        try:
            # Step 1: Scrape content
            if scrape:
                scraped_count = self.scrape_from_sources()
                summary["scraped_items"] = scraped_count
                logger.info("Pipeline scraping completed", items=scraped_count)
            
            # Step 2: Process and send to Opus
            if process:
                opus_results = self.process_content_for_opus(
                    min_relevance=min_relevance,
                    max_items=max_items
                )
                summary["processed_items"] = len(opus_results)
                summary["opus_jobs"] = opus_results
                logger.info("Pipeline processing completed", items=len(opus_results))
            
            logger.info("Full pipeline execution completed", summary=summary)
            return summary
            
        except Exception as e:
            logger.error("Pipeline execution failed", error=str(e))
            summary["error"] = str(e)
            return summary
    
    def retry_failed_jobs(self, max_retries: int = 3) -> int:
        """
        Retry failed Opus jobs.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            Number of jobs successfully retried
        """
        logger.info("Retrying failed jobs", max_retries=max_retries)
        
        # This would need additional database queries to find failed jobs
        # Implementation left as extension point
        logger.warning("Retry functionality not yet implemented")
        return 0


# Global orchestrator instance
orchestrator = PipelineOrchestrator()
