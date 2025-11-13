"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    """Request model for search endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="Medical query in natural language")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results to return")

class TopicResult(BaseModel):
    """Single topic result"""
    topic_id: str = Field(..., description="Unique identifier for the topic")
    topic_name: str = Field(..., description="Name of the chapter/section")
    hierarchy: str = Field(..., description="Part > Chapter hierarchy path")
    preview: str = Field(..., description="Brief preview of content")
    pages: str = Field(..., description="Page range (e.g., '543-547')")
    start_page: int = Field(..., description="Starting page number")
    end_page: int = Field(..., description="Ending page number")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    tables: List[str] = Field(default_factory=list, description="Tables referenced in this section")
    figures: List[str] = Field(default_factory=list, description="Figures referenced in this section")
    pdf_source: str = Field(default="harrisons", description="PDF source: 'harrisons' or 'independent'")
    pdf_filename: str = Field(default="", description="Filename for independent PDFs")
    pdf_name: str = Field(default="", description="Display name for independent PDFs")

class SearchResponse(BaseModel):
    """Response model for search endpoint"""
    query: str = Field(..., description="Original search query")
    results: List[TopicResult] = Field(..., description="List of matching topics")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: int = Field(..., description="Search time in milliseconds")

class TopicDetail(BaseModel):
    """Detailed topic information"""
    topic_id: str
    topic_name: str
    hierarchy: str
    start_page: int
    end_page: int
    text_content: str = Field(..., description="Full text content of the topic")
    preview: str
    word_count: int
    tables: List[str]
    figures: List[str]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="System status")
    version: str = Field(..., description="API version")
    vector_store_count: int = Field(..., description="Number of indexed documents")
    message: str = Field(default="", description="Additional status message")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

# ============================================================================
# Content Management & Personal Notes Models
# ============================================================================

from datetime import datetime
from typing import Dict, Any, Literal

class ContentSource(BaseModel):
    """Base model for all content sources in the system"""
    id: str = Field(..., description="Unique identifier")
    type: Literal["harrison", "independent_pdf", "personal_note"] = Field(..., description="Content type")
    title: str = Field(..., description="Content title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    word_count: int = Field(..., description="Total word count")
    is_indexed: bool = Field(..., description="Whether content is indexed in vector store")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class HarrisonSource(ContentSource):
    """Harrison's Principles of Internal Medicine"""
    type: Literal["harrison"] = "harrison"
    total_chapters: int = Field(..., description="Total number of chapters")
    total_pages: int = Field(..., description="Total number of pages")
    
class IndependentPDFSource(ContentSource):
    """Independent PDF document"""
    type: Literal["independent_pdf"] = "independent_pdf"
    filename: str = Field(..., description="PDF filename")
    pdf_path: str = Field(..., description="Path to PDF file")
    total_pages: int = Field(..., description="Total number of pages")
    file_size: int = Field(..., description="File size in bytes")
    
class PersonalNote(ContentSource):
    """User's personal medical note"""
    type: Literal["personal_note"] = "personal_note"
    note_id: str = Field(..., description="Note identifier")
    content: str = Field(..., description="Note text content")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    linked_sources: List[str] = Field(default_factory=list, description="IDs of linked content")
    is_public: bool = Field(default=False, description="Whether note is shareable")

class PersonalNoteCreate(BaseModel):
    """Model for creating a new personal note"""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, max_length=50000, description="Note content")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    linked_sources: List[str] = Field(default_factory=list, description="Linked content IDs")

class PersonalNoteUpdate(BaseModel):
    """Model for updating an existing personal note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title")
    content: Optional[str] = Field(None, min_length=1, max_length=50000, description="Updated content")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    linked_sources: Optional[List[str]] = Field(None, description="Updated linked sources")

class LibraryStats(BaseModel):
    """Statistics about the library"""
    total_sources: int = Field(..., description="Total number of content sources")
    harrison_chapters: int = Field(..., description="Number of Harrison's chapters")
    independent_pdfs: int = Field(..., description="Number of independent PDFs")
    personal_notes: int = Field(..., description="Number of personal notes")
    total_words: int = Field(..., description="Total word count across all content")
    total_indexed: int = Field(..., description="Total indexed documents")
    last_updated: datetime = Field(..., description="Last update timestamp")
    storage_used_mb: float = Field(..., description="Storage used in megabytes")

class ContentSourceResponse(BaseModel):
    """Response model for content source operations"""
    status: str = Field(..., description="Operation status")
    source_id: str = Field(..., description="Content source ID")
    message: str = Field(default="", description="Status message")

