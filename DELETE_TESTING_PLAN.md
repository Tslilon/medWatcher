# 🗑️ Delete Testing Plan

## ✅ **What Should Be Deleted (9 Locations):**

Based on `multimodal_indexer.py` → `delete_content()` method:

### **Local Files:**
1. ✅ Content file (e.g., `user_notes/note_xyz.txt`)
2. ✅ Chunk files (e.g., `user_notes_chunks/note_xyz_chunk*.json`)
3. ✅ Local `summary.json` updated (item removed)

### **GCS Files:**
4. ✅ GCS content file (`gs://harrisons-rag-data-flingoos/processed/user_notes/note_xyz.txt`)
5. ✅ GCS chunk files (`gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/note_xyz_chunk*.json`)
6. ✅ GCS `summary.json` updated

### **Database:**
7. ✅ ChromaDB local (remove all chunk entries)
8. ✅ ChromaDB GCS (upload updated database)
9. ✅ Version marker updated (`version.txt` timestamp incremented)

### **In-Memory:**
10. ✅ Search engine reloaded (singleton reset)

---

## 🧪 **Test Scenarios:**

### **Test 1: Delete Note from Library**
1. Go to: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/library
2. Find a user note
3. Click "🗑️ Delete"
4. Confirm deletion
5. **Expected:**
   - Alert: "✅ Content deleted successfully!"
   - Note disappears from library
   - Library refreshes

### **Test 2: Verify Content Removed from Search**
1. Before deletion: Search for content (e.g., "hyponatremia")
2. Note the result showing
3. Delete the content via library
4. Click 🔄 REFRESH
5. Search again for same term
6. **Expected:**
   - Content no longer appears in search results

### **Test 3: Verify GCS Cleanup**
After deletion, check GCS:
```bash
# Check if content file removed
gsutil ls gs://harrisons-rag-data-flingoos/processed/user_notes/

# Check if chunks removed
gsutil ls gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/

# Check summary.json
gsutil cat gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/summary.json
```

**Expected:**
- Deleted file NOT in list
- Deleted chunks NOT in list
- Summary.json does NOT contain deleted item

### **Test 4: Verify ChromaDB Update**
After deletion:
```bash
# Check version marker
gsutil cat gs://harrisons-rag-data-flingoos/version.txt

# Compare with pre-deletion version (should be newer)
```

**Expected:**
- Version timestamp is AFTER deletion time

### **Test 5: Multi-Type Deletion**
Test deletion for each content type:
- [ ] Delete a **Note**
- [ ] Delete an **Image**
- [ ] Delete a **Drawing**
- [ ] Delete an **Audio**

**Expected:**
- All types delete successfully
- No errors in console
- All removed from library
- All removed from search

---

## 🔍 **Verification Checklist:**

### **Before Each Delete:**
1. Note the `content_id`
2. Search for the content → should appear
3. Check library → should be listed

### **During Delete:**
1. Click delete button
2. Confirm dialog appears
3. Button shows "⏳ Deleting..."
4. Button is disabled

### **After Delete:**
1. Alert shows success message
2. Library refreshes automatically
3. Content no longer in library
4. Click 🔄 REFRESH
5. Search for content → should NOT appear
6. Check GCS (optional) → files removed

---

## ⚠️ **Potential Issues to Watch For:**

1. **Button not disabling:** User can click delete multiple times
2. **Partial deletion:** Files removed locally but not from GCS
3. **Search still shows:** ChromaDB not refreshed
4. **Library doesn't refresh:** Need manual reload
5. **Error handling:** What if GCS upload fails?

---

## ✅ **Success Criteria:**

✅ Delete button works from library  
✅ Confirmation dialog appears  
✅ Success message shown  
✅ Content removed from library  
✅ Content removed from search (after refresh)  
✅ GCS files removed  
✅ ChromaDB updated  
✅ Version marker incremented  
✅ No console errors  
✅ Works for all content types  

---

## 🚀 **Ready to Test!**

The delete functionality is **already implemented** in:
- `backend/multimodal_indexer.py` → `delete_content()`
- `backend/static/library.js` → `deleteMultimodalContent()`
- `backend/main.py` → `DELETE /api/content/{content_id}`

Just need to **verify it works end-to-end on deployed server**.


