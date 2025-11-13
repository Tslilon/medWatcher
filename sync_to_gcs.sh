#!/bin/bash
# Sync local data to GCS bucket for deployment

set -e

# Configuration
GCS_BUCKET="harrisons-rag-data-flingoos"
LOCAL_DATA_DIR="../data"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      Syncing Local Data to GCS Bucket                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if gcloud is installed
if ! command -v gsutil &> /dev/null; then
    echo "❌ Error: gsutil not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if data directory exists
if [ ! -d "$LOCAL_DATA_DIR" ]; then
    echo "❌ Error: Data directory not found: $LOCAL_DATA_DIR"
    exit 1
fi

echo "📦 Uploading independent PDFs..."
gsutil -m rsync -r "$LOCAL_DATA_DIR/independant_pdfs" "gs://$GCS_BUCKET/independant_pdfs/"

echo "📦 Uploading independent chunks..."
gsutil -m rsync -r "$LOCAL_DATA_DIR/processed/independent_chunks" "gs://$GCS_BUCKET/processed/independent_chunks/"

echo "📦 Uploading ChromaDB..."
gsutil -m rsync -r "$LOCAL_DATA_DIR/chroma_db" "gs://$GCS_BUCKET/chroma_db/"

echo ""
echo "✅ Sync complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Deploy your updated code: cd backend && ./deploy.sh"
echo "   2. Or just restart Cloud Run to reload from GCS"
echo ""

