# InsightLens

InsightLens answers questions about business reports. It uses exact CSV
calculations for supported sales questions and retrieval-augmented generation
(RAG) for questions that need report text.

## How question answering works

- **Sales calculations:** `RAGPipeline` recognizes supported revenue and profit
  questions and uses `DataAnalyzer` to read the sales CSV. These results do not
  depend on a language model.
- **Report questions:** The `Retriever` converts the question to an embedding,
  a numeric representation of its meaning, and uses that vector to search a
  prepared ChromaDB collection. It returns matching text and metadata.
- **Generated answers:** `LLMService` places the retrieved text, source
  metadata, and question into a prompt for OpenAI. The returned answer includes
  the metadata of the documents used as sources.

The retrieval path requires both a configured ChromaDB collection and a
`OPENAI_API_KEY`. Numerical questions can be handled without either service.

## Setup and tests

Install the project dependencies and run the test suite:

```bash
pip install -r requirements.txt
pytest -v tests/
```

Set `OPENAI_API_KEY` in your environment or a local `.env` file before creating
`LLMService`. Do not commit credentials.

Copy `.env.example` to `.env` and fill in your own OpenAI API key:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`. Answer generation
uses the OpenAI Responses API; embeddings remain local Sentence Transformers.
See the [official OpenAI quickstart](https://developers.openai.com/api/docs/quickstart).
Run `python -m pytest -q test_llm.py` to test the provider integration offline.

## Run the app

```bash
python -m streamlit run app.py
```

Use Python 3.11 or later. All supplied business data is synthetic. The current
app constructs `RAGPipeline()` without retrieval services: numerical questions
work, while document questions display a retrieval-not-connected message.
Setting an API key alone does not connect a vector collection or initialize
the retriever in the app.

## Evaluation and presentation

- [Architecture diagram (PNG)](docs/architecture.png)
- [Architecture details and editable diagram](docs/architecture.md)

Run the reproducible 15-question baseline without API access:

```bash
python -m src.evaluation.evaluate
python -m pytest -q tests/test_evaluation.py
```

For an evaluation-only installation, the required packages are:

```bash
python -m pip install pytest pandas pymupdf python-dotenv openai
```

The evaluator checks original CSV figures, chart evidence, PDF page references,
transcript timestamps, missing information, and numerical accuracy. It records
actual pipeline errors rather than replacing them with expected answers.

- [Evaluation report and final presentation content](docs/evaluation_report.md)
- [Expected versus actual answers CSV](docs/evaluation/evaluation_results.csv)
- [Browsable evaluation evidence](docs/evaluation/evaluation_evidence.html)
- [Dataset fingerprints and run timestamp](docs/evaluation/evaluation_manifest.json)
- [Three saved live-app screenshots](docs/evaluation/screenshots/)

Current baseline: **8/15 content matches, 0/15 complete citations, 7 service
errors**. Correct numerical answers still lack CSV row locations, and chart
questions lack chart citations. The report includes the failures, owner handoff,
test results, and a 3–5 minute presentation script. Three saved screenshots show the Streamlit UI; two failure/edge-case
screenshots are still pending. The report links the saved images and records
the missing evidence. Six existing transcript-validation
tests fail; see the report before claiming full-suite success.
