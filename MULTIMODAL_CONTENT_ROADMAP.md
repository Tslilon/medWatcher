# 🎨 Multimodal Content Addition Roadmap
**Goal:** Add images, text notes, drawings, and voice recordings to RAG with full CRUD support

**Note:** This is a web-based application. Mobile device support means accepting file formats produced by iPhone/Android cameras (JPEG, PNG, HEIC), not native mobile app development.

---

## 📋 TABLE OF CONTENTS
1. [Content Types](#content-types)
2. [Storage Architecture](#storage-architecture)
3. [Data Flow](#data-flow)
4. [UI/UX Design](#uiux-design)
5. [Implementation Phases](#implementation-phases)
6. [Testing Strategy](#testing-strategy)
7. [Critical Checkpoints](#critical-checkpoints)

---

## 🎯 CONTENT TYPES

### 1. **Images** (JPEG/PNG/HEIC/WEBP)
- Upload from gallery/camera (web file picker)
- Supports formats produced by iPhone/Android cameras:
  - JPEG (.jpg, .jpeg) - standard
  - PNG (.png) - screenshots
  - HEIC (.heic) - iPhone default format
  - WEBP (.webp) - modern format
- Optional caption/description
- OCR text extraction (for searchability)
- Thumbnail generation
- EXIF metadata extraction
- Auto-convert HEIC to JPEG for compatibility

### 2. **Text Notes**
- Plain text input
- Markdown support (optional)
- Tags/categories
- Auto-generated title from first line

### 3. **Drawings**
- Canvas-based drawing pad (HTML5 Canvas)
- Save as PNG with transparency
- Optional caption
- Size: 800x600 (optimized for web)

### 4. **Voice Recordings** (NEW!)
- Record audio in browser (MediaRecorder API)
- Formats: WebM, MP4, WAV (browser-dependent)
- Convert to MP3 for universal playback
- Audio transcription (Whisper API or Google Speech-to-Text)
- Playback with HTML5 audio player
- Optional title/description
- Duration metadata
- Waveform visualization (optional)

---

## 🗄️ STORAGE ARCHITECTURE

### **GCS Bucket Structure:**
```
gs://harrisons-rag-data-flingoos/
├── independant_pdfs/                    # (existing)
├── processed/
│   ├── independent_chunks/              # (existing)
│   │   └── summary.json                 # (UPDATE THIS!)
│   ├── user_images/                     # NEW!
│   │   ├── image_001.jpg
│   │   ├── image_002.png
│   │   └── ...
│   ├── user_images_chunks/              # NEW!
│   │   ├── image_image_001_chunk1.json
│   │   ├── image_image_002_chunk1.json
│   │   └── summary.json                 # NEW!
│   ├── user_notes/                      # NEW!
│   │   ├── note_001.txt
│   │   ├── note_002.md
│   │   └── ...
│   ├── user_notes_chunks/               # NEW!
│   │   ├── note_note_001_chunk1.json
│   │   ├── note_note_002_chunk1.json
│   │   └── summary.json                 # NEW!
│   ├── user_drawings/                   # NEW!
│   │   ├── drawing_001.png
│   │   ├── drawing_002.png
│   │   └── ...
│   ├── user_drawings_chunks/            # NEW!
│   │   ├── drawing_drawing_001_chunk1.json
│   │   ├── drawing_drawing_002_chunk1.json
│   │   └── summary.json                 # NEW!
│   ├── user_audio/                      # NEW!
│   │   ├── audio_001.mp3
│   │   ├── audio_002.mp3
│   │   └── ...
│   └── user_audio_chunks/               # NEW!
│       ├── audio_audio_001_chunk1.json
│       ├── audio_audio_002_chunk1.json
│       └── summary.json                 # NEW!
├── chroma_db/                           # (existing - will contain all new content)
└── version.txt                          # (existing)
```

### **Local Storage (Container):**
```
/app/data/
├── processed/
│   ├── independent_chunks/              # (existing)
│   ├── user_images/                     # NEW!
│   ├── user_images_chunks/              # NEW!
│   ├── user_notes/                      # NEW!
│   ├── user_notes_chunks/               # NEW!
│   ├── user_drawings/                   # NEW!
│   └── user_drawings_chunks/            # NEW!
└── chroma_db/                           # (existing)
```

---

## 🔄 DATA FLOW

### **UPLOAD FLOW:**

```
1. USER ACTION
   ├─> Click + button
   ├─> Choose: [Gallery | Files | Text Note | Drawing]
   └─> Select/Create content

2. FRONTEND PROCESSING
   ├─> Image: Validate format, compress if needed
   ├─> Text: Validate length, sanitize
   └─> Drawing: Export canvas to PNG

3. UPLOAD TO SERVER
   POST /api/content/upload
   ├─> Content-Type header
   ├─> File data (multipart/form-data)
   └─> Metadata (caption, tags, etc.)

4. SERVER PROCESSING
   ├─> Save original to GCS (user_images/notes/drawings/)
   ├─> Extract text:
   │   ├─> Images: OCR (Tesseract or Cloud Vision API)
   │   ├─> Notes: Direct text
   │   └─> Drawings: OCR (optional)
   ├─> Chunk text (if needed)
   ├─> Generate embeddings (OpenAI)
   ├─> Save chunks to GCS (user_xxx_chunks/)
   ├─> Update summary.json
   ├─> Index to ChromaDB
   ├─> Upload ChromaDB to GCS
   └─> Update version.txt

5. RESPONSE
   └─> Success message with content ID
```

### **SEARCH FLOW:**

```
1. USER SEARCHES
   └─> Query: "chest xray findings"

2. SEARCH ENGINE
   ├─> Generate query embedding
   ├─> Search ChromaDB (all content types)
   └─> Return results with metadata

3. RESULTS DISPLAY
   ├─> PDF: Shows PDF icon + page range
   ├─> Image: Shows thumbnail + caption
   ├─> Note: Shows text preview
   └─> Drawing: Shows thumbnail + caption
```

### **DELETE FLOW:**

```
1. USER CLICKS DELETE
   └─> Content ID passed to API

2. SERVER PROCESSING
   ├─> Identify content type (image/note/drawing)
   ├─> Delete from GCS:
   │   ├─> user_xxx/{filename}
   │   └─> user_xxx_chunks/{chunk_files}
   ├─> Remove from ChromaDB
   ├─> Update summary.json
   ├─> Upload ChromaDB to GCS
   ├─> Update version.txt
   └─> Reload search engine

3. RESPONSE
   └─> Success + refresh library UI
```

---

## 🎨 UI/UX DESIGN

### **Button Layout (index.html):**

```html
<!-- Row 1: Search button (full width) -->
<button id="searchBtn">🔍 Search</button>

<!-- Row 2: Action buttons (equal width, fit in one line) -->
<div style="display: flex; gap: 8px;">
    <button id="voiceBtn">🎤</button>
    <button id="addBtn">➕</button>      <!-- NEW! -->
    <button id="refreshBtn">🔄</button>
    <button id="libraryBtn">📚</button>
</div>
```

### **Add Content Modal:**

```
┌─────────────────────────────────────┐
│  ➕ Add Content                     │
├─────────────────────────────────────┤
│                                     │
│  Choose content type:               │
│                                     │
│  [ 📷 Upload Image ]                │
│  [ 📝 Create Note ]                 │
│  [ ✏️  Draw Something ]              │
│  [ 🎤 Record Audio ]                │
│  [ 📁 Upload File ]                 │
│                                     │
│           [ Cancel ]                │
└─────────────────────────────────────┘
```

### **Content Type Flows:**

#### **1. Image Upload:**
```
1. File picker opens
2. User selects image
3. Preview shown with:
   - Image thumbnail
   - Caption input (optional)
   - Tags input (optional)
4. Upload button
```

#### **2. Text Note:**
```
1. Text editor opens with:
   - Title input
   - Large text area
   - Tags input (optional)
   - Markdown toggle (optional)
2. Save button
```

#### **3. Drawing:**
```
1. Canvas opens with:
   - Drawing tools (pen, eraser, colors)
   - Clear button
   - Caption input
2. Save button (exports to PNG)
```

#### **4. Voice Recording:**
```
1. Audio recorder opens with:
   - Record button (press to start/stop)
   - Timer showing duration
   - Playback button (review before saving)
   - Waveform visualization (optional)
   - Title/description input
2. Save button (uploads audio file)
```

---

## 🚀 IMPLEMENTATION PHASES

### **PHASE 1: Infrastructure & Data Models** (Day 1-2)

**Backend:**
- [ ] Create data models (`models.py`):
  ```python
  class UserContent(BaseModel):
      content_id: str
      content_type: Literal["image", "note", "drawing"]
      title: str
      filename: str
      caption: Optional[str]
      tags: List[str]
      created_at: datetime
      file_size: int
      metadata: Dict
  
  class ContentChunk(TypedDict):
      chunk_id: str
      content_id: str
      content_type: str
      text: str
      preview: str
      metadata: Dict
  ```

- [ ] Create GCS directories:
  ```python
  # gcs_helper.py additions
  def setup_multimodal_storage():
      dirs = [
          "processed/user_images",
          "processed/user_images_chunks",
          "processed/user_notes", 
          "processed/user_notes_chunks",
          "processed/user_drawings",
          "processed/user_drawings_chunks"
      ]
      for dir in dirs:
          create_gcs_directory(dir)
  ```

- [ ] Create `content_processor.py`:
  ```python
  class ContentProcessor:
      def process_image(self, image_file, caption, tags)
      def process_note(self, text, title, tags)
      def process_drawing(self, canvas_data, caption, tags)
      def extract_text_from_image(self, image_path)  # OCR
      def chunk_content(self, text, content_type)
      def save_to_gcs(self, content, chunks)
  ```

**Tests:**
- [ ] Test GCS directory creation
- [ ] Test data model validation
- [ ] Test ContentProcessor initialization

---

### **PHASE 2: Backend API Endpoints** (Day 2-3)

**Create endpoints in `main.py`:**

```python
@app.post("/api/content/upload", tags=["Content"])
async def upload_content(
    file: Optional[UploadFile] = File(None),
    content_type: str = Form(...),
    title: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None)  # For text notes
):
    """
    Universal upload endpoint for images, notes, and drawings
    """
    pass

@app.get("/api/content/{content_id}", tags=["Content"])
async def get_content(content_id: str):
    """Get content details and file URL"""
    pass

@app.delete("/api/content/{content_id}", tags=["Content"])
async def delete_content(content_id: str):
    """Delete content from all locations"""
    pass

@app.get("/api/content/image/{image_filename}", tags=["Content"])
async def serve_image(image_filename: str):
    """Serve image file (with thumbnail option)"""
    pass
```

**Key Implementation Details:**

1. **Image Processing:**
   ```python
   # Install: pip install pytesseract pillow
   from PIL import Image
   import pytesseract
   
   def process_image(file: UploadFile, caption: str):
       # Save original
       image_path = save_to_gcs(file, "processed/user_images/")
       
       # Extract text via OCR
       img = Image.open(file.file)
       ocr_text = pytesseract.image_to_string(img)
       
       # Combine caption + OCR text
       full_text = f"{caption}\n\n{ocr_text}" if caption else ocr_text
       
       # Chunk and embed
       chunks = create_chunks(full_text, content_type="image")
       return chunks
   ```

2. **Note Processing:**
   ```python
   def process_note(text: str, title: str, tags: List[str]):
       # Generate ID
       note_id = f"note_{int(time.time())}_{uuid4().hex[:8]}"
       
       # Save to GCS
       filename = f"{note_id}.txt"
       upload_text_to_gcs(text, f"processed/user_notes/{filename}")
       
       # Chunk if long
       chunks = create_chunks(text, content_type="note")
       return chunks
   ```

3. **Drawing Processing:**
   ```python
   def process_drawing(canvas_data: bytes, caption: str):
       # Save PNG
       drawing_id = f"drawing_{int(time.time())}_{uuid4().hex[:8]}"
       filename = f"{drawing_id}.png"
       upload_to_gcs(canvas_data, f"processed/user_drawings/{filename}")
       
       # OCR (optional)
       ocr_text = extract_text_from_image(canvas_data)
       full_text = f"{caption}\n\n{ocr_text}" if caption else ocr_text
       
       # Chunk
       chunks = create_chunks(full_text, content_type="drawing")
       return chunks
   ```

**Tests:**
- [ ] Test upload endpoint with mock files
- [ ] Test OCR extraction
- [ ] Test chunking for each content type
- [ ] Test GCS upload
- [ ] Test ChromaDB indexing
- [ ] Test version marker update

---

### **PHASE 3: Frontend UI Components** (Day 3-4)

**1. Add + Button (`index.html`):**

```html
<button class="btn" id="addBtn" title="Add Content" 
        style="flex: 1; padding: 12px; font-size: 20px; 
               background: #2196f3; color: white; font-weight: bold;">
    ➕
</button>
```

**2. Create Add Content Modal (`static/add-content-modal.html` or inline):**

```html
<div id="addContentModal" class="modal">
    <div class="modal-content">
        <h2>➕ Add Content</h2>
        
        <!-- Content Type Selection -->
        <div id="contentTypeSelect" class="content-type-grid">
            <button class="content-type-btn" data-type="image">
                <span class="icon">📷</span>
                <span>Upload Image</span>
            </button>
            <button class="content-type-btn" data-type="note">
                <span class="icon">📝</span>
                <span>Create Note</span>
            </button>
            <button class="content-type-btn" data-type="drawing">
                <span class="icon">✏️</span>
                <span>Draw</span>
            </button>
            <button class="content-type-btn" data-type="file">
                <span class="icon">📁</span>
                <span>Upload File</span>
            </button>
        </div>
        
        <!-- Dynamic Content Form (hidden initially) -->
        <div id="contentForm" style="display: none;">
            <!-- Image Upload Form -->
            <div id="imageForm" class="content-form">
                <input type="file" id="imageFile" accept="image/*" capture="environment">
                <div id="imagePreview"></div>
                <input type="text" id="imageCaption" placeholder="Add a caption...">
                <input type="text" id="imageTags" placeholder="Tags (comma-separated)">
                <button id="uploadImageBtn">Upload</button>
            </div>
            
            <!-- Note Form -->
            <div id="noteForm" class="content-form">
                <input type="text" id="noteTitle" placeholder="Note title...">
                <textarea id="noteText" rows="10" placeholder="Type your note..."></textarea>
                <input type="text" id="noteTags" placeholder="Tags (comma-separated)">
                <button id="saveNoteBtn">Save Note</button>
            </div>
            
            <!-- Drawing Form -->
            <div id="drawingForm" class="content-form">
                <canvas id="drawingCanvas" width="800" height="600"></canvas>
                <div class="drawing-tools">
                    <button id="penTool" class="active">✏️ Pen</button>
                    <button id="eraserTool">🧹 Eraser</button>
                    <input type="color" id="penColor" value="#000000">
                    <input type="range" id="penSize" min="1" max="20" value="3">
                    <button id="clearCanvas">🗑️ Clear</button>
                </div>
                <input type="text" id="drawingCaption" placeholder="Add a caption...">
                <button id="saveDrawingBtn">Save Drawing</button>
            </div>
            
            <!-- Audio Recording Form -->
            <div id="audioForm" class="content-form">
                <div class="audio-recorder">
                    <button id="recordBtn" class="record-btn">🎤 Start Recording</button>
                    <div id="recordingStatus" style="display: none;">
                        <span class="recording-indicator">🔴 Recording</span>
                        <span id="recordingTimer">00:00</span>
                    </div>
                    <audio id="audioPlayback" controls style="display: none;"></audio>
                    <canvas id="waveformCanvas" width="400" height="100"></canvas>
                </div>
                <input type="text" id="audioTitle" placeholder="Title (optional)...">
                <textarea id="audioDescription" rows="3" placeholder="Description (optional)..."></textarea>
                <input type="text" id="audioTags" placeholder="Tags (comma-separated)">
                <button id="saveAudioBtn" disabled>Save Recording</button>
            </div>
        </div>
        
        <button id="closeAddModal" class="close-btn">Cancel</button>
    </div>
</div>
```

**3. JavaScript Logic (`static/add-content.js`):**

```javascript
// Add Content Modal Management
const addBtn = document.getElementById('addBtn');
const addModal = document.getElementById('addContentModal');

addBtn.addEventListener('click', () => {
    addModal.style.display = 'block';
    showContentTypeSelect();
});

// Content Type Selection
document.querySelectorAll('.content-type-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const type = e.currentTarget.dataset.type;
        showContentForm(type);
    });
});

function showContentForm(type) {
    // Hide type selection
    document.getElementById('contentTypeSelect').style.display = 'none';
    
    // Show appropriate form
    document.getElementById('contentForm').style.display = 'block';
    document.querySelectorAll('.content-form').forEach(f => f.style.display = 'none');
    document.getElementById(`${type}Form`).style.display = 'block';
    
    if (type === 'drawing') {
        initDrawingCanvas();
    }
}

// Image Upload
document.getElementById('uploadImageBtn').addEventListener('click', async () => {
    const file = document.getElementById('imageFile').files[0];
    const caption = document.getElementById('imageCaption').value;
    const tags = document.getElementById('imageTags').value;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('content_type', 'image');
    formData.append('caption', caption);
    formData.append('tags', tags);
    
    const response = await fetch('/api/content/upload', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        alert('Image uploaded successfully!');
        closeAddModal();
    }
});

// Note Creation
document.getElementById('saveNoteBtn').addEventListener('click', async () => {
    const title = document.getElementById('noteTitle').value;
    const text = document.getElementById('noteText').value;
    const tags = document.getElementById('noteTags').value;
    
    const formData = new FormData();
    formData.append('content_type', 'note');
    formData.append('title', title);
    formData.append('text_content', text);
    formData.append('tags', tags);
    
    const response = await fetch('/api/content/upload', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        alert('Note saved successfully!');
        closeAddModal();
    }
});

// Drawing Canvas
let canvas, ctx, drawing = false;

function initDrawingCanvas() {
    canvas = document.getElementById('drawingCanvas');
    ctx = canvas.getContext('2d');
    
    // Touch/mouse events for drawing
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
}

function startDrawing(e) {
    drawing = true;
    draw(e);
}

function draw(e) {
    if (!drawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches[0].clientX) - rect.left;
    const y = (e.clientY || e.touches[0].clientY) - rect.top;
    
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function stopDrawing() {
    drawing = false;
    ctx.beginPath();
}

document.getElementById('saveDrawingBtn').addEventListener('click', async () => {
    const caption = document.getElementById('drawingCaption').value;
    
    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'drawing.png');
        formData.append('content_type', 'drawing');
        formData.append('caption', caption);
        
        const response = await fetch('/api/content/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Drawing saved successfully!');
            closeAddModal();
        }
    }, 'image/png');
});

// Audio Recording
let mediaRecorder, audioChunks = [], recordingStartTime, timerInterval;
let recordedAudioBlob = null;

document.getElementById('recordBtn').addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        await startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = () => {
            recordedAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(recordedAudioBlob);
            
            const playback = document.getElementById('audioPlayback');
            playback.src = audioUrl;
            playback.style.display = 'block';
            
            document.getElementById('saveAudioBtn').disabled = false;
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        
        // Update UI
        document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
        document.getElementById('recordingStatus').style.display = 'block';
        
        // Start timer
        recordingStartTime = Date.now();
        timerInterval = setInterval(updateTimer, 100);
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        
        // Update UI
        document.getElementById('recordBtn').textContent = '🎤 Start Recording';
        document.getElementById('recordingStatus').style.display = 'none';
        
        // Stop timer
        clearInterval(timerInterval);
    }
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');
    document.getElementById('recordingTimer').textContent = `${minutes}:${seconds}`;
}

document.getElementById('saveAudioBtn').addEventListener('click', async () => {
    if (!recordedAudioBlob) {
        alert('No recording to save!');
        return;
    }
    
    const title = document.getElementById('audioTitle').value || 'Voice Note';
    const description = document.getElementById('audioDescription').value;
    const tags = document.getElementById('audioTags').value;
    
    const formData = new FormData();
    formData.append('file', recordedAudioBlob, 'recording.webm');
    formData.append('content_type', 'audio');
    formData.append('title', title);
    formData.append('description', description);
    formData.append('tags', tags);
    
    const response = await fetch('/api/content/upload', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        alert('Recording saved successfully!');
        closeAddModal();
    } else {
        alert('Failed to save recording');
    }
});
```

**Tests:**
- [ ] Test button layout (visual)
- [ ] Test modal open/close
- [ ] Test image file picker
- [ ] Test note text input
- [ ] Test drawing canvas
- [ ] Test form submission

---

### **PHASE 4: Library Integration** (Day 4-5)

**Update `library_manager.py`:**

```python
def get_all_sources(self, source_type: Optional[str] = None) -> List[Dict]:
    """Get all content sources (PDFs, images, notes, drawings)"""
    sources = []
    
    # Existing: Harrison's + Independent PDFs
    sources.extend(self._get_harrison_source())
    sources.extend(self._get_pdf_sources())
    
    # NEW: Images
    if source_type in [None, "image"]:
        sources.extend(self._get_image_sources())
    
    # NEW: Notes
    if source_type in [None, "note"]:
        sources.extend(self._get_note_sources())
    
    # NEW: Drawings
    if source_type in [None, "drawing"]:
        sources.extend(self._get_drawing_sources())
    
    return sources

def _get_image_sources(self) -> List[Dict]:
    """Get all user images from summary.json"""
    summary_file = self.data_dir / "processed/user_images_chunks/summary.json"
    if not summary_file.exists():
        return []
    
    with open(summary_file, 'r') as f:
        summary = json.load(f)
    
    return [
        {
            "id": f"image_{img['content_id']}",
            "type": "image",
            "title": img['title'],
            "filename": img['filename'],
            "caption": img.get('caption', ''),
            "tags": img.get('tags', []),
            "created_at": img['created_at'],
            "thumbnail_url": f"/api/content/image/{img['filename']}?thumbnail=true"
        }
        for img in summary.get('images', [])
    ]
```

**Update Delete Functionality:**

```python
def delete_source(self, source_id: str) -> Dict[str, str]:
    """Delete any content source"""
    source = self.get_source_by_id(source_id)
    
    source_type = source['type']
    
    if source_type == "independent_pdf":
        self._delete_pdf_source(source)
    elif source_type == "image":
        self._delete_image_source(source)  # NEW!
    elif source_type == "note":
        self._delete_note_source(source)   # NEW!
    elif source_type == "drawing":
        self._delete_drawing_source(source)  # NEW!
    
    return {"status": "success", "message": f"Deleted {source['title']}"}

def _delete_image_source(self, source: Dict):
    """Delete image from ALL locations"""
    import re, subprocess
    
    content_id = source['id'].replace('image_', '')
    filename = source['filename']
    
    # 1. Delete image file from GCS
    delete_from_gcs(f"processed/user_images/{filename}")
    
    # 2. Delete chunks from GCS (using pattern matching)
    slug = re.sub(r'[^\w]', '_', content_id.lower())
    chunk_pattern = f"image_{slug}_chunk"
    
    result = subprocess.run(
        ["gsutil", "ls", f"gs://harrisons-rag-data-flingoos/processed/user_images_chunks/{chunk_pattern}*.json"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        for chunk_path in result.stdout.strip().split('\n'):
            if chunk_path:
                chunk_filename = chunk_path.split('/')[-1]
                delete_from_gcs(f"processed/user_images_chunks/{chunk_filename}")
    
    # 3. Update summary.json
    summary_file = self.data_dir / "processed/user_images_chunks/summary.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        summary['images'] = [
            img for img in summary['images']
            if img['content_id'] != content_id
        ]
        summary['total_images'] = len(summary['images'])
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        upload_to_gcs(str(summary_file), "processed/user_images_chunks/summary.json")
    
    # 4. Remove from ChromaDB
    self.vector_store.delete_by_metadata('content_id', content_id)
    
    # 5. Upload ChromaDB + version marker
    upload_chromadb_and_version()
    
    # 6. Reload search engine
    reload_search_engine()
```

**Tests:**
- [ ] Test library displays all content types
- [ ] Test filtering by content type
- [ ] Test delete for each content type
- [ ] Test summary.json updates

---

### **PHASE 5: Search & Display Integration** (Day 5-6)

**Update Search Results Display:**

```javascript
function displaySearchResults(results) {
    results.forEach(result => {
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';
        
        // Different display based on content type
        if (result.pdf_source === 'harrison' || result.pdf_source === 'independent') {
            // Existing PDF display
            resultCard.innerHTML = `
                <div class="result-icon">📄</div>
                <div class="result-content">
                    <h3>${result.topic_name}</h3>
                    <p>${result.preview}</p>
                </div>
            `;
        } else if (result.content_type === 'image') {
            // NEW: Image display
            resultCard.innerHTML = `
                <div class="result-icon">
                    <img src="/api/content/image/${result.filename}?thumbnail=true" 
                         alt="${result.title}" style="width: 60px; height: 60px; object-fit: cover;">
                </div>
                <div class="result-content">
                    <h3>📷 ${result.title}</h3>
                    <p>${result.caption || result.preview}</p>
                    <small>${result.tags.join(', ')}</small>
                </div>
            `;
        } else if (result.content_type === 'note') {
            // NEW: Note display
            resultCard.innerHTML = `
                <div class="result-icon">📝</div>
                <div class="result-content">
                    <h3>${result.title}</h3>
                    <p>${result.preview}</p>
                    <small>${result.tags.join(', ')}</small>
                </div>
            `;
        } else if (result.content_type === 'drawing') {
            // NEW: Drawing display
            resultCard.innerHTML = `
                <div class="result-icon">
                    <img src="/api/content/image/${result.filename}?thumbnail=true" 
                         alt="${result.title}" style="width: 60px; height: 60px;">
                </div>
                <div class="result-content">
                    <h3>✏️ ${result.title}</h3>
                    <p>${result.caption || result.preview}</p>
                </div>
            `;
        }
        
        resultCard.addEventListener('click', () => openContent(result));
        resultsContainer.appendChild(resultCard);
    });
}

function openContent(result) {
    if (result.pdf_source) {
        // Open PDF viewer (existing)
        window.location.href = `/viewer?start=${result.start_page}&end=${result.end_page}...`;
    } else if (result.content_type === 'image' || result.content_type === 'drawing') {
        // Open image viewer modal
        showImageModal(result);
    } else if (result.content_type === 'note') {
        // Open note viewer modal
        showNoteModal(result);
    }
}
```

**Tests:**
- [ ] Test search returns mixed content types
- [ ] Test result card displays correctly for each type
- [ ] Test clicking on each result type
- [ ] Test image/note viewer modals

---

### **PHASE 6: Refresh Button Integration** (Day 6)

**Already handled!** The existing refresh button will work because:
1. All new content is added to ChromaDB
2. Version marker is updated after upload
3. `rsync` ensures fresh download
4. Search engine reloads automatically

**Additional Test:**
- [ ] Upload image → Click refresh → Search for image content → Verify found

---

### **PHASE 7: Testing** (Day 7-8)

#### **Unit Tests (`tests/test_content_processor.py`):**

```python
import pytest
from content_processor import ContentProcessor

def test_image_processing():
    processor = ContentProcessor()
    with open('test_image.jpg', 'rb') as f:
        chunks = processor.process_image(f, "Test caption", ["medical", "xray"])
    
    assert len(chunks) > 0
    assert chunks[0]['content_type'] == 'image'
    assert 'Test caption' in chunks[0]['text']

def test_note_processing():
    processor = ContentProcessor()
    text = "This is a test note about hyponatremia treatment."
    chunks = processor.process_note(text, "Hyponatremia Notes", ["electrolytes"])
    
    assert len(chunks) > 0
    assert chunks[0]['content_type'] == 'note'
    assert 'hyponatremia' in chunks[0]['text'].lower()

def test_drawing_processing():
    processor = ContentProcessor()
    with open('test_drawing.png', 'rb') as f:
        chunks = processor.process_drawing(f, "ECG tracing")
    
    assert len(chunks) > 0
    assert chunks[0]['content_type'] == 'drawing'

def test_ocr_extraction():
    processor = ContentProcessor()
    with open('test_image_with_text.jpg', 'rb') as f:
        text = processor.extract_text_from_image(f)
    
    assert len(text) > 0
    assert isinstance(text, str)
```

#### **Integration Tests (`tests/test_content_api.py`):**

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_image():
    with open('test_image.jpg', 'rb') as f:
        response = client.post(
            "/api/content/upload",
            files={"file": ("test.jpg", f, "image/jpeg")},
            data={
                "content_type": "image",
                "caption": "Test image",
                "tags": "test,medical"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'content_id' in data

def test_upload_note():
    response = client.post(
        "/api/content/upload",
        data={
            "content_type": "note",
            "title": "Test Note",
            "text_content": "This is a test note about medicine.",
            "tags": "test,notes"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'

def test_search_multimodal():
    # Upload content
    test_upload_image()
    test_upload_note()
    
    # Search
    response = client.post(
        "/api/search",
        json={"query": "test"}
    )
    
    assert response.status_code == 200
    results = response.json()['results']
    
    # Should find both image and note
    content_types = [r['content_type'] for r in results if 'content_type' in r]
    assert 'image' in content_types or 'note' in content_types

def test_delete_image():
    # Upload
    response = test_upload_image()
    content_id = response.json()['content_id']
    
    # Delete
    response = client.delete(f"/api/content/{content_id}")
    assert response.status_code == 200
    
    # Verify deleted from library
    response = client.get("/api/library")
    library = response.json()
    assert content_id not in [s['id'] for s in library['sources']]
```

#### **End-to-End Tests (Manual):**

1. **Image Upload Flow:**
   - [ ] Click + button
   - [ ] Select "Upload Image"
   - [ ] Choose image from gallery
   - [ ] Add caption
   - [ ] Upload
   - [ ] Verify appears in library
   - [ ] Search for caption text
   - [ ] Verify appears in results
   - [ ] Click result → Image opens
   - [ ] Delete → Verify gone

2. **Note Flow:**
   - [ ] Click + button
   - [ ] Select "Create Note"
   - [ ] Type title and text
   - [ ] Add tags
   - [ ] Save
   - [ ] Verify in library
   - [ ] Search for note content
   - [ ] Delete → Verify gone

3. **Drawing Flow:**
   - [ ] Click + button
   - [ ] Select "Draw"
   - [ ] Draw on canvas
   - [ ] Add caption
   - [ ] Save
   - [ ] Verify in library
   - [ ] Search for caption
   - [ ] Delete → Verify gone

4. **Refresh Button:**
   - [ ] Upload image on one device
   - [ ] On another device: Click refresh
   - [ ] Search for image → Should find it

---

## ✅ CRITICAL CHECKPOINTS

### **CHECKPOINT 1: Data Storage**
**Before proceeding to Phase 3:**
- [ ] All GCS directories created
- [ ] summary.json format defined for each type
- [ ] Test upload to each GCS location
- [ ] Test download from each GCS location

### **CHECKPOINT 2: Delete Functionality**
**Before deploying:**
- [ ] Test delete for EACH content type
- [ ] Verify deleted from:
  - [ ] GCS original files
  - [ ] GCS chunks
  - [ ] ChromaDB
  - [ ] summary.json
  - [ ] version.txt updated
- [ ] Refresh button works after delete

### **CHECKPOINT 3: Search Integration**
**Before user testing:**
- [ ] Search returns all content types
- [ ] Results sorted by relevance
- [ ] Clicking each result type works
- [ ] Image thumbnails load
- [ ] Note previews display

### **CHECKPOINT 4: UI/UX**
**Before final deployment:**
- [ ] All buttons fit on one line (mobile & desktop)
- [ ] + button same size as other buttons
- [ ] Modal works on iPhone/Android
- [ ] Canvas drawing works on touch devices
- [ ] Image upload works from camera
- [ ] File size limits enforced (warn user)

---

## 📝 SUMMARY.JSON FORMATS

### **user_images_chunks/summary.json:**
```json
{
  "total_images": 3,
  "total_chunks": 5,
  "images": [
    {
      "content_id": "img_1731512345_abc123",
      "title": "Chest X-Ray Findings",
      "filename": "img_1731512345_abc123.jpg",
      "caption": "PA chest showing infiltrates",
      "tags": ["radiology", "chest", "xray"],
      "created_at": "2025-11-13T16:45:23Z",
      "file_size": 245678,
      "chunks": 2,
      "has_ocr": true
    }
  ]
}
```

### **user_notes_chunks/summary.json:**
```json
{
  "total_notes": 5,
  "total_chunks": 8,
  "notes": [
    {
      "content_id": "note_1731512345_def456",
      "title": "Hyponatremia Management",
      "filename": "note_1731512345_def456.txt",
      "tags": ["electrolytes", "treatment"],
      "created_at": "2025-11-13T17:22:10Z",
      "word_count": 342,
      "chunks": 2
    }
  ]
}
```

### **user_drawings_chunks/summary.json:**
```json
{
  "total_drawings": 2,
  "total_chunks": 2,
  "drawings": [
    {
      "content_id": "draw_1731512345_ghi789",
      "title": "ECG Interpretation",
      "filename": "draw_1731512345_ghi789.png",
      "caption": "ST elevation in V1-V4",
      "created_at": "2025-11-13T18:05:55Z",
      "file_size": 125430,
      "chunks": 1
    }
  ]
}
```

### **user_audio_chunks/summary.json:**
```json
{
  "total_audio": 3,
  "total_chunks": 5,
  "audio": [
    {
      "content_id": "audio_1731512345_jkl012",
      "title": "Case Discussion - DKA Management",
      "filename": "audio_1731512345_jkl012.mp3",
      "description": "Notes from morning rounds on DKA patient",
      "tags": ["case", "dka", "rounds"],
      "created_at": "2025-11-13T19:30:12Z",
      "file_size": 1245678,
      "duration_seconds": 125,
      "has_transcription": true,
      "chunks": 2
    }
  ]
}
```

---

## 🚨 CRITICAL: ALL DELETION LOCATIONS

When deleting content, **MUST** remove from:

1. **GCS Original File:**
   - `gs://harrisons-rag-data-flingoos/processed/user_images/{filename}`
   - `gs://harrisons-rag-data-flingoos/processed/user_notes/{filename}`
   - `gs://harrisons-rag-data-flingoos/processed/user_drawings/{filename}`
   - `gs://harrisons-rag-data-flingoos/processed/user_audio/{filename}`

2. **GCS Chunk Files:**
   - `gs://harrisons-rag-data-flingoos/processed/user_images_chunks/{chunk_pattern}*.json`
   - `gs://harrisons-rag-data-flingoos/processed/user_notes_chunks/{chunk_pattern}*.json`
   - `gs://harrisons-rag-data-flingoos/processed/user_drawings_chunks/{chunk_pattern}*.json`
   - `gs://harrisons-rag-data-flingoos/processed/user_audio_chunks/{chunk_pattern}*.json`

3. **Summary JSON:**
   - Remove entry from `user_images_chunks/summary.json`
   - Remove entry from `user_notes_chunks/summary.json`
   - Remove entry from `user_drawings_chunks/summary.json`
   - Remove entry from `user_audio_chunks/summary.json`
   - Re-upload updated summary to GCS

4. **ChromaDB:**
   - `self.vector_store.delete_by_metadata('content_id', content_id)`
   - Upload ChromaDB to GCS

5. **Version Marker:**
   - Update `version.txt` with new timestamp
   - Upload to GCS

6. **Local Files (Container):**
   - Delete from `/app/data/processed/user_xxx/{filename}`
   - Delete from `/app/data/processed/user_xxx_chunks/{chunk_files}`

---

## 📦 NEW DEPENDENCIES

Add to `requirements.txt`:
```txt
pytesseract==0.3.10         # OCR for images
Pillow==10.1.0              # Image processing (JPEG, PNG, HEIC)
pillow-heif==0.13.1         # HEIC format support (iPhone photos)
google-cloud-vision==3.4.5  # Alternative OCR (Cloud Vision API)
openai-whisper==20231117    # Audio transcription (Whisper)
pydub==0.25.1               # Audio format conversion
```

Install system dependencies in `Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    ffmpeg \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*
```

**File Format Support:**
- **Images:** JPEG (.jpg, .jpeg), PNG (.png), HEIC (.heic), WEBP (.webp)
  - HEIC files auto-converted to JPEG for compatibility
- **Audio:** WebM (.webm), MP4 (.mp4), WAV (.wav)
  - All audio converted to MP3 for universal playback
  - Transcribed via Whisper API for searchability

---

## 🎯 FINAL VERIFICATION CHECKLIST

Before marking as complete:
- [ ] All 4 content types (image, note, drawing, audio) can be uploaded
- [ ] iPhone/Android camera photos (HEIC, JPEG) upload successfully
- [ ] Audio recordings work in web browser (mic permission)
- [ ] Audio transcription generates searchable text
- [ ] All content appears in library
- [ ] All content is searchable
- [ ] Clicking results opens correct viewer/player
- [ ] Audio files play back in browser
- [ ] Delete works for all content types (all 6 locations)
- [ ] Refresh button syncs new content
- [ ] + button fits on one line with other buttons (responsive)
- [ ] Image formats: JPEG, PNG, HEIC, WEBP all supported
- [ ] Audio formats: WebM, WAV converted to MP3
- [ ] All tests pass (unit + integration)
- [ ] Summary.json files correct for all 4 types
- [ ] No orphaned files in GCS after delete
- [ ] ChromaDB document count is accurate
- [ ] Microphone permissions handled gracefully
- [ ] Large file uploads (images/audio) don't timeout

---

**Estimated Total Time:** 8-10 days (added audio transcription complexity)
**Priority:** High (extends core functionality significantly)
**Risk Level:** Medium (complex integration, many moving parts + audio processing)

