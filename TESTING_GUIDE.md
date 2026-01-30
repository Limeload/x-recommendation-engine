# Quick Start & Testing Guide

## Installation & Running

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
python main.py
```
Server runs at: `http://localhost:8000`

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## Testing All New Features

### 1. ✅ Unique Tweet Content

**What to look for:**
- Each tweet has different content and emojis
- Tweets vary by persona type (Founder tweets vs Engineer tweets differ)
- Topics are different combinations in each tweet

**How to verify:**
```
Open http://localhost:3000
Scroll through feed and observe:
✓ Founder tweets: 🚀 Shipping, 💰 Fundraising, 🎯 Market insights
✓ Journalist tweets: 🚨 Breaking, 📖 Investigation, 🎬 Features
✓ Engineer tweets: ⚙️ Open source, 🧠 Architecture, ⚡ Performance tips
✓ Each tweet is unique in content
```

### 2. ✅ Username Display

**What to look for:**
- Author names displayed instead of user IDs
- Format: "Alice Founder @user_1" not "@user_1 @user_1"

**How to verify:**
```
Look at any tweet in the feed
✓ First name shows human-readable: "Alice Founder", "Bob Journalist"
✓ Handle shows as @user_0, @user_1, etc.
✓ Not showing duplicate user_1 twice
```

### 3. ✅ Real-Time "Just Now" Highlighting

**What to look for:**
- New tweets highlighted in blue background
- "🔥 just now" or "🔥 2m ago" in blue text
- Tweets older than 1 hour show normal gray timestamps
- Blue "Added to Feed" badge appears temporarily

**How to verify:**
```
Step 1: Refresh the feed (🔄 Refresh button)
Step 2: Notice first 5 tweets have:
  - Blue background (#EFF6FF)
  - Blue timestamp: "🔥 just now"
  - Badge: "📌 Added to Feed"
Step 3: Wait 3 seconds - highlighting fades away
Step 4: Adjust weights to trigger re-ranking
Step 5: New top tweets get blue highlighting again
```

### 4. ✅ Settings Applied Feedback

**What to look for:**
- "✅ Settings Applied!" message in header
- Shows for 2 seconds after saving
- Green background color
- Checkmark icon

**How to verify:**
```
Step 1: Click "⚙️ Settings" button
Step 2: Adjust any weight slider (e.g., increase Recency to 0.4)
Step 3: Click "💾 Save Changes"
Step 4: Observe header shows: "✅ Settings Applied!"
Step 5: Message disappears after 2 seconds
Step 6: Feed re-ranks with new weights
Step 7: First 5 tweets highlighted as "new"
```

### 5. ✅ Last Update Time

**What to look for:**
- "Updated: HH:MM:SS" shown in header
- Updates when weights are saved or refresh clicked
- Displays in gray text

**How to verify:**
```
Notice header shows timestamp
✓ When page loads: "Updated: 10:30:45"
✓ Click Refresh: timestamp updates
✓ Save settings: timestamp updates to save time
```

### 6. ✅ Better Settings Panel

**What to look for:**
- Blue accent color scheme
- Color-coded preset buttons
- Better visual hierarchy
- Shows valid/invalid weight status

**How to verify:**
```
Click "⚙️ Settings"
Observe panel shows:
✓ Blue styling (not gray)
✓ Colored preset buttons:
  - Latest 🔵 (blue)
  - Trending 🔴 (red)
  - Personal 🟣 (purple)
  - Balanced 🟠 (amber)
✓ Weight sum shows: "✅ Valid configuration"
✓ "💾 Save Changes" button (not just "Save")
```

---

## Test Scenarios

### Scenario A: Settings Change Flow

```
1. Open http://localhost:3000
2. Notice timestamp in header (e.g., "Updated: 10:30:45")
3. Click "⚙️ Settings"
4. Drag "Recency" slider to 0.5 (increase freshness preference)
5. Click "💾 Save Changes"
6. Observe:
   ✓ Header shows "✅ Settings Applied!" (2 seconds)
   ✓ Last update time changes
   ✓ First 5 tweets get blue highlight + "📌 Added to Feed"
   ✓ Feed re-ranks based on new weights
   ✓ Timestamps show relative times (just now, 2h ago, etc.)
7. Close settings panel
8. Wait 3 seconds - blue highlighting fades
9. Select different user from dropdown
10. Repeat process - each user has independent weights
```

### Scenario B: Timestamp Verification

```
1. Look at feed - check timestamps on different tweets
2. Tweets from last hour should show: "🔥 just now" to "🔥 59m ago"
3. Tweets from 2-24 hours ago should show: "Xh ago"
4. Tweets from older than 24 hours should show: "Xd ago"
5. Very old tweets show: "Jan 25, 2026"
```

### Scenario C: Persona-Specific Content

```
Choose different users from dropdown:
✓ Founder tweets focus on: shipping, fundraising, growth
✓ Journalist tweets focus on: investigations, features, breaking news
✓ Engineer tweets focus on: open source, performance, architecture
✓ Investor tweets focus on: market analysis, returns, portfolio
✓ Each has unique emoji signature and tone
```

### Scenario D: Multiple Weight Adjustments

```
1. Try "Latest" preset (high recency)
2. Save - see different tweet ordering
3. Try "Trending" preset (high popularity)
4. Save - see engagement-focused ordering
5. Try "Personal" preset (high topic relevance)
6. Save - see interest-aligned tweets
7. Try "Balanced" preset (equal weights)
8. Save - see diverse mix
```

---

## Expected Results

### Feed Display
- [ ] Each tweet has unique, diverse content
- [ ] Author names display correctly (not user IDs)
- [ ] Topics shown as blue pills
- [ ] Score shown with visual bar
- [ ] Explanation available on click

### New Tweets
- [ ] Top 5 tweets after refresh/update have blue background
- [ ] "Added to Feed" badge visible
- [ ] Blue "just now" timestamp
- [ ] Highlighting fades after 3 seconds

### Settings Panel
- [ ] Blue color scheme
- [ ] Colored preset buttons
- [ ] Weight sum shows status (✅ or ⚠️)
- [ ] Sliders work smoothly
- [ ] Save button is enabled only when valid

### Header
- [ ] Settings Applied indicator shows on save
- [ ] Disappears after 2 seconds
- [ ] Update timestamp is current
- [ ] Emoji buttons enhance visual appeal

### Overall UX
- [ ] Feels responsive and modern
- [ ] Clear feedback on actions
- [ ] Easy to understand what's happening
- [ ] No confusing duplicate information
- [ ] Professional appearance

---

## Troubleshooting

### Backend Issues
```
Error: ModuleNotFoundError
Solution: Make sure you're running from backend directory
cd backend && python main.py

Error: Port 8000 already in use
Solution: Kill existing process or use different port
lsof -i :8000
kill -9 <PID>
```

### Frontend Issues
```
Error: Cannot find module
Solution: Install dependencies
cd frontend && npm install

Error: Module is not found
Solution: Clear Next.js cache
cd frontend && rm -rf .next && npm run dev
```

### API Connection Issues
```
Error: Failed to fetch users
Solution: Check backend is running on :8000
Check NEXT_PUBLIC_API_URL env var points to http://localhost:8000

Error: CORS errors
Solution: Backend has CORS enabled for all origins
If still issues, check main.py for CORSMiddleware
```

---

## Demo Tips

### Impressive Features to Show
1. **Diversity**: Show how different personas have completely different tweet styles
2. **Real-time**: Change weights → instant re-ranking with visual feedback
3. **Transparency**: Click "Show Explanation" to see why tweets ranked that way
4. **Personalization**: Switch users → completely different feed based on interests
5. **Polish**: Point out professional styling, relative timestamps, success indicators

### Quick Demo Flow (2 minutes)
```
1. Load page - show diverse tweet content
2. Point out author names vs old user ID display
3. Highlight blue "just now" timestamps
4. Click Settings
5. Drag one slider dramatically (e.g., Recency to 0.7)
6. Click Save
7. Show "Settings Applied!" notification
8. Point out feed re-ranked completely
9. Notice top tweets highlighted in blue
10. Click "Show Explanation" to reveal ranking logic
```

---

## Performance Notes

- Backend loads 50 tweets with realistic engagement metrics
- Frontend renders smoothly with large lists
- Settings changes apply instantly
- No API latency concerns (all in-memory)
- Highlighting animations are smooth (CSS-based)

---

## Files to Review

- **Backend**: `backend/simulation/synthetic_data.py` - Tweet templates
- **Frontend**: `frontend/components/TweetCard.tsx` - Display logic
- **Frontend**: `frontend/app/page.tsx` - Main page state management
- **Frontend**: `frontend/components/TuningDashboard.tsx` - Settings styling

