# JSearch API Setup Guide

JSearch is a job aggregator API that searches across:
- **LinkedIn Jobs**
- **Indeed**
- **Glassdoor**
- **ZipRecruiter**
- **Google Jobs**

This means you'll get jobs from **Amazon, Google, Microsoft, Meta, Netflix, and all major companies** automatically!

## Quick Setup (5 minutes)

### 1. Get Free API Key

1. Go to [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Click "Sign Up" (free account)
3. Click "Subscribe to Test" 
4. Select **Free tier** (1,000 requests/month - plenty for personal use)
5. Copy your API key

### 2. Add to Environment

```bash
# In apps/portal-python/.env
JSEARCH_API_KEY=your_rapidapi_key_here
```

### 3. Restart Backend

```bash
cd apps/portal-python
pnpm dev
```

That's it! The auto-apply feature will now search JSearch automatically.

## What You Get

### Without JSearch:
- Remotive (remote tech jobs)
- Arbeitnow (EU/US remote jobs)
- ~50-100 results

### With JSearch:
- **Everything above, PLUS:**
- LinkedIn jobs (all companies including FAANG)
- Indeed jobs
- Glassdoor jobs
- ZipRecruiter jobs
- ~100-200 results per search
- Better coverage of Amazon, Google, Microsoft, etc.

## Free Tier Limits

- **1,000 requests/month** (free forever)
- Each search = 1 request
- ~30 applications/day without hitting limits
- More than enough for personal job hunting

## Example Search Results

When you search for "Senior Software Engineer":

**Before (just Remotive/Arbeitnow):**
- 20-30 remote-only positions

**After (with JSearch):**
- 100+ positions including:
  - Amazon - Seattle, Remote
  - Google - Mountain View, Remote
  - Microsoft - Redmond, Remote
  - Meta - Menlo Park, Remote
  - Netflix - Los Gatos, Remote
  - Plus all the remote startups

## Testing

```bash
# Test JSearch integration
curl "http://localhost:8000/api/jobs/auto-apply" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "Senior Software Engineer Amazon",
    "location": "Remote",
    "max_applications": 5
  }'
```

Check the logs - you should see:
```
JSearch: Found X jobs (sources: LinkedIn, Indeed, Glassdoor, ZipRecruiter)
```

## Troubleshooting

### "JSearch API key not configured" warning
- Check `.env` file has `JSEARCH_API_KEY=...`
- Restart backend after adding key
- Make sure no spaces around the `=`

### Rate limit errors
- Free tier: 1,000/month
- Upgrade to Basic ($9.99/month) for 10,000/month if needed
- Or space out your searches

### No Amazon jobs showing up
- Try more specific keywords: "Software Engineer AWS" or "SDE Amazon"
- Amazon posts mostly on LinkedIn/Indeed which JSearch covers

## Alternative: Just Search Amazon

If you only want Amazon jobs, you can add this filter in the UI or use keywords like:
- "Software Engineer Amazon AWS"
- "SDE Amazon"
- "Backend Engineer Amazon Web Services"

The JSearch API will automatically filter results to match your keywords including company names.
