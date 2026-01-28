"""
Test script for RSS feed functionality.
Validates RSS reader and feed availability.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rss_reader import rss_reader
from src.logger import logger


# Test RSS feeds
TEST_FEEDS = [
    ('OpenAI News', 'https://openai.com/news/rss/'),
    ('Google Research', 'https://research.google/blog/feed/'),
    ('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/feed/'),
    ('VentureBeat AI', 'https://venturebeat.com/category/ai/feed/'),
    ('Microsoft Research', 'https://www.microsoft.com/en-us/research/blog/feed/'),
]


def test_feed(name: str, url: str):
    """Test a single RSS feed."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    try:
        # Check availability
        print("\n1. Checking feed availability...")
        is_valid = rss_reader.check_feed_availability(url)
        
        if not is_valid:
            print(f"❌ Feed is not valid or unavailable")
            return False
        
        print(f"✅ Feed is valid and accessible")
        
        # Fetch recent entries
        print(f"\n2. Fetching recent entries (last {rss_reader.freshness_days} days)...")
        entries = rss_reader.fetch_feed(url, only_recent=True)
        
        if not entries:
            print(f"⚠️  No recent entries found")
            return True
        
        print(f"✅ Found {len(entries)} recent entries")
        
        # Show sample entries
        print(f"\n3. Sample entries:")
        for i, entry in enumerate(entries[:3], 1):
            print(f"\n   {i}. {entry['title']}")
            print(f"      Published: {entry['published_at']}")
            print(f"      Link: {entry['link']}")
            if entry.get('summary'):
                summary = entry['summary'][:100] + '...' if len(entry['summary']) > 100 else entry['summary']
                print(f"      Summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing feed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all RSS tests."""
    print("\n" + "="*80)
    print("RSS FEED TESTING SCRIPT")
    print("="*80)
    print(f"\nTesting {len(TEST_FEEDS)} RSS feeds...")
    print(f"Freshness threshold: {rss_reader.freshness_days} days")
    
    results = []
    
    for name, url in TEST_FEEDS:
        success = test_feed(name, url)
        results.append((name, success))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    success_count = sum(1 for _, success in results if success)
    fail_count = len(results) - success_count
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {len(results)} feeds")
    print(f"Passed: {success_count}")
    print(f"Failed: {fail_count}")
    print("="*80 + "\n")
    
    if fail_count == 0:
        print("🎉 All RSS feeds tested successfully!")
        return 0
    else:
        print(f"⚠️  {fail_count} feed(s) failed testing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
