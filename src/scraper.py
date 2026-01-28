"""
Web scraping module using Firecrawl.
Handles scraping content from various web sources.
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from firecrawl import Firecrawl
    from firecrawl.types import ScrapeOptions
except ImportError:
    # Fallback for older SDK version
    from firecrawl import FirecrawlApp as Firecrawl
    ScrapeOptions = None

from src.config import settings
from src.logger import logger
from src.models import ScrapedContent, ContentSource
from src.rss_reader import rss_reader


class ScraperError(Exception):
    """Custom exception for scraping errors."""
    pass


class WebScraper:
    """Web scraper using Firecrawl API."""
    
    def __init__(self):
        """Initialize Firecrawl client."""
        self.client = Firecrawl(api_key=settings.firecrawl_api_key)
        logger.info("Web scraper initialized with Firecrawl SDK")
    
    def _is_valid_article_url(self, url: str, title: str = "") -> bool:
        """
        Validate if URL is an actual article, not an archive/category/pagination page.
        
        Args:
            url: URL to validate
            title: Page title (optional, for additional validation)
            
        Returns:
            True if URL appears to be a valid article
        """
        # Reject archive/category/pagination URLs
        invalid_patterns = [
            '/page/',
            '/category/',
            '/archives/',
            '/archive/',
            '/tag/',
            '/tags/',
            '/author/',
            '/feed/',
            '/rss',
        ]
        
        url_lower = url.lower()
        for pattern in invalid_patterns:
            if pattern in url_lower:
                logger.debug("URL rejected (invalid pattern)",
                           url=url[:100],
                           pattern=pattern)
                return False
        
        # Check title for archive page indicators
        if title:
            title_lower = title.lower()
            invalid_title_patterns = [
                'page ',
                ' of ',
                'archives',
                'category:',
                'tag:',
            ]
            
            # Check if title matches multiple invalid patterns (more strict)
            invalid_count = sum(1 for pattern in invalid_title_patterns if pattern in title_lower)
            if invalid_count >= 2:  # Title contains 2+ invalid patterns
                logger.debug("Title rejected (archive page indicator)",
                           title=title[:100],
                           url=url[:100])
                return False
        
        return True
    
    def _is_quality_content(self, content: str, title: str = "", url: str = "") -> bool:
        """
        Validate if content meets minimum quality standards.
        
        Args:
            content: Content text to validate
            title: Page title
            url: Page URL
            
        Returns:
            True if content meets quality standards
        """
        if not content:
            logger.debug("Content rejected (empty)", url=url[:100])
            return False
        
        # Minimum content length (500 chars for meaningful articles)
        if len(content) < 500:
            logger.debug("Content rejected (too short)",
                       url=url[:100],
                       length=len(content),
                       min_required=500)
            return False
        
        # Check for actual article content vs. navigation/list pages
        content_lower = content.lower()
        
        # Archive pages often have lots of links but little actual content
        link_count = content_lower.count('[')  # Markdown links
        if link_count > 20 and len(content) < 2000:
            # Many links but short content = likely a listing page
            logger.debug("Content rejected (link-heavy listing page)",
                       url=url[:100],
                       links=link_count,
                       length=len(content))
            return False
        
        # Check for meaningful paragraph content
        paragraphs = [p.strip() for p in content.split('\n') if len(p.strip()) > 50]
        if len(paragraphs) < 3:
            logger.debug("Content rejected (insufficient paragraphs)",
                       url=url[:100],
                       paragraphs=len(paragraphs))
            return False
        
        return True
    
    def _generate_content_hash(self, content: str) -> str:
        """
        Generate hash of content for deduplication.
        
        Args:
            content: Content text to hash
            
        Returns:
            SHA256 hash of content
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text (simple implementation).
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction - in production, use NLP library like spaCy or NLTK
        # For now, extract common meaningful words
        if not text:
            return []
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their'
        }
        
        # Extract words
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            word = ''.join(c for c in word if c.isalnum())
            # Filter
            if (len(word) > 3 and 
                word not in stop_words and 
                word not in keywords):
                keywords.append(word)
                if len(keywords) >= max_keywords:
                    break
        
        return keywords
    
    def scrape_url(self, url: str, source: Optional[ContentSource] = None) -> Optional[ScrapedContent]:
        """
        Scrape content from a single URL using Firecrawl.
        
        Args:
            url: URL to scrape
            source: ContentSource object if available
            
        Returns:
            ScrapedContent object or None if scraping failed
        """
        logger.info("Scraping URL", url=url)
        
        try:
            # Scrape URL with Firecrawl (new SDK uses scrape method)
            if ScrapeOptions:
                # New SDK with ScrapeOptions (uses snake_case parameters)
                result = self.client.scrape(
                    url,
                    formats=['markdown', 'html'],
                    only_main_content=True
                )
            else:
                # Fallback for old SDK
                result = self.client.scrape_url(url, params={
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True
                })
            
            if not result:
                logger.warning("No result from Firecrawl", url=url)
                return None
            
            # Handle both new SDK (object) and old SDK (dict) response formats
            if hasattr(result, 'markdown'):
                # New SDK returns Document object
                markdown_content = result.markdown or ''
                html_content = result.html if hasattr(result, 'html') else ''
                metadata = result.metadata if hasattr(result, 'metadata') else {}
                if isinstance(metadata, dict):
                    pass  # Already a dict
                else:
                    # Convert metadata object to dict
                    metadata = vars(metadata) if hasattr(metadata, '__dict__') else {}
            else:
                # Old SDK returns dict
                metadata = result.get('metadata', {})
                markdown_content = result.get('markdown', '')
                html_content = result.get('html', '')
            
            # Use markdown as primary content, fallback to HTML
            content = markdown_content or html_content
            
            if not content:
                logger.warning("No content extracted", url=url)
                return None
            
            # Extract title from metadata or content
            title = metadata.get('title') or metadata.get('ogTitle') or url.split('/')[-1]
            
            # Validate URL is an actual article (not archive/category page)
            if not self._is_valid_article_url(url, title):
                logger.info("Skipping non-article URL",
                          url=url,
                          title=title[:100] if title else None)
                return None
            
            # Validate content quality
            if not self._is_quality_content(content, title, url):
                logger.info("Skipping low-quality content",
                          url=url,
                          title=title[:100] if title else None,
                          content_length=len(content))
                return None
            
            # Extract description/summary
            summary = (
                metadata.get('description') or 
                metadata.get('ogDescription') or 
                content[:500]  # First 500 chars as fallback
            )
            
            # Extract author
            author = metadata.get('author') or metadata.get('ogSiteName')
            
            # Extract published date if available
            published_at = None
            if metadata.get('publishedTime'):
                try:
                    published_at = datetime.fromisoformat(metadata['publishedTime'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
            
            # Generate content hash
            content_hash = self._generate_content_hash(content)
            
            # Extract keywords
            keywords = self._extract_keywords(content, max_keywords=10)
            
            # Create ScrapedContent object
            scraped_content = ScrapedContent(
                source_id=source.id if source else None,
                url=url,
                title=title,
                content=content,
                summary=summary,
                author=author,
                published_at=published_at,
                scraped_at=datetime.utcnow(),
                content_hash=content_hash,
                keywords=keywords,
                is_processed=False,
                metadata={
                    'firecrawl_metadata': metadata,
                    'content_length': len(content),
                    'source_type': source.source_type if source else 'unknown',
                    'source_name': source.name if source else 'Unknown Source'
                }
            )
            
            logger.info("Successfully scraped URL", 
                       url=url, 
                       title=title,
                       content_length=len(content))
            
            return scraped_content
            
        except Exception as e:
            logger.error("Failed to scrape URL", url=url, error=str(e))
            return None
    
    def scrape_multiple_urls(self, urls: List[str], 
                            source: Optional[ContentSource] = None) -> List[ScrapedContent]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            source: ContentSource object if available
            
        Returns:
            List of successfully scraped ScrapedContent objects
        """
        logger.info("Scraping multiple URLs", count=len(urls))
        
        scraped_contents = []
        
        for url in urls:
            try:
                content = self.scrape_url(url, source)
                if content:
                    scraped_contents.append(content)
            except Exception as e:
                logger.error("Error scraping URL in batch", url=url, error=str(e))
                continue
        
        logger.info("Batch scraping completed", 
                   total_urls=len(urls),
                   successful=len(scraped_contents))
        
        return scraped_contents
    
    def scrape_from_rss(self, rss_feed_url: str, 
                       source: Optional[ContentSource] = None,
                       scrape_full_content: bool = True,
                       max_articles: Optional[int] = None) -> List[ScrapedContent]:
        """
        Scrape content from RSS feed.
        Uses RSS for content discovery, optionally scrapes full content from article URLs.
        
        Args:
            rss_feed_url: URL of the RSS feed
            source: ContentSource object if available
            scrape_full_content: Whether to scrape full content from article URLs
            max_articles: Maximum number of articles to scrape (for credit optimization)
            
        Returns:
            List of ScrapedContent objects
        """
        from .config import settings
        
        # Use config default if not specified
        if max_articles is None:
            max_articles = settings.max_articles_per_source
        
        logger.info("Scraping from RSS feed",
                   rss_url=rss_feed_url,
                   scrape_full=scrape_full_content,
                   max_articles=max_articles)
        
        try:
            # Fetch RSS entries
            entries = rss_reader.fetch_feed(rss_feed_url, only_recent=True)
            
            if not entries:
                logger.warning("No recent entries found in RSS feed",
                             rss_url=rss_feed_url)
                return []
            
            # Limit entries for credit optimization
            original_count = len(entries)
            entries = entries[:max_articles]
            
            if original_count > max_articles:
                logger.info("Limited RSS entries for credit optimization",
                           total_available=original_count,
                           processing=len(entries),
                           max_limit=max_articles)
            
            scraped_contents = []
            estimated_credits = 0  # Track credit usage
            skipped_duplicates = 0
            
            for entry in entries:
                try:
                    article_url = entry.get('link')
                    
                    if not article_url:
                        logger.warning("RSS entry has no link, skipping",
                                     title=entry.get('title'))
                        continue
                    
                    # Validate URL is an actual article (not archive/category page)
                    article_title = entry.get('title', '')
                    if not self._is_valid_article_url(article_url, article_title):
                        logger.info("Skipping non-article RSS entry",
                                  url=article_url[:100],
                                  title=article_title[:100] if article_title else None)
                        continue
                    
                    # Check for duplicate URLs (deduplication optimization)
                    from .config import settings
                    if settings.enable_url_deduplication:
                        from .database import db
                        if db.url_exists(article_url):
                            logger.debug("Skipping duplicate URL",
                                       url=article_url[:100],
                                       title=entry.get('title', '')[:50])
                            skipped_duplicates += 1
                            continue
                    
                    # Option 1: Use RSS data + scrape full content
                    if scrape_full_content:
                        # Scrape full content from article URL (1 credit per article)
                        full_content = self.scrape_url(article_url, source)
                        estimated_credits += 1  # Each scrape costs 1 credit
                        
                        if full_content:
                            # Enhance with RSS metadata
                            if entry.get('published_at') and not full_content.published_at:
                                full_content.published_at = entry['published_at']
                            if entry.get('author') and not full_content.author:
                                full_content.author = entry['author']
                            if entry.get('tags'):
                                full_content.metadata['rss_tags'] = entry['tags']
                            
                            full_content.metadata['discovered_via'] = 'rss'
                            full_content.metadata['rss_feed_url'] = rss_feed_url
                            full_content.metadata['firecrawl_credits_used'] = 1
                            
                            scraped_contents.append(full_content)
                        else:
                            logger.warning("Failed to scrape full content, using RSS data only",
                                         url=article_url)
                            # Fallback to RSS data (0 credits)
                            rss_content = self._create_content_from_rss(entry, source, rss_feed_url)
                            if rss_content:
                                rss_content.metadata['firecrawl_credits_used'] = 0
                                scraped_contents.append(rss_content)
                    
                    # Option 2: Use RSS data only (0 credits - no API call)
                    else:
                        rss_content = self._create_content_from_rss(entry, source, rss_feed_url)
                        if rss_content:
                            rss_content.metadata['firecrawl_credits_used'] = 0
                            scraped_contents.append(rss_content)
                    
                except Exception as e:
                    logger.error("Error processing RSS entry",
                               title=entry.get('title'),
                               error=str(e))
                    continue
            
            logger.info("RSS feed scraping completed",
                       rss_url=rss_feed_url,
                       total_entries=len(entries),
                       scraped=len(scraped_contents),
                       skipped_duplicates=skipped_duplicates,
                       estimated_credits=estimated_credits)
            
            # Log credit usage if tracking enabled
            from .config import settings
            if settings.track_credit_usage and estimated_credits > 0:
                logger.warning("💰 Firecrawl Credits Used",
                             source=source.name if source else "Unknown",
                             credits_used=estimated_credits,
                             articles_scraped=len(scraped_contents),
                             duplicates_skipped=skipped_duplicates)
            
            return scraped_contents
            
        except Exception as e:
            logger.error("Failed to scrape from RSS feed",
                       rss_url=rss_feed_url,
                       error=str(e))
            return []
    
    def _create_content_from_rss(self, entry: Dict[str, Any],
                                source: Optional[ContentSource],
                                rss_feed_url: str) -> Optional[ScrapedContent]:
        """
        Create ScrapedContent object from RSS entry data.
        
        Args:
            entry: RSS entry dictionary
            source: ContentSource object
            rss_feed_url: RSS feed URL
            
        Returns:
            ScrapedContent object or None
        """
        try:
            url = entry.get('link')
            title = entry.get('title', '')
            content = entry.get('content', '')
            summary = entry.get('summary', '')
            
            # Use summary if no full content
            if not content:
                content = summary
            
            if not content or not url:
                return None
            
            # Generate content hash
            content_hash = self._generate_content_hash(content)
            
            # Extract keywords from title and summary
            keywords = self._extract_keywords(f"{title} {summary}", max_keywords=10)
            
            scraped_content = ScrapedContent(
                source_id=source.id if source else None,
                url=url,
                title=title,
                content=content,
                summary=summary,
                author=entry.get('author'),
                published_at=entry.get('published_at'),
                scraped_at=datetime.utcnow(),
                content_hash=content_hash,
                keywords=keywords,
                is_processed=False,
                metadata={
                    'source_type': 'rss',
                    'source_name': source.name if source else entry.get('feed_title', 'Unknown Source'),
                    'rss_feed_url': rss_feed_url,
                    'rss_tags': entry.get('tags', []),
                    'feed_title': entry.get('feed_title', ''),
                    'content_length': len(content),
                    'full_content_scraped': False
                }
            )
            
            return scraped_content
            
        except Exception as e:
            logger.error("Failed to create content from RSS entry",
                       entry_title=entry.get('title'),
                       error=str(e))
            return None
    
    def crawl_website(self, url: str, 
                     max_pages: int = 10,
                     source: Optional[ContentSource] = None) -> List[ScrapedContent]:
        """
        Crawl a website and scrape multiple pages using Firecrawl's crawl feature.
        
        Args:
            url: Base URL to crawl
            max_pages: Maximum number of pages to crawl
            source: ContentSource object if available
            
        Returns:
            List of scraped ScrapedContent objects
        """
        logger.info("Crawling website", url=url, max_pages=max_pages)
        
        try:
            # Use Firecrawl's crawl functionality with new SDK
            if ScrapeOptions:
                # New SDK - synchronous crawl that waits for completion (uses snake_case)
                logger.debug("Using new Firecrawl SDK crawl method")
                crawl_result = self.client.crawl(
                    url,
                    limit=max_pages,
                    scrape_options=ScrapeOptions(
                        formats=['markdown', 'html'],
                        only_main_content=True
                    ),
                    poll_interval=5  # Poll every 5 seconds
                )
            else:
                # Old SDK fallback
                logger.debug("Using legacy Firecrawl SDK crawl_url method")
                crawl_result = self.client.crawl_url(url, params={
                    'limit': max_pages,
                    'scrapeOptions': {
                        'formats': ['markdown', 'html'],
                        'onlyMainContent': True
                    }
                })
            
            # Handle response - new SDK returns CrawlResponse object with data attribute
            if hasattr(crawl_result, 'data'):
                # New SDK response
                if not crawl_result.data:
                    logger.warning("No crawl results", url=url)
                    return []
                
                logger.info("Crawl completed", 
                           status=crawl_result.status if hasattr(crawl_result, 'status') else 'unknown',
                           completed=crawl_result.completed if hasattr(crawl_result, 'completed') else len(crawl_result.data),
                           total=crawl_result.total if hasattr(crawl_result, 'total') else len(crawl_result.data))
                
                page_data_list = crawl_result.data
            elif isinstance(crawl_result, dict) and 'data' in crawl_result:
                # Old SDK response
                if not crawl_result.get('data'):
                    logger.warning("No crawl results", url=url)
                    return []
                page_data_list = crawl_result['data']
            else:
                logger.error("Unexpected crawl result format", result_type=type(crawl_result))
                return []
            
            scraped_contents = []
            
            for page_data in page_data_list:
                try:
                    # Handle both new SDK (Document object) and old SDK (dict) formats
                    if hasattr(page_data, 'markdown'):
                        # New SDK Document object
                        markdown_content = page_data.markdown or ''
                        html_content = page_data.html if hasattr(page_data, 'html') else ''
                        
                        # Get metadata
                        if hasattr(page_data, 'metadata'):
                            metadata = page_data.metadata
                            if not isinstance(metadata, dict):
                                # Convert metadata object to dict
                                metadata = vars(metadata) if hasattr(metadata, '__dict__') else {}
                        else:
                            metadata = {}
                        
                        # Get URL from metadata
                        page_url = metadata.get('url') or metadata.get('sourceURL') or url
                    else:
                        # Old SDK dict format
                        page_url = page_data.get('metadata', {}).get('url', url)
                        metadata = page_data.get('metadata', {})
                        markdown_content = page_data.get('markdown', '')
                        html_content = page_data.get('html', '')
                    
                    content = markdown_content or html_content
                    
                    if not content:
                        continue
                    
                    title = (
                        metadata.get('title') or 
                        metadata.get('ogTitle') or 
                        page_url.split('/')[-1]
                    )
                    
                    # Validate URL is an actual article (not archive/category page)
                    if not self._is_valid_article_url(page_url, title):
                        logger.debug("Skipping non-article crawled page",
                                   url=page_url[:100],
                                   title=title[:100] if title else None)
                        continue
                    
                    # Validate content quality
                    if not self._is_quality_content(content, title, page_url):
                        logger.debug("Skipping low-quality crawled page",
                                   url=page_url[:100],
                                   title=title[:100] if title else None,
                                   content_length=len(content))
                        continue
                    
                    summary = (
                        metadata.get('description') or 
                        metadata.get('ogDescription') or 
                        content[:500]
                    )
                    
                    author = metadata.get('author') or metadata.get('ogSiteName')
                    
                    published_at = None
                    if metadata.get('publishedTime'):
                        try:
                            published_at = datetime.fromisoformat(
                                metadata['publishedTime'].replace('Z', '+00:00')
                            )
                        except (ValueError, AttributeError):
                            pass
                    
                    content_hash = self._generate_content_hash(content)
                    keywords = self._extract_keywords(content, max_keywords=10)
                    
                    scraped_content = ScrapedContent(
                        source_id=source.id if source else None,
                        url=page_url,
                        title=title,
                        content=content,
                        summary=summary,
                        author=author,
                        published_at=published_at,
                        scraped_at=datetime.utcnow(),
                        content_hash=content_hash,
                        keywords=keywords,
                        is_processed=False,
                        metadata={
                            'firecrawl_metadata': metadata,
                            'content_length': len(content),
                            'source_type': source.source_type if source else 'crawl',
                            'source_name': source.name if source else 'Unknown Source',
                            'firecrawl_credits_used': max_pages  # Crawl credits (estimated)
                        }
                    )
                    
                    scraped_contents.append(scraped_content)
                    logger.debug("Crawled page", url=page_url, title=title)
                    
                except Exception as e:
                    logger.error("Error processing crawled page", error=str(e))
                    continue
            
            # Estimate credits: crawl typically costs 10+ credits minimum
            # More accurate estimate: 1 credit per page found, minimum 10
            estimated_credits = max(10, len(scraped_contents))
            
            logger.info("Website crawl completed", 
                       base_url=url,
                       pages_crawled=len(scraped_contents),
                       estimated_credits=estimated_credits)
            
            # Log credit usage if tracking enabled
            from .config import settings
            if settings.track_credit_usage:
                logger.warning("💰 Firecrawl Credits Used (Crawl)",
                             source=source.name if source else "Unknown",
                             method="crawl",
                             credits_used=estimated_credits,
                             pages_found=len(scraped_contents),
                             max_pages_limit=max_pages)
            
            return scraped_contents
            
        except Exception as e:
            logger.error("Failed to crawl website", url=url, error=str(e))
            return []


# Global scraper instance
scraper = WebScraper()
