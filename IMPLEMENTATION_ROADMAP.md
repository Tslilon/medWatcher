# Harrison's Medical RAG System - Complete Implementation Guide

## Project Goal
Build a hierarchical RAG system enabling medical professionals to query Harrison's Principles of Internal Medicine (3,600 pages) via voice commands on Apple Watch, with intelligent semantic search and accurate page retrieval.

---

## Table of Contents
- [Phase 0: Prerequisites & Setup](#phase-0-prerequisites--setup)
- [Phase 1: Environment & API Configuration](#phase-1-environment--api-configuration)
- [Phase 2: PDF Structure Analysis](#phase-2-pdf-structure-analysis)
- [Phase 3: PDF Processing & Text Extraction](#phase-3-pdf-processing--text-extraction)
- [Phase 4: Vector Database & Embeddings](#phase-4-vector-database--embeddings)
- [Phase 5: Hierarchical Search Implementation](#phase-5-hierarchical-search-implementation)
- [Phase 6: FastAPI Backend](#phase-6-fastapi-backend)
- [Phase 7: Testing & Validation](#phase-7-testing--validation)
- [Phase 8: Cloud Deployment (GCP)](#phase-8-cloud-deployment-gcp)
- [Phase 9: Apple Watch App Development](#phase-9-apple-watch-app-development)
- [Phase 10: Voice Integration](#phase-10-voice-integration)
- [Phase 11: PDF Display on Watch](#phase-11-pdf-display-on-watch)
- [Phase 12: Production & Monitoring](#phase-12-production--monitoring)

---

# Phase 0: Prerequisites & Setup

## 0.1 System Requirements

**Development Machine:**
- macOS (for Apple Watch development)
- 16GB+ RAM recommended
- 10GB+ free disk space
- Python 3.11 or higher
- Xcode 15+ (for WatchOS development)

**Accounts Needed:**
- OpenAI account (API access)
- Google Cloud Platform account
- Apple Developer account ($99/year)
- Pinecone account (optional, for managed vector DB)

## 0.2 Install Development Tools

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Verify Python installation
python3 --version  # Should show 3.11 or higher

# Install git
brew install git

# Install Node.js (for some utilities)
brew install node

# Install Xcode from App Store
# Then install command line tools:
xcode-select --install
```

**✅ Testing Phase 0:**
```bash
# Verify all installations
python3 --version
git --version
node --version
xcodebuild -version
```

Expected output: All commands should return version numbers without errors.

---

# Phase 1: Environment & API Configuration

## 1.1 Get OpenAI API Key

**Step-by-step:**

1. Navigate to: https://platform.openai.com/signup
2. Create account or sign in
3. Go to: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Name: `harrisons-rag-system`
6. Copy the key (format: `sk-proj-...`)
7. ⚠️ **Save immediately** - only shown once!
8. Set up billing: https://platform.openai.com/account/billing
9. Add $10-20 credit to start

**Cost estimates:**
- Embedding generation (one-time): ~$0.50
- Query costs: ~$0.01-0.05 per query
- Monthly estimate: $5-20 depending on usage

## 1.2 Create Project Structure

```bash
# Navigate to your project folder
cd "/Users/maayan/medicinal rag"

# Create project structure
mkdir -p backend/tests
mkdir -p data/processed/chunks
mkdir -p data/embeddings
mkdir -p watch-app
mkdir -p scripts
mkdir -p docs

# Create initial files
touch backend/__init__.py
touch backend/config.py
touch backend/models.py
touch backend/pdf_processor.py
touch backend/embeddings.py
touch backend/vector_store.py
touch backend/hierarchical_search.py
touch backend/main.py
touch backend/requirements.txt
touch backend/.env
touch backend/.env.example
touch .gitignore
```

## 1.3 Create .gitignore

Create `.gitignore` file:

```gitignore
# API Keys and Secrets
.env
*.env
secrets/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data files
data/processed/
data/embeddings/
*.pdf

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

## 1.4 Initialize Python Virtual Environment

```bash
cd "/Users/maayan/medicinal rag/backend"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## 1.5 Create requirements.txt

Create `backend/requirements.txt`:

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# OpenAI
openai==1.12.0

# Vector Database
pinecone-client==3.0.0
# chromadb==0.4.22  # Alternative to Pinecone

# LangChain (for easier integration)
langchain==0.1.4
langchain-openai==0.0.5
langchain-community==0.0.16

# PDF Processing
PyMuPDF==1.23.20  # fitz
pdfplumber==0.10.3

# Utilities
python-multipart==0.0.6
httpx==0.26.0
aiofiles==23.2.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

## 1.6 Install Dependencies

```bash
# Make sure venv is activated
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

## 1.7 Configure Environment Variables

Create `backend/.env.example`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4-turbo-preview

# Pinecone Configuration (if using)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=harrisons-medical

# ChromaDB Configuration (if using instead of Pinecone)
CHROMA_PERSIST_DIRECTORY=../data/chroma_db

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
MAX_RESULTS=10

# GCP Configuration
GCP_PROJECT_ID=flingoos-bridge
GCS_BUCKET_NAME=harrisons-pdf-storage

# PDF Paths
HARRISON_PDF_PATH=../data/Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf
```

**Then create actual `.env` file:**

```bash
cp backend/.env.example backend/.env
# Now edit backend/.env and add your actual API keys
```

## 1.8 Create Basic Configuration Module

Create `backend/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-large"
    openai_chat_model: str = "gpt-4-turbo-preview"
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "harrisons-medical"
    
    # ChromaDB
    chroma_persist_directory: str = "../data/chroma_db"
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    max_results: int = 10
    
    # GCP
    gcp_project_id: str = "flingoos-bridge"
    gcs_bucket_name: str = "harrisons-pdf-storage"
    
    # PDF
    harrison_pdf_path: str = "../data/Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

**✅ Testing Phase 1:**

Create `backend/test_config.py`:

```python
from config import settings

def test_configuration():
    """Test that all required configuration is loaded"""
    print("Testing configuration...")
    
    # Test OpenAI
    assert settings.openai_api_key, "OpenAI API key not set!"
    assert settings.openai_api_key.startswith("sk-"), "Invalid OpenAI API key format"
    print(f"✅ OpenAI API Key: {settings.openai_api_key[:10]}...")
    
    # Test paths
    import os
    pdf_path = settings.harrison_pdf_path
    if os.path.exists(pdf_path):
        print(f"✅ Harrison's PDF found: {pdf_path}")
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"   File size: {file_size:.2f} MB")
    else:
        print(f"⚠️  Harrison's PDF not found at: {pdf_path}")
    
    print(f"✅ GCP Project: {settings.gcp_project_id}")
    print("\n✅ All configuration tests passed!")

if __name__ == "__main__":
    test_configuration()
```

**Run test:**
```bash
cd backend
source venv/bin/activate
python test_config.py
```

---

# Phase 2: PDF Structure Analysis

## 2.1 Manual Structure Discovery

**Your Task:** Analyze Harrison's table of contents

1. Open the PDF: `Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf`
2. Find the Table of Contents (usually pages 5-20)
3. Document the structure in a spreadsheet or text file

**Template to fill out:**

```
Part Number | Part Name | Start Page | End Page | Chapter Count
------------|-----------|------------|----------|---------------
1 | Cardinal Manifestations... | 10 | 200 | 20
2 | ... | ... | ... | ...

Chapter Number | Chapter Name | Part | Start Page | End Page
---------------|--------------|------|------------|----------
1 | Approach to the Patient | 1 | 10 | 15
2 | ... | ... | ... | ...
```

## 2.2 Create Initial Hierarchy Template

Create `data/hierarchy_template.json`:

```json
{
  "metadata": {
    "title": "Harrison's Principles of Internal Medicine",
    "edition": "21st",
    "year": 2022,
    "total_pages": 3600,
    "total_parts": 0,
    "total_chapters": 0
  },
  "parts": [
    {
      "part_number": 1,
      "part_name": "Part Name Here",
      "start_page": 0,
      "end_page": 0,
      "description": "",
      "chapters": [
        {
          "chapter_number": 1,
          "chapter_name": "Chapter Name Here",
          "start_page": 0,
          "end_page": 0,
          "topics": [
            {
              "topic_name": "Topic/Section Name",
              "start_page": 0,
              "end_page": 0,
              "subsections": []
            }
          ]
        }
      ]
    }
  ]
}
```

## 2.3 Create TOC Extraction Script

Create `scripts/extract_toc.py`:

```python
#!/usr/bin/env python3
"""
Extract Table of Contents from Harrison's PDF
"""
import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_toc_from_pdf(pdf_path: str, output_path: str = "data/extracted_toc.json"):
    """Extract TOC using PDF outline/bookmarks"""
    
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    # Get PDF outline (bookmarks)
    toc = doc.get_toc()
    
    if not toc:
        print("⚠️  No TOC/bookmarks found in PDF. Will need manual extraction.")
        return None
    
    print(f"Found {len(toc)} TOC entries")
    
    # Parse TOC structure
    structure = {
        "metadata": {
            "total_pages": len(doc),
            "toc_entries": len(toc)
        },
        "entries": []
    }
    
    for level, title, page in toc:
        entry = {
            "level": level,  # 1=Part, 2=Chapter, 3=Section
            "title": title,
            "page": page
        }
        structure["entries"].append(entry)
        print(f"  Level {level}: {title} (page {page})")
    
    # Save extracted TOC
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ TOC saved to: {output_file}")
    doc.close()
    return structure

def analyze_toc_patterns(toc_file: str = "data/extracted_toc.json"):
    """Analyze TOC to identify Parts, Chapters, Sections"""
    
    with open(toc_file, 'r') as f:
        data = json.load(f)
    
    print("\n📊 Analyzing TOC Structure...")
    
    # Count by level
    levels = {}
    for entry in data["entries"]:
        level = entry["level"]
        levels[level] = levels.get(level, 0) + 1
    
    print(f"\nLevel distribution:")
    for level, count in sorted(levels.items()):
        print(f"  Level {level}: {count} entries")
    
    # Pattern detection
    print("\n🔍 Pattern Detection:")
    
    # Look for "Part" indicators
    parts = [e for e in data["entries"] if re.search(r'\bPart\s+\d+', e["title"], re.I)]
    print(f"  Found {len(parts)} 'Part' entries")
    
    # Look for "Chapter" indicators  
    chapters = [e for e in data["entries"] if re.search(r'\bChapter\s+\d+', e["title"], re.I)]
    print(f"  Found {len(chapters)} 'Chapter' entries")
    
    return data

if __name__ == "__main__":
    import sys
    
    pdf_path = "../Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf"
    
    # Extract TOC
    structure = extract_toc_from_pdf(pdf_path)
    
    if structure:
        # Analyze patterns
        analyze_toc_patterns()
    else:
        print("\n❌ Could not extract TOC automatically.")
        print("   You'll need to manually create the hierarchy structure.")
```

**✅ Testing Phase 2:**

```bash
cd "/Users/maayan/medicinal rag"
source backend/venv/bin/activate
python scripts/extract_toc.py
```

**Expected output:** 
- `data/extracted_toc.json` created
- Console output showing TOC structure
- Part/Chapter counts

**If TOC extraction fails:** You'll need to manually create the hierarchy by reading the PDF.

---

# Phase 3: PDF Processing & Text Extraction

## 3.1 Create PDF Processor Module

Create `backend/pdf_processor.py`:

```python
"""
PDF Processing for Harrison's Medical Textbook
Extracts text, identifies sections, and maintains hierarchy
"""
import fitz  # PyMuPDF
import json
from pathlib import Path
from typing import Dict, List, Optional
import re
from dataclasses import dataclass, asdict

@dataclass
class Topic:
    """Represents a topic/section within a chapter"""
    topic_id: str
    topic_name: str
    start_page: int
    end_page: int
    text_content: str
    preview: str  # First 120 chars
    word_count: int
    has_tables: List[str]
    has_figures: List[str]

@dataclass
class Chapter:
    """Represents a chapter"""
    chapter_id: str
    chapter_number: int
    chapter_name: str
    part_number: int
    start_page: int
    end_page: int
    topics: List[Topic]

@dataclass
class Part:
    """Represents a major part/section"""
    part_id: str
    part_number: int
    part_name: str
    start_page: int
    end_page: int
    chapters: List[Chapter]

class HarrisonPDFProcessor:
    """Process Harrison's PDF into structured hierarchy"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        print(f"Loaded PDF: {self.total_pages} pages")
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page"""
        page = self.doc[page_num - 1]  # 0-indexed
        text = page.get_text("text")
        return text
    
    def extract_text_from_range(self, start_page: int, end_page: int) -> str:
        """Extract text from a range of pages"""
        text_parts = []
        for page_num in range(start_page, end_page + 1):
            if page_num > self.total_pages:
                break
            text = self.extract_text_from_page(page_num)
            text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def find_tables_in_range(self, start_page: int, end_page: int) -> List[str]:
        """Find table references in page range"""
        text = self.extract_text_from_range(start_page, end_page)
        
        # Look for "Table X-Y" patterns
        table_pattern = r'Table\s+\d+[-\.]?\d*'
        tables = re.findall(table_pattern, text, re.I)
        
        # Deduplicate and return
        return list(set(tables))
    
    def find_figures_in_range(self, start_page: int, end_page: int) -> List[str]:
        """Find figure references in page range"""
        text = self.extract_text_from_range(start_page, end_page)
        
        # Look for "Figure X-Y" patterns
        figure_pattern = r'Figure\s+\d+[-\.]?\d*'
        figures = re.findall(figure_pattern, text, re.I)
        
        return list(set(figures))
    
    def create_preview(self, text: str, max_length: int = 120) -> str:
        """Create preview text (first meaningful sentence)"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Get first max_length characters
        preview = text[:max_length]
        
        # Try to end at sentence boundary
        if len(text) > max_length:
            last_period = preview.rfind('.')
            if last_period > max_length * 0.5:  # At least halfway
                preview = preview[:last_period + 1]
            else:
                preview += "..."
        
        return preview
    
    def process_hierarchy_file(self, hierarchy_file: str) -> List[Part]:
        """Process PDF based on hierarchy JSON file"""
        
        print(f"\n📖 Processing PDF with hierarchy from: {hierarchy_file}")
        
        with open(hierarchy_file, 'r') as f:
            hierarchy = json.load(f)
        
        processed_parts = []
        
        for part_data in hierarchy.get('parts', []):
            print(f"\n📚 Processing {part_data['part_name']}...")
            
            chapters = []
            for chapter_data in part_data.get('chapters', []):
                print(f"  📄 Chapter {chapter_data['chapter_number']}: {chapter_data['chapter_name']}")
                
                topics = []
                for topic_data in chapter_data.get('topics', []):
                    print(f"    📍 {topic_data['topic_name']} (pages {topic_data['start_page']}-{topic_data['end_page']})")
                    
                    # Extract content
                    text = self.extract_text_from_range(
                        topic_data['start_page'],
                        topic_data['end_page']
                    )
                    
                    # Find references
                    tables = self.find_tables_in_range(
                        topic_data['start_page'],
                        topic_data['end_page']
                    )
                    
                    figures = self.find_figures_in_range(
                        topic_data['start_page'],
                        topic_data['end_page']
                    )
                    
                    # Create topic
                    topic = Topic(
                        topic_id=f"part{part_data['part_number']}_ch{chapter_data['chapter_number']}_{self._slugify(topic_data['topic_name'])}",
                        topic_name=topic_data['topic_name'],
                        start_page=topic_data['start_page'],
                        end_page=topic_data['end_page'],
                        text_content=text,
                        preview=self.create_preview(text),
                        word_count=len(text.split()),
                        has_tables=tables,
                        has_figures=figures
                    )
                    
                    topics.append(topic)
                
                # Create chapter
                chapter = Chapter(
                    chapter_id=f"part{part_data['part_number']}_ch{chapter_data['chapter_number']}",
                    chapter_number=chapter_data['chapter_number'],
                    chapter_name=chapter_data['chapter_name'],
                    part_number=part_data['part_number'],
                    start_page=chapter_data['start_page'],
                    end_page=chapter_data['end_page'],
                    topics=topics
                )
                
                chapters.append(chapter)
            
            # Create part
            part = Part(
                part_id=f"part{part_data['part_number']}",
                part_number=part_data['part_number'],
                part_name=part_data['part_name'],
                start_page=part_data['start_page'],
                end_page=part_data['end_page'],
                chapters=chapters
            )
            
            processed_parts.append(part)
        
        print(f"\n✅ Processed {len(processed_parts)} parts")
        return processed_parts
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text[:50]  # Limit length
    
    def save_processed_data(self, parts: List[Part], output_dir: str = "data/processed"):
        """Save processed data to JSON files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save complete hierarchy
        hierarchy_data = {
            "parts": [
                {
                    **asdict(part),
                    "chapters": [
                        {
                            **asdict(chapter),
                            "topics": [asdict(topic) for topic in chapter.topics]
                        }
                        for chapter in part.chapters
                    ]
                }
                for part in parts
            ]
        }
        
        hierarchy_file = output_path / "complete_hierarchy.json"
        with open(hierarchy_file, 'w', encoding='utf-8') as f:
            json.dump(hierarchy_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved complete hierarchy to: {hierarchy_file}")
        
        # Save individual topics as separate files (for easier retrieval)
        chunks_dir = output_path / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        for part in parts:
            for chapter in part.chapters:
                for topic in chapter.topics:
                    topic_file = chunks_dir / f"{topic.topic_id}.json"
                    with open(topic_file, 'w', encoding='utf-8') as f:
                        json.dump(asdict(topic), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {sum(len(c.topics) for p in parts for c in p.chapters)} topic chunks")
        
        # Create summary
        summary = {
            "total_parts": len(parts),
            "total_chapters": sum(len(p.chapters) for p in parts),
            "total_topics": sum(len(c.topics) for p in parts for c in p.chapters),
            "total_words": sum(t.word_count for p in parts for c in p.chapters for t in c.topics)
        }
        
        summary_file = output_path / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Processing summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        return hierarchy_data
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()


def main():
    """Main processing function"""
    import sys
    
    # Paths
    pdf_path = "../Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf"
    hierarchy_file = "../data/hierarchy_template.json"
    
    # Check if hierarchy file exists
    if not Path(hierarchy_file).exists():
        print(f"❌ Hierarchy file not found: {hierarchy_file}")
        print("   Please create it first by analyzing the PDF TOC.")
        sys.exit(1)
    
    # Process PDF
    processor = HarrisonPDFProcessor(pdf_path)
    
    try:
        parts = processor.process_hierarchy_file(hierarchy_file)
        processor.save_processed_data(parts)
    finally:
        processor.close()
    
    print("\n✅ PDF processing complete!")


if __name__ == "__main__":
    main()
```

## 3.2 Create Test Hierarchy

Before running the full processor, create a test hierarchy with just 1-2 chapters:

Create `data/test_hierarchy.json`:

```json
{
  "metadata": {
    "title": "Harrison's Test Processing",
    "note": "Small subset for testing"
  },
  "parts": [
    {
      "part_number": 1,
      "part_name": "Test Part 1",
      "start_page": 10,
      "end_page": 50,
      "chapters": [
        {
          "chapter_number": 1,
          "chapter_name": "Test Chapter 1",
          "start_page": 10,
          "end_page": 30,
          "topics": [
            {
              "topic_name": "Test Topic 1",
              "start_page": 10,
              "end_page": 15
            },
            {
              "topic_name": "Test Topic 2",
              "start_page": 16,
              "end_page": 20
            }
          ]
        }
      ]
    }
  ]
}
```

**✅ Testing Phase 3:**

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate

# Test with small hierarchy
python pdf_processor.py

# Check output
ls -lh ../data/processed/
cat ../data/processed/summary.json
ls ../data/processed/chunks/ | head -5
```

**Expected output:**
- `data/processed/complete_hierarchy.json` created
- `data/processed/chunks/` directory with JSON files
- `data/processed/summary.json` with statistics
- No errors during processing

---

# Phase 4: Vector Database & Embeddings

## 4.1 Choose Vector Database

**Option A: Pinecone (Recommended for Production)**
- Pros: Managed, scalable, fast
- Cons: Costs $70/month (after free tier)
- Setup: Get API key from pinecone.io

**Option B: ChromaDB (Recommended for Development)**
- Pros: Free, local, easy to start
- Cons: Need to self-host for production
- Setup: No API key needed

**For this guide, we'll use ChromaDB initially** (easier to start, can migrate to Pinecone later)

## 4.2 Create Vector Store Module

Create `backend/vector_store.py`:

```python
"""
Vector Store for Harrison's Medical RAG
Supports both ChromaDB and Pinecone
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from config import settings

class VectorStore:
    """Abstract vector store interface"""
    
    def __init__(self):
        self.client = None
        self.collection = None
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        raise NotImplementedError
    
    def search(self, query_embedding: List[float], top_k: int = 10, filter_dict: Optional[Dict] = None):
        raise NotImplementedError


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation"""
    
    def __init__(self, collection_name: str = "harrisons_medical"):
        super().__init__()
        
        # Initialize ChromaDB
        persist_dir = Path(settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.Client(Settings(
            persist_directory=str(persist_dir),
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Harrison's Principles of Internal Medicine"}
            )
            print(f"✅ Created new collection: {collection_name}")
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Add documents with embeddings to collection"""
        
        ids = [doc['id'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
        
        print(f"✅ Added {len(documents)} documents to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 10, filter_dict: Optional[Dict] = None):
        """Search for similar documents"""
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict if filter_dict else None
        )
        
        return results
    
    def count_documents(self) -> int:
        """Get total document count"""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection.name)
        print(f"✅ Deleted collection: {self.collection.name}")


class EmbeddingGenerator:
    """Generate embeddings using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        print(f"✅ Initialized embedding generator with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        
        return response.data[0].embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            print(f"  Generating embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        print(f"✅ Generated {len(all_embeddings)} embeddings")
        return all_embeddings


def load_processed_topics(processed_dir: str = "../data/processed") -> List[Dict]:
    """Load all processed topics from chunks directory"""
    
    chunks_dir = Path(processed_dir) / "chunks"
    
    if not chunks_dir.exists():
        raise FileNotFoundError(f"Chunks directory not found: {chunks_dir}")
    
    topics = []
    
    for topic_file in sorted(chunks_dir.glob("*.json")):
        with open(topic_file, 'r') as f:
            topic_data = json.load(f)
            topics.append(topic_data)
    
    print(f"✅ Loaded {len(topics)} topics")
    return topics


def prepare_documents_for_indexing(topics: List[Dict]) -> List[Dict]:
    """Convert topics to documents ready for vector store"""
    
    documents = []
    
    for topic in topics:
        # Create combined text for embedding
        # Include topic name for better semantic matching
        embedding_text = f"{topic['topic_name']}\n\n{topic['text_content']}"
        
        doc = {
            'id': topic['topic_id'],
            'text': embedding_text[:8000],  # Limit text length
            'metadata': {
                'topic_id': topic['topic_id'],
                'topic_name': topic['topic_name'],
                'start_page': topic['start_page'],
                'end_page': topic['end_page'],
                'preview': topic['preview'],
                'word_count': topic['word_count'],
                'has_tables': ','.join(topic['has_tables']) if topic['has_tables'] else '',
                'has_figures': ','.join(topic['has_figures']) if topic['has_figures'] else '',
            }
        }
        
        documents.append(doc)
    
    return documents


def index_documents():
    """Main function to index all documents"""
    
    print("\n🚀 Starting document indexing...\n")
    
    # Load processed topics
    topics = load_processed_topics()
    
    # Prepare documents
    documents = prepare_documents_for_indexing(topics)
    
    # Generate embeddings
    print("\n📊 Generating embeddings...")
    generator = EmbeddingGenerator()
    texts = [doc['text'] for doc in documents]
    embeddings = generator.generate_embeddings_batch(texts)
    
    # Initialize vector store
    print("\n💾 Storing in vector database...")
    vector_store = ChromaVectorStore()
    
    # Add documents
    vector_store.add_documents(documents, embeddings)
    
    # Verify
    count = vector_store.count_documents()
    print(f"\n✅ Indexing complete! Total documents: {count}")
    
    return vector_store


if __name__ == "__main__":
    index_documents()
```

**✅ Testing Phase 4:**

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate

# Index documents (this will cost ~$0.01-0.50 in OpenAI API calls)
python vector_store.py
```

**Expected output:**
- Embeddings generated for all topics
- ChromaDB collection created
- No errors
- Summary showing total documents indexed

**Test retrieval:**

Create `backend/test_vector_store.py`:

```python
from vector_store import ChromaVectorStore, EmbeddingGenerator

def test_search():
    """Test vector store search"""
    
    print("🧪 Testing vector store search...\n")
    
    # Initialize
    vector_store = ChromaVectorStore()
    generator = EmbeddingGenerator()
    
    # Test queries
    test_queries = [
        "basal cell carcinoma treatment",
        "acute myocardial infarction",
        "diabetes mellitus type 2"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("=" * 50)
        
        # Generate query embedding
        query_embedding = generator.generate_embedding(query)
        
        # Search
        results = vector_store.search(query_embedding, top_k=3)
        
        # Display results
        for i, (doc_id, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"\n  Result {i+1}:")
            print(f"    Topic: {metadata['topic_name']}")
            print(f"    Pages: {metadata['start_page']}-{metadata['end_page']}")
            print(f"    Preview: {metadata['preview']}")
            print(f"    Relevance: {1 - distance:.3f}")
    
    print("\n✅ Search test complete!")

if __name__ == "__main__":
    test_search()
```

Run test:
```bash
python test_vector_store.py
```

---

# Phase 5: Hierarchical Search Implementation

## 5.1 Create Models

Create `backend/models.py`:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    """Request model for search endpoint"""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(10, ge=1, le=50)

class TopicResult(BaseModel):
    """Single topic result"""
    topic_id: str
    topic_name: str
    hierarchy: str  # e.g., "Part 4 > Ch 81 > Nonmelanoma Skin Cancers"
    preview: str
    pages: str  # e.g., "543-547"
    start_page: int
    end_page: int
    relevance_score: float
    tables: List[str] = []
    figures: List[str] = []

class SearchResponse(BaseModel):
    """Response model for search endpoint"""
    query: str
    results: List[TopicResult]
    total_results: int
    search_time_ms: int

class TopicDetail(BaseModel):
    """Detailed topic information"""
    topic_id: str
    topic_name: str
    hierarchy: str
    start_page: int
    end_page: int
    text_content: str
    preview: str
    word_count: int
    tables: List[str]
    figures: List[str]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    vector_store_count: int
```

## 5.2 Create Hierarchical Search

Create `backend/hierarchical_search.py`:

```python
"""
Hierarchical search implementation for Harrison's RAG
Searches: Part → Chapter → Topic
"""
import time
from typing import List, Dict, Optional
import json
from pathlib import Path
from vector_store import ChromaVectorStore, EmbeddingGenerator
from models import TopicResult

class HierarchicalSearch:
    """Implements 3-level hierarchical search"""
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.generator = EmbeddingGenerator()
        self.hierarchy = self._load_hierarchy()
        print("✅ Hierarchical search initialized")
    
    def _load_hierarchy(self) -> Dict:
        """Load complete hierarchy for metadata"""
        hierarchy_file = Path("../data/processed/complete_hierarchy.json")
        
        if not hierarchy_file.exists():
            print("⚠️  Hierarchy file not found, continuing without it")
            return {}
        
        with open(hierarchy_file, 'r') as f:
            return json.load(f)
    
    def search(self, query: str, max_results: int = 10, min_relevance: float = 0.5) -> List[TopicResult]:
        """
        Hierarchical search across Harrison's
        Returns all matching topics with relevance > threshold
        """
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.generator.generate_embedding(query)
        
        # Search vector store (flat search for now)
        # In a more advanced implementation, you could filter by part/chapter
        raw_results = self.vector_store.search(
            query_embedding,
            top_k=max_results * 2  # Get more to filter
        )
        
        # Convert to TopicResult objects
        results = []
        
        for i, (doc_id, metadata, distance) in enumerate(zip(
            raw_results['ids'][0],
            raw_results['metadatas'][0],
            raw_results['distances'][0]
        )):
            # Calculate relevance score (1 - distance)
            relevance = 1 - distance
            
            if relevance < min_relevance:
                continue
            
            # Parse metadata
            tables = metadata.get('has_tables', '').split(',') if metadata.get('has_tables') else []
            figures = metadata.get('has_figures', '').split(',') if metadata.get('has_figures') else []
            
            # Create hierarchy string
            hierarchy = self._build_hierarchy_string(metadata['topic_id'])
            
            result = TopicResult(
                topic_id=metadata['topic_id'],
                topic_name=metadata['topic_name'],
                hierarchy=hierarchy,
                preview=metadata['preview'],
                pages=f"{metadata['start_page']}-{metadata['end_page']}",
                start_page=metadata['start_page'],
                end_page=metadata['end_page'],
                relevance_score=round(relevance, 3),
                tables=[t.strip() for t in tables if t.strip()],
                figures=[f.strip() for f in figures if f.strip()]
            )
            
            results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to max_results
        results = results[:max_results]
        
        search_time = int((time.time() - start_time) * 1000)
        print(f"🔍 Search completed in {search_time}ms, found {len(results)} results")
        
        return results, search_time
    
    def _build_hierarchy_string(self, topic_id: str) -> str:
        """Build human-readable hierarchy string"""
        
        # Parse topic_id: part4_ch81_nonmelanoma
        parts = topic_id.split('_')
        
        if len(parts) < 2:
            return "Unknown"
        
        part_str = parts[0].replace('part', 'Part ')
        chapter_str = parts[1].replace('ch', 'Ch ')
        
        # Try to find full names from hierarchy
        # For now, just return simple version
        return f"{part_str} > {chapter_str}"
    
    def get_topic_details(self, topic_id: str) -> Optional[Dict]:
        """Get full details for a specific topic"""
        
        topic_file = Path(f"../data/processed/chunks/{topic_id}.json")
        
        if not topic_file.exists():
            return None
        
        with open(topic_file, 'r') as f:
            return json.load(f)


# Global instance
search_engine = None

def get_search_engine() -> HierarchicalSearch:
    """Get or create search engine instance"""
    global search_engine
    
    if search_engine is None:
        search_engine = HierarchicalSearch()
    
    return search_engine


if __name__ == "__main__":
    # Test search
    engine = HierarchicalSearch()
    
    test_queries = [
        "myocardial infarction treatment",
        "diabetes management",
        "skin cancer"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        results, time_ms = engine.search(query, max_results=5)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.topic_name}")
            print(f"   {result.hierarchy}")
            print(f"   Pages: {result.pages}")
            print(f"   Relevance: {result.relevance_score:.3f}")
            print(f"   Preview: {result.preview}")
```

**✅ Testing Phase 5:**

```bash
python hierarchical_search.py
```

---

# Phase 6: FastAPI Backend

## 6.1 Create Main API

Create `backend/main.py`:

```python
"""
FastAPI Backend for Harrison's Medical RAG System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from typing import Optional

from models import (
    SearchRequest,
    SearchResponse,
    TopicDetail,
    HealthResponse
)
from hierarchical_search import get_search_engine
from vector_store import ChromaVectorStore

# Initialize FastAPI app
app = FastAPI(
    title="Harrison's Medical RAG API",
    description="Hierarchical RAG system for Harrison's Principles of Internal Medicine",
    version="1.0.0"
)

# Add CORS middleware (for web/mobile clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Harrison's Medical RAG API...")
    get_search_engine()  # Initialize search engine
    print("✅ API ready!")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Harrison's Medical RAG API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "topic": "/api/topic/{topic_id}",
            "health": "/health"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        vector_store = ChromaVectorStore()
        count = vector_store.count_documents()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vector_store_count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_harrisons(request: SearchRequest):
    """
    Search Harrison's using hierarchical RAG
    
    Returns matching topics with page numbers and relevance scores
    """
    try:
        search_engine = get_search_engine()
        
        results, search_time_ms = search_engine.search(
            query=request.query,
            max_results=request.max_results
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/topic/{topic_id}", response_model=TopicDetail)
async def get_topic(topic_id: str):
    """
    Get full details for a specific topic
    """
    try:
        search_engine = get_search_engine()
        topic_data = search_engine.get_topic_details(topic_id)
        
        if not topic_data:
            raise HTTPException(status_code=404, detail=f"Topic not found: {topic_id}")
        
        # Build hierarchy string
        hierarchy = search_engine._build_hierarchy_string(topic_id)
        
        return TopicDetail(
            topic_id=topic_data['topic_id'],
            topic_name=topic_data['topic_name'],
            hierarchy=hierarchy,
            start_page=topic_data['start_page'],
            end_page=topic_data['end_page'],
            text_content=topic_data['text_content'],
            preview=topic_data['preview'],
            word_count=topic_data['word_count'],
            tables=topic_data['has_tables'],
            figures=topic_data['has_figures']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 6.2 Create Run Script

Create `backend/run.sh`:

```bash
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Make it executable:
```bash
chmod +x backend/run.sh
```

**✅ Testing Phase 6:**

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate

# Start server
python main.py

# Or use the run script
./run.sh
```

**In another terminal, test the API:**

```bash
# Health check
curl http://localhost:8000/health

# Search test
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "myocardial infarction", "max_results": 5}'

# Get topic details
curl http://localhost:8000/api/topic/part1_ch1_test_topic_1
```

**Or open in browser:**
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

---

# Phase 7: Testing & Validation

## 7.1 Create Comprehensive Test Suite

Create `backend/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append('..')

from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store_count" in data

def test_search_basic():
    """Test basic search"""
    response = client.post("/api/search", json={
        "query": "heart disease",
        "max_results": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_results" in data
    assert len(data["results"]) <= 5

def test_search_medical_terms():
    """Test medical terminology search"""
    queries = [
        "myocardial infarction",
        "diabetes mellitus",
        "hypertension treatment",
        "pneumonia antibiotics"
    ]
    
    for query in queries:
        response = client.post("/api/search", json={
            "query": query,
            "max_results": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] >= 0
        print(f"✅ Query '{query}': {data['total_results']} results")

def test_search_empty_query():
    """Test empty query handling"""
    response = client.post("/api/search", json={
        "query": "",
        "max_results": 5
    })
    assert response.status_code == 422  # Validation error

def test_search_max_results_validation():
    """Test max_results validation"""
    # Too high
    response = client.post("/api/search", json={
        "query": "test",
        "max_results": 100
    })
    assert response.status_code == 422
    
    # Valid
    response = client.post("/api/search", json={
        "query": "test",
        "max_results": 10
    })
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## 7.2 Create Manual Test Script

Create `backend/test_medical_queries.py`:

```python
"""
Manual testing with clinically relevant queries
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_query(query: str, expected_topics: list = None):
    """Test a single query and validate results"""
    
    print(f"\n{'='*70}")
    print(f"🔍 Query: {query}")
    print('='*70)
    
    response = requests.post(
        f"{API_URL}/api/search",
        json={"query": query, "max_results": 5}
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return False
    
    data = response.json()
    
    print(f"\n📊 Found {data['total_results']} results in {data['search_time_ms']}ms\n")
    
    for i, result in enumerate(data['results'], 1):
        print(f"{i}. {result['topic_name']}")
        print(f"   📍 {result['hierarchy']}")
        print(f"   📄 Pages: {result['pages']}")
        print(f"   📈 Relevance: {result['relevance_score']:.3f}")
        print(f"   💬 {result['preview'][:100]}...")
        
        if result['tables']:
            print(f"   📊 Tables: {', '.join(result['tables'][:3])}")
        if result['figures']:
            print(f"   🖼️  Figures: {', '.join(result['figures'][:3])}")
        print()
    
    # Validation
    if expected_topics:
        found_topics = [r['topic_name'].lower() for r in data['results']]
        for expected in expected_topics:
            if any(expected.lower() in topic for topic in found_topics):
                print(f"✅ Found expected topic: {expected}")
            else:
                print(f"⚠️  Missing expected topic: {expected}")
    
    return True

# Test cases with expected results
test_cases = [
    {
        "query": "acute myocardial infarction management",
        "expected": ["acute MI", "myocardial infarction", "STEMI"]
    },
    {
        "query": "type 2 diabetes treatment guidelines",
        "expected": ["diabetes", "type 2", "treatment"]
    },
    {
        "query": "basal cell carcinoma",
        "expected": ["skin cancer", "basal cell", "nonmelanoma"]
    },
    {
        "query": "DVT treatment anticoagulation",
        "expected": ["thrombosis", "anticoagulation", "DVT"]
    },
    {
        "query": "pneumonia antibiotic selection",
        "expected": ["pneumonia", "antibiotics"]
    },
    {
        "query": "hypertension first line therapy",
        "expected": ["hypertension", "treatment"]
    },
    {
        "query": "atrial fibrillation rate control",
        "expected": ["atrial fibrillation", "arrhythmia"]
    },
    {
        "query": "acute kidney injury management",
        "expected": ["kidney", "renal", "AKI"]
    }
]

def run_all_tests():
    """Run all test cases"""
    
    print("\n" + "="*70)
    print("🧪 HARRISON'S RAG SYSTEM - MEDICAL QUERY TESTING")
    print("="*70)
    
    # Check API is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print("❌ API is not healthy")
            return
        print("✅ API is running and healthy\n")
    except:
        print("❌ Cannot connect to API. Make sure server is running on port 8000")
        return
    
    # Run test cases
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            success = test_query(test_case["query"], test_case.get("expected"))
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
```

**✅ Testing Phase 7:**

```bash
# Make sure API server is running in one terminal
cd backend
python main.py

# In another terminal, run tests
cd backend
python test_medical_queries.py

# Run pytest suite
pytest tests/test_api.py -v
```

---

# Phase 8: Cloud Deployment (GCP)

## 8.1 Setup GCP Project

```bash
# Install gcloud CLI (if not already installed)
brew install --cask google-cloud-sdk

# Initialize gcloud
gcloud init

# Login
gcloud auth login

# Set project
gcloud config set project flingoos-bridge

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## 8.2 Create Cloud Storage Bucket

```bash
# Create bucket for PDFs
gsutil mb -p flingoos-bridge -l us-central1 gs://harrison-medical-pdfs

# Upload PDF
gsutil cp "/Users/maayan/medicinal rag/Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf" \
  gs://harrison-medical-pdfs/harrisons_screen.pdf

# Set permissions (private)
gsutil iam ch allUsers:objectViewer gs://harrison-medical-pdfs
```

## 8.3 Store API Keys in Secret Manager

```bash
# Store OpenAI API key
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key \
  --data-file=- \
  --project=flingoos-bridge

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 8.4 Create Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 8.5 Create Cloud Run Configuration

Create `backend/.dockerignore`:

```
venv/
__pycache__/
*.pyc
.env
.env.local
tests/
*.log
.DS_Store
```

## 8.6 Deploy to Cloud Run

Create `backend/deploy.sh`:

```bash
#!/bin/bash

# Configuration
PROJECT_ID="flingoos-bridge"
SERVICE_NAME="harrisons-api"
REGION="us-central1"

# Build and deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project=$PROJECT_ID \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --set-env-vars="APP_ENV=production" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest"

echo "✅ Deployment complete!"
```

Make executable and deploy:

```bash
chmod +x backend/deploy.sh
cd backend
./deploy.sh
```

**✅ Testing Phase 8:**

After deployment:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe harrisons-api \
  --platform managed \
  --region us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl $SERVICE_URL/health

# Test search
curl -X POST $SERVICE_URL/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "myocardial infarction", "max_results": 5}'
```

---

# Phase 9: Apple Watch App Development

## 9.1 Create Watch App Project

1. Open Xcode
2. File → New → Project
3. Choose "Watch App"
4. Product Name: `HarrisonsWatch`
5. Organization Identifier: `com.yourname.harrisons`
6. Interface: SwiftUI
7. Language: Swift

## 9.2 Project Structure

```
HarrisonsWatch/
├── HarrisonsWatch Watch App/
│   ├── HarrisonsWatchApp.swift
│   ├── ContentView.swift
│   ├── Views/
│   │   ├── SearchView.swift
│   │   ├── ResultsListView.swift
│   │   ├── TopicDetailView.swift
│   │   └── PDFViewerView.swift
│   ├── Models/
│   │   ├── SearchModels.swift
│   │   └── APIClient.swift
│   ├── Services/
│   │   ├── NetworkService.swift
│   │   └── VoiceService.swift
│   └── Assets.xcassets/
```

## 9.3 Create API Client

Create `Models/SearchModels.swift`:

```swift
import Foundation

struct SearchRequest: Codable {
    let query: String
    let maxResults: Int
    
    enum CodingKeys: String, CodingKey {
        case query
        case maxResults = "max_results"
    }
}

struct TopicResult: Codable, Identifiable {
    let topicId: String
    let topicName: String
    let hierarchy: String
    let preview: String
    let pages: String
    let startPage: Int
    let endPage: Int
    let relevanceScore: Double
    let tables: [String]
    let figures: [String]
    
    var id: String { topicId }
    
    enum CodingKeys: String, CodingKey {
        case topicId = "topic_id"
        case topicName = "topic_name"
        case hierarchy, preview, pages
        case startPage = "start_page"
        case endPage = "end_page"
        case relevanceScore = "relevance_score"
        case tables, figures
    }
}

struct SearchResponse: Codable {
    let query: String
    let results: [TopicResult]
    let totalResults: Int
    let searchTimeMs: Int
    
    enum CodingKeys: String, CodingKey {
        case query, results
        case totalResults = "total_results"
        case searchTimeMs = "search_time_ms"
    }
}
```

Create `Models/APIClient.swift`:

```swift
import Foundation

class APIClient: ObservableObject {
    static let shared = APIClient()
    
    // Update with your Cloud Run URL
    private let baseURL = "YOUR_CLOUD_RUN_URL_HERE"
    
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func search(query: String, maxResults: Int = 10) async throws -> SearchResponse {
        isLoading = true
        defer { isLoading = false }
        
        let url = URL(string: "\(baseURL)/api/search")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let searchRequest = SearchRequest(query: query, maxResults: maxResults)
        request.httpBody = try JSONEncoder().encode(searchRequest)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let searchResponse = try JSONDecoder().decode(SearchResponse.self, from: data)
        return searchResponse
    }
}
```

## 9.4 Create Search View

Create `Views/SearchView.swift`:

```swift
import SwiftUI

struct SearchView: View {
    @StateObject private var apiClient = APIClient.shared
    @State private var searchQuery = ""
    @State private var searchResults: [TopicResult] = []
    @State private var isSearching = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Search input
                TextField("Search Harrison's", text: $searchQuery)
                    .textFieldStyle(.roundedBorder)
                    .padding()
                    .submitLabel(.search)
                    .onSubmit {
                        performSearch()
                    }
                
                // Voice search button
                Button(action: {
                    // Voice search (Phase 10)
                }) {
                    Image(systemName: "mic.fill")
                        .font(.title2)
                }
                .buttonStyle(.bordered)
                
                // Results
                if isSearching {
                    ProgressView()
                        .padding()
                } else if !searchResults.isEmpty {
                    ResultsListView(results: searchResults)
                } else {
                    Text("Search for medical topics")
                        .foregroundColor(.secondary)
                        .padding()
                }
                
                Spacer()
            }
            .navigationTitle("Harrison's")
        }
    }
    
    private func performSearch() {
        guard !searchQuery.isEmpty else { return }
        
        isSearching = true
        
        Task {
            do {
                let response = try await apiClient.search(query: searchQuery)
                await MainActor.run {
                    searchResults = response.results
                    isSearching = false
                }
            } catch {
                await MainActor.run {
                    isSearching = false
                    // Handle error
                }
            }
        }
    }
}
```

## 9.5 Create Results List View

Create `Views/ResultsListView.swift`:

```swift
import SwiftUI

struct ResultsListView: View {
    let results: [TopicResult]
    
    var body: some View {
        List(results) { result in
            NavigationLink(destination: TopicDetailView(topic: result)) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(result.topicName)
                        .font(.headline)
                        .lineLimit(2)
                    
                    Text(result.hierarchy)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text("📄 Pages \(result.pages)")
                        .font(.caption2)
                        .foregroundColor(.blue)
                    
                    Text(result.preview)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                .padding(.vertical, 4)
            }
        }
    }
}
```

## 9.6 Create Topic Detail View

Create `Views/TopicDetailView.swift`:

```swift
import SwiftUI

struct TopicDetailView: View {
    let topic: TopicResult
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                // Header
                Text(topic.topicName)
                    .font(.headline)
                
                Text(topic.hierarchy)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Divider()
                
                // Preview
                VStack(alignment: .leading, spacing: 8) {
                    Label("Summary", systemImage: "doc.text.magnifyingglass")
                        .font(.subheadline)
                        .bold()
                    
                    Text(topic.preview)
                        .font(.caption)
                        .padding(8)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
                
                Divider()
                    .background(Color.blue)
                
                // Open PDF button
                NavigationLink(destination: PDFViewerView(startPage: topic.startPage, endPage: topic.endPage)) {
                    HStack {
                        Image(systemName: "doc.fill")
                        Text("View in PDF")
                        Text("Pages \(topic.pages)")
                            .font(.caption2)
                    }
                }
                .buttonStyle(.bordered)
                
                // Tables and Figures
                if !topic.tables.isEmpty {
                    VStack(alignment: .leading) {
                        Text("📊 Tables")
                            .font(.caption)
                            .bold()
                        ForEach(topic.tables, id: \.self) { table in
                            Text(table)
                                .font(.caption2)
                        }
                    }
                }
                
                if !topic.figures.isEmpty {
                    VStack(alignment: .leading) {
                        Text("🖼️ Figures")
                            .font(.caption)
                            .bold()
                        ForEach(topic.figures, id: \.self) { figure in
                            Text(figure)
                                .font(.caption2)
                        }
                    }
                }
            }
            .padding()
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

**✅ Testing Phase 9:**

1. Build and run on Apple Watch simulator
2. Test search functionality
3. Test results display
4. Test navigation

---

# Phase 10: Voice Integration

## 10.1 Add Speech Recognition

Add capability in Xcode:
1. Select project → Capabilities
2. Enable "Speech Recognition"
3. Add to Info.plist:
   - `NSSpeechRecognitionUsageDescription`: "To search Harrison's with voice"

## 10.2 Create Voice Service

Create `Services/VoiceService.swift`:

```swift
import Speech
import AVFoundation

class VoiceService: ObservableObject {
    @Published var transcribedText = ""
    @Published var isRecording = false
    @Published var isAuthorized = false
    
    private var audioEngine: AVAudioEngine?
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    
    init() {
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        requestAuthorization()
    }
    
    func requestAuthorization() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            DispatchQueue.main.async {
                self.isAuthorized = (authStatus == .authorized)
            }
        }
    }
    
    func startRecording(completion: @escaping (String) -> Void) {
        guard isAuthorized else {
            print("Not authorized for speech recognition")
            return
        }
        
        // Cancel any existing task
        if let recognitionTask = recognitionTask {
            recognitionTask.cancel()
            self.recognitionTask = nil
        }
        
        // Setup audio session
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("Audio session setup failed: \(error)")
            return
        }
        
        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }
        recognitionRequest.shouldReportPartialResults = true
        
        // Setup audio engine
        audioEngine = AVAudioEngine()
        guard let audioEngine = audioEngine else { return }
        
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        audioEngine.prepare()
        
        do {
            try audioEngine.start()
        } catch {
            print("Audio engine failed to start: \(error)")
            return
        }
        
        isRecording = true
        
        // Start recognition
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            guard let self = self else { return }
            
            if let result = result {
                let transcription = result.bestTranscription.formattedString
                DispatchQueue.main.async {
                    self.transcribedText = transcription
                }
                
                if result.isFinal {
                    self.stopRecording()
                    completion(transcription)
                }
            }
            
            if error != nil {
                self.stopRecording()
            }
        }
    }
    
    func stopRecording() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        isRecording = false
    }
}
```

## 10.3 Update Search View with Voice

Update `Views/SearchView.swift`:

```swift
import SwiftUI

struct SearchView: View {
    @StateObject private var apiClient = APIClient.shared
    @StateObject private var voiceService = VoiceService()
    @State private var searchQuery = ""
    @State private var searchResults: [TopicResult] = []
    @State private var isSearching = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Search input
                TextField("Search Harrison's", text: $searchQuery)
                    .textFieldStyle(.roundedBorder)
                    .padding()
                    .submitLabel(.search)
                    .onSubmit {
                        performSearch()
                    }
                
                // Voice search button
                Button(action: {
                    if voiceService.isRecording {
                        voiceService.stopRecording()
                    } else {
                        startVoiceSearch()
                    }
                }) {
                    Image(systemName: voiceService.isRecording ? "mic.fill" : "mic")
                        .font(.title2)
                        .foregroundColor(voiceService.isRecording ? .red : .blue)
                }
                .buttonStyle(.bordered)
                
                // Show transcription
                if voiceService.isRecording {
                    Text(voiceService.transcribedText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding()
                }
                
                // Results
                if isSearching {
                    ProgressView()
                        .padding()
                } else if !searchResults.isEmpty {
                    ResultsListView(results: searchResults)
                } else {
                    Text("Search for medical topics")
                        .foregroundColor(.secondary)
                        .padding()
                }
                
                Spacer()
            }
            .navigationTitle("Harrison's")
        }
    }
    
    private func startVoiceSearch() {
        voiceService.startRecording { transcription in
            searchQuery = transcription
            performSearch()
        }
    }
    
    private func performSearch() {
        guard !searchQuery.isEmpty else { return }
        
        isSearching = true
        
        Task {
            do {
                let response = try await apiClient.search(query: searchQuery)
                await MainActor.run {
                    searchResults = response.results
                    isSearching = false
                }
            } catch {
                await MainActor.run {
                    isSearching = false
                    apiClient.errorMessage = error.localizedDescription
                }
            }
        }
    }
}
```

**✅ Testing Phase 10:**

1. Build and run on Apple Watch
2. Tap microphone button
3. Speak: "myocardial infarction treatment"
4. Verify transcription appears
5. Verify search is performed
6. Check results display

---

# Phase 11: PDF Display on Watch

## 11.1 Add PDF Support

Create `Views/PDFViewerView.swift`:

```swift
import SwiftUI
import PDFKit

struct PDFViewerView: View {
    let startPage: Int
    let endPage: Int
    
    @State private var currentPage: Int
    @State private var isLoading = true
    @State private var pdfDocument: PDFDocument?
    
    init(startPage: Int, endPage: Int) {
        self.startPage = startPage
        self.endPage = endPage
        _currentPage = State(initialValue: startPage)
    }
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView("Loading PDF...")
            } else if let document = pdfDocument {
                PDFViewRepresentable(
                    document: document,
                    currentPage: $currentPage
                )
                
                // Page controls
                HStack {
                    Button(action: previousPage) {
                        Image(systemName: "chevron.left")
                    }
                    .disabled(currentPage <= startPage)
                    
                    Text("Page \(currentPage)")
                        .font(.caption2)
                    
                    Button(action: nextPage) {
                        Image(systemName: "chevron.right")
                    }
                    .disabled(currentPage >= endPage)
                }
                .padding()
            } else {
                Text("Failed to load PDF")
            }
        }
        .onAppear {
            loadPDF()
        }
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func loadPDF() {
        // In production, download from GCS
        // For now, assume PDF is in bundle
        guard let url = Bundle.main.url(forResource: "harrisons", withExtension: "pdf"),
              let document = PDFDocument(url: url) else {
            isLoading = false
            return
        }
        
        pdfDocument = document
        isLoading = false
    }
    
    private func previousPage() {
        if currentPage > startPage {
            currentPage -= 1
        }
    }
    
    private func nextPage() {
        if currentPage < endPage {
            currentPage += 1
        }
    }
}

struct PDFViewRepresentable: WKInterfaceObjectRepresentable {
    let document: PDFDocument
    @Binding var currentPage: Int
    
    func makeWKInterfaceObject(context: Context) -> WKInterfacePDFView {
        let pdfView = WKInterfacePDFView()
        return pdfView
    }
    
    func updateWKInterfaceObject(_ pdfView: WKInterfacePDFView, context: Context) {
        if let page = document.page(at: currentPage - 1) {
            pdfView.setDocument(document)
            pdfView.goToPage(page)
        }
    }
}
```

## 11.2 Alternative: On-Demand PDF Loading

For better performance, implement on-demand page loading:

Create `Services/PDFService.swift`:

```swift
import Foundation

class PDFService {
    static let shared = PDFService()
    
    private let baseURL = "YOUR_CLOUD_RUN_URL"
    
    func downloadPages(startPage: Int, endPage: Int) async throws -> Data {
        // In a real implementation, you'd have an endpoint that returns
        // just the requested pages
        let url = URL(string: "\(baseURL)/api/pdf_pages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["start_page": startPage, "end_page": endPage]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return data
    }
}
```

**✅ Testing Phase 11:**

1. Add PDF to Watch app bundle (or implement download)
2. Test PDF display
3. Test page navigation
4. Verify readability on watch screen
5. Test pinch-to-zoom (Digital Crown)

---

# Phase 12: Production & Monitoring

## 12.1 Add Analytics

Add Firebase or custom analytics to track:
- Search queries
- Response times
- Error rates
- Most accessed topics

## 12.2 Create Monitoring Dashboard

In GCP Console:
1. Cloud Run → Select service
2. Metrics tab
3. Create custom dashboard with:
   - Request count
   - Latency
   - Error rate
   - Memory usage

## 12.3 Setup Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Harrison's API Errors" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

## 12.4 Create User Documentation

Create `docs/USER_GUIDE.md` with:
- How to use voice search
- Search tips
- Common medical queries
- Troubleshooting

## 12.5 App Store Submission

1. Complete App Store Connect setup
2. Add app description, screenshots
3. Submit for review
4. Handle feedback

**✅ Final Testing:**

1. End-to-end user journey test
2. Voice search → Results → PDF display
3. Performance testing (response times)
4. Battery usage testing
5. Different query types
6. Edge cases (no results, errors)

---

# Appendix A: Quick Reference

## Environment Variables

```bash
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=...  # If using Pinecone
GCP_PROJECT_ID=flingoos-bridge
```

## Common Commands

```bash
# Start backend
cd backend && ./run.sh

# Run tests
pytest tests/ -v

# Deploy to GCP
cd backend && ./deploy.sh

# Check logs
gcloud run logs read harrisons-api --limit 50
```

## API Endpoints

- Health: `GET /health`
- Search: `POST /api/search`
- Topic: `GET /api/topic/{topic_id}`

## Cost Estimates

- Development: ~$5-10
- Monthly production: ~$20-100
  - Cloud Run: $5-20
  - OpenAI API: $10-30
  - Vector DB: $0-70
  - Storage: $1-5

---

# Appendix B: Troubleshooting

## Common Issues

**PDF extraction fails:**
- Check PDF path in config
- Verify PDF is not password protected
- Try different extraction library

**Embeddings are expensive:**
- Limit topic text to 8000 chars
- Batch process to reduce API calls
- Use cheaper model (text-embedding-3-small)

**Search results irrelevant:**
- Adjust minimum relevance threshold
- Improve chunking strategy
- Add more context to embeddings

**Watch app crashes:**
- Check memory usage
- Reduce PDF page range
- Implement pagination

**Voice recognition fails:**
- Check microphone permissions
- Verify internet connection
- Test with simple queries first

---

# Next Steps After Implementation

1. **User Testing**: Get feedback from medical professionals
2. **Optimize Performance**: Cache common queries
3. **Add Features**: 
   - Bookmarks
   - Search history
   - Offline mode
   - Multi-language support
4. **Scale**: Move to Pinecone for production
5. **Monitor**: Track usage patterns and improve

---

**🎉 Congratulations! You now have a complete roadmap to build Harrison's Medical RAG system with Apple Watch integration!**

