# InsightLens evaluation report

Evaluated 4 November 2026 on branch `pallavi`. These are synthetic teaching
datasets, not real business records. Scope: evaluation code, tests, evidence,
README, and presentation content. Application and ingestion fixes belong to
their respective owners.

## Reproduce and inspect

From the repository root, use Python 3.11+:

```bash
python -m pip install pytest pandas pymupdf python-dotenv openai
python -m src.evaluation.evaluate
python -m pytest -q tests/test_evaluation.py
```

The CLI evaluates the same `RAGPipeline()` configuration constructed by `app.py`:
no retriever and no LLM. It makes no API calls and does not mock answers.
Every question is attempted, including questions that raise service errors.

- [Full expected versus actual results CSV](evaluation/evaluation_results.csv)
- [HTML evidence with all recorded answers](evaluation/evaluation_evidence.html)
- [Run time and dataset SHA-256 fingerprints](evaluation/evaluation_manifest.json)
- [Evaluation implementation](../src/evaluation/evaluate.py)
- [Evaluation tests](../tests/test_evaluation.py)

For an already initialized, connected pipeline, call
`write_artifacts(run_evaluation(pipeline), output_dir)` from
`src.evaluation.evaluate`. Save to a distinct output directory and document the
model, index configuration, and run time. The committed baseline does not measure
embedding retrieval relevance or OpenAI generation quality.

## Ground-truth verification

Compared the original `RAG_Assignments_3_Groups_Complete_Pack.zip` supplied by the
user with `data/raw/`. Both chart images and the sales CSV match byte for byte.
Transcript JSON structures are identical despite whitespace differences. Extracted
PDF text is identical on its single page despite different PDF file bytes.
Local dataset fingerprints are in the manifest; no source dataset was modified.

Both original charts were visually inspected. Titles are **H1 2026 Revenue** and
**H1 2026 Profit**. X-axis: Month, Jan–Jun. Y-axis: Revenue or Profit, **INR lakh**.
Exact figures below come from CSV, not estimates from image pixels.
CSV row numbers include the header as line 1.

| CSV line | Month | Revenue (lakh INR) | Profit (lakh INR) |
| --- | --- | ---: | ---: |
| 2 | Jan | 120 | 18 |
| 3 | Feb | 130 | 19 |
| 4 | Mar | 125 | 17 |
| 5 | Apr | 150 | 23 |
| 6 | May | 145 | 20 |
| 7 | Jun | 180 | 29 |

Independent Decimal arithmetic in the evaluator verifies May margin as
`20 / 145 * 100 = 13.79%`, June margin as `29 / 180 * 100 = 16.11%`,
and the change as **2.32 percentage points**. June revenue rose by 35 lakh INR,
or `35 / 145 * 100 = 24.14%`, compared with May. One lakh INR is 100,000 INR:
June revenue of 180 lakh equals 18,000,000 INR. Revenue is not steadily rising:
March and May decline relative to the previous month.

PDF page 1 says June revenue grew following a regional campaign launched in late
May. It warns that absolute profit growth does not automatically imply higher
margin and that customer acquisition cost is unavailable.

Transcript evidence, checked against the original JSON:

| Time | Verified content |
| --- | --- |
| 00:10–00:35 | April distribution expansion to two additional districts |
| 00:36–00:58 | Late-May promotion and stronger June revenue |
| 00:59–01:23 | Marketing costs must be examined before declaring efficiency |
| 01:24–01:48 | No verified customer acquisition cost |

This is transcript-first simulated video; no actual video exists. A temporal
association is not proof of campaign causality, ROI, or customer profitability.

## Question set and observed behavior

Full question wording, expected answers, original evidence quotes, actual answers,
actual sources, score dimensions, and errors are recorded in the CSV. The table
below is the human review of that run. Chart-only describes the requested primary
modality; exact numerical chart answers also require CSV cross-checking.

| ID | Coverage | Expected answer | Actual result / defect |
| --- | --- | --- | --- |
| Q01 | Numerical | Jun revenue 180, profit 29 lakh INR | Correct values; CSV filename only |
| Q02 | Numerical | May revenue 145, profit 20 lakh INR | Correct values; CSV filename only |
| Q03 | Numerical | Mar revenue 125, profit 17 lakh INR | Correct values; CSV filename only |
| Q04 | Numerical | May margin 13.79% | Correct; CSV row missing |
| Q05 | Numerical | Jun margin 16.11% | Correct; CSV row missing |
| Q06 | Numerical | Margin improved 13.79% to 16.11%, +2.32 points | Correct; both CSV row references missing |
| Q07 | Revenue chart | June maximum, 180 lakh; chart plus CSV | Correct value; chart and row citations missing |
| Q08 | Revenue chart / misleading trend | No; March and May declines | Service error; no answer |
| Q09 | Profit chart | June profit 29 lakh; chart plus CSV | Correct value, extra revenue figure; chart and row missing |
| Q10 | Transcript | April; two additional districts; 00:10–00:35 | Service error; no answer |
| Q11 | Transcript / timestamp | Late May; 00:36–00:58 | Service error; no answer |
| Q12 | PDF | Late-May campaign followed by June growth; page 1 | Service error; no answer |
| Q13 | Cross-modal | 145 to 180 lakh after promotion; no causal proof | Service error; no answer |
| Q14 | Missing evidence | CAC unavailable; 01:24–01:48 | Service error rather than grounded abstention |
| Q15 | Missing evidence / ROI | Insufficient marketing costs; 00:59–01:23 | Service error rather than grounded abstention |

## Results and scoring

| Measure | Result |
| --- | ---: |
| Content rubric matches | 8 / 15 (53.33%) |
| Numerical checks among numeric cases, including unanswerable attempts | 8 / 10 (80%) |
| Numerical checks among returned numeric answers | 8 / 8 (100%) |
| Complete source citations with required locations | 0 / 15 |
| Strict passes (content, numerical where applicable, all evidence) | 0 / 15 |
| Runtime service errors | 7 / 15 |

No incorrect figure was found in the eight returned answers. This does not imply
end-to-end assignment acceptance: missing citations and unanswered questions are
failures. The seven runtime errors all say that Retriever and LLM services are
required for non-numerical questions. The UI catches this error and tells the user
that document retrieval is not connected; this run records the underlying pipeline
error, not an invented answer or a fabricated UI interaction.

The automated rubric checks required content phrases, expected numbers with
absolute tolerance 0.01, units through required phrases, exact source filenames,
CSV rows, PDF pages, and transcript start/end seconds. For chart citations, the
unique image filename identifies the chart. Human inspection above confirmed
all eight returned numerical answers and source omissions. Phrase checks are not
a semantic judge: they can miss contradictory text, additional invented figures,
or number-to-month misassociation. Connected-model results need manual review,
especially for causal claims. A result with no numerical expectation is `N/A`,
not a numerical success. Filename-only citations intentionally do not pass the
location requirement.

## Error analysis and handoff

| Defect | Evidence | Recommended owner action |
| --- | --- | --- |
| Missing CSV locations | Q01–Q07, Q09 return only a source filename | Numerical pipeline owner: attach row numbers and both comparison rows |
| Chart citations omitted | Q07 and Q09 route directly to CSV | Pipeline owner: preserve requested chart evidence and CSV verification |
| Retrieval not connected | Q08, Q10–Q15 raise ValueError | Retrieval/UI owners: initialize index, retriever, and configured answer service |
| Missing grounded abstention | Q14–Q15 error before evidence is inspected | Retrieval owner: use limitation evidence to decline CAC/ROI claims explicitly |
| Transcript validation failures | Six existing transcript tests fail | Ingestion owner: reject absent, reversed, negative, zero-length, noninteger times and non-list JSON |

Two production improvements: (1) validate typed evidence locations at ingestion
and carry them through routing to the answer; (2) add modality-aware retrieval
and a grounded abstention policy, then evaluate a connected pipeline on this same
question set. Avoid claiming the campaign caused growth or that ROI improved
merely because the margin rose.

## Test evidence

Environment: CPython 3.14.7; pandas 3.1.0; PyMuPDF 2.1; pytest 9.2.0;
google-genai 2.34.0. No model key or network service was used for evaluation.

Provider migration note: the baseline above was recorded before the OpenAI
migration. The current `LLMService` uses the OpenAI Responses API with
`OPENAI_API_KEY` and optional `OPENAI_MODEL` (default `gpt-4.1-mini`). The
historical google-genai version describes the original environment only;
current installation commands use `openai`. Offline provider tests are in
`test_llm.py`; no live OpenAI generation quality is claimed by this baseline.

```bash
python -m pytest -q tests/test_evaluation.py tests/test_data_analyzer.py tests/test_rag_pipeline.py tests/test_chart_processor.py
# 31 passed (one PyMuPDF fitz deprecation warning)

python -m pytest -q tests/test_evaluation.py tests/test_data_analyzer.py tests/test_rag_pipeline.py tests/test_transcript_processor.py tests/test_chart_processor.py
# 32 passed, 6 failed (existing transcript validation failures)
```

The full suite was not run: ChromaDB and embedding dependencies were not installed
in this evaluation environment. Tests passing for the evaluator establish that
the harness records and detects failures; they do not mean the evaluated app
passes. Existing timestamp failures were recorded without changing files owned
by the ingestion team.

The new evaluation test file independently passes all **12 tests**, including
incorrect values/units, absent source rows, fabricated filenames/pages, invalid
timestamps, incomplete cross-modal citations, invented CAC, preserved runtime
errors, CSV export, and HTML escaping.

## Screenshots

Three saved PNGs show actual questions, answers, and source metadata in the
running Streamlit chat. They demonstrate correct arithmetic, while the displayed
CSV citations still omit row locations. Numerical success does not mean a strict
citation pass.

| Evaluation case | Live-app screenshot | What it demonstrates |
| --- | --- | --- |
| Q01 | [June revenue and profit](evaluation/screenshots/q1.png) | Correct revenue of 180 lakh INR and profit of 29 lakh INR; CSV filename shown |
| Q04 | [May profit margin](evaluation/screenshots/q2.png) | Correct margin of 13.79%; CSV filename shown |
| Q06 | [June versus May margin](evaluation/screenshots/q3.png) | Correct increase from 13.79% to 16.11%, or 2.32 percentage points; CSV filename shown |
| Q08 | Pending: failure screenshot not saved in the repository | Steady-growth question displays the retrieval-not-connected message |
| Q14 | Pending: failure screenshot not saved in the repository | CAC question displays the retrieval-not-connected message |

The failure behavior for Q08 and Q14 was shown in chat, but its screenshot has
not been saved under `docs/evaluation/screenshots/`. The assignment's screenshot
set remains incomplete until two failure/edge-case screenshots are saved and
linked here. Capture each question with its full response. Record the actual
retrieval-not-connected message as a failure, rather than presenting it as a
grounded abstention or the expected answer.

The [HTML evidence report](evaluation/evaluation_evidence.html) is a separate
view of recorded pipeline results; it is not the source of these live-app
screenshots. A 3?5 minute screen recording remains a team-level deliverable.

## Final presentation content (3–5 minutes)

1. **Problem and sources (30 seconds).** InsightLens answers questions about a
   synthetic H1 2026 report, two charts, six CSV months, and four transcript
   segments. Exact amounts come from CSV; narrative claims need source locations.
2. **Architecture (40 seconds).** Show [architecture](architecture.md). Explain
   PDF/chart/transcript ingestion → metadata and embeddings → vector retrieval →
   grounded answer, with CSV calculations on the numerical route. Distinguish
   implemented modules from retrieval services currently unconnected in the UI.
3. **Verified arithmetic (50 seconds).** Show Q01, Q04, Q06 screenshots. June
   revenue/profit: 180/29 lakh; May margin 13.79%; June 16.11%; increase 2.32
   percentage points. Call out missing CSV row citations.
4. **Cross-modal expected evidence (40 seconds).** Show PDF page 1 and transcript
   00:36–00:58. The campaign preceded stronger June sales. CSV confirms 145 to
   180 lakh. Explain that Q13 currently fails because retrieval is unconfigured;
   present the evidence trail as the target behavior, not a successful live answer.
5. **Failures and uncertainty (40 seconds).** Explain Q08 and Q14 failures; add their screenshots once saved. Revenue
   falls in March and May, so “steadily rising” is false. CAC is unavailable;
   campaign ROI requires costs. Report six existing timestamp-validation defects.
6. **Results and improvements (30 seconds).** Show 8/15 correct content results,
   0/15 complete citations, 7 service errors. Prioritize source-location metadata
   and connected retrieval with explicit abstention. Re-run the same cases after
   the owners fix those components.

Suggested closing statement: “Our evaluation separates numerical correctness
from evidence quality. The calculations we received are accurate, while complete
citations and connected document answers still need work.”
