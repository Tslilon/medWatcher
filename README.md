# 🩺 medWatcher - Medical RAG Search System

A powerful, multi-source medical search system combining Harrison's Principles of Internal Medicine with your own medical notes and PDFs. Optimized for all devices including Apple Watch.

## 🌟 Features

### Multi-Source Search
- **Harrison's Medical Textbook**: 550 indexed chapters
- **Independent PDFs**: Add your own medical notes, study guides, protocols
- **Unified Vector Search**: Search across all sources simultaneously
- **Smart Relevance Scoring**: AI-powered semantic search with OpenAI embeddings

### Device-Optimized Viewers
- 📱 **Standard Viewer**: Full PDF.js with text search, highlighting, progressive loading
- 📱 **Compact Viewer**: 115% zoom for mobile devices
- ⌚ **Watch Viewer**: 130% zoom optimized for Apple Watch
- 📄 **Independent Viewer**: Ultra-high resolution (2000px) with pinch zoom for your PDFs

### Advanced Features
- 🔍 **In-PDF Text Search**: Find and highlight text within chapters
- 🎤 **Voice Search**: Speech-to-text for hands-free searching
- 📊 **Progressive Loading**: See results while pages load
- 🔄 **Continuous Scroll**: Smooth page navigation
- 🖼️ **Pinch Zoom**: Independent PDFs support 1x-5x zoom (Apple Watch compatible)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (for deployment)
- Google Cloud SDK (for Cloud Run deployment)
- OpenAI API Key

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/medWatcher.git
cd medWatcher
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set your OpenAI API key**
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

4. **Run locally**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the app**
- Open: http://localhost:8000/web

## 📚 Adding Your Own PDFs

### One-Command Deployment

1. Copy your PDF to the directory:
```bash
cp your-medical-notes.pdf "data/independant_pdfs/"
```

2. Run the automated script:
```bash
./add_independent_pdfs.sh
```

That's it! The script will:
- ✅ Process the PDF into searchable chunks
- ✅ Generate embeddings
- ✅ Re-index the database
- ✅ Upload to Google Cloud Storage
- ✅ Deploy to Cloud Run

### Manual Process

```bash
cd backend

# 1. Process PDFs
python process_independent_pdfs.py

# 2. Re-index
python index_documents.py --force

# 3. Upload to GCS (if using Cloud Run)
gsutil -m cp -r "../data/independant_pdfs" gs://your-bucket/
gsutil -m cp -r "../data/processed/independent_chunks" gs://your-bucket/
gsutil -m cp -r "../data/chroma_db" gs://your-bucket/

# 4. Deploy
bash deploy.sh
```

## 🌐 Cloud Deployment

### Deploy to Google Cloud Run

```bash
cd backend
bash deploy.sh
```

The deployment script will:
1. Build a multi-platform Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure public access (HTTPS enabled)

### Environment Variables

Set these in your environment:
- `OPENAI_API_KEY`: Your OpenAI API key for embeddings
- `PORT`: Port for the server (default: 8000)

## 📖 Documentation

- **[Quick Workflow](ADD_NEW_PDF_WORKFLOW.md)**: Simple guide for adding PDFs
- **[Technical Guide](INDEPENDENT_PDFS_GUIDE.md)**: Complete technical documentation
- **[Deployment Summary](DEPLOYMENT_COMPLETE.md)**: Latest deployment details

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **ChromaDB**: Vector database for embeddings
- **OpenAI API**: text-embedding-3-large for semantic search
- **PyMuPDF**: PDF processing and rendering
- **Google Cloud Storage**: Data persistence
- **Google Cloud Run**: Serverless deployment

### Frontend
- **PDF.js**: Native PDF rendering
- **Vanilla JavaScript**: Fast, no framework overhead
- **Progressive Web App**: Offline-capable
- **Responsive Design**: Optimized for all screen sizes

## 📊 System Components

### Core Files
```
backend/
├── main.py                    # FastAPI application
├── hierarchical_search.py     # Search logic
├── vector_store.py           # ChromaDB interface
├── index_documents.py        # Indexing pipeline
├── process_independent_pdfs.py # PDF processing
├── download_data.py          # GCS data fetcher
└── static/
    ├── index.html            # Main search interface
    ├── pdfviewer.html        # Standard PDF viewer
    ├── watch-simple-viewer.html # Watch viewer
    ├── compact-viewer.html   # Compact viewer
    └── independent-viewer.html # Independent PDF viewer
```

### Data Pipeline
```
PDF → Text Extraction → Chunking → Embeddings → ChromaDB → Search
```

## 🎯 Use Cases

- 🏥 **Medical Students**: Search textbooks + personal notes
- 👨‍⚕️ **Physicians**: Quick reference for clinical guidelines
- 📚 **Researchers**: Cross-reference multiple medical sources
- ⌚ **On-the-Go**: Access on Apple Watch during rounds
- 📱 **Mobile First**: Optimized for phones and tablets

## 🔐 Security

- API keys never committed to repository
- SSL/TLS enabled by default on Cloud Run
- Google Cloud IAM for access control
- No user data stored (stateless search)

## 🛠️ Development

### Project Structure
```
medWatcher/
├── backend/              # FastAPI backend
├── data/                 # Data files (gitignored)
│   ├── independant_pdfs/
│   ├── processed/
│   └── chroma_db/
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── tests/               # Test suite
```

### Adding New Features
1. Create feature branch
2. Implement and test locally
3. Update documentation
4. Deploy to staging
5. Merge to main

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Search returns no results**
- Check OpenAI API key is set
- Verify ChromaDB is indexed
- Check network connectivity

**PDF viewer not loading**
- Ensure data is in GCS bucket
- Check CORS configuration
- Verify Cloud Run permissions

**Deployment fails**
- Check Docker is running
- Verify gcloud authentication
- Ensure proper IAM roles

See [INDEPENDENT_PDFS_GUIDE.md](INDEPENDENT_PDFS_GUIDE.md) for detailed troubleshooting.

## 📧 Support

For issues or questions:
- Open a GitHub issue
- Check documentation
- Review deployment logs

## 🎉 Acknowledgments

- **Harrison's Principles of Internal Medicine** - McGraw Hill Education
- **OpenAI** - Embedding models
- **PDF.js** - Mozilla Foundation
- **FastAPI** - Sebastián Ramírez
- **ChromaDB** - Chroma team

## 🔮 Future Roadmap

- [ ] Personal note-taking system (in progress)
- [ ] File management interface
- [ ] Multi-user support
- [ ] Custom embedding models
- [ ] Export/import functionality
- [ ] Mobile native apps

---

**Made with ❤️ for medical professionals and students**

🩺 Search smarter, not harder.

