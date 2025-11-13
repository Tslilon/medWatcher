# Data Flow Map - Complete Upload & Delete Tracking

## When Uploading a PDF

### 1. PDF File Storage
**Upload:**
- ✅ Local: `data/independant_pdfs/<filename>.pdf`
- ✅ GCS: `gs://harrisons-rag-data-flingoos/independant_pdfs/<filename>.pdf`

**Delete:**
- ✅ Local: **KEPT** (backup)
- ✅ GCS: **DELETED**

### 2. Chunk JSON Files
**Upload:**
- ✅ Local: `data/processed/independent_chunks/independent_<filename>_chunk1.json`
- ✅ GCS: `gs://harrisons-rag-data-flingoos/processed/independent_chunks/independent_<filename>_chunk1.json`

**Delete:**
- ✅ Local: **DELETED**
- ✅ GCS: **DELETED**

### 3. Summary JSON
**Upload:**
- ✅ Local: `data/processed/independent_chunks/summary.json` (updated)
- ✅ GCS: `gs://harrisons-rag-data-flingoos/processed/independent_chunks/summary.json` (updated)

**Delete:**
- ✅ Local: **UPDATED** (entry removed)
- ✅ GCS: **UPDATED** (entry removed)

### 4. ChromaDB Storage
**Upload:**
- ✅ Local: `data/chroma_db/chroma.sqlite3` (new documents added)
- ✅ Local: `data/chroma_db/<uuid>/` (vector embeddings)
- ✅ GCS: `gs://harrisons-rag-data-flingoos/chroma_db/chroma.sqlite3` (uploaded)
- ✅ GCS: `gs://harrisons-rag-data-flingoos/chroma_db/<uuid>/` (uploaded)

**Delete:**
- ✅ Local: Documents removed via `delete_by_metadata('pdf_filename', filename)`
- ✅ GCS: Updated ChromaDB uploaded
- ✅ In-Memory: Vector store singleton reloaded

### 5. In-Memory Cache
**Upload:**
- ✅ Local: Vector store singleton reloaded
- ✅ Deployed: Vector store reloads from GCS (NEW!)

**Delete:**
- ✅ Local: Vector store singleton reloaded
- ✅ Deployed: Vector store reloads from GCS (NEW!)

## Verification Checklist

After Upload:
- [ ] PDF in GCS
- [ ] Chunks in GCS
- [ ] summary.json updated in GCS
- [ ] ChromaDB in GCS
- [ ] Local search works
- [ ] Deployed search works (auto-reloads now!)

After Delete:
- [ ] PDF removed from GCS (kept locally)
- [ ] Chunks removed from GCS
- [ ] summary.json updated in GCS
- [ ] ChromaDB updated in GCS
- [ ] Local search doesn't find it
- [ ] Deployed search doesn't find it (auto-reloads now!)

## Key Improvements

### Before:
- Deployed server: Needed full redeploy to see new files
- Delete: Might leave data in vector store cache

### After:
- Deployed server: Auto-reloads from GCS after upload/delete
- Delete: Guaranteed to reload fresh ChromaDB
- No redeployment needed for new files! ✅

## Manual Reload Endpoint

If needed, you can manually trigger a reload:

```bash
curl -X POST https://your-app.run.app/api/reload-from-gcs
```

This will:
1. Download fresh ChromaDB from GCS
2. Reload vector store singleton
3. Search immediately reflects latest data

