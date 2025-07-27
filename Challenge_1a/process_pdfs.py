import os
import json
import fitz  # PyMuPDF

INPUT_DIR = './input'
OUTPUT_DIR = './output'

HEADING_LEVELS = [
    (16, 'H1'),
    (14, 'H2'),
    (12, 'H3'),
]

def is_bold(span):
    return "bold" in span["font"].lower()

def is_all_caps(text):
    return text.isupper() and len(text) > 1

def is_centered(span, page_width, tolerance=0.15):
    x0, _, x1, _ = span["bbox"]
    text_center = (x0 + x1) / 2
    page_center = page_width / 2
    return abs(text_center - page_center) < (page_width * tolerance)

def get_title_from_page(page):
    blocks = page.get_text('dict')['blocks']
    max_size = 0
    title = ''
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    if span['size'] > max_size and span['text']:
                        max_size = span['size']
                        title = span['text']
    return title if title else ''

def extract_headings(doc):
    outline = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_width = page.rect.width
        blocks = page.get_text('dict')['blocks']
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if not text:
                            continue
                        
                        size = span['size']
                        bold = is_bold(span)
                        all_caps = is_all_caps(text)
                        centered = is_centered(span, page_width)
                        
                        # Enhanced scoring system
                        score = size
                        if bold:
                            score += 2.0  # Increased weight for bold
                        if all_caps:
                            score += 1.5  # Increased weight for all caps
                        if centered:
                            score += 1.0
                        
                        # Additional heuristics
                        if len(text) < 100 and (text.endswith(':') or text.isupper()):
                            score += 1.0
                        
                        # Check if text looks like a heading (short, meaningful)
                        if 3 <= len(text) <= 50 and not text.isdigit():
                            score += 0.5
                        
                        # Determine heading level based on enhanced scoring
                        if score >= 16:
                            level = "H1"
                        elif score >= 14:
                            level = "H2"
                        elif score >= 12:
                            level = "H3"
                        else:
                            continue
                        
                        # Avoid duplicate entries
                        if not any(item['text'] == text and item['page'] == page_num + 1 for item in outline):
                            outline.append({
                                "level": level,
                                "text": text,
                                "page": page_num + 1  # Convert to 1-based indexing
                            })
    return outline

def process_pdf(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        if len(doc) > 50:
            print(f"Skipping {pdf_path}: more than 50 pages.")
            return
        
        title = get_title_from_page(doc[0])
        outline = extract_headings(doc)
        
        result = {
            'title': title,
            'outline': outline
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        doc.close()
        print(f"Successfully processed: {pdf_path}")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        # Create a minimal output file to avoid breaking the pipeline
        result = {
            'title': '',
            'outline': []
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_filename = os.path.splitext(filename)[0] + '.json'
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            process_pdf(pdf_path, output_path)

if __name__ == '__main__':
    main() 