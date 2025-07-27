# Adobe Connecting the Dots Challenge – Round 1A & 1B

## Project 1A: PDF Outline Extractor

### Overview

This project is designed for Round 1A of the Adobe Connecting the Dots Challenge. Its primary function is to extract the document title and a structured outline from PDF files. The outline includes headings (H1, H2, H3) along with their respective page numbers.

### Tech Stack

* Python 3.10
* PyMuPDF (fitz): Lightweight PDF processing library
* Docker (linux/amd64)

### How It Works

#### Input Processing

* Accepts PDF files, each up to 50 pages.
* PDFs are placed in the `/input` directory on the host machine, mounted to `/app/input` in Docker.
* The script automatically processes all PDFs in this directory.

#### Heading Detection Algorithm

The approach uses a scoring system for heading detection, not solely based on font size.

1. **Base Score**: Font size
2. **Style Bonuses**:

   * Bold text: +2.0
   * All caps text: +1.5
   * Centered text: +1.0
3. **Content Heuristics**:

   * Short text (3–50 characters): +0.5
   * Ends with colon or all caps: +1.0
4. **Heading Levels**:

   * Score ≥16: H1
   * Score ≥14: H2
   * Score ≥12: H3

#### Title Extraction

* Extracts the largest text on the first page as the document title.

### Output Format

* Generates a JSON file for each PDF in `/output`, containing:

  * Document title
  * Outline array: heading level, heading text, page number

### How to Build and Run

1. **Build Docker Image**:

   ```bash
   docker build -t pdf-outline-extractor .
   ```
2. **Run Container**:

   ```bash
   docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-outline-extractor
   ```

### Technical Features

* **Error Handling**: Handles corrupted PDFs and produces empty output files on failure.
* **Performance**:

  * Efficient PyMuPDF parsing
  * Duplicate heading removal
  * Memory-efficient (under 200MB)
* **Compliance**:

  * Offline, CPU-only, <10s per 50-page PDF
  * No hardcoded values or internet calls

---

## Project 1B: Persona-Driven Document Intelligence

### Overview

An advanced PDF analysis engine for extracting persona-relevant content from multiple document collections. Tailors output to roles such as Travel Planner, HR Professional, or Food Contractor.

### Features

* Persona-specific content extraction
* Intelligent section ranking
* Multi-document, multi-collection handling
* Optimized for CPU processing
* Docker-ready deployment

### Collections Processed

#### Collection 1: Travel Planning

* **Persona**: Travel Planner
* **Job**: Plan a 4-day trip for 10 friends to South of France
* **Documents**: 7 guides
* **Focus**: Itinerary, group stays, budget, local spots
* **Keywords**: destination, itinerary, hotel, attraction, etc.

#### Collection 2: Acrobat Learning

* **Persona**: HR Professional
* **Job**: Create and manage onboarding forms
* **Documents**: 15 Acrobat tutorials
* **Focus**: Form creation, automation, compliance
* **Keywords**: form, digital, onboarding, signature, pdf, etc.

#### Collection 3: Recipe Collection

* **Persona**: Food Contractor
* **Job**: Plan vegetarian buffet dinner
* **Documents**: 9 cooking guides
* **Focus**: Veg dishes, buffet service, menu planning
* **Keywords**: recipe, ingredient, vegetarian, menu, catering

### Technical Architecture

#### 1. Persona Analysis Engine

* Classifies personas using keyword dictionaries
* Weights: 60% persona, 40% job-specific

#### 2. PDF Processing Pipeline

* **Text Extraction**: PyMuPDF
* **Section Detection**: Regex-based pattern analysis
* **Content Analysis**: Based on keyword density
* **Output**: JSON with metadata and top 15 relevant sections
* **Error Handling**: Skips failures, logs issues

#### 3. Content Scoring

* Frequency-based scoring with 15x amplification
* Relevance scores capped at 1.0
* Prioritized section output

### Input/Output

* Processes structured JSON inputs
* Outputs JSON with:

  * Metadata (docs, persona, job, timestamp)
  * Extracted sections (title, page, rank)

### Usage

* Can be executed via Python script or Docker container
* Generates outputs in:

  * `Collection 1/challenge1b_output.json`
  * `Collection 2/challenge1b_output.json`
  * `Collection 3/challenge1b_output.json`

### Performance

* 2–5 seconds per collection
* <500MB RAM usage
* No GPU needed
* JSON with top 15 sections per collection

### Highlights

* Persona-contextual intelligence
* Multi-domain adaptability
* CPU-only, scalable architecture
* Validated and schema-compliant outputs

### Quality Assurance

* Strict schema checks
* Recovery mechanisms for failures
* Processing logs
* Output quality validation
* Balanced output variety

---

This repository includes both Project 1A (PDF Outline Extractor) and Project 1B (Persona-Driven Document Intelligence) for Adobe’s Connecting the Dots Challenge.
