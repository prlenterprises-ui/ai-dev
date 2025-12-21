# 24-Hour Rate Limiting for Job Search

## ✅ What Was Implemented

Added a **24-hour cooldown** between job searches to protect your limited API quota (200 calls/month).

### Backend Changes

1. **New API Endpoint**: `GET /api/jobs/search-status`
   - Returns whether search is allowed
   - Shows hours since last search
   - Shows hours until next search is allowed
   - Tracks total API calls used

2. **Tracking System**: `.jsearch_tracking.json`
   - Automatically updated after each search
   - Stores timestamp of last run
   - Tracks total API calls used
   - Maintains history of all searches

3. **Auto-Update Tracking**: Modified `POST /api/jobs/find`
   - Updates tracking file after successful search
   - Records timestamp and API calls used

### Frontend Changes

1. **Status Check**: Added `checkSearchStatus()` function
   - Runs on page load
   - Checks if 24 hours have passed since last search

2. **Disabled Button**: "Find Jobs" button
   - Disabled if less than 24 hours since last search
   - Shows tooltip with hours remaining
   - Visual feedback (opacity reduced when disabled)

3. **Warning Banner**: Yellow alert appears when cooldown active
   - Shows remaining time
   - Displays last search time
   - Explains the cooldown

## 🎯 How It Works

### First Search
```
User clicks "Find Jobs"
  ↓
Search runs normally
  ↓
Tracking saved: { last_run: "2025-12-21T10:00:00", api_calls: 3 }
  ↓
Button becomes available again in 24 hours
```

### Within 24 Hours
```
User loads page
  ↓
Frontend checks: GET /api/jobs/search-status
  ↓
Response: { can_search: false, hours_until_next: 18.5 }
  ↓
Button disabled + warning banner shown
```

### After 24 Hours
```
User loads page
  ↓
Frontend checks: GET /api/jobs/search-status
  ↓
Response: { can_search: true, hours_since_last_run: 24.2 }
  ↓
Button enabled + ready to search
```

## 📊 Benefits

### API Conservation
- **Before**: Could accidentally search multiple times per day (3 calls × multiple runs = quota exhausted fast)
- **After**: Maximum 1 search per 24 hours = ~30 searches per month = 90 API calls
- **Savings**: 110 API calls per month reserved for manual/targeted searches

### User Experience
- Clear feedback when search is not allowed
- Shows exactly how long to wait
- Prevents frustration from "why isn't this working?"
- Displays API usage tracking

## 🔍 API Response Examples

### Can Search
```json
{
  "can_search": true,
  "last_run": "2025-12-21T10:00:00",
  "hours_since_last_run": 25.3,
  "hours_until_next": 0,
  "total_api_calls": 15,
  "runs_count": 5,
  "message": "Ready to search! Last search was 25.3 hours ago."
}
```

### Cannot Search
```json
{
  "can_search": false,
  "last_run": "2025-12-21T10:00:00",
  "hours_since_last_run": 12.5,
  "hours_until_next": 11.5,
  "total_api_calls": 18,
  "runs_count": 6,
  "message": "Please wait 11.5 more hours. Last search was 12.5 hours ago."
}
```

## 🎨 UI Changes

### Button States

**Enabled** (can search):
```jsx
<button className="bg-gradient-to-r from-electric-500 to-electric-600">
  Find Jobs
</button>
```

**Disabled** (cooldown active):
```jsx
<button 
  disabled 
  className="opacity-50 cursor-not-allowed"
  title="Wait 11.5 hours"
>
  Find Jobs
</button>
```

### Warning Banner (shows when disabled)
```
⏰ Search Cooldown Active
   Please wait 11.5 more hours. Last search was 12.5 hours ago.
   Last search: 12/21/2025, 10:00:00 AM
```

## 🔧 Configuration

Want to change the cooldown period? Edit this value:

**Backend** ([jobs_routes.py](apps/portal-python/apis/jobs_routes.py)):
```python
# Line ~50: Change 24 to desired hours
can_search = hours_since >= 24  # <-- Change this number
hours_until_next = max(0, 24 - hours_since)  # <-- And this one
```

Examples:
- `12` = 12-hour cooldown (2 searches per day)
- `48` = 48-hour cooldown (every 2 days)
- `168` = Weekly searches

## 📁 Files Modified

1. **Backend**:
   - [apis/jobs_routes.py](apps/portal-python/apis/jobs_routes.py) - Added status endpoint and tracking
   
2. **Frontend**:
   - [pages/AutoJobApply.jsx](apps/portal-ui/src/pages/AutoJobApply.jsx) - Added status check and button disable logic

3. **Tracking File** (auto-created):
   - `.jsearch_tracking.json` - Stores search history

## 🚀 Testing

### Test the Status Endpoint
```bash
# Check current status
curl http://localhost:8000/api/jobs/search-status

# Expected response (first time)
{
  "can_search": true,
  "last_run": null,
  "message": "No previous searches. Ready to search!"
}
```

### Test After Search
```bash
# Run a search via UI, then check status again
curl http://localhost:8000/api/jobs/search-status

# Expected response (within 24 hours)
{
  "can_search": false,
  "hours_until_next": 23.5,
  "message": "Please wait 23.5 more hours..."
}
```

### Manually Reset (for testing)
```bash
# Delete tracking file to reset
rm /workspaces/ai-dev/apps/portal-python/.jsearch_tracking.json
```

## 💡 Future Enhancements

Possible improvements:
1. **Admin Override**: Allow admins to bypass cooldown
2. **Different Limits by User**: VIP users get more frequent searches
3. **API Quota Display**: Show "X/200 calls remaining this month"
4. **Countdown Timer**: Live countdown showing hours:minutes:seconds
5. **Email Notification**: Alert when cooldown expires
6. **Configurable via UI**: Change cooldown in settings page

## ✅ Summary

Your job search is now rate-limited to once per 24 hours, protecting your precious 200 API calls per month while providing clear feedback to users about when they can search again! 🎯
