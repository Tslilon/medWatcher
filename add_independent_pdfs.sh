#!/bin/bash

echo "════════════════════════════════════════════════════════════════════"
echo "   📚 ADDING INDEPENDENT PDFs TO HARRISON'S RAG SYSTEM"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set!"
    echo "   Please set it first: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

# Change to backend directory
cd "$(dirname "$0")/backend" || exit 1

echo "📁 Current directory: $(pwd)"
echo ""

# Step 1: Process independent PDFs
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 1: Processing Independent PDFs"
echo "════════════════════════════════════════════════════════════════════"
echo ""

python process_independent_pdfs.py
if [ $? -ne 0 ]; then
    echo "❌ Error processing PDFs"
    exit 1
fi

echo ""

# Step 2: Re-index all documents
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 2: Re-indexing All Documents (Harrison's + Independent)"
echo "════════════════════════════════════════════════════════════════════"
echo ""

python index_documents.py --force
if [ $? -ne 0 ]; then
    echo "❌ Error indexing documents"
    exit 1
fi

echo ""

# Step 3: Upload to GCS
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 3: Uploading to Google Cloud Storage"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "📤 Uploading independent PDFs..."
gsutil -m cp -r "../data/independant_pdfs" gs://harrisons-rag-data-flingoos/
if [ $? -ne 0 ]; then
    echo "❌ Error uploading PDFs"
    exit 1
fi

echo ""
echo "📤 Uploading independent chunks..."
gsutil -m cp -r "../data/processed/independent_chunks" gs://harrisons-rag-data-flingoos/
if [ $? -ne 0 ]; then
    echo "❌ Error uploading chunks"
    exit 1
fi

echo ""
echo "📤 Uploading updated ChromaDB..."
gsutil -m cp -r "../data/chroma_db" gs://harrisons-rag-data-flingoos/
if [ $? -ne 0 ]; then
    echo "❌ Error uploading ChromaDB"
    exit 1
fi

echo ""

# Step 4: Deploy to Cloud Run
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 4: Deploying to Google Cloud Run"
echo "════════════════════════════════════════════════════════════════════"
echo ""

bash deploy.sh
if [ $? -ne 0 ]; then
    echo "❌ Error deploying"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "   ✅ INDEPENDENT PDFs SUCCESSFULLY ADDED!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "🎉 Your independent PDFs are now:"
echo "   ✓ Processed and chunked"
echo "   ✓ Indexed in ChromaDB"
echo "   ✓ Uploaded to GCS"
echo "   ✓ Deployed to Cloud Run"
echo ""
echo "🔍 Try searching for content from your new PDFs!"
echo "   URL: https://harrisons-medical-rag-7l3dm3kvsa-uc.a.run.app/web"
echo ""
echo "⌚ On Apple Watch:"
echo "   - Independent PDFs: 100% zoom (normal)"
echo "   - Harrison's: 130% zoom (very zoomed)"
echo ""
echo "════════════════════════════════════════════════════════════════════"

