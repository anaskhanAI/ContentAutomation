"""
Configuration management for the Content Automation System.
Loads environment variables and provides typed configuration objects.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Opus API Configuration
    opus_api_key: str = Field(..., description="Opus service key for API authentication")
    opus_base_url: str = Field(default="https://operator.opus.com", description="Opus API base URL")
    opus_workflow_id: str = Field(..., description="Workflow ID for content generation")
    
    # Firecrawl Configuration
    firecrawl_api_key: str = Field(..., description="Firecrawl API key for web scraping")
    
    # Supabase Configuration
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anonymous key")
    
    # Application Configuration
    environment: str = Field(default="development", description="Environment: development, staging, production")
    log_level: str = Field(default="INFO", description="Logging level")
    scraping_interval_minutes: int = Field(default=60, description="Interval between scraping runs in minutes")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed operations")
    retry_delay_seconds: int = Field(default=5, description="Delay between retries in seconds")
    
    # Content Processing Configuration
    max_items_per_run: int = Field(default=15, description="Maximum items to send to Opus per processing run")
    min_relevance_score: float = Field(default=0.5, description="Minimum relevance score to send to Opus")
    daily_post_limit: int = Field(default=30, description="Maximum posts to send to Opus per day (safety limit)")
    enable_content_diversity: bool = Field(default=True, description="Enable intelligent content diversity selection")
    immediate_processing: bool = Field(default=True, description="Process content immediately after scraping")
    
    # RSS Feed Configuration
    use_rss_feeds: bool = Field(default=True, description="Use RSS feeds for content discovery when available")
    rss_freshness_days: int = Field(default=7, description="Only fetch RSS entries from last N days")
    rss_fallback_to_crawl: bool = Field(default=True, description="Fallback to web crawling if RSS not available")
    
    # Credit Optimization (Firecrawl API)
    max_articles_per_source: int = Field(default=3, description="Maximum articles to scrape per source (credit optimization)")
    max_crawl_pages: int = Field(default=3, description="Maximum pages to crawl when RSS unavailable (credit optimization)")
    enable_url_deduplication: bool = Field(default=True, description="Skip scraping URLs already in database")
    track_credit_usage: bool = Field(default=True, description="Track and log estimated Firecrawl credit usage")
    
    # Content Sources
    content_sources: str = Field(
        default="",
        description="Comma-separated list of URLs to scrape"
    )
    
    # Content Strategy
    content_types: str = Field(
        default="industry_news,thought_leadership,case_study",
        description="Comma-separated list of content types"
    )
    target_audience: str = Field(
        default="B2B_decision_makers",
        description="Target audience for content"
    )
    
    @property
    def sources_list(self) -> List[str]:
        """Parse content sources into a list."""
        if not self.content_sources:
            return []
        return [s.strip() for s in self.content_sources.split(",") if s.strip()]
    
    @property
    def content_types_list(self) -> List[str]:
        """Parse content types into a list."""
        return [ct.strip() for ct in self.content_types.split(",") if ct.strip()]
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
