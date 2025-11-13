# Independent PDFs Integration Guide

This guide explains how to add independent medical PDFs to your RAG system alongside Harrison's.

## 🎯 Features

- **Separate indexing**: Independent PDFs are indexed alongside Harrison's
- **Auto-detection**: System automatically detects PDF source and opens correct viewer
- **100% zoom on Watch**: Independent PDFs use 100% zoom (vs 130% for Harrison's)
- **High quality**: 800px width, 100% quality images
- **Continuous scroll**: Same smooth scrolling experience
- **Searchable**: Fully integrated into the search system

## 📁 Directory Structure

```
data/
├── independant_pdfs/           # Place your PDFs here
│   └── em-basic-chest-pain-show-notes4.pdf
├── processed/
│   ├── chunks/                 # Harrison's chunks
│   └── independent_chunks/     # Independent PDF chunks
```

## 🚀 Step-by-Step Process

### 1. Add PDFs

Place your PDF files in `/data/independant_pdfs/` directory:

```bash
cp your-medical-pdf.pdf "/Users/maayan/medicinal rag/data/independant_pdfs/"
```

### 2. Process PDFs

Run the processing script to create searchable chunks:

```bash
cd "/Users/maayan/medicinal rag/backend"
python process_independent_pdfs.py
```

This will:
- Extract text from all PDFs in `/data/independant_pdfs/`
- Create 5-page chunks
- Extract titles and metadata
- Save chunks to `/data/processed/independent_chunks/`

### 3. Re-Index Documents

Re-index to include the new PDFs in the vector database:

```bash
cd "/Users/maayan/medicinal rag/backend"
python index_documents.py
```

This will:
- Load Harrison's chunks
- Load independent PDF chunks
- Generate embeddings for all documents
- Update ChromaDB with combined index

### 4. Upload to GCS

Upload the new PDFs and chunks to Google Cloud Storage:

```bash
# Upload independent PDFs
gsutil -m cp -r "/Users/maayan/medicinal rag/data/independant_pdfs" gs://harrisons-rag-data-flingoos/

# Upload independent chunks
gsutil -m cp -r "/Users/maayan/medicinal rag/data/processed/independent_chunks" gs://harrisons-rag-data-flingoos/

# Upload updated ChromaDB
gsutil -m cp -r "/Users/maayan/medicinal rag/backend/chroma_db" gs://harrisons-rag-data-flingoos/
```

### 5. Deploy to Cloud Run

Deploy the updated application:

```bash
cd "/Users/maayan/medicinal rag/backend"
bash deploy.sh
```

## 📊 How It Works

### Search Results

When a user searches:
1. Query is embedded
2. Vector search returns matching chunks from BOTH Harrison's and independent PDFs
3. Results show with clear indicators:
   - Harrison's: "Part X > Chapter"
   - Independent: "📄 PDF Name"

### Viewer Selection

When clicking a search result:
- **Independent PDF**: Always uses `/viewer/independent` (100% zoom)
- **Harrison's**: Uses selected mode (Standard/Compact/Watch)

### File Metadata

Each indexed chunk includes:
```json
{
  "chunk_id": "independent_filename_chunk1",
  "pdf_source": "independent",
  "pdf_filename": "em-basic-chest-pain-show-notes4.pdf",
  "pdf_name": "EM Basic: Chest Pain",
  "start_page": 1,
  "end_page": 5,
  "total_pages": 15,
  "text_content": "...",
  "preview": "...",
  "word_count": 1234
}
```

## 🔧 Technical Details

### Processing

- **Chunk Size**: 5 pages per chunk (adjustable)
- **Text Extraction**: PyMuPDF (fitz)
- **Title Detection**: Auto-extracts from first page
- **Fallback**: Uses filename if no title found

### Viewing

- **Resolution**: 800px width
- **Quality**: 100% JPEG
- **Zoom**: 100% (no scaling)
- **Scrolling**: Vertical continuous scroll
- **Watch Compatible**: Works on Apple Watch

### API Endpoints

New endpoints added:
- `GET /viewer/independent` - Independent PDF viewer
- `GET /pdf/independent/page/{filename}/{page}` - Render PDF page

## 🎯 Current Status

### ✅ Completed

- [x] Independent PDF processor
- [x] Updated indexing system
- [x] New viewer (100% zoom)
- [x] Page rendering endpoint
- [x] Search result routing
- [x] Metadata tracking
- [x] GCS download support

### 📝 Files Modified

1. **New Files**:
   - `backend/process_independent_pdfs.py` - PDF processor
   - `backend/static/independent-viewer.html` - 100% zoom viewer

2. **Modified Files**:
   - `backend/index_documents.py` - Combined indexing
   - `backend/main.py` - New endpoints
   - `backend/models.py` - Extended metadata
   - `backend/hierarchical_search.py` - PDF source handling
   - `backend/download_data.py` - Download independent PDFs
   - `backend/static/index.html` - Viewer routing

## 🚀 Quick Start (Already Done)

The first PDF (`em-basic-chest-pain-show-notes4.pdf`) is ready to process:

```bash
# 1. Process the PDF
cd "/Users/maayan/medicinal rag/backend"
python process_independent_pdfs.py

# 2. Re-index everything
export OPENAI_API_KEY='your-key-here'
python index_documents.py

# 3. Upload to GCS
gsutil -m cp -r "../data/independant_pdfs" gs://harrisons-rag-data-flingoos/
gsutil -m cp -r "../data/processed/independent_chunks" gs://harrisons-rag-data-flingoos/
gsutil -m cp -r "./chroma_db" gs://harrisons-rag-data-flingoos/

# 4. Deploy
bash deploy.sh
```

## 🎨 User Experience

### On Search Page

User sees combined results:
```
Harrison's Results:
✓ Part 2 > 81 Cancer of the Skin
  Pages: 675-682

Independent Results:
✓ 📄 EM Basic: Chest Pain
  Pages: 1-5
```

### On Click

- **Harrison's result** → Opens with user's viewer preference (Standard/Compact/Watch)
- **Independent result** → Opens with independent viewer (100% zoom, always)

### On Watch

- Harrison's chapters: 130% zoom (very zoomed)
- Independent PDFs: 100% zoom (normal)
- Both: High quality, continuous scroll

## 📚 Adding More PDFs

To add more independent PDFs in the future:

1. Copy PDF to `/data/independant_pdfs/`
2. Run `python process_independent_pdfs.py`
3. Run `python index_documents.py` (answer 'y' to re-index)
4. Upload to GCS (3 commands above)
5. Deploy

That's it! The system will automatically handle the rest.

## 🔍 Troubleshooting

### PDF not appearing in search

1. Check chunks were created: `ls ../data/processed/independent_chunks/`
2. Check indexing: Run `index_documents.py` again
3. Verify upload: `gsutil ls gs://harrisons-rag-data-flingoos/independant_pdfs/`

### Viewer not loading

1. Check PDF is in GCS: `gsutil ls gs://harrisons-rag-data-flingoos/independant_pdfs/`
2. Check Cloud Run logs for errors
3. Verify page rendering: Visit `/pdf/independent/page/{filename}/1`

### Wrong zoom level

- Independent PDFs should always use 100% zoom
- Check that `pdf_source` metadata is set to `'independent'`
- Verify routing in `index.html` checks `result.pdf_source`

## ✨ That's It!

Your system now supports:
- ✅ Harrison's 21st Edition (existing)
- ✅ Independent medical PDFs (new)
- ✅ Unified search across all sources
- ✅ Optimized viewers for each type
- ✅ Perfect Watch support

All functionality remains exactly as before, with seamless integration of new PDFs!

