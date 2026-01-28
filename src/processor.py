"""
Data processing module for content automation.
Handles data cleaning, relevance scoring, and preparation for Opus workflows.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from collections import defaultdict

from src.logger import logger
from src.models import ScrapedContent
from src.database import db


class ContentProcessor:
    """Processes scraped content for relevance and prepares it for Opus."""
    
    def __init__(self):
        """Initialize content processor."""
        # Keywords related to automation, AI, and business process
        self.relevant_keywords = {
            'automation', 'ai', 'artificial intelligence', 'machine learning',
            'workflow', 'process', 'business', 'efficiency', 'productivity',
            'digital transformation', 'rpa', 'intelligent automation',
            'enterprise', 'saas', 'b2b', 'technology', 'innovation',
            'integration', 'orchestration', 'optimization', 'streamline'
        }
        logger.info("Content processor initialized")
    
    def calculate_relevance_score(self, content: ScrapedContent) -> float:
        """
        Calculate relevance score for scraped content.
        Score is between 0.0 and 1.0.
        
        Args:
            content: ScrapedContent object
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.0
        weights = {
            'keywords': 0.4,
            'title': 0.3,
            'content_quality': 0.2,
            'freshness': 0.1
        }
        
        # 1. Keyword matching (40% weight)
        keyword_score = 0.0
        content_text = f"{content.title or ''} {content.summary or ''} {' '.join(content.keywords)}".lower()
        
        matched_keywords = 0
        for keyword in self.relevant_keywords:
            if keyword in content_text:
                matched_keywords += 1
        
        if matched_keywords > 0:
            # Normalize: 5+ matches = perfect score
            keyword_score = min(matched_keywords / 5.0, 1.0)
        
        score += keyword_score * weights['keywords']
        
        # 2. Title relevance (30% weight)
        title_score = 0.0
        if content.title:
            title_lower = content.title.lower()
            for keyword in self.relevant_keywords:
                if keyword in title_lower:
                    title_score = 1.0
                    break
        
        score += title_score * weights['title']
        
        # 3. Content quality (20% weight)
        quality_score = 0.0
        
        # Check content length (prefer substantial articles)
        if content.content:
            content_length = len(content.content)
            if content_length > 1000:  # Substantial content
                quality_score += 0.5
            elif content_length > 500:  # Medium content
                quality_score += 0.3
            elif content_length > 200:  # Short content
                quality_score += 0.1
        
        # Check if has summary
        if content.summary and len(content.summary) > 50:
            quality_score += 0.3
        
        # Check if has author
        if content.author:
            quality_score += 0.2
        
        quality_score = min(quality_score, 1.0)
        score += quality_score * weights['content_quality']
        
        # 4. Freshness (10% weight)
        freshness_score = 0.5  # Default neutral score
        if content.published_at:
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            age = now - content.published_at.replace(tzinfo=None)
            
            if age < timedelta(days=1):
                freshness_score = 1.0
            elif age < timedelta(days=7):
                freshness_score = 0.8
            elif age < timedelta(days=30):
                freshness_score = 0.6
            elif age < timedelta(days=90):
                freshness_score = 0.4
            else:
                freshness_score = 0.2
        
        score += freshness_score * weights['freshness']
        
        logger.debug("Calculated relevance score",
                    url=content.url,
                    score=round(score, 3),
                    keyword_score=round(keyword_score, 3),
                    title_score=round(title_score, 3),
                    quality_score=round(quality_score, 3),
                    freshness_score=round(freshness_score, 3))
        
        return round(score, 3)
    
    def process_scraped_content(self, content: ScrapedContent) -> UUID:
        """
        Process and store scraped content.
        
        Args:
            content: ScrapedContent object to process
            
        Returns:
            UUID of stored content
        """
        logger.info("Processing scraped content", url=content.url)
        
        # Calculate relevance score
        relevance_score = self.calculate_relevance_score(content)
        content.relevance_score = relevance_score
        
        # Store in database
        content_id = db.insert_scraped_content(content)
        
        if content_id:
            logger.info("Scraped content processed and stored",
                       content_id=str(content_id),
                       url=content.url,
                       relevance_score=relevance_score)
        else:
            logger.error("Failed to store scraped content", url=content.url)
        
        return content_id
    
    def process_batch(self, contents: List[ScrapedContent]) -> List[UUID]:
        """
        Process a batch of scraped content.
        
        Args:
            contents: List of ScrapedContent objects
            
        Returns:
            List of UUIDs of stored content
        """
        logger.info("Processing content batch", count=len(contents))
        
        content_ids = []
        for content in contents:
            try:
                content_id = self.process_scraped_content(content)
                if content_id:
                    content_ids.append(content_id)
            except Exception as e:
                logger.error("Error processing content in batch",
                           url=content.url,
                           error=str(e))
                continue
        
        logger.info("Batch processing completed",
                   total=len(contents),
                   successful=len(content_ids))
        
        return content_ids
    
    def prepare_for_opus(self, content: ScrapedContent, content_type: str) -> Dict[str, Any]:
        """
        Prepare scraped content for Opus workflow input.
        
        Args:
            content: ScrapedContent object
            content_type: Type of content to generate
            
        Returns:
            Dictionary ready for Opus job payload
        """
        logger.debug("Preparing content for Opus",
                    content_id=str(content.id) if content.id else "unknown",
                    content_type=content_type)
        
        # Extract source name from metadata or fallback to type
        source_name = content.metadata.get("source_name", content.metadata.get("source_type", "web"))
        
        # Create structured data for Opus
        opus_input = {
            "source": source_name,  # Source name like "VentureBeat AI", "TechCrunch AI"
            "url": content.url,
            "title": content.title or "Untitled",
            "content": content.content or "",  # Full content for Opus workflow
            "summary": content.summary or content.content[:500] if content.content else "",
            "keywords": content.keywords or [],
            "author": content.author,
            "published_at": content.published_at.isoformat() if content.published_at else None,
            "content_type": content_type,
            "relevance_score": content.relevance_score
        }
        
        logger.debug("Prepared Opus input",
                    source=source_name,
                    title=opus_input['title'][:50],
                    content_length=len(opus_input['content']))
        
        return opus_input
    
    def filter_by_relevance(self, min_score: float = 0.5) -> List[ScrapedContent]:
        """
        Get high-relevance unprocessed content from database.
        
        Args:
            min_score: Minimum relevance score threshold
            
        Returns:
            List of high-relevance ScrapedContent objects
        """
        logger.info("Filtering content by relevance", min_score=min_score)
        
        # Get unprocessed content
        all_content = db.get_unprocessed_content(limit=50)
        
        # Filter by relevance score
        filtered = [c for c in all_content if c.relevance_score and c.relevance_score >= min_score]
        
        logger.info("Filtered content by relevance",
                   total=len(all_content),
                   filtered=len(filtered),
                   min_score=min_score)
        
        return filtered
    
    def categorize_content(self, content: ScrapedContent) -> str:
        """
        Categorize content into content type based on characteristics.
        
        Args:
            content: ScrapedContent object
            
        Returns:
            Content type (industry_news, thought_leadership, or case_study)
        """
        content_text = f"{content.title or ''} {content.summary or ''}".lower()
        
        # Keywords indicating different content types
        news_indicators = ['announce', 'launch', 'release', 'new', 'latest', 'update']
        thought_indicators = ['future', 'trend', 'prediction', 'analysis', 'insight', 'perspective']
        case_study_indicators = ['success', 'case study', 'customer', 'client', 'implementation', 'roi', 'results']
        
        # Count indicators
        news_score = sum(1 for indicator in news_indicators if indicator in content_text)
        thought_score = sum(1 for indicator in thought_indicators if indicator in content_text)
        case_score = sum(1 for indicator in case_study_indicators if indicator in content_text)
        
        # Determine category
        scores = {
            'industry_news': news_score,
            'thought_leadership': thought_score,
            'case_study': case_score
        }
        
        content_type = max(scores, key=scores.get)
        
        # Default to industry_news if all scores are 0
        if scores[content_type] == 0:
            content_type = 'industry_news'
        
        logger.debug("Categorized content",
                    content_id=str(content.id) if content.id else "unknown",
                    category=content_type,
                    scores=scores)
        
        return content_type
    
    def select_diverse_content(self, contents: List[ScrapedContent], 
                              max_items: int = 15,
                              ensure_diversity: bool = True) -> List[ScrapedContent]:
        """
        Intelligently select content ensuring diversity and quality.
        
        Args:
            contents: List of ScrapedContent to select from
            max_items: Maximum number of items to select
            ensure_diversity: Whether to ensure category diversity
            
        Returns:
            Selected list of ScrapedContent
        """
        if not contents:
            return []
        
        if len(contents) <= max_items:
            return contents
        
        if not ensure_diversity:
            # Simple: just take top N by score
            sorted_contents = sorted(contents, key=lambda x: x.relevance_score or 0, reverse=True)
            return sorted_contents[:max_items]
        
        logger.info("Selecting diverse content", 
                   total_available=len(contents),
                   target_count=max_items)
        
        # Categorize content by type
        categorized = defaultdict(list)
        for content in contents:
            category = self.categorize_content(content)
            categorized[category].append(content)
        
        # Sort each category by relevance score
        for category in categorized:
            categorized[category].sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        # Intelligent distribution across categories
        selected = []
        categories = list(categorized.keys())
        num_categories = len(categories)
        
        if num_categories == 0:
            return []
        
        # Calculate base allocation per category
        base_per_category = max_items // num_categories
        remainder = max_items % num_categories
        
        # Allocate items from each category
        for i, category in enumerate(categories):
            # Give extra items to first categories for remainder
            allocation = base_per_category + (1 if i < remainder else 0)
            category_items = categorized[category][:allocation]
            selected.extend(category_items)
            
            logger.debug("Selected from category",
                        category=category,
                        allocated=allocation,
                        available=len(categorized[category]),
                        selected=len(category_items))
        
        # If we still haven't hit max_items (due to category limitations),
        # fill with highest-scoring remaining items
        if len(selected) < max_items:
            remaining = [c for c in contents if c not in selected]
            remaining.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            needed = max_items - len(selected)
            selected.extend(remaining[:needed])
        
        # Final sort by relevance score
        selected.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        logger.info("Diverse content selection completed",
                   selected_count=len(selected),
                   category_distribution={
                       cat: len([c for c in selected if self.categorize_content(c) == cat])
                       for cat in categories
                   })
        
        return selected[:max_items]
    
    def select_tiered_content(self, contents: List[ScrapedContent],
                            max_items: int = 15) -> List[ScrapedContent]:
        """
        Select content using tiered approach for quality.
        
        Tier 1: Excellent (>= 0.8) - Must include
        Tier 2: Great (0.6-0.8) - Should include with diversity
        Tier 3: Good (0.5-0.6) - Fill to target if needed
        
        Args:
            contents: List of ScrapedContent to select from
            max_items: Maximum number of items to select
            
        Returns:
            Selected list of ScrapedContent
        """
        logger.info("Selecting tiered content", total_available=len(contents))
        
        # Tier 1: Excellence - always include (up to 40% of max)
        tier1 = [c for c in contents if c.relevance_score and c.relevance_score >= 0.8]
        tier1.sort(key=lambda x: x.relevance_score, reverse=True)
        tier1_limit = min(len(tier1), max(int(max_items * 0.4), 5))
        selected = tier1[:tier1_limit]
        
        # Tier 2: Quality with diversity (up to 50% of max)
        tier2 = [c for c in contents 
                if c.relevance_score and 0.6 <= c.relevance_score < 0.8
                and c not in selected]
        tier2_limit = min(len(tier2), max(int(max_items * 0.5), 7))
        
        # Apply diversity to tier 2
        if tier2:
            tier2_selected = self.select_diverse_content(tier2, tier2_limit, ensure_diversity=True)
            selected.extend(tier2_selected)
        
        # Tier 3: Fill remaining slots
        if len(selected) < max_items:
            tier3 = [c for c in contents 
                    if c.relevance_score and 0.5 <= c.relevance_score < 0.6
                    and c not in selected]
            tier3.sort(key=lambda x: x.relevance_score, reverse=True)
            needed = max_items - len(selected)
            selected.extend(tier3[:needed])
        
        logger.info("Tiered selection completed",
                   tier1_count=tier1_limit,
                   tier2_count=len([c for c in selected if 0.6 <= c.relevance_score < 0.8]),
                   tier3_count=len([c for c in selected if c.relevance_score < 0.6]),
                   total_selected=len(selected))
        
        return selected


# Global processor instance
processor = ContentProcessor()
