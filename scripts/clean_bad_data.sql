-- Clean up bad scraped data (archive/category pages)
-- Run this in Supabase SQL Editor

-- Mark archive/category/pagination pages as processed
-- These aren't real articles and cause workflow failures
UPDATE scraped_content 
SET is_processed = true,
    metadata = metadata || '{"marked_as_processed": "archive_page", "reason": "not_actual_article"}'::jsonb
WHERE 
    -- URLs containing pagination or category indicators
    url LIKE '%/page/%' 
    OR url LIKE '%/category/%'
    OR url LIKE '%/archives/%'
    -- Titles indicating archive pages
    OR title LIKE '%Page % of %'
    OR title LIKE '%Archives%'
    OR title LIKE '%Category:%'
    -- Empty or very short content
    OR LENGTH(content) < 500;

-- Show what was marked
SELECT 
    COUNT(*) as total_marked,
    COUNT(DISTINCT source_id) as sources_affected
FROM scraped_content
WHERE metadata->>'marked_as_processed' = 'archive_page';

-- Show remaining unprocessed content
SELECT 
    COUNT(*) as remaining_unprocessed,
    MIN(scraped_at) as oldest,
    MAX(scraped_at) as newest
FROM scraped_content
WHERE is_processed = false;
