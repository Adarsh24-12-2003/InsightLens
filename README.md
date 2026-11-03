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
  metadata, and question into a prompt for Gemini. The returned answer includes
  the metadata of the documents used as sources.

The retrieval path requires both a configured ChromaDB collection and a
`GEMINI_API_KEY`. Numerical questions can be handled without either service.

## Setup and tests

Install the project dependencies and run the test suite:

```bash
pip install -r requirements.txt
pytest -v tests/
```

Set `GEMINI_API_KEY` in your environment or a local `.env` file before creating
`LLMService`. Do not commit credentials.