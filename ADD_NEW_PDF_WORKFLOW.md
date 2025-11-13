# 📚 Quick Guide: Adding New PDFs

This is your simple, reproducible workflow for adding new medical PDFs.

## 🎯 One-Time Setup (Already Done!)

- ✅ System built and ready
- ✅ Scripts created
- ✅ Infrastructure configured

## 📝 Every Time You Add a New PDF:

### Step 1: Copy PDF to Directory

```bash
cp your-new-pdf.pdf "/Users/maayan/medicinal rag/data/independant_pdfs/"
```

### Step 2: Run the Deployment Script

```bash
cd "/Users/maayan/medicinal rag"
./add_independent_pdfs.sh
```

**That's it!** The script will:
1. ✅ Process all PDFs in the directory
2. ✅ Generate embeddings
3. ✅ Re-index everything
4. ✅ Upload to Google Cloud Storage
5. ✅ Deploy to Cloud Run

### Step 3: Test

Visit: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web

Search for content from your new PDF!

---

## 🔑 API Key Setup

The script needs your OpenAI API key. Store it securely:

### Option A: Environment Variable (Recommended)

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export OPENAI_API_KEY='your-key-here'
```

Then run:
```bash
source ~/.zshrc
```

### Option B: Per-Session

Run before the script:
```bash
export OPENAI_API_KEY='your-key-here'
./add_independent_pdfs.sh
```

---

## 📊 What Happens Behind the Scenes

When you run `./add_independent_pdfs.sh`:

1. **Processing** (`process_independent_pdfs.py`)
   - Scans `/data/independant_pdfs/` for all PDFs
   - Extracts text from each PDF
   - Creates 5-page chunks
   - Saves to `/data/processed/independent_chunks/`

2. **Indexing** (`index_documents.py`)
   - Loads Harrison's chunks
   - Loads independent PDF chunks
   - Generates embeddings via OpenAI
   - Updates ChromaDB with combined index

3. **Upload to GCS**
   ```bash
   gsutil -m cp -r data/independant_pdfs gs://bucket/
   gsutil -m cp -r data/processed/independent_chunks gs://bucket/
   gsutil -m cp -r backend/chroma_db gs://bucket/
   ```

4. **Deploy**
   - Builds Docker image
   - Pushes to Google Container Registry
   - Deploys to Cloud Run
   - Downloads data at startup

---

## 🎨 User Experience After Deployment

### Search Results Show Both Sources:

```
Search: "chest pain"

Results:
✓ 📄 EM Basic- Chest Pain
  Pages: 1-2
  
✓ Part 8 > Chapter 291 Chest Discomfort (Harrison's)
  Pages: 2043-2048
```

### Clicking Opens Correct Viewer:

- **Independent PDF** → 100% zoom viewer
- **Harrison's** → User's preference (Standard/Compact/Watch)

### On Apple Watch:

- **Independent PDFs**: 100% zoom (normal size)
- **Harrison's**: 130% zoom (larger text)
- **Both**: High quality, continuous scroll

---

## 🔍 Troubleshooting

### PDF not appearing in search?

```bash
# 1. Check chunks were created
ls "/Users/maayan/medicinal rag/data/processed/independent_chunks/"

# 2. Check if indexed
cd "/Users/maayan/medicinal rag/backend"
python -c "from vector_store import ChromaVectorStore; vs = ChromaVectorStore(); print(f'Documents: {vs.count_documents()}')"

# 3. Re-run the script
./add_independent_pdfs.sh
```

### Script fails at indexing?

Check your API key:
```bash
echo $OPENAI_API_KEY
```

If empty, export it and try again.

### Script fails at upload?

Check GCS access:
```bash
gsutil ls gs://harrisons-rag-data-flingoos/
```

---

## 📚 Adding Multiple PDFs at Once

Just copy all PDFs to the directory before running the script:

```bash
cp lecture1.pdf lecture2.pdf lecture3.pdf "/Users/maayan/medicinal rag/data/independant_pdfs/"
./add_independent_pdfs.sh
```

The script processes ALL PDFs in the directory automatically!

---

## ⚡ Quick Reference

```bash
# Add new PDF
cp new-pdf.pdf "/Users/maayan/medicinal rag/data/independant_pdfs/"

# Deploy everything
cd "/Users/maayan/medicinal rag"
./add_independent_pdfs.sh

# Test
open "https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web"
```

---

## 🎯 Files You'll Work With

- **Input**: `/data/independant_pdfs/` - Put your PDFs here
- **Script**: `/add_independent_pdfs.sh` - Run this to deploy
- **Output**: `/data/processed/independent_chunks/` - Generated chunks

Everything else is automatic!

---

## 💡 Pro Tips

1. **Name your PDFs clearly** - The filename becomes part of the chunk ID
2. **Keep PDFs organized** - All PDFs in the directory will be processed
3. **Wait for deployment** - Takes ~5 minutes for full deployment
4. **Test locally first** (optional):
   ```bash
   cd backend
   python process_independent_pdfs.py
   python index_documents.py
   ```

---

## ✅ That's It!

Your workflow:
1. Copy PDF to folder
2. Run script
3. Search and use!

**Reproducible, simple, automated.** 🚀

