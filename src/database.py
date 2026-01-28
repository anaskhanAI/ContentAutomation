"""
Supabase database client for the Content Automation System.
Handles all database operations with proper error handling.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from supabase import create_client, Client

from src.config import settings
from src.logger import logger
from src.models import (
    ContentSource,
    ScrapedContent,
    OpusJob,
    GeneratedContent,
    PublishedPost,
    ContentTemplate
)


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


class DatabaseClient:
    """Client for interacting with Supabase database."""
    
    def __init__(self):
        """Initialize Supabase client."""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                
                settings.supabase_key
            )
            logger.info("Database client initialized", supabase_url=settings.supabase_url)
        except Exception as e:
            error_msg = str(e)
            logger.error("Failed to initialize database client", 
                        error=error_msg,
                        url=settings.supabase_url)
            
            # Provide helpful error message
            if "Invalid API key" in error_msg or "invalid" in error_msg.lower():
                raise DatabaseError(
                    f"Invalid Supabase credentials. Please check your .env file:\n"
                    f"  - SUPABASE_URL should be like: https://xxxxx.supabase.co\n"
                    f"  - SUPABASE_KEY should be your anon/public key (starts with 'eyJ...')\n"
                    f"Current URL: {settings.supabase_url}"
                )
            else:
                raise DatabaseError(f"Failed to connect to Supabase: {error_msg}")
    
    # ===== Content Sources =====
    
    def get_active_sources(self) -> List[ContentSource]:
        """
        Get all active content sources.
        
        Returns:
            List of active ContentSource objects
        """
        try:
            response = self.client.table("content_sources")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            sources = [ContentSource(**item) for item in response.data]
            logger.info("Retrieved active sources", count=len(sources))
            return sources
        except Exception as e:
            logger.error("Failed to get active sources", error=str(e))
            return []
    
    def get_source_by_url(self, url: str) -> Optional[ContentSource]:
        """
        Get content source by URL.
        
        Args:
            url: Source URL
            
        Returns:
            ContentSource object or None if not found
        """
        try:
            response = self.client.table("content_sources")\
                .select("*")\
                .eq("url", url)\
                .execute()
            
            if response.data and len(response.data) > 0:
                source = ContentSource(**response.data[0])
                logger.debug("Retrieved source by URL", url=url)
                return source
            
            return None
        except Exception as e:
            logger.error("Failed to get source by URL", url=url, error=str(e))
            return None
    
    def insert_content_source(self, source: ContentSource) -> Optional[UUID]:
        """
        Insert a new content source.
        
        Args:
            source: ContentSource object to insert
            
        Returns:
            UUID of inserted source or None if failed
        """
        try:
            data = {
                "url": source.url,
                "name": source.name,
                "source_type": source.source_type,
                "scraping_frequency_minutes": source.scraping_frequency_minutes,
                "is_active": source.is_active,
                "reliability_score": source.reliability_score,
                "metadata": source.metadata
            }
            
            response = self.client.table("content_sources")\
                .insert(data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                source_id = UUID(response.data[0]["id"])
                logger.info("Content source inserted",
                          source_id=str(source_id),
                          name=source.name,
                          url=source.url)
                return source_id
            
            return None
        except Exception as e:
            logger.error("Failed to insert content source",
                       name=source.name,
                       url=source.url,
                       error=str(e))
            return None
    
    def update_source_scraped_time(self, source_id: UUID) -> None:
        """
        Update last_scraped_at timestamp for a source.
        
        Args:
            source_id: UUID of the source
        """
        try:
            self.client.table("content_sources")\
                .update({"last_scraped_at": datetime.utcnow().isoformat()})\
                .eq("id", str(source_id))\
                .execute()
            logger.debug("Updated source scraped time", source_id=str(source_id))
        except Exception as e:
            logger.error("Failed to update source scraped time", source_id=str(source_id), error=str(e))
    
    # ===== Scraped Content =====
    
    def url_exists(self, url: str) -> bool:
        """
        Check if a URL already exists in scraped_content table.
        Used for deduplication to avoid re-scraping.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL exists, False otherwise
        """
        try:
            response = self.client.table("scraped_content")\
                .select("id")\
                .eq("url", url)\
                .limit(1)\
                .execute()
            
            exists = response.data and len(response.data) > 0
            
            if exists:
                logger.debug("URL already exists in database (deduplication)",
                           url=url[:100])
            
            return exists
        except Exception as e:
            logger.error("Error checking URL existence",
                       url=url[:100],
                       error=str(e))
            # On error, assume URL doesn't exist to allow scraping
            return False
    
    def insert_scraped_content(self, content: ScrapedContent) -> Optional[UUID]:
        """
        Insert scraped content into database.
        
        Args:
            content: ScrapedContent object to insert
            
        Returns:
            UUID of inserted content or None if failed
        """
        try:
            data = content.model_dump(exclude={"id"}, exclude_none=True)
            # Convert datetime objects to ISO strings
            if data.get("scraped_at"):
                data["scraped_at"] = data["scraped_at"].isoformat()
            if data.get("published_at"):
                data["published_at"] = data["published_at"].isoformat()
            # Convert UUID to string if present
            if data.get("source_id"):
                data["source_id"] = str(data["source_id"])
            
            response = self.client.table("scraped_content")\
                .insert(data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                content_id = UUID(response.data[0]["id"])
                logger.info("Inserted scraped content", content_id=str(content_id), url=content.url)
                return content_id
            return None
        except Exception as e:
            logger.error("Failed to insert scraped content", url=content.url, error=str(e))
            return None
    
    def get_unprocessed_content(self, limit: int = 10) -> List[ScrapedContent]:
        """
        Get unprocessed scraped content with highest relevance scores.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns:
            List of ScrapedContent objects
        """
        try:
            response = self.client.table("scraped_content")\
                .select("*")\
                .eq("is_processed", False)\
                .not_.is_("relevance_score", "null")\
                .order("relevance_score", desc=True)\
                .limit(limit)\
                .execute()
            
            content_list = [ScrapedContent(**item) for item in response.data]
            logger.info("Retrieved unprocessed content", count=len(content_list))
            return content_list
        except Exception as e:
            logger.error("Failed to get unprocessed content", error=str(e))
            return []
    
    def mark_content_processed(self, content_id: UUID) -> None:
        """
        Mark scraped content as processed.
        
        Args:
            content_id: UUID of the content
        """
        try:
            self.client.table("scraped_content")\
                .update({"is_processed": True})\
                .eq("id", str(content_id))\
                .execute()
            logger.debug("Marked content as processed", content_id=str(content_id))
        except Exception as e:
            logger.error("Failed to mark content as processed", content_id=str(content_id), error=str(e))
    
    def update_content_relevance(self, content_id: UUID, score: float) -> None:
        """
        Update relevance score for scraped content.
        
        Args:
            content_id: UUID of the content
            score: Relevance score (0.0 to 1.0)
        """
        try:
            self.client.table("scraped_content")\
                .update({"relevance_score": score})\
                .eq("id", str(content_id))\
                .execute()
            logger.debug("Updated content relevance", content_id=str(content_id), score=score)
        except Exception as e:
            logger.error("Failed to update content relevance", content_id=str(content_id), error=str(e))
    
    # ===== Opus Jobs =====
    
    def insert_opus_job(self, job: OpusJob) -> Optional[UUID]:
        """
        Insert Opus job record.
        
        Args:
            job: OpusJob object to insert
            
        Returns:
            UUID of inserted job or None if failed
        """
        try:
            data = job.model_dump(exclude={"id"}, exclude_none=True)
            # Convert datetime objects to ISO strings
            if data.get("initiated_at"):
                data["initiated_at"] = data["initiated_at"].isoformat()
            if data.get("completed_at"):
                data["completed_at"] = data["completed_at"].isoformat()
            # Convert UUIDs to strings
            if data.get("scraped_content_id"):
                data["scraped_content_id"] = str(data["scraped_content_id"])
            
            response = self.client.table("opus_jobs")\
                .insert(data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                job_id = UUID(response.data[0]["id"])
                logger.info("Inserted Opus job", job_id=str(job_id), job_execution_id=job.job_execution_id)
                return job_id
            return None
        except Exception as e:
            logger.error("Failed to insert Opus job", error=str(e))
            return None
    
    def update_opus_job_status(self, job_execution_id: str, status: str, 
                               results: Optional[Dict[str, Any]] = None,
                               error_message: Optional[str] = None) -> None:
        """
        Update Opus job status.
        
        Args:
            job_execution_id: Opus job execution ID
            status: New status (IN_PROGRESS, COMPLETED, FAILED)
            results: Job results if completed
            error_message: Error message if failed
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if status == "COMPLETED":
                update_data["completed_at"] = datetime.utcnow().isoformat()
                if results:
                    update_data["job_results"] = results
            
            if error_message:
                update_data["error_message"] = error_message
            
            self.client.table("opus_jobs")\
                .update(update_data)\
                .eq("job_execution_id", job_execution_id)\
                .execute()
            
            logger.info("Updated Opus job status", job_execution_id=job_execution_id, status=status)
        except Exception as e:
            logger.error("Failed to update Opus job status", job_execution_id=job_execution_id, error=str(e))
    
    def get_opus_job_by_execution_id(self, job_execution_id: str) -> Optional[OpusJob]:
        """
        Get Opus job by execution ID.
        
        Args:
            job_execution_id: Opus job execution ID
            
        Returns:
            OpusJob object or None if not found
        """
        try:
            response = self.client.table("opus_jobs")\
                .select("*")\
                .eq("job_execution_id", job_execution_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return OpusJob(**response.data[0])
            return None
        except Exception as e:
            logger.error("Failed to get Opus job", job_execution_id=job_execution_id, error=str(e))
            return None
    
    def get_daily_job_count(self) -> int:
        """
        Get count of Opus jobs initiated today.
        
        Returns:
            Number of jobs initiated today
        """
        try:
            from datetime import datetime, timedelta
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            response = self.client.table("opus_jobs")\
                .select("id", count="exact")\
                .gte("initiated_at", today_start.isoformat())\
                .execute()
            
            count = response.count if hasattr(response, 'count') and response.count else len(response.data)
            logger.debug("Retrieved daily job count", count=count)
            return count
        except Exception as e:
            logger.error("Failed to get daily job count", error=str(e))
            return 0
    
    # ===== Generated Content =====
    
    def insert_generated_content(self, content: GeneratedContent) -> Optional[UUID]:
        """
        Insert generated content.
        
        Args:
            content: GeneratedContent object to insert
            
        Returns:
            UUID of inserted content or None if failed
        """
        try:
            data = content.model_dump(exclude={"id"}, exclude_none=True)
            # Convert UUIDs to strings
            if data.get("opus_job_id"):
                data["opus_job_id"] = str(data["opus_job_id"])
            if data.get("scraped_content_id"):
                data["scraped_content_id"] = str(data["scraped_content_id"])
            if data.get("approved_at"):
                data["approved_at"] = data["approved_at"].isoformat()
            
            response = self.client.table("generated_content")\
                .insert(data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                content_id = UUID(response.data[0]["id"])
                logger.info("Inserted generated content", content_id=str(content_id))
                return content_id
            return None
        except Exception as e:
            logger.error("Failed to insert generated content", error=str(e))
            return None
    
    # ===== Published Posts =====
    
    def insert_published_post(self, post: PublishedPost) -> Optional[UUID]:
        """
        Insert published post record.
        
        Args:
            post: PublishedPost object to insert
            
        Returns:
            UUID of inserted post or None if failed
        """
        try:
            data = post.model_dump(exclude={"id"}, exclude_none=True)
            # Convert UUIDs to strings
            if data.get("generated_content_id"):
                data["generated_content_id"] = str(data["generated_content_id"])
            if data.get("opus_job_id"):
                data["opus_job_id"] = str(data["opus_job_id"])
            # Convert datetime to ISO string
            if data.get("published_at"):
                data["published_at"] = data["published_at"].isoformat()
            if data.get("last_metrics_update"):
                data["last_metrics_update"] = data["last_metrics_update"].isoformat()
            
            response = self.client.table("published_posts")\
                .insert(data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                post_id = UUID(response.data[0]["id"])
                logger.info("Inserted published post", post_id=str(post_id), platform=post.platform)
                return post_id
            return None
        except Exception as e:
            logger.error("Failed to insert published post", error=str(e))
            return None
    
    # ===== Content Templates =====
    
    def get_content_template(self, content_type: str) -> Optional[ContentTemplate]:
        """
        Get content template by type.
        
        Args:
            content_type: Type of content template
            
        Returns:
            ContentTemplate object or None if not found
        """
        try:
            response = self.client.table("content_templates")\
                .select("*")\
                .eq("content_type", content_type)\
                .eq("is_active", True)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return ContentTemplate(**response.data[0])
            return None
        except Exception as e:
            logger.error("Failed to get content template", content_type=content_type, error=str(e))
            return None
    
    # ===== System Logs =====
    
    def log_system_event(self, level: str, component: str, message: str, context: Dict[str, Any] = None) -> None:
        """
        Log system event to database.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            component: Component name
            message: Log message
            context: Additional context data
        """
        try:
            data = {
                "log_level": level,
                "component": component,
                "message": message,
                "context": context or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.client.table("system_logs")\
                .insert(data)\
                .execute()
        except Exception as e:
            logger.error("Failed to log system event", error=str(e))


# Global database client instance (lazy initialization)
_db_instance = None

def get_db() -> DatabaseClient:
    """
    Get or create the global database client instance.
    Uses lazy initialization to avoid connecting at import time.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseClient()
    return _db_instance

# Backward compatibility - access db as before, but with lazy init
class _DBProxy:
    """Proxy object that lazily initializes the database client."""
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = _DBProxy()
