# 📱 iPhone Testing Guide

## Quick Start: Test Harrison's API from Your iPhone

Before building the Watch app, let's make sure everything works from your iPhone!

---

## Step 1: Find Your Mac's IP Address

Your Mac's IP is: **`172.20.10.2`**

(You can always find it by running: `ipconfig getifaddr en0`)

---

## Step 2: Make Sure API is Running

On your Mac, the server should be running. You should see:

```
🏥 Starting Harrison's Medical RAG API Server
======================================================================
📍 API: http://localhost:8000
📱 Web Interface: http://localhost:8000/web
📚 Docs: http://localhost:8000/docs
======================================================================
```

If it's not running, start it:

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

---

## Step 3: Access from iPhone

### ✅ Method 1: Safari (Easiest!)

1. **Open Safari** on your iPhone
2. **Type this URL** in the address bar:

   ```
   http://172.20.10.2:8000/web
   ```

3. **Bookmark it** for easy access!

### What You'll See:

- 🎨 Beautiful purple gradient interface
- 🔍 Search box with voice button (microphone icon)
- 💊 Quick query buttons (Hyponatremia, Acute MI, etc.)
- 📱 Mobile-optimized and touch-friendly

---

## Step 4: Try Searching!

### Option A: Voice Search 🎤

1. Tap the **microphone button** (🎤) next to the search box
2. Say a medical query: *"hyponatremia workup"*
3. Tap **Search**
4. Results appear in 2-3 seconds!

### Option B: Type Search ⌨️

1. Tap the search box
2. Type: *"acute MI management"*
3. Press **Search**
4. See the results!

### Option C: Quick Queries 🚀

Just tap any of the preset buttons:
- **Hyponatremia**
- **Acute MI**
- **Pneumonia**
- **Diabetes**
- **Heart Failure**

---

## Step 5: View Results

When results appear, you'll see:

- ✅ **Topic name** (e.g., "53 Fluid and Electrolyte Disturbances")
- 📖 **Page numbers** (e.g., "Pages 1383-1448")
- 📂 **Hierarchy** (Part > Chapter)
- 📄 **Preview text**
- ⭐ **Relevance score** (percentage)
- 📊 **Tables/Figures** count (if any)

**Tap any result** to see full details including:
- Start and end page numbers (prominently displayed)
- Full preview
- List of tables and figures
- Location in textbook hierarchy

---

## 🎯 What to Test

Try these queries to verify everything works:

### Nephrology
```
hyponatremia workup
acute kidney injury
```

### Cardiology
```
acute MI management
heart failure treatment
atrial fibrillation
```

### Infectious Disease
```
pneumonia antibiotics
sepsis management
```

### Endocrinology
```
diabetes type 2 treatment
thyroid disorders
```

---

## 🔧 Troubleshooting

### "Can't Connect" or Page Won't Load

**Problem:** Safari shows "Safari Cannot Open the Page"

**Solutions:**

1. **Check same WiFi:** Make sure iPhone and Mac are on the **same WiFi network**
2. **Check IP:** Run on Mac: `ipconfig getifaddr en0` - has it changed?
3. **Ping test:** Run on Mac: `ping $(ipconfig getifaddr en0)` - should respond
4. **Firewall:** Check Mac's firewall isn't blocking port 8000
   - System Settings → Network → Firewall
5. **Server running:** Make sure `python main.py` is still running

### Voice Search Not Working

**Problem:** Microphone button doesn't work

**Solutions:**

1. **Safari Permissions:** Safari may ask for microphone permission - allow it
2. **Settings:** iPhone Settings → Safari → Microphone → Allow
3. **Fallback:** Just type your query instead!

### Slow Searches

**Problem:** Searches take 5-10+ seconds

**Possible causes:**
- Normal on first search after server start (loading models)
- OpenAI API might be slow
- WiFi connection quality
- Subsequent searches should be faster (~2-3 seconds)

### No Results Found

**Problem:** Search returns 0 results

**Try:**
- Simpler terms: "hyponatremia" instead of "workup for low sodium in elderly"
- Medical terminology: "myocardial infarction" works better than "heart attack"
- Check spelling
- Try a different query

---

## 📊 What This Proves

If the iPhone web interface works, it means:

✅ Your Mac's API server is accessible over WiFi  
✅ The search engine is working correctly  
✅ OpenAI embeddings are functioning  
✅ The 550 topics are properly indexed  
✅ Your network setup is ready for Watch app  

---

## 🎉 Next Steps

### If Everything Works:

**You're ready to build the Apple Watch app!**

Open `WATCH_APP_GUIDE.md` and follow the Xcode instructions. The Watch app will use the exact same API you just tested.

### If You Love the Web Interface:

You can also:
- **Add to Home Screen** on iPhone (works like a native app!)
  - Safari → Share → Add to Home Screen
- **Use on iPad** (same URL, even better on larger screen)
- **Keep using it** instead of Watch (if you prefer)

---

## 💡 Pro Tips

### Add to Home Screen

1. Open `http://172.20.10.2:8000/web` in Safari
2. Tap the **Share button** (square with arrow)
3. Scroll down, tap **"Add to Home Screen"**
4. Name it **"Harrison's"**
5. Now you have an app icon! 📱

### Bookmark for Quick Access

1. In Safari, tap the **Bookmarks button**
2. **Add Bookmark**
3. Save to **Favorites**
4. Now it's always one tap away!

### Use on Other Devices

This same URL works on:
- iPad
- Another iPhone
- Any device on your WiFi network

---

## 🔐 Privacy Note

**Your data stays local:**
- ✅ API runs on YOUR Mac only
- ✅ Only accessible on YOUR WiFi
- ✅ Harrison's text stays on YOUR machine
- ✅ Only search queries go to OpenAI (for embeddings)
- ✅ No data collected or stored externally

---

## 📞 Need Help?

If something's not working:

1. **Check the logs:**
   ```bash
   tail -f /tmp/harrison_api.log
   ```

2. **Restart the server:**
   ```bash
   cd "/Users/maayan/medicinal rag/backend"
   source venv/bin/activate
   pkill -f "python main.py"
   python main.py
   ```

3. **Re-run network checker:**
   ```bash
   python3 scripts/check_network.py
   ```

---

## ✅ Testing Checklist

Before proceeding to Watch app development, verify:

- [ ] Can access `http://172.20.10.2:8000/web` from iPhone Safari
- [ ] Search box appears and is usable
- [ ] Can type or speak queries
- [ ] Quick query buttons work
- [ ] Search returns results in 2-5 seconds
- [ ] Can tap results to see details
- [ ] Page numbers are clearly displayed
- [ ] Modal close button works
- [ ] Everything looks good on mobile screen

---

**Once all checks pass, you're 100% ready for Watch app development!** 🎉

Open `WATCH_APP_GUIDE.md` for the next phase.

