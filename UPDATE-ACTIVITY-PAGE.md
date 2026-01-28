# Activity Page Update

Replace the entire `frontend/src/app/activity/page.tsx` with content that shows scraped articles instead of Opus jobs.

Key changes:
1. Call `api.getScrapedContent()` instead of `api.getActivity()`
2. Show article title, URL, source name
3. Add "Send to Opus" button for each unprocessed article
4. Show "Processed" / "Unprocessed" badge
5. Handle individual processing with loading states

The page should display a list of scraped content with ability to process each item individually to Opus.
