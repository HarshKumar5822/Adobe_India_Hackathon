# PDF Outline Extractor – Adobe Connecting the Dots Challenge (Round 1A)

## Overview
This project extracts the document title and structured outline (headings H1, H2, H3 with page numbers) from PDF files. It is designed for the Adobe Connecting the Dots Challenge (Round 1A).

## Tech Stack
- Python 3.10
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - Lightweight PDF processing library
- Docker (linux/amd64)

## How It Works

### Input Processing
- **Input:** Place PDF files (max 50 pages each) in `/input` (mounted to `/app/input` in the container).
- **Automatic Processing:** Script processes all PDFs in the input directory automatically.

### Heading Detection Algorithm
Our approach uses a **multi-factor scoring system** rather than relying solely on font size:

1. **Base Score:** Font size (primary factor)
2. **Style Bonuses:**
   - Bold text: +2.0 points
   - All caps text: +1.5 points  
   - Centered text: +1.0 point
3. **Content Heuristics:**
   - Short text (3-50 chars): +0.5 points
   - Ends with colon or is uppercase: +1.0 point
4. **Heading Level Assignment:**
   - Score ≥16 → H1
   - Score ≥14 → H2  
   - Score ≥12 → H3

### Title Extraction
- Extracts the largest text from the first page as the document title.

### Output Format
For each PDF, a JSON file is saved to `/output` (mounted to `/app/output`):

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## How to Build and Run

1. **Build the Docker image:**
   ```sh
   docker build --platform linux/amd64 -t mysolution:xyz123 .
   ```

2. **Run the container:**
   ```sh
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution:xyz123
   ```
   - Place your PDF files in the `input` directory before running.
   - Output JSONs will appear in the `output` directory.

## Technical Features

### Robust Error Handling
- Graceful handling of corrupted or unreadable PDFs
- Continues processing other files if one fails
- Creates empty output files for failed PDFs to maintain pipeline integrity

### Performance Optimizations
- Efficient PDF parsing with PyMuPDF
- Duplicate heading detection and removal
- Memory-efficient processing for large documents

### Compliance with Requirements
- ✅ Works fully offline (no internet required)
- ✅ Runs on CPU (no GPU needed)
- ✅ Processes up to 50 pages per PDF in ≤10 seconds
- ✅ No hardcoded filenames or headings
- ✅ Supports linux/amd64 via Docker
- ✅ Model size < 200MB (PyMuPDF is ~50MB)
- ✅ No network/API calls

## Constraints Met
- **Execution time:** ≤ 10 seconds for a 50-page PDF
- **Model size:** ≤ 200MB (PyMuPDF is lightweight)
- **Network:** No internet access required
- **Runtime:** CPU-only (amd64 compatible)
- **Architecture:** linux/amd64 support 