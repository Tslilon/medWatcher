"""
FastAPI Backend for Harrison's Medical RAG System
Provides REST API for natural language medical queries
"""
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import time
from typing import Optional
import traceback
from pathlib import Path
import tempfile
import os

from models import (
    SearchRequest,
    SearchResponse,
    TopicDetail,
    HealthResponse,
    ErrorResponse
)
from hierarchical_search import get_search_engine
from vector_store import ChromaVectorStore
from whisper_transcribe import get_transcriber

# Initialize FastAPI app
app = FastAPI(
    title="Harrison's Medical RAG API",
    description="Semantic search API for Harrison's Principles of Internal Medicine (21st Edition)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (for web/mobile clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory path for web interface
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize search engine on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("\n" + "="*70)
    print("🚀 Starting Harrison's Medical RAG API...")
    print("="*70)
    try:
        get_search_engine()  # Initialize search engine
        print("✅ Search engine ready!")
        print("✅ API server started successfully!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        traceback.print_exc()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc)
        }
    )

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Harrison's Medical RAG API",
        "version": "1.0.0",
        "description": "Natural language search for Harrison's Principles of Internal Medicine",
        "endpoints": {
            "web": "GET /web - Web interface for mobile testing",
            "health": "GET /health - Health check",
            "search": "POST /api/search - Search medical topics",
            "topic": "GET /api/topic/{topic_id} - Get topic details",
            "docs": "GET /docs - Interactive API documentation",
        },
        "coverage": "Harrison's Principles of Internal Medicine, 21st Edition (15,164 pages)",
        "indexed_topics": 550
    }

@app.get("/web", response_class=HTMLResponse, tags=["General"])
async def web_interface():
    """
    Mobile-friendly web interface for testing
    
    Access this from your iPhone/iPad to test the API before building the Watch app
    """
    static_file = Path(__file__).parent / "static" / "index.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Web interface not found")

@app.get("/library", response_class=HTMLResponse, tags=["General"])
async def library_interface():
    """
    Library management interface
    
    View and manage all content sources (Harrison's, PDFs, notes)
    """
    static_file = Path(__file__).parent / "static" / "library.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Library interface not found")

@app.get("/viewer", response_class=HTMLResponse, tags=["General"])
async def pdf_viewer(request: Request):
    """
    PDF viewer with automatic page jumping
    
    Opens Harrison's PDF at the specified page
    Query params: start, end, topic
    
    For Apple Watch: Uses simple page-by-page image viewer
    For desktop/mobile: Uses PDF.js viewer
    """
    # Check if request is from Apple Watch
    user_agent = request.headers.get("user-agent", "").lower()
    is_watch = "watch" in user_agent or request.query_params.get("watch") == "1"
    
    if is_watch:
        # For Watch: redirect to simple page-by-page viewer
        query_string = str(request.query_params)
        redirect_url = f"/viewer/watch-simple?{query_string}" if query_string else "/viewer/watch-simple"
        return RedirectResponse(url=redirect_url)
    
    # Standard PDF.js viewer for desktop/mobile
    static_file = Path(__file__).parent / "static" / "pdfviewer.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Viewer not found")

@app.get("/viewer/watch-simple", response_class=HTMLResponse, tags=["General"])
async def watch_simple_viewer():
    """
    Ultra-simple page-by-page image viewer for Apple Watch
    
    Shows ONE page at a time as a small JPEG image
    Query params: start, end
    """
    static_file = Path(__file__).parent / "static" / "watch-simple-viewer.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Watch viewer not found")

@app.get("/viewer/compact", response_class=HTMLResponse, tags=["General"])
async def compact_viewer():
    """
    Compact image-based viewer (115% zoom)
    
    Continuous scroll image viewer with 115% zoom
    Query params: start, end
    """
    static_file = Path(__file__).parent / "static" / "compact-viewer.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Compact viewer not found")

@app.get("/viewer/independent", response_class=HTMLResponse, tags=["General"])
async def independent_pdf_viewer():
    """
    Viewer for independent PDFs (100% zoom)
    
    Query params: start, end, pdf (filename)
    """
    static_file = Path(__file__).parent / "static" / "independent-viewer.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Independent viewer not found")

@app.get("/viewer/watch-wristdocs", response_class=HTMLResponse, tags=["General"])
async def watch_wristdocs_instructions(request: Request):
    """
    Instructions for using WristDocs app (alternative for Watch users)
    """
    start_page = request.query_params.get("start", "1")
    end_page = request.query_params.get("end", start_page)
    topic = request.query_params.get("topic", "Chapter")
    
    watch_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Apple Watch - Use WristDocs</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                    background: #000;
                    color: #fff;
                    padding: 15px;
                    font-size: 13px;
                    line-height: 1.4;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                h1 {{ font-size: 16px; margin: 0; }}
                .info {{ 
                    background: #1a1a1a; 
                    padding: 12px; 
                    border-radius: 8px; 
                    margin-bottom: 12px;
                    border: 1px solid #333;
                }}
                .app-link {{
                    background: #28a745;
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                    text-decoration: none;
                    display: block;
                    margin: 12px 0;
                    font-weight: 600;
                }}
                .pdf-link {{
                    background: #007bff;
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                    text-decoration: none;
                    display: block;
                    margin: 12px 0;
                    font-weight: 600;
                }}
                .step {{ margin: 8px 0; }}
                .emoji {{ font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⌚ Apple Watch Detected</h1>
            </div>
            
            <div class="info">
                <p><strong>📖 {topic}</strong></p>
                <p>Pages {start_page}-{end_page}</p>
            </div>
            
            <div class="info">
                <p><span class="emoji">⚠️</span> <strong>Web viewer doesn't work on Watch</strong></p>
                <p style="margin-top: 8px;">The 196MB PDF is too heavy for Watch's browser. Use <strong>WristDocs</strong> app instead!</p>
            </div>
            
            <a href="https://apps.apple.com/app/pdf-watch-viewer-wristdocs/id6745387064" class="app-link">
                📲 Get WristDocs App
            </a>
            
            <a href="https://storage.googleapis.com/harrisons-rag-data-flingoos/harrisons.pdf" class="pdf-link">
                📥 Download Harrison's PDF
            </a>
            
            <div class="info">
                <p><strong>How to use:</strong></p>
                <div class="step">1. Install WristDocs on iPhone</div>
                <div class="step">2. Download PDF (link above)</div>
                <div class="step">3. Open PDF in WristDocs</div>
                <div class="step">4. Sync to Watch</div>
                <div class="step">5. View on Watch offline!</div>
            </div>
            
            <div class="info" style="font-size: 11px; color: #999;">
                <p>💡 <strong>Tip:</strong> Jump to page {start_page} in WristDocs to read this chapter</p>
            </div>
        </body>
        </html>
        """
    return HTMLResponse(content=watch_html)

@app.get("/viewer/watch", response_class=HTMLResponse, tags=["General"])
async def watch_viewer(request: Request):
    """
    Lightweight PDF viewer for Apple Watch using server-rendered images
    
    Query params: start, end, topic
    """
    static_file = Path(__file__).parent / "static" / "watchviewer.html"
    if static_file.exists():
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Watch viewer not found")

@app.get("/pdf", tags=["General"])
async def serve_pdf():
    """
    Serve Harrison's PDF file
    
    For production: Redirects to Google Cloud Storage (avoids Cloud Run size limits)
    For local: Serves from local file
    """
    import os
    
    # Check if running in Cloud Run
    if os.getenv("K_SERVICE"):
        # Production: Redirect to GCS public URL
        gcs_url = "https://storage.googleapis.com/harrisons-rag-data-flingoos/harrisons.pdf"
        return RedirectResponse(url=gcs_url)
    else:
        # Local: Serve from file
        local_pdf = Path(__file__).parent / "static" / "harrisons.pdf"
        if local_pdf.exists():
            return FileResponse(
                local_pdf,
                media_type="application/pdf",
                filename="harrisons.pdf"
            )
        else:
            raise HTTPException(status_code=404, detail="PDF not found")

@app.get("/pdf/page/{page_number}", tags=["General"])
async def render_pdf_page(page_number: int, width: int = 250, quality: int = 60):
    """
    Render a single PDF page as an ultra-lightweight JPEG for Apple Watch
    
    Args:
        page_number: Page number (1-indexed)
        width: Image width in pixels (default 250 for Apple Watch ~200px screen)
        quality: JPEG quality 1-100 (default 60 for smaller files)
    """
    import fitz  # PyMuPDF
    from PIL import Image
    from io import BytesIO
    
    # Get PDF path
    cloud_pdf = Path("/app/static/harrisons.pdf")
    local_pdf = Path(__file__).parent / "static" / "harrisons.pdf"
    pdf_path = cloud_pdf if cloud_pdf.exists() else local_pdf
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        
        # Validate page number
        if page_number < 1 or page_number > doc.page_count:
            doc.close()
            raise HTTPException(status_code=400, detail=f"Invalid page number. Must be between 1 and {doc.page_count}")
        
        # Get page (0-indexed in PyMuPDF)
        page = doc[page_number - 1]
        
        # Calculate zoom for very small width (Apple Watch)
        zoom = width / page.rect.width
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap with lower quality
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to JPEG with compression
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
        img_bytes = img_buffer.getvalue()
        
        doc.close()
        
        # Return as JPEG (much smaller than PNG)
        from fastapi.responses import Response
        return Response(
            content=img_bytes, 
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                "Content-Length": str(len(img_bytes))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering page: {str(e)}")

@app.get("/pdf/independent/page/{pdf_filename}/{page_number}", tags=["General"])
async def render_independent_pdf_page(pdf_filename: str, page_number: int, width: int = 800, quality: int = 100):
    """
    Render a single page from an independent PDF as a JPEG
    
    Args:
        pdf_filename: Name of the PDF file
        page_number: Page number (1-indexed)
        width: Image width in pixels (default 800)
        quality: JPEG quality 1-100 (default 100 for high quality)
    """
    import fitz  # PyMuPDF
    from PIL import Image
    from io import BytesIO
    import os
    
    # Get PDF path - check both cloud and local locations
    cloud_pdf = Path(f"/app/data/independant_pdfs/{pdf_filename}")
    local_pdf = Path(__file__).parent.parent / "data" / "independant_pdfs" / pdf_filename
    
    pdf_path = cloud_pdf if cloud_pdf.exists() else local_pdf
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_filename}")
    
    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        
        # Validate page number
        if page_number < 1 or page_number > doc.page_count:
            doc.close()
            raise HTTPException(status_code=400, detail=f"Invalid page number. Must be between 1 and {doc.page_count}")
        
        # Get page (0-indexed in PyMuPDF)
        page = doc[page_number - 1]
        
        # Calculate zoom
        zoom = width / page.rect.width
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to JPEG
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
        img_bytes = img_buffer.getvalue()
        
        doc.close()
        
        # Return as JPEG
        from fastapi.responses import Response
        return Response(
            content=img_bytes,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                "Content-Length": str(len(img_bytes))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering page: {str(e)}")

@app.get("/static/sw.js", tags=["General"])
async def serve_service_worker():
    """Serve the service worker for PWA offline support"""
    sw_file = Path(__file__).parent / "static" / "sw.js"
    if sw_file.exists():
        return FileResponse(sw_file, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="Service worker not found")

@app.get("/static/manifest.json", tags=["General"])
async def serve_manifest():
    """Serve the PWA manifest"""
    manifest_file = Path(__file__).parent / "static" / "manifest.json"
    if manifest_file.exists():
        return FileResponse(manifest_file, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and document count
    """
    try:
        vector_store = ChromaVectorStore()
        count = vector_store.count_documents()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vector_store_count=count,
            message=f"System operational with {count} indexed documents"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
async def search_harrisons(request: SearchRequest):
    """
    Search Harrison's using natural language
    
    **Examples:**
    - "What is the workup for hyponatremia?"
    - "Acute myocardial infarction management"
    - "Pneumonia antibiotic selection"
    - "Diabetes type 2 treatment guidelines"
    
    **Returns:**
    - List of relevant medical topics with page numbers
    - Relevance scores
    - References to tables and figures
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
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/topic/{topic_id}", response_model=TopicDetail, tags=["Topics"])
async def get_topic(topic_id: str):
    """
    Get full details for a specific topic
    
    **Parameters:**
    - topic_id: Unique identifier (e.g., 'part4_ch76_cancer_of_the_skin')
    
    **Returns:**
    - Complete topic information including full text content
    """
    try:
        search_engine = get_search_engine()
        topic_data = search_engine.get_topic_details(topic_id)
        
        if not topic_data:
            raise HTTPException(
                status_code=404,
                detail=f"Topic not found: {topic_id}"
            )
        
        # Build hierarchy string
        hierarchy = search_engine._build_hierarchy_string(
            topic_id,
            topic_data['topic_name']
        )
        
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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve topic: {str(e)}"
        )

@app.get("/api/stats", tags=["General"])
async def get_stats():
    """
    Get system statistics
    
    Returns information about indexed content and system status
    """
    try:
        vector_store = ChromaVectorStore()
        search_engine = get_search_engine()
        
        return {
            "indexed_documents": vector_store.count_documents(),
            "total_pages": 15164,
            "edition": "21st",
            "year": 2022,
            "embedding_model": "text-embedding-3-large",
            "vector_dimensions": 3072,
            "total_parts": 20,
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

@app.post("/api/transcribe", tags=["Voice"])
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio using OpenAI Whisper API with medical context
    
    **Supports:** webm, mp3, wav, m4a, ogg
    
    **Features:**
    - High-quality medical terminology recognition
    - Context-aware transcription
    - Understands: hyponatremia, hypernatremia, acute MI, etc.
    
    **Returns:**
    - Transcribed text optimized for medical queries
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()
        
        # Get transcriber
        transcriber = get_transcriber()
        
        # Transcribe with medical context
        result = transcriber.transcribe_audio_bytes(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio.webm"
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "text": result["text"],
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio transcription error: {str(e)}"
        )

# ============================================================================
# Library Management API Endpoints
# ============================================================================

from library_manager import LibraryManager
library_manager = LibraryManager()

@app.get("/api/library", tags=["Library"])
async def get_library(source_type: Optional[str] = None):
    """
    Get all content sources in the library
    
    Query params:
    - source_type: Filter by type ('harrison', 'independent_pdf', 'personal_note')
    """
    try:
        sources = library_manager.get_all_sources(source_type)
        return {
            "sources": sources,
            "total": len(sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving library: {str(e)}")

@app.get("/api/library/stats", tags=["Library"])
async def get_library_stats():
    """Get statistics about the library"""
    try:
        stats = library_manager.get_library_stats()
        return stats.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@app.get("/api/library/search", tags=["Library"])
async def search_library(query: str, source_type: Optional[str] = None):
    """Search library by title or content"""
    try:
        results = library_manager.search_library(query, source_type)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching library: {str(e)}")

@app.get("/api/library/{source_id}", tags=["Library"])
async def get_source_details(source_id: str):
    """Get detailed information about a specific content source"""
    try:
        source = library_manager.get_source_by_id(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving source: {str(e)}")

@app.delete("/api/library/{source_id}", tags=["Library"])
async def delete_source(source_id: str):
    """Delete a content source (PDF or note, not Harrison's)"""
    try:
        result = library_manager.delete_source(source_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting source: {str(e)}")

# ============================================================================
# Personal Notes API Endpoints
# ============================================================================

from models import PersonalNoteCreate, PersonalNoteUpdate

@app.post("/api/notes", tags=["Notes"])
async def create_note(note: PersonalNoteCreate):
    """Create a new personal note"""
    try:
        # Implementation will be in note_processor.py (Phase 2)
        return {"status": "pending", "message": "Note creation coming in Phase 2"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")

@app.get("/api/notes", tags=["Notes"])
async def get_all_notes():
    """Get all personal notes"""
    try:
        sources = library_manager.get_all_sources(source_type="personal_note")
        return {
            "notes": sources,
            "total": len(sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notes: {str(e)}")

@app.get("/api/notes/{note_id}", tags=["Notes"])
async def get_note(note_id: str):
    """Get a specific note"""
    try:
        note = library_manager.get_source_by_id(note_id)
        if not note or note['type'] != 'personal_note':
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving note: {str(e)}")

@app.put("/api/notes/{note_id}", tags=["Notes"])
async def update_note(note_id: str, note: PersonalNoteUpdate):
    """Update an existing note"""
    try:
        # Implementation will be in note_processor.py (Phase 2)
        return {"status": "pending", "message": "Note update coming in Phase 2"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")

@app.delete("/api/notes/{note_id}", tags=["Notes"])
async def delete_note(note_id: str):
    """Delete a note"""
    try:
        result = library_manager.delete_source(note_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")

# ============================================================================
# PDF Upload & Processing Endpoint
# ============================================================================

import shutil
import subprocess
from fastapi import Form

@app.post("/api/reload-from-gcs", tags=["Library"])
async def reload_from_gcs_endpoint():
    """
    Manually reload ChromaDB from GCS
    
    Useful when:
    - Files uploaded to GCS externally
    - Want to sync deployed server without redeploying
    - Testing/debugging
    """
    try:
        from reload_from_gcs import full_reload
        
        if full_reload():
            return {
                "status": "success",
                "message": "ChromaDB reloaded from GCS successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reload from GCS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload error: {str(e)}")

@app.post("/api/upload-pdf", tags=["Library"])
async def upload_pdf(file: UploadFile = File(...), pdf_name: str = Form(...)):
    """
    Upload a PDF directly to GCS, process it, and index it into the RAG
    
    Steps:
    1. Save PDF to local temp directory
    2. Upload PDF to GCS
    3. Process PDF into chunks (saves to local)
    4. Upload chunks to GCS
    5. Index chunks into ChromaDB
    6. Upload ChromaDB to GCS
    7. Return success
    """
    try:
        from gcs_helper import upload_to_gcs, upload_directory_to_gcs, check_gcs_available
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check if GCS is available
        if not check_gcs_available():
            raise HTTPException(status_code=500, detail="GCS not available. Please install Google Cloud SDK.")
        
        # Determine paths
        data_dir = Path("../data")
        if not data_dir.exists():
            data_dir = Path("data")
        
        pdfs_dir = data_dir / "independant_pdfs"
        pdfs_dir.mkdir(parents=True, exist_ok=True)
        
        chunks_dir = data_dir / "processed" / "independent_chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        
        chroma_dir = data_dir / "chroma_db"
        
        # Save uploaded file locally (temp)
        pdf_filename = file.filename
        pdf_path = pdfs_dir / pdf_filename
        
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload PDF to GCS immediately
        print(f"☁️ Uploading PDF to GCS: {pdf_filename}")
        if not upload_to_gcs(str(pdf_path), f"independant_pdfs/{pdf_filename}"):
            raise HTTPException(status_code=500, detail="Failed to upload PDF to GCS")
        
        # Process the PDF (chunk it)
        print(f"📄 Processing PDF: {pdf_filename}")
        process_result = subprocess.run(
            ["python3", "process_independent_pdfs.py", str(pdf_path), pdf_name],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if process_result.returncode != 0:
            print(f"❌ Processing error: {process_result.stderr}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {process_result.stderr}")
        
        # Upload chunks to GCS (includes summary.json)
        print(f"☁️ Uploading chunks to GCS...")
        if not upload_directory_to_gcs(str(chunks_dir), "processed/independent_chunks"):
            print("⚠️ Warning: Failed to upload chunks to GCS")
        else:
            print(f"   ✅ Uploaded chunks and summary.json")
        
        # Index the chunks
        print(f"🔍 Indexing PDF chunks...")
        index_result = subprocess.run(
            ["python3", "index_documents.py", "--force"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if index_result.returncode != 0:
            print(f"❌ Indexing error: {index_result.stderr}")
            raise HTTPException(status_code=500, detail=f"Indexing failed: {index_result.stderr}")
        
        # Upload ChromaDB to GCS
        print(f"☁️ Uploading ChromaDB to GCS...")
        if not upload_directory_to_gcs(str(chroma_dir), "chroma_db"):
            print("⚠️ Warning: Failed to upload ChromaDB to GCS")
        
        # Reload the vector store to pick up new documents
        print(f"🔄 Reloading vector store...")
        
        # Check if we're on Cloud Run (deployed)
        is_cloud = Path("/app/data").exists()
        
        if is_cloud:
            # On Cloud Run: Reload from GCS
            print(f"   ☁️ Cloud environment detected - reloading from GCS...")
            from reload_from_gcs import full_reload
            if full_reload():
                print(f"   ✅ Reloaded from GCS successfully")
            else:
                print(f"   ⚠️ GCS reload failed, using local reload")
                import hierarchical_search
                hierarchical_search._search_engine = None
                search_engine = get_search_engine()
                print(f"   ✅ Vector store reloaded with {search_engine.vector_store.count_documents()} documents")
        else:
            # Local: Just reload from disk
            import hierarchical_search
            hierarchical_search._search_engine = None  # Reset singleton
            search_engine = get_search_engine()  # Will create new instance
            print(f"   ✅ Vector store reloaded with {search_engine.vector_store.count_documents()} documents")
        
        print(f"✅ PDF uploaded to GCS and indexed successfully: {pdf_name}")
        
        return {
            "status": "success",
            "message": f"PDF '{pdf_name}' uploaded to GCS and indexed successfully",
            "filename": pdf_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

# Development mode run
if __name__ == "__main__":
    import uvicorn
    
    import socket
    
    # Get local IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "localhost"
    
    print("\n" + "="*70)
    print("🏥 Starting Harrison's Medical RAG API Server (HTTPS)")
    print("="*70)
    print(f"📍 API: https://{local_ip}:8000")
    print(f"📱 Web Interface: https://{local_ip}:8000/web")
    print(f"📚 Docs: https://{local_ip}:8000/docs")
    print("="*70)
    print("⚠️  FIRST TIME: Accept self-signed certificate on iPhone!")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )

