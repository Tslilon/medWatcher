# 🧪 Comprehensive Testing Guide - medWatcher Multimodal Features

## 🚀 **Live URL**
https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web

---

## ✅ **ALL FEATURES IMPLEMENTED & DEPLOYED**

### **Phase 1-3: Multimodal UI** ✅
- ➕ Add content button
- 📝 Text note creation
- 📷 Image upload (drag-drop + file picker)
- ✏️ Drawing pad (accurate cursor, undo/clear)
- 🎤 Audio recording (with timer)

### **Phase 4: Library Integration** ✅
- Show all multimodal content in library
- View button for each content type
- Delete button with confirmation

### **Phase 5: Search Integration** ✅
- Multimodal content appears in search results
- Click to view in modal
- Appropriate icons for each type

---

## 🧪 **TESTING PLAN: Step-by-Step**

### **TEST 1: Upload Content (All Types)**

#### **1A: Upload a Note**
1. Open: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web
2. Click **➕** button
3. Click **📝 Note**
4. Enter:
   - Title: "Test Note"
   - Text: "This is a test note for hyponatremia management"
   - Tags: "test,electrolytes"
5. Click "Save Note"
6. **Expected:**
   - ✅ Success message appears
   - ✅ Modal closes

#### **1B: Upload an Image**
1. Click **➕** button
2. Click **📷 Image**
3. Either drag-drop or click to select an image
4. Add caption: "Test Image"
5. Add tags: "test,radiology"
6. Click "Upload Image"
7. **Expected:**
   - ✅ Image preview shows
   - ✅ Success message appears
   - ✅ Modal closes

#### **1C: Create a Drawing**
1. Click **➕** button
2. Click **✏️ Drawing**
3. Draw something on canvas
4. Test **Undo** button → should undo last stroke
5. Test **Clear** button → should clear canvas
6. Draw again
7. Add caption: "Test Drawing"
8. Click "Save Drawing"
9. **Expected:**
   - ✅ Drawing saves
   - ✅ Success message appears

#### **1D: Record Audio** (Mac/iPhone only, not Watch)
1. Click **➕** button
2. Click **🎤 Audio**
3. Click "Start Recording"
4. Allow microphone access
5. Speak for 5-10 seconds
6. Click "Stop Recording"
7. **Expected:**
   - ✅ Timer shows during recording
   - ✅ Audio preview appears
   - ✅ Can play back recording
8. Add title: "Test Audio"
9. Click "Save Audio"
10. **Expected:**
    - ✅ Success message appears

---

### **TEST 2: Library Page**

1. Open: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/library
2. **Expected:** You should see all your uploaded content with icons:
   - 📝 Test Note
   - 📷 Test Image
   - ✏️ Test Drawing
   - 🎤 Test Audio

#### **2A: View Each Content Type**
For each item:
1. Click "👁️ View" button
2. **Expected:**
   - **Note:** Shows title, text, tags in modal
   - **Image:** Shows image, OCR text if available
   - **Drawing:** Shows drawing image
   - **Audio:** Shows audio player, transcription if available
3. Close modal

---

### **TEST 3: Search Integration**

1. Go back to main page: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web
2. Click **🔄 REFRESH** button
3. Wait 5-10 seconds for ChromaDB to reload
4. Search for "test" or "hyponatremia"
5. **Expected:** Search results should include:
   - Your note (📝 My Note)
   - Your image (📷 My Image)
   - Your drawing (✏️ My Drawing)
   - Your audio (🎤 My Audio)
   - Harrison's content (if matches)

#### **3A: View from Search Results**
1. Click on one of your multimodal results
2. **Expected:**
   - Modal opens with content
   - No page navigation (multimodal content doesn't have pages)
3. Close modal
4. Try clicking a Harrison's result
5. **Expected:**
   - Navigates to PDF viewer

---

### **TEST 4: Delete Functionality**

⚠️ **This is the critical test!**

#### **4A: Delete from Library**
1. Go to library page
2. Find your "Test Note"
3. Click "🗑️ Delete"
4. **Expected:**
   - Confirmation dialog appears with warning
   - Warning mentions removing from:
     - Content file
     - Chunks
     - ChromaDB
     - GCS backups
5. Click "OK" to confirm
6. **Expected:**
   - Button shows "⏳ Deleting..."
   - Button is disabled
   - After 5-10 seconds: "✅ Content deleted successfully!"
   - Library refreshes
   - Note is gone from library

#### **4B: Verify Removal from Search**
1. Go to main page
2. Click **🔄 REFRESH**
3. Search for "test" or the content you just deleted
4. **Expected:**
   - Deleted note should NOT appear in results
   - Other content still appears

#### **4C: Verify GCS Cleanup** (Optional - requires `gcloud` CLI)
```bash
# Check if files removed from GCS
gsutil ls gs://harrisons-rag-data-flingoos/processed/user_notes/
gsutil ls gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/

# Check summary.json
gsutil cat gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/summary.json
```

**Expected:**
- Deleted file NOT in GCS
- Summary.json does NOT list deleted item

---

### **TEST 5: End-to-End Workflow**

Full cycle test:
1. Upload new note: "Final Test Note - Delete Me"
2. Check library → should appear
3. Refresh search → search for it → should find it
4. Click result → should view in modal
5. Go to library
6. Delete the note
7. Refresh search → search again → should NOT find it

---

## 📱 **DEVICE-SPECIFIC TESTING**

### **iPhone Testing:**
1. Open Safari: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web
2. Test:
   - ✅ Upload note (typing works)
   - ✅ Upload image (from Photos app)
   - ✅ Drawing (touch drawing works)
   - ✅ Audio recording (microphone works)
   - ✅ Search and view results
   - ✅ Library page scrolling
   - ✅ View content in modals
   - ✅ Delete content

### **Apple Watch Testing:**
1. Open Safari: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web
2. **Note:** Audio recording won't work on Watch (MediaRecorder API not supported)
3. Test:
   - ✅ Search works
   - ✅ Results display (compact)
   - ✅ Can view Harrison's in Watch viewer
   - ❓ Multimodal content viewing (may need adjustment for Watch screen)

### **Mac/Chrome Testing:**
1. Open Chrome: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web
2. Open Console (F12)
3. Test all features
4. **Expected:** No errors in console

---

## ⚠️ **Known Limitations:**

1. **Audio Recording:**
   - ❌ Does NOT work on Apple Watch (MediaRecorder API not available)
   - ✅ Works on Mac, iPhone, iPad, Chrome, Firefox
   - Fallback: Can upload audio file instead

2. **Image Formats:**
   - ✅ JPEG, PNG, WEBP supported
   - ⚠️ HEIC might need conversion on backend

3. **Audio Formats:**
   - ✅ WebM (recorded audio)
   - ✅ M4A, AAC, WAV (uploaded files)
   - ⚠️ Some formats may not play on all devices

---

## ✅ **Success Checklist:**

### **Upload Features:**
- [ ] ➕ Button works
- [ ] Modal opens
- [ ] Note upload works
- [ ] Image upload works (drag-drop + file picker)
- [ ] Drawing works (accurate cursor, undo, clear)
- [ ] Audio recording works (Mac/iPhone)
- [ ] Success messages show
- [ ] Modal closes after save

### **Library Features:**
- [ ] All content types displayed
- [ ] Correct icons for each type
- [ ] View button opens modal
- [ ] Content displays correctly in modal:
  - [ ] Notes show text
  - [ ] Images show image + OCR
  - [ ] Drawings show drawing
  - [ ] Audio shows player + transcription
- [ ] Delete button works
- [ ] Confirmation dialog appears
- [ ] Delete removes from library
- [ ] Library refreshes after delete

### **Search Features:**
- [ ] Multimodal content appears in search
- [ ] Correct icons in results
- [ ] Click opens modal (not PDF viewer)
- [ ] Modal shows content correctly
- [ ] Deleted content doesn't appear after refresh
- [ ] Refresh button works

### **Delete Features:**
- [ ] Delete button in library works
- [ ] Confirmation dialog shows warning
- [ ] Button shows loading state
- [ ] Button disabled during delete
- [ ] Success message appears
- [ ] Library updates automatically
- [ ] Content removed from search
- [ ] GCS files removed (optional check)
- [ ] No errors in console

---

## 🐛 **If Something Doesn't Work:**

### **Upload Not Working:**
1. Open browser console (F12)
2. Check for errors
3. Verify server is responding: `curl https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/api/`

### **Content Not Appearing in Search:**
1. Wait 10 seconds
2. Click **🔄 REFRESH** button
3. Wait another 10 seconds
4. Try searching again

### **Delete Not Working:**
1. Check console for errors
2. Verify DELETE request sent: Network tab in DevTools
3. Check if 500 error → server issue

### **Modal Not Opening:**
1. Check console for JavaScript errors
2. Hard refresh: Ctrl+Shift+R (Chrome) or Cmd+Shift+R (Mac)
3. Clear browser cache

---

## 📊 **Testing Report Template:**

After testing, report back:

```
✅ WORKING:
- [List what works]

❌ NOT WORKING:
- [List what doesn't work]
- [Include console errors if any]

⚠️ ISSUES:
- [List any bugs or unexpected behavior]

📱 DEVICE TESTED:
- [Mac/iPhone/Watch/Chrome]

🔧 SUGGESTIONS:
- [Any improvements or changes needed]
```

---

## 🎯 **Priority Test Order:**

1. **High Priority:**
   - Upload note
   - Search finds note
   - Delete note
   - Note removed from search

2. **Medium Priority:**
   - Upload image/drawing
   - View in library
   - View from search

3. **Low Priority:**
   - Audio recording (if supported on device)
   - GCS verification
   - Watch testing

---

## 🚀 **Ready to Test!**

Everything is deployed and ready. Start with TEST 1 and work your way through!


