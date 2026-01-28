"""
Data models for the Content Automation System.
Pydantic models for type safety and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class ContentSource(BaseModel):
    """Model for content source configuration."""
    id: Optional[UUID] = None
    url: str
    name: str
    source_type: str
    scraping_frequency_minutes: int = 60
    is_active: bool = True
    reliability_score: float = 1.0
    last_scraped_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class ScrapedContent(BaseModel):
    """Model for scraped web content."""
    id: Optional[UUID] = None
    source_id: Optional[UUID] = None
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None
    keywords: List[str] = []
    relevance_score: Optional[float] = None
    is_processed: bool = False
    metadata: Dict[str, Any] = {}


class OpusJob(BaseModel):
    """Model for Opus job execution tracking."""
    id: Optional[UUID] = None
    job_execution_id: Optional[str] = None
    workflow_id: str
    scraped_content_id: Optional[UUID] = None
    status: str = "INITIATED"
    job_payload: Optional[Dict[str, Any]] = None
    job_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class GeneratedContent(BaseModel):
    """Model for AI-generated content."""
    id: Optional[UUID] = None
    opus_job_id: Optional[UUID] = None
    scraped_content_id: Optional[UUID] = None
    content_type: str
    generated_text: str
    target_platform: str = "twitter"
    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class PublishedPost(BaseModel):
    """Model for published social media posts."""
    id: Optional[UUID] = None
    generated_content_id: Optional[UUID] = None
    opus_job_id: Optional[UUID] = None
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    post_text: str
    published_at: datetime = Field(default_factory=datetime.utcnow)
    engagement_metrics: Dict[str, Any] = {}
    last_metrics_update: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class ContentTemplate(BaseModel):
    """Model for content generation templates."""
    id: Optional[UUID] = None
    content_type: str
    template_name: str
    system_prompt: str
    user_prompt_template: str
    temperature: float = 0.7
    model_preference: str = "gpt-4"
    is_active: bool = True
    metadata: Dict[str, Any] = {}


class OpusWorkflowInput(BaseModel):
    """Model for Opus workflow input payload."""
    scraped_content: Dict[str, Any]
    content_type: str
    target_audience: str


class OpusJobInitiateRequest(BaseModel):
    """Model for Opus job initiation request."""
    workflowId: str
    title: str
    description: str


class OpusJobExecuteRequest(BaseModel):
    """Model for Opus job execution request."""
    jobExecutionId: str
    jobPayloadSchemaInstance: Dict[str, Any]
