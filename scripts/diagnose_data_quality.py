"""
Diagnostic script to analyze data quality in the Supabase database.
Helps identify archive pages, duplicate content, source diversity issues, etc.
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import db
from src.logger import logger


def analyze_scraped_content():
    """Analyze all scraped content for quality issues."""
    
    print("\n" + "="*80)
    print("🔍 DATA QUALITY DIAGNOSTIC REPORT")
    print("="*80)
    
    # Get all sources
    sources = db.get_active_sources()
    all_sources = db.client.table("content_sources").select("*").execute()
    
    print(f"\n📊 SOURCES OVERVIEW")
    print(f"  Total sources configured: {len(all_sources.data) if all_sources.data else 0}")
    print(f"  Active sources: {len(sources)}")
    print(f"  Inactive sources: {len(all_sources.data) - len(sources) if all_sources.data else 0}")
    
    # Analyze content by source
    print(f"\n📁 CONTENT BY SOURCE")
    print("-" * 80)
    
    for source in sources:
        content_query = db.client.table("scraped_content")\
            .select("*")\
            .eq("source_id", str(source.id))\
            .execute()
        
        content_items = content_query.data if content_query.data else []
        
        # Count processed vs unprocessed
        processed = len([c for c in content_items if c.get('is_processed')])
        unprocessed = len([c for c in content_items if not c.get('is_processed')])
        
        # Count archive pages (if marked)
        archive_pages = len([c for c in content_items 
                           if c.get('metadata', {}).get('marked_as_processed') == 'archive_page'])
        
        # Check URL patterns
        category_urls = len([c for c in content_items if '/category/' in c.get('url', '')])
        page_urls = len([c for c in content_items if '/page/' in c.get('url', '')])
        archive_urls = len([c for c in content_items if '/archive' in c.get('url', '')])
        
        total = len(content_items)
        status_icon = "✅" if total > 0 else "❌"
        rss_icon = "📰" if source.metadata.get('has_rss') else "🌐"
        
        print(f"\n{status_icon} {rss_icon} {source.name}")
        print(f"    Type: {source.source_type}")
        print(f"    URL: {source.url}")
        print(f"    Total scraped: {total}")
        print(f"    └─ Processed: {processed}")
        print(f"    └─ Unprocessed: {unprocessed}")
        
        if archive_pages > 0 or category_urls > 0 or page_urls > 0 or archive_urls > 0:
            print(f"    ⚠️  Quality Issues:")
            if archive_pages > 0:
                print(f"       └─ Marked archive pages: {archive_pages}")
            if category_urls > 0:
                print(f"       └─ Category URLs: {category_urls}")
            if page_urls > 0:
                print(f"       └─ Pagination URLs: {page_urls}")
            if archive_urls > 0:
                print(f"       └─ Archive URLs: {archive_urls}")
    
    # Overall statistics
    all_content_query = db.client.table("scraped_content").select("*").execute()
    all_content = all_content_query.data if all_content_query.data else []
    
    print(f"\n" + "="*80)
    print(f"📈 OVERALL STATISTICS")
    print("="*80)
    
    total_items = len(all_content)
    processed_items = len([c for c in all_content if c.get('is_processed')])
    unprocessed_items = len([c for c in all_content if not c.get('is_processed')])
    
    # Quality issues
    archive_marked = len([c for c in all_content 
                         if c.get('metadata', {}).get('marked_as_processed') == 'archive_page'])
    category_urls_total = len([c for c in all_content if '/category/' in c.get('url', '')])
    page_urls_total = len([c for c in all_content if '/page/' in c.get('url', '')])
    archive_urls_total = len([c for c in all_content if '/archive' in c.get('url', '')])
    short_content = len([c for c in all_content if len(c.get('content', '')) < 500])
    
    print(f"\n  Total items: {total_items}")
    print(f"    ├─ Processed: {processed_items} ({processed_items*100//total_items if total_items > 0 else 0}%)")
    print(f"    └─ Unprocessed: {unprocessed_items} ({unprocessed_items*100//total_items if total_items > 0 else 0}%)")
    
    print(f"\n  🗑️  Quality Issues Found:")
    print(f"    ├─ Archive pages (marked): {archive_marked}")
    print(f"    ├─ Category URLs: {category_urls_total}")
    print(f"    ├─ Pagination URLs: {page_urls_total}")
    print(f"    ├─ Archive URLs: {archive_urls_total}")
    print(f"    └─ Short content (<500 chars): {short_content}")
    
    total_bad = archive_marked + category_urls_total + page_urls_total + archive_urls_total + short_content
    if total_bad > 0:
        print(f"\n  ⚠️  TOTAL QUALITY ISSUES: {total_bad} items ({total_bad*100//total_items if total_items > 0 else 0}% of all content)")
    
    # Source diversity
    print(f"\n" + "="*80)
    print(f"🌈 SOURCE DIVERSITY")
    print("="*80)
    
    source_counts = {}
    for item in all_content:
        source_id = item.get('source_id')
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
    
    # Map source IDs to names
    source_map = {str(s.id): s.name for s in sources}
    
    print(f"\n  Content distribution:")
    sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
    for source_id, count in sorted_sources:
        source_name = source_map.get(source_id, f"Unknown ({source_id})")
        percentage = count * 100 // total_items if total_items > 0 else 0
        bar = "█" * (percentage // 2)  # Visual bar
        print(f"    {source_name:30s} {count:4d} ({percentage:2d}%) {bar}")
    
    # Sources with no content
    sources_with_no_content = [s.name for s in sources if str(s.id) not in source_counts]
    if sources_with_no_content:
        print(f"\n  ❌ Sources with NO content scraped:")
        for name in sources_with_no_content:
            print(f"    • {name}")
    
    # Recent content
    print(f"\n" + "="*80)
    print(f"📅 FRESHNESS ANALYSIS")
    print("="*80)
    
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    
    # Count by age
    last_24h = len([c for c in all_content 
                    if datetime.fromisoformat(c.get('scraped_at').replace('Z', '+00:00')) > now - timedelta(hours=24)])
    last_7d = len([c for c in all_content 
                   if datetime.fromisoformat(c.get('scraped_at').replace('Z', '+00:00')) > now - timedelta(days=7)])
    last_30d = len([c for c in all_content 
                    if datetime.fromisoformat(c.get('scraped_at').replace('Z', '+00:00')) > now - timedelta(days=30)])
    older = total_items - last_30d
    
    print(f"\n  Content by age (scraped_at):")
    print(f"    Last 24 hours: {last_24h}")
    print(f"    Last 7 days:   {last_7d}")
    print(f"    Last 30 days:  {last_30d}")
    print(f"    Older:         {older}")
    
    # Recommendations
    print(f"\n" + "="*80)
    print(f"💡 RECOMMENDATIONS")
    print("="*80)
    
    if total_bad > total_items * 0.2:  # More than 20% bad data
        print(f"\n  ⚠️  HIGH PERCENTAGE OF LOW-QUALITY DATA ({total_bad*100//total_items if total_items > 0 else 0}%)")
        print(f"      Action: Run scripts/clean_bad_data.sql in Supabase")
    
    if sources_with_no_content:
        print(f"\n  ⚠️  {len(sources_with_no_content)} SOURCES HAVE NO CONTENT")
        print(f"      Action: Run 'python main.py scrape' to scrape fresh content")
    
    if last_24h < 10:
        print(f"\n  ⚠️  VERY LITTLE FRESH CONTENT (last 24h: {last_24h})")
        print(f"      Action: Run 'python main.py scrape' to get latest articles")
    
    # Check for diversity
    if len(source_counts) < len(sources) * 0.5:  # Less than 50% of sources represented
        print(f"\n  ⚠️  LOW SOURCE DIVERSITY ({len(source_counts)}/{len(sources)} sources have content)")
        print(f"      Action: Ensure all sources are properly configured and scraped")
    
    # Check for single-source dominance
    if sorted_sources and sorted_sources[0][1] > total_items * 0.5:  # One source > 50%
        dominant_source = source_map.get(sorted_sources[0][0], "Unknown")
        print(f"\n  ⚠️  SINGLE SOURCE DOMINANCE: {dominant_source} has {sorted_sources[0][1]*100//total_items if total_items > 0 else 0}% of all content")
        print(f"      Action: Run fresh scrape to diversify content sources")
    
    print(f"\n" + "="*80)
    print(f"✅ Diagnostic complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        analyze_scraped_content()
    except Exception as e:
        logger.error("Diagnostic failed", error=str(e))
        print(f"\n❌ Diagnostic failed: {e}")
        sys.exit(1)
