# 🎨 Complete Frontend Setup Guide
# AI-Assisted IDS Dashboard
# Muhammad Abdul Rahman (B01821977)

## 📦 ALL FRONTEND FILES

```
frontend/
├── package.json           ← npm dependencies
├── public/
│   └── index.html        ← HTML template
└── src/
    ├── index.js          ← React entry point
    ├── index.css         ← Global styles
    └── App.js            ← Main dashboard component
```

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Create Frontend Directory

```bash
cd ~/Documents/Abdul_Rahman/project/ai-ids-iot
mkdir -p frontend/src frontend/public
```

### Step 2: Copy Files

Download all frontend files and place them:

```bash
# Copy these files (download them first):
frontend/package.json          ← package.json
frontend/public/index.html     ← public_index.html  
frontend/src/index.js          ← index.js
frontend/src/index.css         ← index.css
frontend/src/App.js            ← App.js
```

### Step 3: Install Dependencies

```bash
cd frontend
npm install
```

**This installs:**
- React 18.2.0
- Material-UI 5.15.0
- Chart.js 4.4.0
- Axios 1.6.2
- And all their dependencies (~200 packages)

**Installation time:** 2-3 minutes

### Step 4: Start Development Server

```bash
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view ai-ids-dashboard in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

webpack compiled successfully
```

Your browser will automatically open to http://localhost:3000 🎉

---

## ✅ WHAT YOU'LL SEE

### Dashboard Features:

#### 1. **Top Metrics Bar** (4 colorful cards)
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Devices         │ Threats         │ Detection       │ Response Time   │
│ Monitored       │ Detected        │ Accuracy        │                 │
│    12          │     8          │   94.2%        │    380ms       │
│ (Purple)       │ (Red)          │ (Blue)         │ (Yellow)       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### 2. **Device Status Grid** (8 columns)
Shows all 12 IoT devices with:
- Green border = Safe
- Red border = Compromised
- Device name, IP, type
- Hover effect (cards lift up)

#### 3. **Live Threat Feed** (4 columns, right side)
Real-time scrolling alerts showing:
- Attack type (DDoS, PortScan, Bot)
- Confidence score
- Response action taken
- Color-coded severity

#### 4. **Three Analytics Charts** (bottom row)
- **Pie Chart:** Attack type distribution
- **Line Chart:** Detection confidence over time
- **Bar Chart:** Response actions (Alert/Isolate/Block)

---

## 🎨 Dashboard Screenshots

### Header:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️  AI-Assisted IDS Dashboard - IoT Network Security
                                    [System Online] [Refresh]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Device Cards:
```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ Smart Camera 1   ✅ │  │ Thermostat       ✅ │  │ Door Lock        ✅ │
│ IP: 192.168.1.10    │  │ IP: 192.168.1.11    │  │ IP: 192.168.1.12    │
│ Type: Camera        │  │ Type: Thermostat    │  │ Type: Lock          │
│ (Green background)  │  │ (Green background)  │  │ (Green background)  │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

### Alert Example:
```
⚠️ DDoS detected
Confidence: 96.5% | Action: BLOCK | Device: dev_001
```

---

## 🧪 TEST THE DASHBOARD

### Test 1: Open Dashboard
```
http://localhost:3000
```
You should see:
- ✅ 4 metric cards with data
- ✅ 12 device cards (all green)
- ✅ Empty threat feed (no alerts yet)
- ✅ Charts with minimal data

### Test 2: Create Test Alert (click button)
Click **"Create Test Alert"** button

You'll see:
- ✅ New alert appears in threat feed
- ✅ Threats Detected counter increases
- ✅ Charts update with new data
- ✅ Smooth animations

### Test 3: Backend Connection
If backend is NOT running, you'll see:
```
❌ Cannot connect to backend API at http://localhost:8000
   Please ensure the backend is running.
```

Start backend:
```bash
# In another terminal
cd ~/Documents/Abdul_Rahman/project/ai-ids-iot
python main_api.py
```

Refresh dashboard → Connection restored! ✅

---

## 🔄 HOW IT WORKS

### Data Flow:

```
1. Dashboard loads → Fetches from API
   ↓
2. GET /api/devices → Shows 12 IoT devices
   ↓
3. GET /api/alerts → Shows recent threats
   ↓
4. GET /api/metrics → Shows system stats
   ↓
5. Auto-refresh every 5 seconds
   ↓
6. Charts update with new data
```

### API Calls:

```javascript
// On load:
axios.get('http://localhost:8000/api/devices')
axios.get('http://localhost:8000/api/alerts?limit=20')
axios.get('http://localhost:8000/api/metrics')

// Every 5 seconds:
Refresh alerts and metrics

// Manual:
Click "Create Test Alert" → POST /api/test-alert
```

---

## 🐛 TROUBLESHOOTING

### Issue: npm install fails
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

### Issue: "Cannot connect to backend"
```bash
# Make sure backend is running
cd ~/Documents/Abdul_Rahman/project/ai-ids-iot
python main_api.py

# Check backend is accessible
curl http://localhost:8000/health
```

### Issue: Charts not displaying
```bash
# Reinstall chart.js
npm install chart.js react-chartjs-2
```

### Issue: Module not found errors
```bash
# Install missing dependencies
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install chart.js react-chartjs-2 axios
```

---

## 📊 FOR YOUR DISSERTATION

### Chapter 4: Frontend Implementation

```markdown
## 4.4 Frontend Dashboard Implementation

The web-based dashboard was developed using React 18 with Material-UI 
components to provide an intuitive real-time monitoring interface.

### Technology Stack:
- React 18.2.0: Component-based UI framework
- Material-UI 5.15.0: Professional UI component library
- Chart.js 4.4.0: Data visualization
- Axios 1.6.2: HTTP client for API communication

### Key Features:
1. **Real-time Device Monitoring:** Grid layout displaying status 
   of 12 simulated IoT devices with color-coded indicators
   
2. **Live Threat Feed:** Scrolling alert panel showing detected 
   threats with confidence scores and automated response actions

3. **Interactive Analytics:** Three chart types (Pie, Line, Bar) 
   providing visual analysis of attack patterns and system responses

4. **Auto-refresh Mechanism:** Polls backend API every 5 seconds 
   for updated data without page reload

### Implementation Highlights:
- Responsive design adapts to desktop/tablet/mobile screens
- Gradient backgrounds enhance visual appeal
- Hover effects improve user interaction
- Error handling displays connection status
- Manual refresh button for immediate updates

The dashboard successfully demonstrates real-time threat visualization
and provides security operators with actionable intelligence.
```

---

## 📸 SCREENSHOTS FOR DISSERTATION

Take these screenshots:

1. ✅ **Full dashboard view** - Show all 4 sections
2. ✅ **Metric cards** - Highlight the 4 colorful cards
3. ✅ **Device grid** - Show green safe devices
4. ✅ **Alert example** - Show threat feed with alerts
5. ✅ **Charts** - Show pie/line/bar charts with data
6. ✅ **Test alert creation** - Click button → new alert appears

---

## ✅ SUCCESS CHECKLIST

After following this guide:

- [x] Frontend folder created
- [x] All files in correct locations
- [x] npm packages installed (~200 packages)
- [x] Dashboard opens at http://localhost:3000
- [x] Backend connection successful
- [x] 12 devices displayed
- [x] Metrics cards show data
- [x] Charts render correctly
- [x] Test alert button works
- [x] Auto-refresh every 5 seconds
- [x] No console errors

---

## 🚀 FINAL SYSTEM TEST

### Test Complete System:

**Terminal 1: Backend**
```bash
cd ~/Documents/Abdul_Rahman/project/ai-ids-iot
python main_api.py
```
✅ API running on http://localhost:8000

**Terminal 2: Frontend**
```bash
cd ~/Documents/Abdul_Rahman/project/ai-ids-iot/frontend
npm start
```
✅ Dashboard opens at http://localhost:3000

**Browser:**
1. See 12 devices displayed
2. Click "Create Test Alert"
3. Watch new alert appear
4. See charts update
5. Metrics counter increases

**✅ FULL SYSTEM WORKING!** 🎉

---

## 📝 NEXT STEPS

1. ✅ Take screenshots for dissertation
2. ✅ Write Chapter 4 (Implementation)
3. ✅ Document features in Chapter 6 (Results)
4. ✅ Include dashboard in demo video
5. ✅ Show to supervisor

---

**DASHBOARD IS READY! START WITH STEP 1 NOW! 🚀**

npm install takes 2-3 minutes, then you're done! 💪
