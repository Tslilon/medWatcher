#!/usr/bin/env python3
"""
Extract Table of Contents from Harrison's PDF
This script analyzes the PDF structure to identify:
- Parts (major sections like "Oncology and Hematology")
- Chapters (e.g., "Chapter 81: Cancer of the Skin")
- Page numbers for each section
"""
import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_toc_from_pdf(pdf_path: str, output_path: str = "../data/extracted_toc.json"):
    """
    Extract TOC using PDF outline/bookmarks
    
    PDFs often have embedded bookmarks that represent the structure.
    We'll extract these and analyze them.
    """
    
    print(f"📖 Opening PDF: {pdf_path}")
    print(f"   This may take a moment for large files...\n")
    
    doc = fitz.open(pdf_path)
    
    print(f"✅ PDF loaded successfully!")
    print(f"   Total pages: {len(doc):,}")
    print(f"   File size: {Path(pdf_path).stat().st_size / (1024*1024):.1f} MB\n")
    
    # Get PDF outline (bookmarks/table of contents)
    toc = doc.get_toc()
    
    if not toc:
        print("⚠️  No TOC/bookmarks found in PDF.")
        print("   The PDF may not have an embedded table of contents.")
        print("   We'll need to extract it manually or from text patterns.\n")
        return None
    
    print(f"✅ Found {len(toc)} TOC entries in PDF outline!\n")
    
    # Parse TOC structure
    # TOC format: [(level, title, page_number), ...]
    # Level 1 = Parts, Level 2 = Chapters, Level 3 = Sections
    
    structure = {
        "metadata": {
            "source_pdf": pdf_path,
            "total_pages": len(doc),
            "toc_entries": len(toc),
            "extraction_date": str(Path(pdf_path).stat().st_mtime)
        },
        "entries": []
    }
    
    print("📊 Analyzing TOC structure...")
    print("="*70)
    
    for level, title, page in toc:
        entry = {
            "level": level,
            "title": title.strip(),
            "page": page
        }
        structure["entries"].append(entry)
        
        # Print with indentation based on level
        indent = "  " * (level - 1)
        level_icon = "📚" if level == 1 else "📄" if level == 2 else "📍"
        print(f"{indent}{level_icon} Lvl {level}: {title[:60]:<60} (page {page})")
    
    print("="*70 + "\n")
    
    # Save extracted TOC
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"✅ TOC saved to: {output_file}")
    
    doc.close()
    return structure


def analyze_toc_patterns(toc_file: str = "../data/extracted_toc.json"):
    """
    Analyze TOC to identify Parts, Chapters, and Sections
    This helps us understand the hierarchy pattern
    """
    
    print("\n" + "="*70)
    print("🔍 ANALYZING TOC PATTERNS")
    print("="*70 + "\n")
    
    with open(toc_file, 'r') as f:
        data = json.load(f)
    
    # Count by level
    levels = {}
    for entry in data["entries"]:
        level = entry["level"]
        levels[level] = levels.get(level, 0) + 1
    
    print("📊 Level Distribution:")
    for level, count in sorted(levels.items()):
        print(f"   Level {level}: {count} entries")
    
    print("\n🔍 Pattern Detection:\n")
    
    # Look for "Part" indicators
    parts = [e for e in data["entries"] if re.search(r'\bPart\s+\d+', e["title"], re.I)]
    print(f"   📚 Found {len(parts)} 'Part' entries:")
    for p in parts[:5]:  # Show first 5
        print(f"      - {p['title']} (page {p['page']})")
    if len(parts) > 5:
        print(f"      ... and {len(parts) - 5} more")
    
    # Look for "Chapter" indicators  
    chapters = [e for e in data["entries"] if re.search(r'\bChapter\s+\d+', e["title"], re.I) or re.search(r'^\d+\s+[A-Z]', e["title"])]
    print(f"\n   📄 Found {len(chapters)} 'Chapter' entries:")
    for c in chapters[:5]:
        print(f"      - {c['title'][:60]} (page {c['page']})")
    if len(chapters) > 5:
        print(f"      ... and {len(chapters) - 5} more")
    
    # Analyze level patterns
    print(f"\n📈 Hierarchy Analysis:")
    
    level_samples = {}
    for entry in data["entries"]:
        level = entry["level"]
        if level not in level_samples:
            level_samples[level] = []
        if len(level_samples[level]) < 3:
            level_samples[level].append(entry["title"])
    
    for level in sorted(level_samples.keys()):
        print(f"\n   Level {level} examples:")
        for title in level_samples[level]:
            print(f"      - {title[:70]}")
    
    # Summary
    print("\n" + "="*70)
    print("📝 RECOMMENDATIONS:")
    print("="*70)
    
    if len(parts) > 0:
        print(f"\n✅ Harrison's has {len(parts)} major Parts")
        print(f"   Likely Level 1 entries represent Parts")
    
    if len(chapters) > 0:
        print(f"\n✅ Harrison's has ~{len(chapters)} Chapters")
        print(f"   Likely Level 2 entries represent Chapters")
    
    print(f"\n✅ Level 3+ entries likely represent:")
    print(f"   - Section headings within chapters")
    print(f"   - Topics and subtopics")
    
    print("\n💡 Next Steps:")
    print("   1. Review the extracted_toc.json file")
    print("   2. Verify the hierarchy structure")
    print("   3. Create hierarchy_template.json with proper structure")
    print("="*70 + "\n")
    
    return data


def create_hierarchy_template(toc_data: dict, output_file: str = "../data/hierarchy_template.json"):
    """
    Create a hierarchy template from extracted TOC
    This creates a structured JSON that we'll manually refine
    """
    
    print("\n🏗️  Creating hierarchy template...")
    
    hierarchy = {
        "metadata": {
            "title": "Harrison's Principles of Internal Medicine",
            "edition": "21st",
            "year": 2022,
            "total_pages": toc_data["metadata"]["total_pages"],
            "note": "This is a template. Please review and adjust as needed."
        },
        "parts": []
    }
    
    current_part = None
    current_chapter = None
    
    for entry in toc_data["entries"]:
        level = entry["level"]
        title = entry["title"]
        page = entry["page"]
        
        # Level 1: Parts
        if level == 1:
            # Try to extract part number
            part_match = re.search(r'Part\s+(\d+)', title, re.I)
            part_num = int(part_match.group(1)) if part_match else len(hierarchy["parts"]) + 1
            
            current_part = {
                "part_number": part_num,
                "part_name": title,
                "start_page": page,
                "end_page": 0,  # Will be updated
                "chapters": []
            }
            hierarchy["parts"].append(current_part)
            current_chapter = None
        
        # Level 2: Chapters
        elif level == 2 and current_part:
            # Try to extract chapter number
            chapter_match = re.search(r'(?:Chapter\s+)?(\d+)', title, re.I)
            chapter_num = int(chapter_match.group(1)) if chapter_match else len(current_part["chapters"]) + 1
            
            current_chapter = {
                "chapter_number": chapter_num,
                "chapter_name": title,
                "start_page": page,
                "end_page": 0,  # Will be updated
                "topics": []
            }
            current_part["chapters"].append(current_chapter)
        
        # Level 3+: Topics/Sections
        elif level >= 3 and current_chapter:
            topic = {
                "topic_name": title,
                "start_page": page,
                "end_page": 0  # Will be updated
            }
            current_chapter["topics"].append(topic)
    
    # Update end pages (each section ends where next begins - 1)
    for i, part in enumerate(hierarchy["parts"]):
        # Part end page
        if i < len(hierarchy["parts"]) - 1:
            part["end_page"] = hierarchy["parts"][i + 1]["start_page"] - 1
        else:
            part["end_page"] = toc_data["metadata"]["total_pages"]
        
        # Chapter end pages
        for j, chapter in enumerate(part["chapters"]):
            if j < len(part["chapters"]) - 1:
                chapter["end_page"] = part["chapters"][j + 1]["start_page"] - 1
            else:
                chapter["end_page"] = part["end_page"]
            
            # Topic end pages
            for k, topic in enumerate(chapter["topics"]):
                if k < len(chapter["topics"]) - 1:
                    topic["end_page"] = chapter["topics"][k + 1]["start_page"] - 1
                else:
                    topic["end_page"] = chapter["end_page"]
    
    # Save template
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    
    # Print summary
    total_chapters = sum(len(p["chapters"]) for p in hierarchy["parts"])
    total_topics = sum(len(c["topics"]) for p in hierarchy["parts"] for c in p["chapters"])
    
    print(f"\n✅ Hierarchy template created!")
    print(f"   Parts: {len(hierarchy['parts'])}")
    print(f"   Chapters: {total_chapters}")
    print(f"   Topics: {total_topics}")
    print(f"   Saved to: {output_path}")
    
    return hierarchy


def main():
    """Main execution function"""
    
    print("\n" + "="*70)
    print("🏥 HARRISON'S MEDICAL TEXTBOOK - TOC EXTRACTION")
    print("="*70 + "\n")
    
    # Path to PDF (using the compressed version)
    pdf_path = "../Harrison's Principles of Internal Medicine 2022, 21st Edition - Screen.pdf"
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        print(f"   Please ensure the PDF is in the correct location.")
        return
    
    # Step 1: Extract TOC from PDF
    print("STEP 1: Extracting Table of Contents\n")
    toc_data = extract_toc_from_pdf(pdf_path)
    
    if toc_data:
        # Step 2: Analyze patterns
        print("\nSTEP 2: Analyzing TOC Structure\n")
        analyze_toc_patterns()
        
        # Step 3: Create hierarchy template
        print("\nSTEP 3: Creating Hierarchy Template\n")
        create_hierarchy_template(toc_data)
        
        print("\n" + "="*70)
        print("✅ TOC EXTRACTION COMPLETE!")
        print("="*70)
        print("\n📋 Next steps:")
        print("   1. Review data/extracted_toc.json")
        print("   2. Review data/hierarchy_template.json")
        print("   3. Manually verify and adjust the hierarchy if needed")
        print("   4. This will be used for PDF processing in the next phase")
        print("\n")
    else:
        print("\n❌ Could not extract TOC from PDF")
        print("   Manual hierarchy creation will be required")
        print("   Please examine the PDF and create hierarchy_template.json manually")


if __name__ == "__main__":
    main()

