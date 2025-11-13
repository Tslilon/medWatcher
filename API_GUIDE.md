# Harrison's Medical RAG - API Guide

## 🚀 Quick Start

Your API is currently running locally. Here's how to use it:

### Running the Server

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

The server will start on: **http://localhost:8000**

---

## 📡 API Endpoints

### 1. Search Medical Topics

**Endpoint:** `POST /api/search`

**Request:**
```json
{
  "query": "what is the workup for hyponatremia",
  "max_results": 5
}
```

**Response:**
```json
{
  "query": "what is the workup for hyponatremia",
  "results": [
    {
      "topic_id": "part2_ch53_fluid_and_electrolyte_disturbances",
      "topic_name": "53 Fluid and Electrolyte Disturbances",
      "hierarchy": "Part 2 > 53 Fluid and Electrolyte Disturbances",
      "preview": "53 Fluid and Electrolyte Disturbances...",
      "pages": "1383-1448",
      "start_page": 1383,
      "end_page": 1448,
      "relevance_score": 0.394,
      "tables": [],
      "figures": ["FIGURE 53-1", "FIGURE 53-2"]
    }
  ],
  "total_results": 5,
  "search_time_ms": 621
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "acute MI management", "max_results": 3}'
```

---

### 2. Get Topic Details

**Endpoint:** `GET /api/topic/{topic_id}`

**Example:**
```bash
curl "http://localhost:8000/api/topic/part2_ch53_fluid_and_electrolyte_disturbances"
```

**Response:**
```json
{
  "topic_id": "part2_ch53_fluid_and_electrolyte_disturbances",
  "topic_name": "53 Fluid and Electrolyte Disturbances",
  "hierarchy": "Part 2 > 53 Fluid and Electrolyte Disturbances",
  "start_page": 1383,
  "end_page": 1448,
  "text_content": "Full chapter text...",
  "preview": "Brief preview...",
  "word_count": 7700,
  "tables": [],
  "figures": ["FIGURE 53-1"]
}
```

---

### 3. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_store_count": 550,
  "message": "System operational with 550 indexed documents"
}
```

---

### 4. System Statistics

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "indexed_documents": 550,
  "total_pages": 15164,
  "edition": "21st",
  "year": 2022,
  "embedding_model": "text-embedding-3-large",
  "vector_dimensions": 3072,
  "total_parts": 20,
  "status": "operational"
}
```

---

## 🍎 Connecting from Apple Watch

### Finding Your Mac's IP Address

For your Watch to connect to your Mac's API:

```bash
# On your Mac, run:
ipconfig getifaddr en0
# Example output: 192.168.1.105
```

Then use: `http://192.168.1.105:8000/api/search`

### Requirements for Watch Access

1. **Same WiFi Network:** iPhone and Mac must be on same network
2. **Firewall:** May need to allow port 8000
3. **Server Running:** API must be running on Mac

### Testing Connectivity

```bash
# From your iPhone (using Shortcuts app or browser):
curl http://YOUR_MAC_IP:8000/health
```

---

## 🌐 Making API Accessible Over Internet

### Option 1: ngrok (Quick Testing)

```bash
# Install ngrok
brew install ngrok

# Run alongside your API
ngrok http 8000

# You'll get a public URL like:
# https://abc123.ngrok.io
```

Use this URL in your Watch app for testing anywhere!

### Option 2: Deploy to Google Cloud (Production)

See deployment guide in Phase 7 of roadmap.

---

## 🧪 Testing Examples

### Medical Queries That Work Well

**Cardiology:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "acute myocardial infarction management", "max_results": 3}'
```

**Nephrology:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "hyponatremia workup", "max_results": 3}'
```

**Infectious Disease:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "pneumonia antibiotic selection", "max_results": 3}'
```

**Endocrinology:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes type 2 treatment", "max_results": 3}'
```

---

## 📊 Response Time Optimization

Average search times:
- Simple queries: ~500-700ms
- Complex queries: ~800-1200ms
- Topic retrieval: ~50-100ms

**Optimization tips:**
- Limit max_results for faster responses
- Cache frequent queries
- Use simpler query terms

---

## 🔐 Security Notes

**Current Setup (Development):**
- ✅ Local network only
- ✅ No authentication (safe for personal use)
- ✅ CORS enabled for easy testing

**For Production:**
- Add API key authentication
- Use HTTPS
- Restrict CORS origins
- Add rate limiting

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -9 -f "python main.py"
```

### Watch Can't Connect
1. Check Mac's IP: `ipconfig getifaddr en0`
2. Test from iPhone Safari: `http://YOUR_MAC_IP:8000/health`
3. Check firewall settings
4. Ensure both on same WiFi

### Slow Searches
- OpenAI API might be slow - normal
- First search after restart takes longer (loading models)
- Subsequent searches are faster

---

## 📱 Next Steps

1. ✅ API is running and tested
2. ⏭️ Build Apple Watch app (Phase 8)
3. ⏭️ Deploy to cloud (optional, Phase 9)

---

## 💡 Pro Tips

**Keep Server Running:**
```bash
# Use screen or tmux to keep server running in background
screen -S harrison
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
# Press Ctrl+A then D to detach
# Reconnect with: screen -r harrison
```

**Auto-start on Mac Boot:**
Create a Launch Agent (advanced) or just start manually when needed.

**Monitor Performance:**
Check server logs in terminal for request times and errors.

---

Ready for Apple Watch development? See `WATCH_APP_GUIDE.md`!

