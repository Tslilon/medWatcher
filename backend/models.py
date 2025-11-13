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

