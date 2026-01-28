"""
Script to insert content sources into Supabase database.
Run this once to populate the content_sources table with all configured sources.
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import db
from src.models import ContentSource
from src.logger import logger


# Define all content sources with metadata
CONTENT_SOURCES = [
    # Research Papers
    {
        'url': 'https://huggingface.co/papers',
        'name': 'Hugging Face Papers',
        'source_type': 'research_papers',
        'scraping_frequency_minutes': 180,  # 3 hours
        'rss_feed_url': None,  # No RSS, use web scraping
        'metadata': {
            'description': 'Latest ML/AI research papers',
            'priority': 'high',
            'language': 'en'
        }
    },
    {
        'url': 'https://paperswithcode.com/',
        'name': 'Papers with Code',
        'source_type': 'research_papers',
        'scraping_frequency_minutes': 180,
        'rss_feed_url': None,
        'metadata': {
            'description': 'Research papers with implementation code',
            'priority': 'high',
            'language': 'en'
        }
    },
    
    # AI News Aggregators
    {
        'url': 'https://alphasignal.ai/',
        'name': 'Alpha Signal',
        'source_type': 'news_aggregator',
        'scraping_frequency_minutes': 120,  # 2 hours
        'rss_feed_url': None,
        'metadata': {
            'description': 'AI news and insights aggregator',
            'priority': 'medium',
            'language': 'en'
        }
    },
    {
        'url': 'https://www.therundown.ai/archive',
        'name': 'The Rundown AI',
        'source_type': 'news_aggregator',
        'scraping_frequency_minutes': 120,
        'rss_feed_url': 'https://www.therundown.ai/rss/',  # May have RSS
        'metadata': {
            'description': 'Daily AI newsletter archive',
            'priority': 'medium',
            'language': 'en'
        }
    },
    {
        'url': 'https://bensbites.beehiiv.com/archive',
        'name': "Ben's Bites",
        'source_type': 'news_aggregator',
        'scraping_frequency_minutes': 120,
        'rss_feed_url': 'https://bensbites.beehiiv.com/feed',  # Beehiiv provides RSS
        'metadata': {
            'description': 'AI news and tools newsletter',
            'priority': 'high',
            'language': 'en'
        }
    },
    {
        'url': 'https://tldr.tech/ai/archives',
        'name': 'TLDR AI',
        'source_type': 'news_aggregator',
        'scraping_frequency_minutes': 120,
        'rss_feed_url': 'https://tldr.tech/ai/rss',  # TLDR has RSS
        'metadata': {
            'description': 'AI tech newsletter archive',
            'priority': 'medium',
            'language': 'en'
        }
    },
    
    # Company Research Blogs
    {
        'url': 'https://openai.com/news/',
        'name': 'OpenAI News',
        'source_type': 'company_blog',
        'scraping_frequency_minutes': 240,  # 4 hours
        'rss_feed_url': None,  # RSS feed has XML parsing issues, use web scraping
        'metadata': {
            'description': 'Official OpenAI news and research',
            'priority': 'very_high',
            'language': 'en',
            'note': 'RSS feed malformed, using web scraping'
        }
    },
    {
        'url': 'https://research.google/blog/',
        'name': 'Google Research Blog',
        'source_type': 'company_blog',
        'scraping_frequency_minutes': 240,
        'rss_feed_url': None,  # RSS feed has XML parsing issues, use web scraping
        'metadata': {
            'description': 'Google AI and ML research updates',
            'priority': 'very_high',
            'language': 'en',
            'note': 'RSS feed malformed, using web scraping'
        }
    },
    {
        'url': 'https://www.anthropic.com/news',
        'name': 'Anthropic News',
        'source_type': 'company_blog',
        'scraping_frequency_minutes': 240,
        'rss_feed_url': 'https://www.anthropic.com/news/rss',  # May have RSS
        'metadata': {
            'description': 'Anthropic AI research and updates',
            'priority': 'very_high',
            'language': 'en'
        }
    },
    {
        'url': 'https://www.microsoft.com/en-us/research/blog/',
        'name': 'Microsoft Research Blog',
        'source_type': 'company_blog',
        'scraping_frequency_minutes': 240,
        'rss_feed_url': 'https://www.microsoft.com/en-us/research/blog/feed/',  # Microsoft has RSS
        'metadata': {
            'description': 'Microsoft AI and research blog',
            'priority': 'high',
            'language': 'en'
        }
    },
    
    # Tech News (one already exists - TechCrunch)
    {
        'url': 'https://techcrunch.com/category/artificial-intelligence/',
        'name': 'TechCrunch AI',
        'source_type': 'tech_news',
        'scraping_frequency_minutes': 60,
        'rss_feed_url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'metadata': {
            'description': 'TechCrunch AI news and coverage',
            'priority': 'high',
            'language': 'en'
        }
    },
    {
        'url': 'https://venturebeat.com/category/ai/',
        'name': 'VentureBeat AI',
        'source_type': 'tech_news',
        'scraping_frequency_minutes': 60,
        'rss_feed_url': None,  # RSS feed has encoding issues, use web scraping
        'metadata': {
            'description': 'VentureBeat AI news and analysis',
            'priority': 'high',
            'language': 'en',
            'note': 'RSS encoding mismatch, using web scraping'
        }
    },
]


def insert_sources():
    """Insert all content sources into database."""
    logger.info("Starting content source insertion",
               total_sources=len(CONTENT_SOURCES))
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for source_data in CONTENT_SOURCES:
        try:
            url = source_data['url']
            
            # Check if source already exists
            existing = db.get_source_by_url(url)
            
            if existing:
                logger.info("Source already exists, skipping",
                           name=source_data['name'],
                           url=url)
                skip_count += 1
                continue
            
            # Extract RSS feed URL from metadata if present
            rss_feed_url = source_data.pop('rss_feed_url', None)
            
            # Add RSS feed to metadata if available
            if rss_feed_url:
                source_data['metadata']['rss_feed_url'] = rss_feed_url
                source_data['metadata']['has_rss'] = True
            else:
                source_data['metadata']['has_rss'] = False
            
            # Create ContentSource model
            source = ContentSource(**source_data)
            
            # Insert into database
            source_id = db.insert_content_source(source)
            
            if source_id:
                logger.info("Successfully inserted source",
                           name=source.name,
                           url=url,
                           source_id=str(source_id),
                           has_rss=source_data['metadata']['has_rss'])
                success_count += 1
            else:
                logger.error("Failed to insert source (no ID returned)",
                           name=source.name,
                           url=url)
                error_count += 1
                
        except Exception as e:
            logger.error("Error inserting source",
                       name=source_data.get('name', 'Unknown'),
                       error=str(e))
            error_count += 1
            continue
    
    logger.info("Source insertion completed",
               total=len(CONTENT_SOURCES),
               inserted=success_count,
               skipped=skip_count,
               errors=error_count)
    
    return success_count, skip_count, error_count


def verify_sources():
    """Verify all sources were inserted successfully."""
    logger.info("Verifying inserted sources")
    
    active_sources = db.get_active_sources()
    
    logger.info("Active sources in database",
               count=len(active_sources))
    
    print("\n" + "="*80)
    print("ACTIVE CONTENT SOURCES")
    print("="*80)
    
    for source in active_sources:
        rss_status = "✅ RSS" if source.metadata.get('has_rss') else "🌐 Web"
        print(f"\n{source.name}")
        print(f"  URL: {source.url}")
        print(f"  Type: {source.source_type}")
        print(f"  Method: {rss_status}")
        print(f"  Frequency: Every {source.scraping_frequency_minutes} minutes")
        if source.metadata.get('rss_feed_url'):
            print(f"  RSS Feed: {source.metadata['rss_feed_url']}")
    
    print("\n" + "="*80)
    print(f"Total Active Sources: {len(active_sources)}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Content Source Insertion Script")
    print("="*80)
    print(f"Inserting {len(CONTENT_SOURCES)} content sources into Supabase...")
    print("="*80 + "\n")
    
    try:
        # Insert sources
        success, skipped, errors = insert_sources()
        
        print("\n📊 Insertion Summary:")
        print(f"  ✅ Successfully inserted: {success}")
        print(f"  ⏭️  Skipped (already exist): {skipped}")
        print(f"  ❌ Errors: {errors}")
        
        # Verify
        print("\n")
        verify_sources()
        
        print("\n✅ Source insertion completed!")
        
    except Exception as e:
        logger.error("Script failed", error=str(e))
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)
