#!/usr/bin/env python3
"""
Process independent PDFs (non-Harrison's)
Creates chunks for vector search with PDF source tracking
"""
import fitz  # PyMuPDF
import json
import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from tqdm import tqdm
import re

@dataclass
class IndependentPDFChunk:
    """Represents a chunk from an independent PDF"""
    chunk_id: str
    pdf_name: str
    pdf_filename: str
    title: str
    start_page: int
    end_page: int
    text_content: str
    preview: str
    word_count: int
    total_pages: int


class IndependentPDFProcessor:
    """Process independent PDFs into searchable chunks"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.pdf_filename = self.pdf_path.name
        print(f"📄 Opening PDF: {self.pdf_filename}")
        self.doc = fitz.open(str(pdf_path))
        self.total_pages = len(self.doc)
        print(f"✅ PDF loaded: {self.total_pages} pages\n")
    
    def extract_text_from_range(self, start_page: int, end_page: int) -> str:
        """Extract text from a range of pages"""
        text_parts = []
        
        for page_num in range(start_page, end_page + 1):
            if page_num > self.total_pages:
                break
            page = self.doc[page_num - 1]  # 0-indexed
            text = page.get_text("text")
            text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def create_preview(self, text: str, max_length: int = 120) -> str:
        """Create preview text"""
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return "No content available"
        
        preview = text[:max_length]
        
        if len(text) > max_length:
            last_period = max(preview.rfind('.'), preview.rfind('?'), preview.rfind('!'))
            if last_period > max_length * 0.4:
                preview = preview[:last_period + 1]
            else:
                preview += "..."
        
        return preview
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text[:50]
    
    def extract_title(self) -> str:
        """Try to extract title from first page"""
        if self.total_pages == 0:
            return self.pdf_filename
        
        # Get first page text
        first_page_text = self.doc[0].get_text("text")
        lines = [l.strip() for l in first_page_text.split('\n') if l.strip()]
        
        # Try to find title (usually first substantial line)
        for line in lines[:10]:  # Check first 10 lines
            if len(line) > 10 and len(line) < 200:  # Reasonable title length
                return line
        
        # Fallback to filename without extension
        return self.pdf_filename.rsplit('.', 1)[0]
    
    def process_pdf(self, chunk_size: int = 5, custom_name: str = None) -> List[IndependentPDFChunk]:
        """
        Process PDF into chunks
        chunk_size: pages per chunk (default 5)
        custom_name: optional custom name for the PDF (overrides auto-detected title)
        """
        print(f"📚 Processing {self.pdf_filename}...")
        print(f"   Total pages: {self.total_pages}")
        print(f"   Chunk size: {chunk_size} pages\n")
        
        title = custom_name if custom_name else self.extract_title()
        print(f"   Title: {title}\n")
        
        chunks = []
        base_slug = self._slugify(self.pdf_filename.rsplit('.', 1)[0])
        
        # Create chunks
        for chunk_num, start_page in enumerate(range(1, self.total_pages + 1, chunk_size), 1):
            end_page = min(start_page + chunk_size - 1, self.total_pages)
            
            # Extract text
            text_content = self.extract_text_from_range(start_page, end_page)
            
            # Skip empty chunks
            if not text_content.strip():
                continue
            
            # Create chunk ID
            chunk_id = f"independent_{base_slug}_chunk{chunk_num}"
            
            # Create preview
            preview = self.create_preview(text_content)
            
            chunk = IndependentPDFChunk(
                chunk_id=chunk_id,
                pdf_name=title,
                pdf_filename=self.pdf_filename,
                title=f"{title} (Pages {start_page}-{end_page})",
                start_page=start_page,
                end_page=end_page,
                text_content=text_content[:10000],  # Limit for embeddings
                preview=preview,
                word_count=len(text_content.split()),
                total_pages=self.total_pages
            )
            
            chunks.append(chunk)
        
        print(f"✅ Created {len(chunks)} chunks from {self.pdf_filename}\n")
        return chunks
    
    def save_chunks(self, chunks: List[IndependentPDFChunk], output_dir: str = None):
        """
        Save chunks to JSON files
        
        Args:
            chunks: List of chunks to save
            output_dir: Directory to save chunks to (auto-detects if None)
        """
        # Auto-detect output directory
        if output_dir is None:
            # Try cloud path first (for deployed app)
            if Path("/app/data/processed/independent_chunks").exists():
                output_dir = "/app/data/processed/independent_chunks"
            # Then try data directory (for local development)
            elif Path("../data/processed/independent_chunks").exists():
                output_dir = "../data/processed/independent_chunks"
            # Finally try relative to current directory
            else:
                output_dir = "../data/processed/independent_chunks"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Saving {len(chunks)} chunks to {output_path}...")
        
        for chunk in chunks:
            chunk_file = output_path / f"{chunk.chunk_id}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(chunk), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(chunks)} chunks successfully\n")
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()


def process_all_independent_pdfs(
    pdfs_dir: str = "../data/independant_pdfs",
    output_dir: str = "../data/processed/independent_chunks"
):
    """Process all PDFs in the independent PDFs directory"""
    
    print("\n" + "="*70)
    print("🔄 PROCESSING INDEPENDENT PDFs")
    print("="*70 + "\n")
    
    pdfs_path = Path(pdfs_dir)
    if not pdfs_path.exists():
        print(f"❌ Directory not found: {pdfs_dir}")
        return []
    
    # Find all PDF files
    pdf_files = list(pdfs_path.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {pdfs_dir}")
        return []
    
    print(f"📁 Found {len(pdf_files)} PDF file(s):\n")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each PDF
    all_chunks = []
    
    for pdf_file in pdf_files:
        try:
            processor = IndependentPDFProcessor(pdf_file)
            chunks = processor.process_pdf()
            
            # Save chunks
            for chunk in chunks:
                chunk_file = output_path / f"{chunk.chunk_id}.json"
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(chunk), f, indent=2, ensure_ascii=False)
            
            all_chunks.extend(chunks)
            processor.close()
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            continue
    
    # Save summary
    summary = {
        "total_pdfs": len(pdf_files),
        "total_chunks": len(all_chunks),
        "pdfs_processed": [
            {
                "filename": chunk.pdf_filename,
                "title": chunk.pdf_name,
                "total_pages": chunk.total_pages,
                "chunks": len([c for c in all_chunks if c.pdf_filename == chunk.pdf_filename])
            }
            for chunk in all_chunks
            if chunk.chunk_id == [c.chunk_id for c in all_chunks if c.pdf_filename == chunk.pdf_filename][0]
        ]
    }
    
    summary_file = output_path / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ INDEPENDENT PDF PROCESSING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   PDFs processed: {summary['total_pdfs']}")
    print(f"   Total chunks: {summary['total_chunks']}")
    print(f"\n📁 Output directory: {output_path}")
    print(f"   Individual chunks: {len(all_chunks)} files")
    print("="*70 + "\n")
    
    return all_chunks


if __name__ == "__main__":
    import sys
    
    # Check if running as single file processor (from API upload)
    if len(sys.argv) > 1:
        # Single PDF processing mode
        try:
            pdf_path = sys.argv[1]
            custom_name = sys.argv[2] if len(sys.argv) > 2 else None
            
            print(f"📄 Processing single PDF: {pdf_path}")
            print(f"   Custom name: {custom_name or 'Auto-detect'}\n")
            
            processor = IndependentPDFProcessor(pdf_path)
            chunks = processor.process_pdf(custom_name=custom_name)
            
            processor.save_chunks(chunks)
            
            print(f"✅ Successfully processed {len(chunks)} chunks!")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Batch processing mode (process all)
        try:
            chunks = process_all_independent_pdfs()
            print(f"✅ Successfully processed {len(chunks)} chunks!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

