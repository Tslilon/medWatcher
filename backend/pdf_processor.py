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
from tqdm import tqdm

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
        print(f"📖 Opening PDF: {pdf_path}")
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        print(f"✅ PDF loaded: {self.total_pages:,} pages\n")
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page"""
        if page_num < 1 or page_num > self.total_pages:
            return ""
        
        page = self.doc[page_num - 1]  # 0-indexed
        text = page.get_text("text")
        return text
    
    def extract_text_from_range(self, start_page: int, end_page: int) -> str:
        """Extract text from a range of pages"""
        text_parts = []
        
        # Limit range to avoid excessive extraction
        actual_end = min(end_page, start_page + 100)  # Max 100 pages per chunk
        if actual_end != end_page:
            print(f"      ⚠️  Limiting extraction to {actual_end - start_page + 1} pages (from {end_page - start_page + 1})")
        
        for page_num in range(start_page, actual_end + 1):
            if page_num > self.total_pages:
                break
            text = self.extract_text_from_page(page_num)
            text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def find_tables_in_range(self, start_page: int, end_page: int) -> List[str]:
        """Find table references in page range"""
        text = self.extract_text_from_range(start_page, min(end_page, start_page + 20))
        
        # Look for "Table X-Y" or "TABLE X-Y" patterns
        table_pattern = r'Table\s+\d+[-\.]?\d*(?:-\d+)?'
        tables = re.findall(table_pattern, text, re.I)
        
        # Deduplicate and clean
        tables = list(set(tables))
        tables = [t.strip() for t in tables if t.strip()]
        
        return sorted(tables)[:10]  # Limit to 10 tables
    
    def find_figures_in_range(self, start_page: int, end_page: int) -> List[str]:
        """Find figure references in page range"""
        text = self.extract_text_from_range(start_page, min(end_page, start_page + 20))
        
        # Look for "Figure X-Y" or "Fig. X-Y" patterns
        figure_pattern = r'(?:Figure|Fig\.)\s+\d+[-\.]?\d*(?:-\d+)?'
        figures = re.findall(figure_pattern, text, re.I)
        
        # Deduplicate and clean
        figures = list(set(figures))
        figures = [f.strip() for f in figures if f.strip()]
        
        return sorted(figures)[:10]  # Limit to 10 figures
    
    def create_preview(self, text: str, max_length: int = 120) -> str:
        """Create preview text (first meaningful sentence)"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return "No content available"
        
        # Get first max_length characters
        preview = text[:max_length]
        
        # Try to end at sentence boundary
        if len(text) > max_length:
            # Look for period, question mark, or exclamation
            last_period = max(preview.rfind('.'), preview.rfind('?'), preview.rfind('!'))
            if last_period > max_length * 0.4:  # At least 40% through
                preview = preview[:last_period + 1]
            else:
                preview += "..."
        
        return preview
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        # Remove chapter numbers at start
        text = re.sub(r'^\d+\s+', '', text)
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'[-\s]+', '_', text)
        return text[:50]  # Limit length
    
    def process_hierarchy_from_toc(self, toc_file: str = "../data/extracted_toc.json") -> List[Part]:
        """
        Process PDF using extracted TOC structure
        This creates a simplified version focusing on chapters as our main units
        """
        
        print(f"📊 Loading TOC from: {toc_file}\n")
        
        with open(toc_file, 'r') as f:
            toc_data = json.load(f)
        
        entries = toc_data["entries"]
        
        # Filter to get actual medical content (skip front matter)
        # Look for entries that start with "PART" followed by a number
        medical_entries = []
        in_medical_content = False
        
        for entry in entries:
            title = entry["title"]
            # Start collecting when we hit PART 1 or similar
            if re.match(r'PART\s+\d+', title, re.I):
                in_medical_content = True
            
            if in_medical_content:
                # Stop at Index
                if title.lower() == "index":
                    break
                medical_entries.append(entry)
        
        print(f"📚 Found {len(medical_entries)} medical content entries")
        print(f"   Processing chapters as main searchable units...\n")
        
        # Process into Parts → Chapters (treating level 2 & 3 as chapters/topics)
        parts = []
        current_part = None
        current_part_num = 0
        
        for entry in tqdm(medical_entries, desc="Processing sections", unit="section"):
            level = entry["level"]
            title = entry["title"]
            page = entry["page"]
            
            # Level 1: PART markers
            if level == 1 and re.match(r'PART\s+\d+', title, re.I):
                # Save previous part
                if current_part:
                    parts.append(current_part)
                
                # Extract part number
                part_match = re.search(r'PART\s+(\d+)', title, re.I)
                current_part_num = int(part_match.group(1)) if part_match else current_part_num + 1
                
                current_part = {
                    "part_id": f"part{current_part_num}",
                    "part_number": current_part_num,
                    "part_name": title,
                    "start_page": page,
                    "chapters": []
                }
            
            # Level 2 & 3: Chapters and Sections (we'll treat both as searchable units)
            elif level in [2, 3] and current_part:
                # Extract chapter number if present
                chapter_match = re.search(r'^(\d+)\s+', title)
                chapter_num = int(chapter_match.group(1)) if chapter_match else len(current_part["chapters"]) + 1
                
                chapter = {
                    "chapter_number": chapter_num,
                    "chapter_name": title,
                    "start_page": page,
                    "level": level  # Track if it's a main chapter or subsection
                }
                
                current_part["chapters"].append(chapter)
        
        # Add last part
        if current_part:
            parts.append(current_part)
        
        print(f"\n✅ Structured into {len(parts)} parts")
        
        # Calculate end pages
        for i, part in enumerate(parts):
            # Part end page
            if i < len(parts) - 1:
                part["end_page"] = parts[i + 1]["start_page"] - 1
            else:
                part["end_page"] = self.total_pages
            
            # Chapter end pages
            chapters = part["chapters"]
            for j, chapter in enumerate(chapters):
                if j < len(chapters) - 1:
                    chapter["end_page"] = chapters[j + 1]["start_page"] - 1
                else:
                    chapter["end_page"] = part["end_page"]
        
        return parts
    
    def extract_chapter_content(self, chapter: Dict, part_number: int) -> Topic:
        """Extract content for a single chapter/section"""
        
        start_page = chapter["start_page"]
        end_page = chapter["end_page"]
        
        # Limit page range to reasonable size
        page_count = end_page - start_page + 1
        if page_count > 50:
            # For very long chapters, just extract first 30 pages
            end_page = start_page + 29
        
        # Extract text
        text_content = self.extract_text_from_range(start_page, end_page)
        
        # Find tables and figures (only in first few pages to save time)
        tables = self.find_tables_in_range(start_page, min(start_page + 5, end_page))
        figures = self.find_figures_in_range(start_page, min(start_page + 5, end_page))
        
        # Create preview
        preview = self.create_preview(text_content)
        
        # Create topic ID
        slug = self._slugify(chapter["chapter_name"])
        topic_id = f"part{part_number}_ch{chapter['chapter_number']}_{slug}"
        
        topic = Topic(
            topic_id=topic_id,
            topic_name=chapter["chapter_name"],
            start_page=chapter["start_page"],
            end_page=chapter["end_page"],
            text_content=text_content[:10000],  # Limit to 10K chars for embeddings
            preview=preview,
            word_count=len(text_content.split()),
            has_tables=tables,
            has_figures=figures
        )
        
        return topic
    
    def process_and_save(self, output_dir: str = "../data/processed"):
        """Main processing function: extract and save all content"""
        
        print("\n" + "="*70)
        print("🚀 STARTING PDF CONTENT EXTRACTION")
        print("="*70 + "\n")
        
        # Load and process TOC
        parts = self.process_hierarchy_from_toc()
        
        # Create output directories
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        chunks_dir = output_path / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        print(f"\n📝 Extracting content from chapters...")
        print(f"   This will take a few minutes...\n")
        
        # Process each part and chapter
        all_topics = []
        
        for part in tqdm(parts, desc="Processing parts", unit="part"):
            part_topics = []
            
            for chapter in tqdm(part["chapters"], desc=f"  Part {part['part_number']} chapters", 
                              unit="ch", leave=False):
                try:
                    topic = self.extract_chapter_content(chapter, part["part_number"])
                    part_topics.append(topic)
                    all_topics.append(topic)
                    
                    # Save individual topic file
                    topic_file = chunks_dir / f"{topic.topic_id}.json"
                    with open(topic_file, 'w', encoding='utf-8') as f:
                        json.dump(asdict(topic), f, indent=2, ensure_ascii=False)
                    
                except Exception as e:
                    print(f"\n    ⚠️  Error processing {chapter['chapter_name']}: {e}")
                    continue
        
        # Save complete hierarchy with all content
        print(f"\n💾 Saving processed data...")
        
        hierarchy_output = {
            "metadata": {
                "title": "Harrison's Principles of Internal Medicine",
                "edition": "21st",
                "year": 2022,
                "total_parts": len(parts),
                "total_topics": len(all_topics),
                "processing_note": "Each chapter/section is a searchable topic"
            },
            "parts": [
                {
                    "part_id": part["part_id"],
                    "part_number": part["part_number"],
                    "part_name": part["part_name"],
                    "start_page": part["start_page"],
                    "end_page": part["end_page"],
                    "topic_count": len([t for t in all_topics if t.topic_id.startswith(f"part{part['part_number']}_")])
                }
                for part in parts
            ]
        }
        
        hierarchy_file = output_path / "complete_hierarchy.json"
        with open(hierarchy_file, 'w', encoding='utf-8') as f:
            json.dump(hierarchy_output, f, indent=2, ensure_ascii=False)
        
        # Create processing summary
        summary = {
            "total_parts": len(parts),
            "total_topics": len(all_topics),
            "total_words": sum(t.word_count for t in all_topics),
            "avg_words_per_topic": sum(t.word_count for t in all_topics) // len(all_topics) if all_topics else 0,
            "topics_with_tables": sum(1 for t in all_topics if t.has_tables),
            "topics_with_figures": sum(1 for t in all_topics if t.has_figures),
            "output_directory": str(output_path),
            "chunks_directory": str(chunks_dir)
        }
        
        summary_file = output_path / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n" + "="*70)
        print("✅ PDF PROCESSING COMPLETE!")
        print("="*70)
        print(f"\n📊 Processing Summary:")
        print(f"   Parts: {summary['total_parts']}")
        print(f"   Searchable topics: {summary['total_topics']}")
        print(f"   Total words extracted: {summary['total_words']:,}")
        print(f"   Average words per topic: {summary['avg_words_per_topic']:,}")
        print(f"   Topics with tables: {summary['topics_with_tables']}")
        print(f"   Topics with figures: {summary['topics_with_figures']}")
        print(f"\n📁 Output files:")
        print(f"   Complete hierarchy: {hierarchy_file}")
        print(f"   Summary: {summary_file}")
        print(f"   Individual topics: {chunks_dir}/ ({len(all_topics)} files)")
        print(f"\n🎯 Next step: Generate embeddings for vector search")
        print("="*70 + "\n")
        
        return all_topics
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()


def main():
    """Main processing function"""
    
    # Path to PDF
    pdf_path = "../Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf"
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        print(f"   Please ensure the PDF is in the correct location.")
        return
    
    # Check if TOC exists
    toc_file = "../data/extracted_toc.json"
    if not Path(toc_file).exists():
        print(f"❌ TOC file not found: {toc_file}")
        print(f"   Please run scripts/extract_toc.py first")
        return
    
    # Process PDF
    processor = HarrisonPDFProcessor(pdf_path)
    
    try:
        topics = processor.process_and_save()
        print(f"✅ Successfully processed {len(topics)} topics!")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.close()


if __name__ == "__main__":
    main()

