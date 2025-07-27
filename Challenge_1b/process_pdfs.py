import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any

from src.document_analyzer import DocumentAnalyzer
from src.persona_processor import PersonaProcessor
from src.section_ranker import SectionRanker
from utils.parser import extract_text_from_pdf


def colored_terminal_text(text, color_code):
    """Return colored text for terminal output."""
    return f"\033[{color_code}m{text}\033[0m"


def load_json_config(config_path):
    """Load JSON configuration from a file."""
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_pdf_file_path(collection_dir, pdf_filename):
    """Construct the full path to a PDF file."""
    return os.path.join(collection_dir, "PDFs", pdf_filename)


def create_output_structure(config):
    """Create the output structure with challenge info and metadata."""
    return {
        "challenge_info": config.get("challenge_info", {}),
        "metadata": {
            "processing_timestamp": int(time.time()),
            "persona_type": config["persona"]["role"].lower().replace(" ", "_"),
            "job_context": config["job_to_be_done"]["task"],
            "total_documents_processed": len(config["documents"]),
            "total_sections_analyzed": 0,
            "top_sections_selected": 0,
            "input_documents": []
        },
        "extracted_sections": [],
        "subsection_analysis": {
            "persona_insights": {},
            "content_distribution": {},
            "top_sections_summary": []
        }
    }


def process_document_collection(config, collection_dir):
    """Process all documents in a collection using advanced persona-driven analysis."""
    print(colored_terminal_text(f"\nProcessing Collection: {collection_dir}", "34"))
    
    # Initialize analysis components
    document_analyzer = DocumentAnalyzer()
    persona_processor = PersonaProcessor()
    section_ranker = SectionRanker()
    
    # Create output structure
    output_data = create_output_structure(config)
    all_sections = []
    
    # Process each document
    for doc_config in config["documents"]:
        pdf_filename = doc_config["filename"]
        pdf_path = get_pdf_file_path(collection_dir, pdf_filename)
        
        if not os.path.exists(pdf_path):
            print(colored_terminal_text(f"File not found: {pdf_path}", "33"))
            continue
            
        print(colored_terminal_text(f"  Analyzing: {pdf_filename}", "36"))
        
        # Analyze document structure
        doc_analysis = document_analyzer.analyze_document(pdf_path)
        
        if doc_analysis.get("sections"):
            # Apply persona-driven processing
            persona_results = persona_processor.process_with_persona(
                doc_analysis, 
                config["persona"], 
                config["job_to_be_done"]
            )
            
            # Rank sections by relevance
            ranked_sections = section_ranker.rank_sections(
                persona_results.get("sections", []),
                config["persona"],
                config["job_to_be_done"]
            )
            
            # Add document sections to collection
            for section in ranked_sections:
                section["document_filename"] = pdf_filename
                all_sections.append(section)
            
            output_data["metadata"]["input_documents"].append(pdf_filename)
            output_data["metadata"]["total_sections_analyzed"] += len(ranked_sections)
    
    # Select top sections across all documents
    all_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    top_sections = all_sections[:15]  # Select top 15 most relevant sections
    
    # Build final output
    for section in top_sections:
        output_data["extracted_sections"].append({
            "document_filename": section["document_filename"],
            "section_title": section.get("title", "Untitled Section"),
            "content": section.get("content", "")[:500] + "..." if len(section.get("content", "")) > 500 else section.get("content", ""),
            "page_number": section.get("page_number", 1),
            "relevance_score": round(section.get("relevance_score", 0), 4)
        })
    
    # Add subsection analysis
    output_data["subsection_analysis"]["persona_insights"] = {
        "identified_persona": config["persona"]["role"],
        "alignment_quality": "high" if any(s.get("relevance_score", 0) > 0.7 for s in top_sections) else "medium",
        "persona_context": config["persona"]["role"],
        "task_context": config["job_to_be_done"]["task"]
    }
    
    # Content distribution analysis
    high_relevance = len([s for s in top_sections if s.get("relevance_score", 0) > 0.7])
    medium_relevance = len([s for s in top_sections if 0.4 <= s.get("relevance_score", 0) <= 0.7])
    low_relevance = len([s for s in top_sections if s.get("relevance_score", 0) < 0.4])
    
    output_data["subsection_analysis"]["content_distribution"] = {
        "high_relevance_sections": high_relevance,
        "medium_relevance_sections": medium_relevance,
        "low_relevance_sections": low_relevance
    }
    
    # Top sections summary
    output_data["subsection_analysis"]["top_sections_summary"] = [
        {
            "document": section["document_filename"],
            "title": section.get("title", "Untitled Section"),
            "score": round(section.get("relevance_score", 0), 4)
        }
        for section in top_sections[:5]  # Top 5 sections
    ]
    
    output_data["metadata"]["top_sections_selected"] = len(top_sections)
    
    return output_data


def save_output(output_data, collection_dir):
    """Save the processed output to JSON file."""
    output_path = os.path.join(collection_dir, "challenge1b_output.json")
    
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=2, ensure_ascii=False)
    
    print(colored_terminal_text(f"Output saved to: {output_path}", "32"))
    return output_path


def process_all_collections(collection_names):
    """Process all collections with persona-driven analysis."""
    total_start_time = time.time()
    
    for collection_name in collection_names:
        input_json_path = os.path.join(collection_name, "challenge1b_input.json")
        
        if not os.path.exists(input_json_path):
            print(colored_terminal_text(f"Skipping {collection_name}: No input JSON found", "33"))
            continue
        
        try:
            # Load configuration
            config = load_json_config(input_json_path)
            
            # Process collection
            output_data = process_document_collection(config, collection_name)
            
            # Save results
            save_output(output_data, collection_name)
            
            # Print summary
            print(colored_terminal_text(f"Summary for {collection_name}:", "35"))
            print(f"   • Documents processed: {output_data['metadata']['total_documents_processed']}")
            print(f"   • Sections analyzed: {output_data['metadata']['total_sections_analyzed']}")
            print(f"   • Top sections selected: {output_data['metadata']['top_sections_selected']}")
            print(f"   • Persona: {config['persona']['role']}")
            print(f"   • Job context: {config['job_to_be_done']['task'][:60]}...")
            
        except Exception as e:
            print(colored_terminal_text(f"Error processing {collection_name}: {str(e)}", "31"))
    
    total_time = time.time() - total_start_time
    print(colored_terminal_text(f"\nProcessing completed in {total_time:.2f} seconds", "32"))


def main():
    """Main execution function."""
    print(colored_terminal_text("Starting Persona-Driven Document Intelligence Processing", "34"))
    print(colored_terminal_text("=" * 60, "34"))
    
    collections = ["Collection 1", "Collection 2", "Collection 3"]
    process_all_collections(collections)
    
    print(colored_terminal_text("\nAll collections processed successfully!", "32"))


if __name__ == "__main__":
    main()