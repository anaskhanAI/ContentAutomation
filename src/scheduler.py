"""
Scheduler for automated content pipeline execution.
Handles periodic scraping and processing based on configuration.
"""

import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.logger import logger
from src.config import settings
from src.orchestrator import orchestrator
from src.database import db


class PipelineScheduler:
    """Schedules and manages automated pipeline execution."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = BlockingScheduler()
        self.is_running = False
        logger.info("Pipeline scheduler initialized")
    
    def scraping_job(self):
        """Scheduled job for scraping content."""
        logger.info("Starting scheduled scraping job")
        
        try:
            # Log to database
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled scraping job started"
            )
            
            # Run scraping
            count = orchestrator.scrape_from_sources()
            
            # Log completion
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled scraping job completed",
                context={"items_scraped": count}
            )
            
            logger.info("Scheduled scraping job completed", items_scraped=count)
            
        except Exception as e:
            logger.error("Scheduled scraping job failed", error=str(e))
            db.log_system_event(
                level="ERROR",
                component="scheduler",
                message="Scheduled scraping job failed",
                context={"error": str(e)}
            )
    
    def processing_job(self):
        """Scheduled job for processing content and sending to Opus."""
        logger.info("Starting scheduled processing job")
        
        try:
            # Log to database
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled processing job started"
            )
            
            # Run processing
            results = orchestrator.process_content_for_opus(
                min_relevance=0.5,
                max_items=5
            )
            
            # Log completion
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled processing job completed",
                context={"items_processed": len(results)}
            )
            
            logger.info("Scheduled processing job completed", items_processed=len(results))
            
        except Exception as e:
            logger.error("Scheduled processing job failed", error=str(e))
            db.log_system_event(
                level="ERROR",
                component="scheduler",
                message="Scheduled processing job failed",
                context={"error": str(e)}
            )
    
    def full_pipeline_job(self):
        """Scheduled job for running the complete pipeline."""
        logger.info("Starting scheduled full pipeline job")
        
        try:
            # Log to database
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled full pipeline job started"
            )
            
            # Run full pipeline
            summary = orchestrator.run_full_pipeline(
                scrape=True,
                process=True,
                min_relevance=0.5,
                max_items=5
            )
            
            # Log completion
            db.log_system_event(
                level="INFO",
                component="scheduler",
                message="Scheduled full pipeline job completed",
                context=summary
            )
            
            logger.info("Scheduled full pipeline job completed", summary=summary)
            
        except Exception as e:
            logger.error("Scheduled full pipeline job failed", error=str(e))
            db.log_system_event(
                level="ERROR",
                component="scheduler",
                message="Scheduled full pipeline job failed",
                context={"error": str(e)}
            )
    
    def add_scraping_schedule(self):
        """Add scraping job to scheduler based on configuration."""
        interval_minutes = settings.scraping_interval_minutes
        
        self.scheduler.add_job(
            func=self.scraping_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='scraping_job',
            name='Scrape content from sources',
            replace_existing=True
        )
        
        logger.info("Added scraping schedule", interval_minutes=interval_minutes)
    
    def add_processing_schedule(self):
        """Add processing job to scheduler."""
        # Process content every 30 minutes
        # This can be adjusted based on needs
        
        self.scheduler.add_job(
            func=self.processing_job,
            trigger=IntervalTrigger(minutes=30),
            id='processing_job',
            name='Process content and send to Opus',
            replace_existing=True
        )
        
        logger.info("Added processing schedule", interval_minutes=30)
    
    def add_full_pipeline_schedule(self):
        """Add full pipeline job to scheduler."""
        # Run full pipeline based on configured interval
        interval_minutes = settings.scraping_interval_minutes
        
        self.scheduler.add_job(
            func=self.full_pipeline_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='full_pipeline_job',
            name='Run full content automation pipeline',
            replace_existing=True
        )
        
        logger.info("Added full pipeline schedule", interval_minutes=interval_minutes)
    
    def add_custom_schedule(self, cron_expression: str):
        """
        Add custom cron-based schedule for full pipeline.
        
        Args:
            cron_expression: Cron expression (e.g., '0 9 * * *' for 9 AM daily)
        """
        # Parse cron expression
        # Format: minute hour day month day_of_week
        parts = cron_expression.split()
        
        if len(parts) != 5:
            logger.error("Invalid cron expression", expression=cron_expression)
            return
        
        self.scheduler.add_job(
            func=self.full_pipeline_job,
            trigger=CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4]
            ),
            id='custom_pipeline_job',
            name='Custom scheduled full pipeline',
            replace_existing=True
        )
        
        logger.info("Added custom cron schedule", expression=cron_expression)
    
    def start(self, mode: str = 'full_pipeline'):
        """
        Start the scheduler.
        
        Args:
            mode: Scheduling mode - 'scraping', 'processing', 'full_pipeline', or 'separate'
        """
        logger.info("Starting scheduler", mode=mode)
        
        if mode == 'scraping':
            # Only schedule scraping
            self.add_scraping_schedule()
        elif mode == 'processing':
            # Only schedule processing
            self.add_processing_schedule()
        elif mode == 'full_pipeline':
            # Schedule complete pipeline
            self.add_full_pipeline_schedule()
        elif mode == 'separate':
            # Schedule scraping and processing separately
            self.add_scraping_schedule()
            self.add_processing_schedule()
        else:
            logger.error("Invalid scheduler mode", mode=mode)
            return
        
        # Log startup
        db.log_system_event(
            level="INFO",
            component="scheduler",
            message="Scheduler started",
            context={"mode": mode}
        )
        
        logger.info("Scheduler started successfully", mode=mode)
        logger.info("Press Ctrl+C to stop the scheduler")
        
        self.is_running = True
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.stop()
    
    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler")
        
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        # Log shutdown
        db.log_system_event(
            level="INFO",
            component="scheduler",
            message="Scheduler stopped"
        )
        
        self.is_running = False
        logger.info("Scheduler stopped successfully")
    
    def list_jobs(self):
        """List all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        
        logger.info("Scheduled jobs", count=len(jobs))
        
        for job in jobs:
            logger.info("Job",
                       id=job.id,
                       name=job.name,
                       next_run=job.next_run_time)
        
        return jobs


# Global scheduler instance
pipeline_scheduler = PipelineScheduler()
