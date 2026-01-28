"""
FastAPI Backend for Content Automation System
Provides REST API endpoints for the web UI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv

# Get parent directory and add to path
parent_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(parent_dir))

# Load .env from project root BEFORE importing src modules
env_path = parent_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

from src.database import db
from src.models import ContentSource
from src.config import settings

app = FastAPI(
    title="Content Automation API",
    description="API for managing content scraping and Opus workflow automation",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task status storage (in-memory for MVP, use Redis for production)
task_status: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# MODELS
# ============================================================================

class SourceCreate(BaseModel):
    url: str
    name: str
    source_type: str
    rss_feed_url: Optional[str] = None
    max_articles: int = Field(default=3, ge=1, le=10)
    priority: str = Field(default="normal")
    scraping_frequency_minutes: int = Field(default=120)


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    rss_feed_url: Optional[str] = None
    max_articles: Optional[int] = Field(default=None, ge=1, le=10)
    priority: Optional[str] = None
    scraping_frequency_minutes: Optional[int] = None


class SourceToggle(BaseModel):
    active: bool


class ProcessRequest(BaseModel):
    max_items: int = Field(default=15, ge=1, le=50)
    min_relevance: float = Field(default=0.5, ge=0.0, le=1.0)


class ScrapeRequest(BaseModel):
    source_ids: Optional[List[str]] = None
    max_articles: Optional[int] = None


class SettingsUpdate(BaseModel):
    max_articles_per_source: Optional[int] = None
    max_crawl_pages: Optional[int] = None
    rss_freshness_days: Optional[int] = None
    max_items_per_run: Optional[int] = None
    daily_post_limit: Optional[int] = None
    min_relevance_score: Optional[float] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_scraping_task(task_id: str, source_ids: Optional[List[str]] = None):
    """Background task for scraping content"""
    try:
        task_status[task_id] = {
            "status": "running",
            "progress": 0,
            "message": "Starting scraping...",
            "articles_scraped": 0,
            "credits_used": 0,
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Import here to avoid circular imports
        from src.orchestrator import orchestrator
        
        # Check for cancellation
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        # If specific sources requested, temporarily filter them
        # For MVP, we scrape all active sources
        # TODO: Implement source filtering
        
        count = orchestrator.scrape_from_sources()
        
        # Check for cancellation before completing
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": f"Successfully scraped {count} articles",
            "articles_scraped": count,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Scraping failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


def run_processing_task(task_id: str, max_items: int, min_relevance: float):
    """Background task for processing content and sending to Opus"""
    try:
        task_status[task_id] = {
            "status": "running",
            "progress": 0,
            "message": "Starting processing...",
            "jobs_submitted": 0,
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Check for cancellation
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        from src.orchestrator import orchestrator
        
        results = orchestrator.process_content_for_opus(
            min_relevance=min_relevance,
            max_items=max_items
        )
        
        # Check for cancellation before completing
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": f"Successfully submitted {len(results)} jobs to Opus",
            "jobs_submitted": len(results),
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Processing failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


def run_single_content_processing(task_id: str, content_id: str):
    """Background task for processing a single content item"""
    try:
        task_status[task_id] = {
            "status": "running",
            "progress": 0,
            "message": f"Processing content {content_id}...",
            "started_at": datetime.utcnow().isoformat()
        }
        
        from src.orchestrator import orchestrator
        from src.models import ScrapedContent
        
        # Fetch the content item
        content_query = db.client.table("scraped_content")\
            .select("*")\
            .eq("id", content_id)\
            .single()\
            .execute()
        
        if not content_query.data:
            raise Exception(f"Content {content_id} not found")
        
        content = content_query.data
        
        # Check for cancellation
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        task_status[task_id]["progress"] = 50
        
        # Create ScrapedContent object
        scraped_content = ScrapedContent(
            id=content["id"],
            source_id=content.get("source_id"),
            url=content["url"],
            title=content.get("title", ""),
            content=content.get("content", ""),
            scraped_at=content["scraped_at"],
            is_processed=content.get("is_processed", False),
            metadata=content.get("metadata", {})
        )
        
        # Send to Opus
        result = orchestrator.send_to_opus(scraped_content, content_type="ai_news")
        
        # Check for cancellation before completing
        if task_status.get(task_id, {}).get("status") == "cancelled":
            return
        
        task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Content processed and sent to Opus",
            "job_execution_id": result.get("job_execution_id"),
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Processing failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Content Automation API",
        "status": "running",
        "version": "1.0.0"
    }


# ----------------------------------------------------------------------------
# STATS & DASHBOARD
# ----------------------------------------------------------------------------

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    try:
        # Get active sources count
        sources = db.get_active_sources()
        active_sources = len(sources)
        
        # Get articles scraped today
        from datetime import date
        today_start = date.today().isoformat()
        articles_today_query = db.client.table("scraped_content")\
            .select("id", count="exact")\
            .gte("scraped_at", today_start)\
            .execute()
        articles_today = articles_today_query.count or 0
        
        # Get pending jobs count
        pending_jobs_query = db.client.table("opus_jobs")\
            .select("id", count="exact")\
            .eq("status", "SUBMITTED")\
            .execute()
        jobs_pending = pending_jobs_query.count or 0
        
        # Get unprocessed content count
        unprocessed_query = db.client.table("scraped_content")\
            .select("id", count="exact")\
            .eq("is_processed", False)\
            .execute()
        unprocessed_count = unprocessed_query.count or 0
        
        # Get last scrape time
        last_scrape_query = db.client.table("content_sources")\
            .select("last_scraped_at")\
            .not_.is_("last_scraped_at", "null")\
            .order("last_scraped_at", desc=True)\
            .limit(1)\
            .execute()
        
        last_scrape = None
        if last_scrape_query.data:
            last_scrape = last_scrape_query.data[0].get("last_scraped_at")
        
        return {
            "active_sources": active_sources,
            "total_sources": len(db.client.table("content_sources").select("id").execute().data),
            "articles_today": articles_today,
            "jobs_pending": jobs_pending,
            "unprocessed_articles": unprocessed_count,
            "last_scrape_at": last_scrape,
            "credits_used_monthly": 0,  # TODO: Implement credit tracking
            "credits_limit_monthly": 3000
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# SCRAPING
# ----------------------------------------------------------------------------

@app.post("/api/scrape")
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """Trigger content scraping"""
    task_id = str(uuid4())
    
    background_tasks.add_task(
        run_scraping_task,
        task_id,
        request.source_ids
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Scraping task started"
    }


@app.get("/api/scrape/status/{task_id}")
async def get_scrape_status(task_id: str):
    """Get scraping task status"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status[task_id]


# ----------------------------------------------------------------------------
# PROCESSING
# ----------------------------------------------------------------------------

@app.post("/api/process")
async def trigger_process(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Trigger content processing and Opus job submission"""
    task_id = str(uuid4())
    
    background_tasks.add_task(
        run_processing_task,
        task_id,
        request.max_items,
        request.min_relevance
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Processing task started"
    }


@app.get("/api/process/status/{task_id}")
async def get_process_status(task_id: str):
    """Get processing task status"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status[task_id]


# ----------------------------------------------------------------------------
# CONTENT SOURCES
# ----------------------------------------------------------------------------

@app.get("/api/sources")
async def get_sources():
    """Get all content sources"""
    try:
        result = db.client.table("content_sources")\
            .select("*")\
            .order("name")\
            .execute()
        
        # Return array directly, not wrapped in object
        return result.data if result.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sources")
async def create_source(source: SourceCreate):
    """Create a new content source"""
    try:
        new_source = ContentSource(
            url=source.url,
            name=source.name,
            source_type=source.source_type,
            is_active=True,
            scraping_frequency_minutes=source.scraping_frequency_minutes,
            metadata={
                "rss_feed_url": source.rss_feed_url,
                "has_rss": bool(source.rss_feed_url),
                "max_articles": source.max_articles,
                "priority": source.priority,
                "description": f"{source.name} - {source.source_type}",
                "language": "en"
            }
        )
        
        source_id = db.insert_content_source(new_source)
        
        return {
            "id": source_id,
            "success": True,
            "message": "Source created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/sources/{source_id}")
async def update_source(source_id: str, updates: SourceUpdate):
    """Update an existing content source"""
    try:
        # Fetch existing source
        existing = db.client.table("content_sources")\
            .select("*")\
            .eq("id", source_id)\
            .single()\
            .execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Merge updates
        update_data = {}
        if updates.name:
            update_data["name"] = updates.name
        if updates.url:
            update_data["url"] = updates.url
        if updates.scraping_frequency_minutes:
            update_data["scraping_frequency_minutes"] = updates.scraping_frequency_minutes
        
        # Update metadata
        existing_metadata = existing.data.get("metadata", {})
        if updates.rss_feed_url is not None:
            existing_metadata["rss_feed_url"] = updates.rss_feed_url
            existing_metadata["has_rss"] = bool(updates.rss_feed_url)
        if updates.max_articles:
            existing_metadata["max_articles"] = updates.max_articles
        if updates.priority:
            existing_metadata["priority"] = updates.priority
        
        update_data["metadata"] = existing_metadata
        
        # Execute update
        db.client.table("content_sources")\
            .update(update_data)\
            .eq("id", source_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Source updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/sources/{source_id}/toggle")
async def toggle_source(source_id: str, toggle: SourceToggle):
    """Toggle source active status"""
    try:
        db.client.table("content_sources")\
            .update({"is_active": toggle.active})\
            .eq("id", source_id)\
            .execute()
        
        return {
            "success": True,
            "active": toggle.active,
            "message": f"Source {'activated' if toggle.active else 'deactivated'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: str):
    """Delete a content source (soft delete)"""
    try:
        # Soft delete by setting is_active to false
        db.client.table("content_sources")\
            .update({"is_active": False})\
            .eq("id", source_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Source deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------------

@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    return {
        "max_articles_per_source": settings.max_articles_per_source,
        "max_crawl_pages": settings.max_crawl_pages,
        "rss_freshness_days": settings.rss_freshness_days,
        "max_items_per_run": settings.max_items_per_run,
        "daily_post_limit": settings.daily_post_limit,
        "min_relevance_score": settings.min_relevance_score,
        "use_rss_feeds": settings.use_rss_feeds,
        "enable_url_deduplication": settings.enable_url_deduplication,
        "track_credit_usage": settings.track_credit_usage
    }


@app.patch("/api/settings")
async def update_settings(updates: SettingsUpdate):
    """Update settings"""
    # Note: This updates in-memory settings only
    # For persistent storage, would need to write to .env or database
    try:
        if updates.max_articles_per_source is not None:
            settings.max_articles_per_source = updates.max_articles_per_source
        if updates.max_crawl_pages is not None:
            settings.max_crawl_pages = updates.max_crawl_pages
        if updates.rss_freshness_days is not None:
            settings.rss_freshness_days = updates.rss_freshness_days
        if updates.max_items_per_run is not None:
            settings.max_items_per_run = updates.max_items_per_run
        if updates.daily_post_limit is not None:
            settings.daily_post_limit = updates.daily_post_limit
        if updates.min_relevance_score is not None:
            settings.min_relevance_score = updates.min_relevance_score
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "note": "Settings updated for current session only"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# SCRAPED CONTENT
# ----------------------------------------------------------------------------

@app.get("/api/content")
async def get_scraped_content():
    """Get recent scraped content"""
    try:
        # Get unprocessed and recently processed content
        content_query = db.client.table("scraped_content")\
            .select("*")\
            .order("scraped_at", desc=True)\
            .limit(50)\
            .execute()
        
        return content_query.data if content_query.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/{content_id}/process")
async def process_single_content(content_id: str, background_tasks: BackgroundTasks):
    """Process a single content item and send to Opus"""
    task_id = str(uuid4())
    
    background_tasks.add_task(
        run_single_content_processing,
        task_id,
        content_id
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Processing content {content_id}"
    }


# ----------------------------------------------------------------------------
# TASK MANAGEMENT
# ----------------------------------------------------------------------------

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_status[task_id]["status"] = "cancelled"
    task_status[task_id]["message"] = "Task cancelled by user"
    
    return {
        "success": True,
        "message": "Task cancelled successfully"
    }


# ----------------------------------------------------------------------------
# ACTIVITY / RECENT JOBS
# ----------------------------------------------------------------------------

@app.get("/api/activity")
async def get_activity():
    """Get recent activity and jobs"""
    try:
        # Get recent Opus jobs
        jobs_query = db.client.table("opus_jobs")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        
        return jobs_query.data if jobs_query.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
