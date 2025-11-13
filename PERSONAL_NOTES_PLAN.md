# 📝 Personal Notes System - Implementation Plan

**Goal**: Transform medWatcher into a dynamic, personalized medical knowledge base where you can add, search, and manage your own notes alongside Harrison's and PDFs.

---

## 🎯 Overview

### Current State
- ✅ Harrison's: 550 indexed chapters (static)
- ✅ Independent PDFs: Uploadable, indexed
- ✅ Search: Unified vector search across sources
- ❌ Personal notes: Not yet implemented

### Target State
- ✅ Harrison's: Static reference
- ✅ Independent PDFs: Managed via interface
- ✅ Personal Notes: Fully dynamic, editable
- ✅ File Management: View, delete, insert all content
- ✅ Note Editor: Quick capture from search interface

---

## 📋 PHASE 1: Content Management System

### Goal
Create a comprehensive file/content viewing and management interface to see and control everything in your RAG system.

---

### 1.1 Content Library Interface

**New Page**: `/library` or `/manage`

#### Features:
```
╔════════════════════════════════════════════════════════════════╗
║                    📚 MY MEDICAL LIBRARY                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  [All Sources ▼]  [Search: filter by name...]  [+ Add New]   ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📖 HARRISON'S PRINCIPLES                               │  ║
║  │ Type: Reference Book                                   │  ║
║  │ Chapters: 550 | Pages: 13,299 | Words: ~2.5M         │  ║
║  │ Status: ✅ Indexed | Last updated: [date]             │  ║
║  │ [View Chapters] [Search Within]                       │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📄 EM Basic: Chest Pain                               │  ║
║  │ Type: Independent PDF                                  │  ║
║  │ Pages: 2 | Words: 988 | Added: Nov 13, 2025          │  ║
║  │ Status: ✅ Indexed | Searchable: Yes                  │  ║
║  │ [View PDF] [Delete] [Re-index]                        │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📝 My Notes: Hyponatremia Cases                       │  ║
║  │ Type: Personal Note                                    │  ║
║  │ Words: 156 | Created: Nov 14, 2025                    │  ║
║  │ Tags: electrolytes, cases, endocrine                  │  ║
║  │ Status: ✅ Indexed | Last edited: 2 hours ago         │  ║
║  │ [Edit] [Delete] [Duplicate]                           │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

#### Components:

**A. Data Model** (`models.py`)
```python
class ContentSource(BaseModel):
    """Base model for all content in the system"""
    id: str
    type: Literal["harrison", "independent_pdf", "personal_note"]
    title: str
    created_at: datetime
    updated_at: datetime
    word_count: int
    is_indexed: bool
    metadata: Dict[str, Any]

class HarrisonSource(ContentSource):
    """Harrison's textbook"""
    type: Literal["harrison"] = "harrison"
    total_chapters: int
    total_pages: int

class IndependentPDFSource(ContentSource):
    """Independent PDF document"""
    type: Literal["independent_pdf"] = "independent_pdf"
    filename: str
    pdf_path: str
    total_pages: int
    file_size: int

class PersonalNote(ContentSource):
    """User's personal note"""
    type: Literal["personal_note"] = "personal_note"
    content: str
    tags: List[str]
    is_public: bool  # Future: sharing feature
```

**B. Backend API** (`main.py`)
```python
@app.get("/api/library", tags=["Library"])
async def get_library():
    """
    Get all content sources in the system
    Returns: List of all Harrison's chapters, PDFs, and notes
    """
    
@app.get("/api/library/{source_id}", tags=["Library"])
async def get_source_details(source_id: str):
    """
    Get detailed info about a specific source
    """
    
@app.delete("/api/library/{source_id}", tags=["Library"])
async def delete_source(source_id: str):
    """
    Delete a source (PDF or note, not Harrison's)
    - Remove from ChromaDB
    - Delete file/data
    - Update index
    """
    
@app.get("/api/library/stats", tags=["Library"])
async def get_library_stats():
    """
    Get statistics about the library
    Returns: Total sources, word count, storage used, etc.
    """
```

**C. Frontend** (`static/library.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Medical Library - medWatcher</title>
</head>
<body>
    <div id="library">
        <!-- Header with filters and add button -->
        <div class="library-header">
            <h1>📚 My Medical Library</h1>
            <div class="controls">
                <select id="filterType">
                    <option value="all">All Sources</option>
                    <option value="harrison">Harrison's</option>
                    <option value="pdf">PDFs</option>
                    <option value="notes">My Notes</option>
                </select>
                <input type="text" id="searchFilter" placeholder="Search library...">
                <button id="addNewBtn">+ Add New</button>
            </div>
        </div>
        
        <!-- Stats summary -->
        <div class="library-stats">
            <div class="stat-card">
                <span class="stat-value" id="totalSources">-</span>
                <span class="stat-label">Total Sources</span>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="totalWords">-</span>
                <span class="stat-label">Total Words</span>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="lastUpdated">-</span>
                <span class="stat-label">Last Updated</span>
            </div>
        </div>
        
        <!-- Content list -->
        <div id="contentList" class="content-list">
            <!-- Dynamically loaded content cards -->
        </div>
    </div>
    
    <script src="/static/library.js"></script>
</body>
</html>
```

---

### 1.2 Harrison's Chapter Browser

**Purpose**: View all 550 Harrison's chapters in a browsable tree structure

#### Features:
- Hierarchical view (Part > Chapter)
- Search/filter chapters
- Quick jump to viewer
- See indexed content for each chapter

```
╔════════════════════════════════════════════════════════════════╗
║              📖 HARRISON'S CHAPTERS (550 total)                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  🔍 [Filter chapters...]                                       ║
║                                                                ║
║  ▼ Part 1: Cardinal Manifestations of Disease                ║
║    ├─ Chapter 1: Approach to the Patient                     ║
║    ├─ Chapter 2: Global Health                               ║
║    └─ Chapter 3: Decision-Making in Medicine                 ║
║                                                                ║
║  ▼ Part 2: Cardinal Manifestations and Presentation          ║
║    ├─ Chapter 10: Chest Discomfort                           ║
║    │   Pages: 67-73 | Words: 4,521                           ║
║    │   [View] [Search Within] [View in RAG]                  ║
║    └─ ...                                                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

### 1.3 Delete Functionality

#### Safe Deletion Process:
1. **Confirmation Dialog**
   ```
   ⚠️  DELETE CONTENT?
   
   You are about to delete:
   "EM Basic: Chest Pain"
   
   This will:
   - Remove from search index
   - Delete the PDF file
   - Remove all embeddings
   
   This action cannot be undone.
   
   [Cancel]  [Delete Permanently]
   ```

2. **Backend Process** (`library_manager.py`)
```python
async def delete_source(source_id: str, source_type: str):
    """
    Complete deletion of a source
    """
    # 1. Remove from ChromaDB
    vector_store.delete_by_id(source_id)
    
    # 2. Delete chunks
    if source_type == "independent_pdf":
        delete_pdf_chunks(source_id)
        delete_pdf_file(source_id)
    elif source_type == "personal_note":
        delete_note_file(source_id)
    
    # 3. Update GCS (if deployed)
    if is_deployed():
        sync_to_gcs()
    
    # 4. Rebuild index statistics
    update_index_stats()
    
    return {"status": "deleted", "source_id": source_id}
```

3. **Undo Feature** (Nice to have)
   - Keep deleted items in "trash" for 30 days
   - Allow restoration

---

### 1.4 Insert/Upload Functionality

#### Upload Options:
```
╔════════════════════════════════════════════════════════════════╗
║                    ➕ ADD NEW CONTENT                          ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Choose content type:                                         ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📄 PDF Document                                        │  ║
║  │ Upload a medical PDF (protocols, guidelines, papers)  │  ║
║  │ [Choose File]                                          │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📝 Personal Note                                       │  ║
║  │ Write a quick medical note or case study              │  ║
║  │ [Create Note]                                          │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📋 Import from Text                                    │  ║
║  │ Paste text content from clipboard                     │  ║
║  │ [Paste & Import]                                       │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

#### Backend Upload Handler:
```python
@app.post("/api/library/upload", tags=["Library"])
async def upload_content(
    file: UploadFile = File(None),
    content_type: str = Form(...),
    title: str = Form(...),
    tags: str = Form("")
):
    """
    Upload new content (PDF or note)
    """
    if content_type == "pdf":
        # 1. Save PDF file
        pdf_path = save_uploaded_pdf(file)
        
        # 2. Process into chunks
        processor = IndependentPDFProcessor(pdf_path)
        chunks = processor.process_and_save(data_dir)
        
        # 3. Generate embeddings
        texts = [chunk['text_content'] for chunk in chunks]
        embeddings = generate_embeddings(texts, openai_client)
        
        # 4. Add to ChromaDB
        vector_store.add_documents(chunks, embeddings)
        
        # 5. Upload to GCS if deployed
        if is_deployed():
            upload_to_gcs(pdf_path)
        
        return {"status": "success", "id": pdf_id}
    
    elif content_type == "note":
        # Handle personal note (see Phase 2)
        pass
```

---

### 1.5 Search Within Library

#### Quick Filter:
- Search by title
- Filter by type (Harrison's/PDF/Notes)
- Filter by date range
- Filter by tags (for notes)
- Sort by: date, name, word count, relevance

#### Implementation:
```javascript
// Client-side filtering (fast)
function filterLibrary(query, type, dateRange) {
    const items = document.querySelectorAll('.content-card');
    items.forEach(item => {
        const title = item.dataset.title.toLowerCase();
        const itemType = item.dataset.type;
        const date = new Date(item.dataset.date);
        
        const matchesQuery = title.includes(query.toLowerCase());
        const matchesType = type === 'all' || itemType === type;
        const matchesDate = isInDateRange(date, dateRange);
        
        item.style.display = 
            matchesQuery && matchesType && matchesDate ? 'block' : 'none';
    });
}
```

---

## 📋 PHASE 2: Personal Notes System

### Goal
Enable quick note-taking directly from the search interface, with full embedding and search integration.

---

### 2.1 Quick Note Interface

#### Location: Below search bar on main page

```
╔════════════════════════════════════════════════════════════════╗
║                      🔍 SEARCH MEDICAL KNOWLEDGE               ║
║                                                                ║
║  [Search: chest pain...................................................] 🎤   ║
║  [🔍 Search]                                                   ║
║                                                                ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                ║
║  💡 Quick Note (optional - searchable later)                  ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ Type your clinical note, case study, or reminder...   │  ║
║  │                                                         │  ║
║  │ Example: "Patient presented with chest pain + ST      │  ║
║  │ elevation. Suspected STEMI. Activated cath lab."      │  ║
║  │                                                         │  ║
║  └────────────────────────────────────────────────────────┘  ║
║  Tags: [electrolytes] [case] [urgent] + Add tag           ║
║  [💾 Save Note]  [📝 Open Full Editor]                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

#### Features:
- ✅ Always visible (optional to use)
- ✅ Auto-saves to local storage (draft)
- ✅ Tag suggestions based on search query
- ✅ Character counter
- ✅ Timestamp automatically added
- ✅ Optional: attach to current search result

---

### 2.2 Note Data Structure

```python
class PersonalNote(BaseModel):
    """Personal medical note"""
    note_id: str  # UUID
    title: str  # Auto-generated or user-provided
    content: str  # The actual note text
    tags: List[str]  # User-defined tags
    created_at: datetime
    updated_at: datetime
    linked_sources: List[str]  # IDs of related content (optional)
    word_count: int
    is_indexed: bool
    metadata: Dict[str, Any]  # Extra data

# Example:
{
    "note_id": "note_uuid_12345",
    "title": "STEMI Case - Nov 14 2025",
    "content": "Patient presented with chest pain + ST elevation...",
    "tags": ["cardiology", "case", "stemi", "urgent"],
    "created_at": "2025-11-14T10:30:00Z",
    "updated_at": "2025-11-14T10:30:00Z",
    "linked_sources": ["part2_ch53_chest_pain"],
    "word_count": 156,
    "is_indexed": true,
    "metadata": {
        "search_query_context": "chest pain STEMI",
        "device": "iPhone"
    }
}
```

---

### 2.3 Note Storage

#### File Structure:
```
data/
├── personal_notes/
│   ├── note_uuid_12345.json
│   ├── note_uuid_67890.json
│   └── ...
├── processed/
│   ├── chunks/                    # Harrison's
│   ├── independent_chunks/        # PDFs
│   └── personal_note_chunks/      # Notes (NEW)
│       ├── note_uuid_12345.json
│       └── ...
└── chroma_db/                     # All embeddings
```

#### Note Processing:
```python
class PersonalNoteProcessor:
    """Process personal notes for RAG indexing"""
    
    def process_note(self, note: PersonalNote) -> Dict:
        """
        Convert note to RAG-compatible chunk
        """
        # Notes are typically short, so 1 note = 1 chunk
        chunk = {
            'chunk_id': note.note_id,
            'note_id': note.note_id,
            'title': note.title,
            'pdf_source': 'personal_note',
            'text_content': f"{note.title}\n\n{note.content}",
            'preview': self.create_preview(note.content),
            'word_count': note.word_count,
            'tags': note.tags,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'is_editable': True  # Flag for frontend
        }
        
        # Save chunk
        chunk_path = self.notes_chunks_dir / f"{note.note_id}.json"
        with open(chunk_path, 'w') as f:
            json.dump(chunk, f, indent=2)
        
        return chunk
    
    def create_preview(self, content: str, max_length: int = 120) -> str:
        """Create preview text"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
```

---

### 2.4 Note Editor

#### Full Editor Interface (`/editor` or `/notes/new`)

```
╔════════════════════════════════════════════════════════════════╗
║                    📝 NEW MEDICAL NOTE                         ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Title: [Auto-generated or custom...]                         ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  Write your note here...                               │  ║
║  │                                                         │  ║
║  │  Supports:                                             │  ║
║  │  - Plain text                                          │  ║
║  │  - Markdown formatting                                 │  ║
║  │  - Lists and bullet points                            │  ║
║  │                                                         │  ║
║  │                                                         │  ║
║  │                                                         │  ║
║  │                                                         │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  Tags: [cardiology] [case] + Add tag                         ║
║                                                                ║
║  Link to sources (optional):                                  ║
║  [+ Harrison's Chapter] [+ PDF] [+ Another Note]             ║
║                                                                ║
║  ──────────────────────────────────────────────────────────── ║
║                                                                ║
║  📊 156 words | Created: Nov 14, 2025 10:30 AM               ║
║  ✅ Will be searchable immediately after saving               ║
║                                                                ║
║  [Cancel]  [Save Draft]  [💾 Save & Index]                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

#### Features:
- Rich text editing (markdown support)
- Auto-save drafts
- Tag autocomplete
- Link to existing content
- Word count
- Preview mode
- Duplicate/template feature

---

### 2.5 Note Indexing & Search

#### Backend API:
```python
@app.post("/api/notes", tags=["Notes"])
async def create_note(note: PersonalNote):
    """
    Create and index a new personal note
    """
    # 1. Save note file
    note_path = save_note(note)
    
    # 2. Process into chunk
    processor = PersonalNoteProcessor()
    chunk = processor.process_note(note)
    
    # 3. Generate embedding
    text = chunk['text_content']
    embedding = generate_embeddings([text], openai_client)[0]
    
    # 4. Add to ChromaDB
    vector_store.add_documents([chunk], [embedding])
    
    # 5. Upload to GCS if deployed
    if is_deployed():
        upload_note_to_gcs(note_path)
    
    return {"status": "created", "note_id": note.note_id}

@app.put("/api/notes/{note_id}", tags=["Notes"])
async def update_note(note_id: str, note: PersonalNote):
    """
    Update existing note and re-index
    """
    # 1. Update note file
    update_note_file(note)
    
    # 2. Re-process chunk
    processor = PersonalNoteProcessor()
    chunk = processor.process_note(note)
    
    # 3. Re-generate embedding
    embedding = generate_embeddings([chunk['text_content']], openai_client)[0]
    
    # 4. Update in ChromaDB
    vector_store.update_document(note_id, chunk, embedding)
    
    return {"status": "updated", "note_id": note_id}

@app.delete("/api/notes/{note_id}", tags=["Notes"])
async def delete_note(note_id: str):
    """Delete note and remove from index"""
    delete_note_file(note_id)
    vector_store.delete_by_id(note_id)
    return {"status": "deleted", "note_id": note_id}
```

#### Search Integration:
```python
# Modify hierarchical_search.py

def search(self, query: str, max_results: int = 10) -> List[TopicResult]:
    """
    Search across ALL sources: Harrison's, PDFs, and Notes
    """
    # ... existing search logic ...
    
    for doc_id, metadata, distance in results:
        pdf_source = metadata.get('pdf_source', 'harrisons')
        
        if pdf_source == 'personal_note':
            # Format note result
            result = TopicResult(
                topic_id=metadata['note_id'],
                topic_name=metadata['title'],
                hierarchy=f"📝 Personal Note",
                preview=metadata['preview'],
                pages=f"Note",  # No pages for notes
                start_page=0,
                end_page=0,
                relevance_score=relevance,
                pdf_source='personal_note',
                tags=metadata.get('tags', []),
                created_at=metadata.get('created_at'),
                is_editable=True
            )
        # ... handle other sources ...
```

---

### 2.6 Search Results with Notes

#### Display Format:
```
╔════════════════════════════════════════════════════════════════╗
║                    SEARCH RESULTS: "hyponatremia"              ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📝 MY NOTE: Hyponatremia Case Study                   │  ║
║  │ Created: Nov 10, 2025 | Tags: electrolytes, case      │  ║
║  │ "Patient with Na 118, symptomatic. Started hypertonic │  ║
║  │  saline. Improved within 6 hours..."                  │  ║
║  │ Relevance: ●●●●● 0.94                                 │  ║
║  │ [View Note] [Edit] [Delete]                           │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📖 Part 2 > Chapter 53: Fluid and Electrolytes        │  ║
║  │ Pages: 289-295                                         │  ║
║  │ "Hyponatremia is defined as serum sodium <135 mEq/L...│  ║
║  │ Relevance: ●●●●○ 0.89                                 │  ║
║  │ [View Chapter]                                         │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📄 EM Basic: Electrolyte Management                   │  ║
║  │ Pages: 3-7                                             │  ║
║  │ "Rapid correction risks osmotic demyelination..."     │  ║
║  │ Relevance: ●●●●○ 0.85                                 │  ║
║  │ [View PDF]                                             │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

#### Note Viewer:
```
╔════════════════════════════════════════════════════════════════╗
║                📝 Hyponatremia Case Study                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Created: Nov 10, 2025 10:45 AM                               ║
║  Last edited: Nov 10, 2025 2:30 PM                            ║
║  Tags: #electrolytes #case #critical                          ║
║  Words: 234                                                    ║
║                                                                ║
║  ──────────────────────────────────────────────────────────── ║
║                                                                ║
║  Patient with Na 118, symptomatic. Started hypertonic         ║
║  saline at 3% solution, 50mL over 30 minutes.                ║
║                                                                ║
║  Initial symptoms: confusion, nausea, headache                ║
║                                                                ║
║  Improved within 6 hours. Na rose to 123. Continued slower   ║
║  correction to avoid ODS.                                     ║
║                                                                ║
║  Key learning: Watch correction rate - no more than 8 mEq/L  ║
║  in 24 hours.                                                 ║
║                                                                ║
║  ──────────────────────────────────────────────────────────── ║
║                                                                ║
║  Linked sources:                                              ║
║  → Chapter 53: Fluid and Electrolyte Disturbances            ║
║                                                                ║
║  [✏️ Edit] [📋 Duplicate] [🗑️ Delete] [←  Back to Search]    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🔧 Technical Implementation Details

### Database Schema Changes

#### ChromaDB Collection:
```python
# Current: harrisons_medical collection contains Harrison's + PDFs

# New: Same collection, expanded metadata
{
    "id": "note_uuid_12345",
    "embedding": [...],  # OpenAI embedding
    "metadata": {
        "note_id": "note_uuid_12345",
        "title": "Hyponatremia Case",
        "pdf_source": "personal_note",  # NEW source type
        "text_content": "...",
        "preview": "...",
        "tags": ["electrolytes", "case"],
        "created_at": "2025-11-14T10:30:00Z",
        "updated_at": "2025-11-14T10:30:00Z",
        "word_count": 234,
        "is_editable": true,
        "linked_sources": ["part2_ch53_fluid..."]
    }
}
```

### File Structure Updates
```
medWatcher/
├── backend/
│   ├── library_manager.py      # NEW: Library CRUD operations
│   ├── note_processor.py       # NEW: Process personal notes
│   ├── note_editor.py          # NEW: Note editing logic
│   └── static/
│       ├── library.html        # NEW: Library interface
│       ├── library.js
│       ├── note-editor.html    # NEW: Note editor
│       ├── note-editor.js
│       └── note-viewer.html    # NEW: Note viewer
└── data/
    ├── personal_notes/          # NEW: Note storage
    └── processed/
        └── personal_note_chunks/ # NEW: Note chunks
```

### API Endpoints Summary
```
Library Management:
GET    /api/library              - List all sources
GET    /api/library/{id}         - Get source details
DELETE /api/library/{id}         - Delete source
GET    /api/library/stats        - Get statistics
POST   /api/library/upload       - Upload new content

Personal Notes:
POST   /api/notes                - Create note
GET    /api/notes                - List all notes
GET    /api/notes/{id}           - Get specific note
PUT    /api/notes/{id}           - Update note
DELETE /api/notes/{id}           - Delete note
GET    /api/notes/search         - Search within notes

Editor:
GET    /editor                   - Note editor page
GET    /notes/{id}/edit          - Edit existing note
GET    /notes/{id}/view          - View note
```

---

## 📅 Implementation Timeline

### Phase 1: Content Management (3-5 days)
1. **Day 1**: Data models + backend API endpoints
2. **Day 2**: Library interface HTML/CSS/JS
3. **Day 3**: Delete functionality + confirmation
4. **Day 4**: Upload interface + processing
5. **Day 5**: Testing + polish

### Phase 2: Personal Notes (3-5 days)
1. **Day 1**: Note data models + storage
2. **Day 2**: Quick note interface (below search)
3. **Day 3**: Full note editor
4. **Day 4**: Note indexing + search integration
5. **Day 5**: Note viewer + linking

### Total: 6-10 days for both phases

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- ✅ Can view all content in library
- ✅ Can delete PDFs/notes (not Harrison's)
- ✅ Can upload new PDFs
- ✅ Can search/filter library
- ✅ Statistics dashboard working

### Phase 2 Complete When:
- ✅ Can create notes from search page
- ✅ Can edit notes in full editor
- ✅ Notes appear in search results
- ✅ Notes are fully embedded and searchable
- ✅ Can link notes to other content
- ✅ Can view note history

---

## 🚀 Future Enhancements (Phase 3+)

### Nice to Have:
- 📸 **Image attachments** in notes
- 🔗 **Bi-directional linking** (backlinks)
- 📊 **Note templates** (case study, quick note, protocol)
- 🏷️ **Smart tagging** (AI-suggested tags)
- 📅 **Calendar view** of notes
- 🔔 **Reminders** for follow-up
- 👥 **Sharing** (share notes with colleagues)
- 📤 **Export** (PDF, Markdown, HTML)
- 🔄 **Sync** across devices
- 📱 **Mobile app** (native iOS/Android)

---

## 💡 Key Design Principles

1. **Non-destructive**: Keep Harrison's static and untouchable
2. **Fast**: Notes should save in <1 second
3. **Simple**: Minimal UI, maximum functionality
4. **Searchable**: Everything embedded and searchable
5. **Portable**: Easy export/backup
6. **Privacy**: User data stays private
7. **Offline-first**: Work without internet when possible

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│ User Types   │
│ Note         │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Save Note    │──────► Local Storage (draft)
│ to File      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Process      │
│ Note         │──────► Create chunk JSON
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Generate     │
│ Embedding    │──────► OpenAI API
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Add to       │
│ ChromaDB     │──────► Vector index updated
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Upload to    │
│ GCS          │──────► Cloud storage (if deployed)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Note is now  │
│ SEARCHABLE!  │
└──────────────┘
```

---

## 🎉 Summary

This plan transforms medWatcher from a static reference tool into a **dynamic, personalized medical knowledge base** where:

✅ You control all content
✅ You can add notes on-the-fly
✅ Everything is searchable via RAG
✅ Your knowledge grows with you
✅ It's tailored to your practice

**Ready to implement when you are!** 🚀

