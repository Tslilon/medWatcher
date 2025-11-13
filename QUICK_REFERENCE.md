# Harrison's Medical RAG - Quick Reference Card

## 🚀 Quick Commands

### Start the API Server

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

Server runs on: **http://localhost:8000**

---

### Check Network Setup (for Watch)

```bash
cd "/Users/maayan/medicinal rag"
python3 scripts/check_network.py
```

This will show you:
- ✅ Your Mac's IP address
- ✅ If API is running
- ✅ Configuration for Xcode

---

### Test the API (Manual)

```bash
# Health check
curl http://localhost:8000/health

# Search test
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "hyponatremia", "max_results": 3}'
```

---

### Interactive Search (CLI)

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python interactive_search.py
```

---

## 📊 What's Implemented

### ✅ Completed Phases

- [x] **Phase 1-2:** Environment & API Setup
- [x] **Phase 3:** PDF Structure Analysis (550 topics indexed)
- [x] **Phase 4:** Text Extraction & Processing
- [x] **Phase 5:** Vector Database (ChromaDB + OpenAI embeddings)
- [x] **Phase 6:** FastAPI Backend (search endpoints)
- [x] **Phase 7:** API Documentation & Testing

### ⏭️ Next Phases (Current)

- [ ] **Phase 8:** Apple Watch App Development
  - 📖 Guide: `WATCH_APP_GUIDE.md`
  - ⏱️ Time: 2-3 hours
  - 💰 Cost: Free (7-day trial)
  
- [ ] **Phase 9:** Cloud Deployment (Optional)
  - ☁️ Deploy to Google Cloud Run
  - 🌐 Access from anywhere
  - 💰 Cost: ~$5-20/month

---

## 📱 Watch App Build Steps

### Prerequisites (One-time)

1. **Install Xcode** (Mac App Store, free, ~12GB)
2. **Sign in** with Apple ID (Xcode → Preferences → Accounts)
3. **Connect iPhone** via USB cable

### Building (Every time)

1. Open Xcode project: `HarrisonsWatch.xcodeproj`
2. Select iPhone as device (top left)
3. Click Run ▶️ button
4. Wait 2-3 minutes for first build
5. App appears on Watch automatically!

### Configuration

Before building, update `APIClient.swift`:

```swift
// Find your Mac's IP: run check_network.py
private let baseURL = "http://192.168.1.XXX:8000"  // ← Change this
```

---

## 🔧 Troubleshooting

### API Won't Start

```bash
# Kill existing process
pkill -9 -f "python main.py"

# Check port 8000
lsof -i :8000

# Restart
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

### Watch Can't Connect

1. **Check IP:** Run `ipconfig getifaddr en0`
2. **Test from iPhone Safari:** `http://YOUR_MAC_IP:8000/health`
3. **Same WiFi:** Ensure iPhone + Mac on same network
4. **Restart API:** Kill and restart the server

### App Expired (After 7 days)

```bash
# Just rebuild and reinstall
# Connect iPhone → Open Xcode → Click Run ▶️
```

---

## 📊 System Statistics

- **Indexed Topics:** 550 chapters/sections
- **Total Pages:** 15,164
- **Edition:** Harrison's 21st (2022)
- **Embedding Model:** text-embedding-3-large (OpenAI)
- **Vector Dimensions:** 3,072
- **Database:** ChromaDB (local)

---

## 🎯 Example Medical Queries

Try these searches (CLI or Watch):

**Cardiology:**
- "acute myocardial infarction management"
- "heart failure treatment"
- "atrial fibrillation"

**Nephrology:**
- "hyponatremia workup"
- "acute kidney injury"
- "chronic kidney disease staging"

**Infectious Disease:**
- "pneumonia antibiotic selection"
- "sepsis management"
- "HIV treatment"

**Endocrinology:**
- "diabetes type 2 treatment"
- "thyroid disorders"
- "adrenal insufficiency"

**Neurology:**
- "stroke management"
- "seizure treatment"
- "migraine headache"

---

## 📁 Project Structure

```
medicinal rag/
├── Harrison's PDF files (original + compressed)
├── backend/
│   ├── main.py              # FastAPI server
│   ├── vector_store.py      # ChromaDB interface
│   ├── hierarchical_search.py  # Search logic
│   ├── models.py            # Data structures
│   ├── interactive_search.py   # CLI testing
│   ├── test_api.py          # API testing
│   └── requirements.txt     # Python dependencies
├── data/
│   ├── extracted_toc.json   # Raw table of contents
│   ├── hierarchy_template.json  # Structured hierarchy
│   ├── processed/chunks/    # 550 topic JSON files
│   └── chroma_db/           # Vector database
├── scripts/
│   ├── extract_toc.py       # TOC extraction
│   ├── pdf_processor.py     # Text extraction
│   └── check_network.py     # Network setup checker
└── docs/
    ├── IMPLEMENTATION_ROADMAP.md  # Full plan
    ├── API_GUIDE.md         # API documentation
    ├── WATCH_APP_GUIDE.md   # Watch app tutorial
    └── QUICK_REFERENCE.md   # This file!
```

---

## 📞 Support Resources

### Documentation Files

- **API Usage:** `API_GUIDE.md`
- **Watch Development:** `WATCH_APP_GUIDE.md`
- **Full Roadmap:** `IMPLEMENTATION_ROADMAP.md`
- **Quick Start (CLI):** `QUICK_START.md`

### Testing Tools

- **CLI Search:** `backend/interactive_search.py`
- **API Tests:** `backend/test_api.py`
- **Network Check:** `scripts/check_network.py`

---

## 🎉 You're Ready!

Current status: **API is fully functional** ✅

Next step: **Build the Apple Watch app** 📱

Open `WATCH_APP_GUIDE.md` and follow the instructions!

---

*Last updated: Phase 7 complete*

