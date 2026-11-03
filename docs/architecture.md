# Architecture

The `RAGPipeline` chooses between a direct calculation and a document-based
answer. Direct calculation is used for supported business metrics so that
numeric answers come from the sales CSV rather than generated text.

```text
                              ┌─ supported sales question
User question → RAGPipeline ──┤       → DataAnalyzer → CSV-backed answer
                              └─ report question
                                      → query embedding
                                      → Retriever → ChromaDB matches
                                      → LLMService → Gemini answer
```

## Direct calculations

`DataAnalyzer` reads the monthly sales CSV with pandas. The pipeline uses it
for highest revenue, monthly revenue and profit, and profit-margin questions.
Margin comparisons retain the order in which the user mentions the months and
report the change in percentage points.

## Retrieval-augmented generation

1. `EmbeddingService` converts the question into a vector. Documents stored in
   ChromaDB must be represented with compatible embeddings.
2. `Retriever` asks ChromaDB for the closest vectors and returns each matched
   text with its metadata and distance. Metadata identifies details such as a
   document's source.
3. `LLMService` combines the question and retrieved text in a prompt sent to
   Gemini. The prompt instructs the model to answer only from the provided
   context.
4. `RAGPipeline` returns the answer together with source metadata.

If there are no matches, the pipeline returns a fallback message instead of
asking the language model to answer without supporting context.