# InsightLens – Multimodal RAG Assistant

InsightLens is a multimodal Retrieval-Augmented Generation (RAG) assistant that answers questions using business reports, charts, CSV data and timestamped video transcripts.

It combines exact numerical calculations, semantic retrieval and LLM-based answer generation to provide grounded answers with supporting source references.

## Features

- **PDF retrieval:** Retrieve information from business reports.
- **Chart retrieval:** Use structured chart captions and chart metadata.
- **CSV analysis:** Calculate monthly revenue, profit and profit margins using verified CSV values.
- **Transcript retrieval:** Retrieve timestamped video transcript segments.
- **Cross-modal question answering:** Combine evidence from different source types.
- **Source citations:** Display supporting files and available page, row or timestamp references.
- **Missing-information handling:** Avoid inventing answers when the supplied data does not contain the requested information.

## How It Works

### 1. Data Ingestion

The ingestion pipeline processes the supplied PDF, chart images, CSV and video transcript. It extracts information, prepares structured records and metadata, generates embeddings and stores indexed records in ChromaDB.

### 2. Embeddings and Retrieval

The project uses the Sentence Transformers `all-MiniLM-L6-v2` model to generate embeddings locally.

The retriever searches the ChromaDB collection using semantic similarity. Metadata-based retrieval is also used to locate specific source records.

### 3. Numerical Analysis

`DataAnalyzer` reads the original sales CSV and performs supported numerical calculations, including revenue, profit and profit-margin comparisons.

These supported calculations use the verified CSV values rather than relying on an LLM to perform arithmetic.

### 4. Answer Generation

`LLMService` uses the OpenAI Responses API to generate answers from retrieved evidence.

The pipeline combines the question, retrieved context and source metadata to produce grounded responses with supporting references.

### 5. User Interface

A Streamlit application provides the interface for asking questions and viewing answers and their supporting sources.

## Technology Stack

- Python 3.11+
- Streamlit
- ChromaDB
- Sentence Transformers
- OpenAI Responses API
- Pandas
- PyMuPDF
- Python-dotenv
- Pytest

## Project Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd insightlens
```

Create and activate a virtual environment:

```bash
python -m venv my_venv
source my_venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`.

The project uses local Sentence Transformers for embeddings and OpenAI for answer generation. Do not commit API keys or your `.env` file.

## Run the Application

First, process the input data and create the vector database:

```bash
python -m src.ingestion.ingest_all
```

Then start the Streamlit application:

```bash
streamlit run app.py
```

Open the application:

```text
http://localhost:8501
```

## Evaluation and Testing

Run the evaluation:

```bash
python -m src.evaluation.evaluate
```

Run the automated test suite:

```bash
python -m pytest -v tests/
```

### Latest Verified Results

- Evaluation: **15/15 strict passes**
- Content matches: **15/15**
- Complete citations: **15/15**
- Automated tests: **51 passed, 1 warning**

These results refer to the reported evaluation and test runs. They demonstrate performance on the defined test cases, not guaranteed accuracy for every possible question.

## Sample Questions

- Which month had the highest revenue?
- Did the revenue chart rise steadily every month?
- What does the profit chart show for June?
- Did profit margin improve in June compared with May?
- What happened after the late-May promotion?
- What was the verified customer acquisition cost?
- Which city generated the highest revenue?

## Project Documentation

- Architecture diagram: `docs/architecture.png`
- Evaluation report: `docs/evaluation_report.md`
- Evaluation results: `docs/evaluation/evaluation_results.csv`
- Evaluation evidence: `docs/evaluation/evaluation_evidence.html`
- Evaluation manifest: `docs/evaluation/evaluation_manifest.json`
- Application screenshots: `docs/evaluation/screenshots/`

## Limitations

- The supplied business dataset is synthetic and intended for educational and demonstration purposes.
- City-wise revenue cannot be determined because the CSV does not contain city-level information.
- Verified customer acquisition cost figures are unavailable in the supplied report and transcript.
- The transcript represents timestamped segments; the project does not process an actual video file.
- The system's answers are limited to the information available in the supplied and indexed data.

## Future Improvements

1. Improve citation presentation by displaying precise CSV row references and removing irrelevant duplicate source entries.
2. Extend retrieval and evaluation to larger datasets and more complex multimodal queries.