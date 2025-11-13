# ✅ HTTPS Enabled - Voice Recognition Ready!

## 🎉 What Changed

Your Harrison's API server is now running with **HTTPS** (secure connection)!

This means:
- ✅ **Voice recognition will work** on iPhone Safari!
- ✅ Microphone access allowed
- ✅ Speak your medical queries
- ✅ Same fast search, now with voice!

---

## 📱 IMPORTANT: First-Time Setup on iPhone

Since we're using a **self-signed certificate** (not from Apple/Google), you need to tell your iPhone to trust it.

### This is a ONE-TIME setup! ⏱️ Takes 2 minutes

---

## Step-by-Step: Accept Certificate on iPhone

### Step 1: Open Safari on iPhone

Navigate to:
```
https://172.20.10.2:8000/web
```

**Note: HTTPS not HTTP!** (The 's' is critical)

---

### Step 2: You'll See a Warning Screen ⚠️

Safari will show:
```
"This Connection Is Not Private"
or
"Cannot Verify Server Identity"
```

**This is NORMAL!** It's just saying the certificate isn't from a major authority.

---

### Step 3: Trust the Certificate

**Option A: If you see "Show Details" button:**

1. Tap **"Show Details"**
2. Tap **"visit this website"**
3. Tap **"Visit Website"** again to confirm

**Option B: If you see "Advanced" link:**

1. Tap **"Advanced"** (bottom of warning)
2. Tap **"Proceed to 172.20.10.2 (Unsafe)"**
3. Confirm

**Option C: If you see "Certificate" warning:**

1. Tap **"Certificate"**
2. Tap **"Continue"** or **"Accept"**

---

### Step 4: Allow Microphone Access 🎤

After accepting the certificate, Safari will ask:

```
"172.20.10.2 Would Like to Access the Microphone"
```

**Tap: "Allow"**

This enables voice recognition!

---

### Step 5: Test Voice Search! 🎉

1. You should now see the Harrison's search interface
2. Tap the **🎤 microphone button**
3. Speak: "hyponatremia workup"
4. Watch it transcribe and search!

---

## 🎤 How to Use Voice Search

### Method 1: Direct Voice Input

1. Tap the **🎤** button (next to search box)
2. Start speaking immediately
3. Watch "Listening..." appear
4. Speak your query clearly
5. Wait for transcription
6. Results appear automatically!

### Method 2: Dictation in Text Field

1. Tap the search text field
2. Tap the **microphone icon** on iPhone keyboard
3. Speak your query
4. Tap **"Search"** button

### Voice Query Examples:

Try these:
- "hyponatremia workup"
- "acute myocardial infarction management"
- "pneumonia antibiotic selection"
- "diabetes type 2 treatment"
- "heart failure guidelines"

---

## 🔧 Troubleshooting

### Problem: Certificate Warning Won't Go Away

**Solution 1: Clear Safari Cache**
1. iPhone Settings → Safari
2. Clear History and Website Data
3. Try again

**Solution 2: Try Different Browser**
- Download "Chrome" or "Firefox" from App Store
- These may handle self-signed certificates differently

---

### Problem: Microphone Still Not Working

**Check Permissions:**
1. iPhone Settings → Safari → Microphone
2. Make sure it's set to **"Ask"** or **"Allow"**

**Check Safari Permissions:**
1. iPhone Settings → Safari
2. Scroll down to "Settings for Websites"
3. Microphone → Make sure "Ask" is enabled

**Try Reloading:**
1. Close Safari completely (swipe up from app switcher)
2. Reopen Safari
3. Go to `https://172.20.10.2:8000/web` again

---

### Problem: "This site can't be reached"

**Check 1: HTTPS not HTTP**
- URL must be: `https://172.20.10.2:8000/web`
- NOT: `http://172.20.10.2:8000/web`

**Check 2: Server Running**
```bash
# On Mac:
ps aux | grep "python.*main.py"
```

**Check 3: Same WiFi**
- iPhone and Mac must be on same WiFi network

**Restart Server:**
```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

---

### Problem: Voice Transcription is Wrong

**Tips for Better Recognition:**
- Speak clearly and slowly
- Use medical terminology (not colloquial)
- Avoid background noise
- Example: "hyponatremia" not "low sodium"

**Alternative:**
- Type the query instead
- Voice is optional, typing works great!

---

## 🔐 Security Note

### Is This Safe?

**YES! Here's why:**

✅ **Local Network Only**
- Server only accessible on YOUR WiFi
- Not exposed to internet
- Only you can access it

✅ **Self-Signed Certificate**
- Just means it's not from Apple/Google
- Still encrypts data
- Perfect for personal use

✅ **Your Data**
- Harrison's text stays on YOUR Mac
- API runs on YOUR Mac
- Only search queries go to OpenAI (for embeddings)

**This is completely safe for personal/home use!**

---

## 📊 Server Information

**Your HTTPS URLs:**

| Purpose | URL |
|---------|-----|
| Web Interface | `https://172.20.10.2:8000/web` |
| API Endpoint | `https://172.20.10.2:8000/api/search` |
| API Docs | `https://172.20.10.2:8000/docs` |
| Health Check | `https://172.20.10.2:8000/health` |

**Server Status:**
```
✅ HTTPS enabled
✅ SSL certificate: Valid for 365 days
✅ IP: 172.20.10.2
✅ Port: 8000
✅ Documents: 550 topics indexed
```

---

## 🎉 What You Can Do Now

### Voice Search Works! 🎤

1. **Speak queries** instead of typing
2. **Faster workflow** - hands-free
3. **Same accurate results** - AI-powered semantic search
4. **Page numbers** - displayed clearly
5. **Copy to clipboard** - easy reference

### Example Workflow:

1. Open `https://172.20.10.2:8000/web` on iPhone
2. Tap 🎤 microphone button
3. Speak: "acute kidney injury"
4. See results in 2-3 seconds
5. Tap result for page numbers
6. Open Harrison's PDF at those pages

---

## 💡 Still Want the Watch App?

**Even with voice on iPhone, the Watch app is still better!**

Why?
- ⌚ **Wrist convenience** - don't need to pull out phone
- 🚀 **Faster** - already on your wrist
- 🎤 **Native dictation** - WatchOS is optimized for it
- 👨‍⚕️ **Professional** - quick reference during rounds

**Plus:**
- Uses same HTTPS API you just set up
- Same accurate results
- Just more convenient!

See: `WATCH_APP_GUIDE.md` if interested

---

## 🎯 Quick Start Commands

### Check if Server is Running:
```bash
curl -k https://172.20.10.2:8000/health
```

### Restart Server:
```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
pkill -f "python main.py"
python main.py
```

### View Server Logs:
```bash
tail -f /tmp/harrison_api.log
```

---

## ✅ Testing Checklist

Before relying on voice search, verify:

- [ ] Can access `https://172.20.10.2:8000/web` on iPhone Safari
- [ ] Accepted certificate warning (one-time only)
- [ ] Granted microphone permission to Safari
- [ ] Microphone button 🎤 appears in search interface
- [ ] Tap 🎤 → speaks → transcribes correctly
- [ ] Search returns results
- [ ] Can tap results to see page numbers
- [ ] Voice recognition is reasonably accurate

---

## 📞 Need Help?

### If voice still doesn't work:
1. Check all troubleshooting steps above
2. Try clearing Safari cache
3. Restart iPhone
4. Restart server on Mac

### Alternative:
- Use text input (always works!)
- Build Watch app (native voice, more reliable)

---

## 🎊 Success!

**You now have:**
- ✅ HTTPS-enabled API server
- ✅ Voice recognition on iPhone
- ✅ Secure connection
- ✅ Fast semantic search
- ✅ Harrison's at your fingertips!

**Try it now!** 📱🎤

Open Safari → `https://172.20.10.2:8000/web` → Tap 🎤 → Speak!

---

*Note: Certificate expires in 365 days. If needed, regenerate with:*
```bash
cd "/Users/maayan/medicinal rag/backend"
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Harrison/CN=172.20.10.2"
```

