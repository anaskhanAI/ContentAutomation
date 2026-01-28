"""
RSS feed parsing module for extracting recent content from RSS/Atom feeds.
Provides efficient content discovery with built-in date filtering.
"""

import feedparser
import ssl
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from src.logger import logger

# Note: SSL certificate verification
# If you get SSL errors on macOS, install certificates:
# /Applications/Python\ 3.14/Install\ Certificates.command
# Or: pip install --upgrade certifi


class RSSReader:
    """RSS/Atom feed reader with date filtering capabilities."""
    
    def __init__(self, freshness_days: int = 7):
        """
        Initialize RSS reader.
        
        Args:
            freshness_days: Only fetch entries from last N days (default: 7)
        """
        self.freshness_days = freshness_days
        logger.info("RSS reader initialized", freshness_days=freshness_days)
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse various date formats from RSS feeds.
        
        Args:
            date_string: Date string from feed
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_string:
            return None
        
        try:
            # feedparser provides parsed_date as time.struct_time
            # Convert to datetime
            if isinstance(date_string, str):
                return date_parser.parse(date_string)
            return None
        except (ValueError, AttributeError, TypeError) as e:
            logger.debug("Failed to parse date", date_string=date_string, error=str(e))
            return None
    
    def _is_recent(self, published_date: Optional[datetime]) -> bool:
        """
        Check if content is recent based on freshness threshold.
        
        Args:
            published_date: Published datetime
            
        Returns:
            True if content is recent enough
        """
        if not published_date:
            # If no date, include it (will get lower freshness score in processor)
            return True
        
        cutoff = datetime.now() - timedelta(days=self.freshness_days)
        
        # Handle timezone-aware dates
        if published_date.tzinfo:
            cutoff = cutoff.replace(tzinfo=published_date.tzinfo)
        
        is_recent = published_date >= cutoff
        
        logger.debug("Checking content freshness",
                    published=published_date.isoformat() if published_date else None,
                    is_recent=is_recent,
                    age_days=(datetime.now().replace(tzinfo=published_date.tzinfo if published_date and published_date.tzinfo else None) - published_date).days if published_date else None)
        
        return is_recent
    
    def fetch_feed(self, feed_url: str, only_recent: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS/Atom feed.
        
        Args:
            feed_url: URL of the RSS/Atom feed
            only_recent: Whether to filter by freshness_days threshold
            
        Returns:
            List of feed entries with standardized fields
        """
        logger.info("Fetching RSS feed", url=feed_url, only_recent=only_recent)
        
        try:
            # Parse feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                # Feed has issues but might still be parseable
                logger.warning("RSS feed has parsing issues",
                             url=feed_url,
                             exception=str(feed.bozo_exception) if hasattr(feed, 'bozo_exception') else None)
            
            if not feed.entries:
                logger.warning("No entries found in RSS feed", url=feed_url)
                return []
            
            logger.info("RSS feed parsed successfully",
                       url=feed_url,
                       total_entries=len(feed.entries),
                       feed_title=feed.feed.get('title', 'Unknown'))
            
            # Process entries
            entries = []
            
            for entry in feed.entries:
                try:
                    # Extract published date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        # Convert struct_time to datetime
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        published_date = self._parse_date(entry.published)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6])
                    elif hasattr(entry, 'updated'):
                        published_date = self._parse_date(entry.updated)
                    
                    # Filter by date if requested
                    if only_recent and not self._is_recent(published_date):
                        continue
                    
                    # Extract entry data
                    entry_data = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'published_at': published_date,
                        'author': entry.get('author', ''),
                        'tags': [tag.get('term', '') for tag in entry.get('tags', [])],
                        'content': self._extract_content(entry),
                        'feed_url': feed_url,
                        'feed_title': feed.feed.get('title', '')
                    }
                    
                    entries.append(entry_data)
                    
                except Exception as e:
                    logger.error("Error processing RSS entry",
                               entry_title=entry.get('title', 'Unknown'),
                               error=str(e))
                    continue
            
            logger.info("RSS feed processing completed",
                       url=feed_url,
                       total_entries=len(feed.entries),
                       recent_entries=len(entries),
                       filtered_out=len(feed.entries) - len(entries))
            
            return entries
            
        except Exception as e:
            logger.error("Failed to fetch RSS feed", url=feed_url, error=str(e))
            return []
    
    def _extract_content(self, entry: Any) -> str:
        """
        Extract full content from RSS entry (prefer content over summary).
        
        Args:
            entry: Feed entry object
            
        Returns:
            Content text
        """
        # Try to get full content first
        if hasattr(entry, 'content') and entry.content:
            # content is usually a list of content objects
            if isinstance(entry.content, list) and len(entry.content) > 0:
                return entry.content[0].get('value', '')
        
        # Fallback to summary/description
        if hasattr(entry, 'summary'):
            return entry.summary
        
        if hasattr(entry, 'description'):
            return entry.description
        
        return ''
    
    def get_recent_articles(self, feed_url: str) -> List[str]:
        """
        Get URLs of recent articles from RSS feed.
        Convenience method for getting just the URLs.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of article URLs
        """
        entries = self.fetch_feed(feed_url, only_recent=True)
        urls = [entry['link'] for entry in entries if entry.get('link')]
        
        logger.info("Extracted recent article URLs",
                   feed_url=feed_url,
                   article_count=len(urls))
        
        return urls
    
    def check_feed_availability(self, feed_url: str) -> bool:
        """
        Check if RSS feed is available and valid.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            True if feed is accessible and valid
        """
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logger.warning("Feed has issues",
                             url=feed_url,
                             exception=str(feed.bozo_exception))
                return False
            
            if not feed.entries:
                logger.warning("Feed has no entries", url=feed_url)
                return False
            
            logger.info("Feed is valid",
                       url=feed_url,
                       entries=len(feed.entries))
            return True
            
        except Exception as e:
            logger.error("Feed check failed", url=feed_url, error=str(e))
            return False


# Global RSS reader instance
rss_reader = RSSReader()
