# InsightLens evaluation report

Evaluated 4 November 2026 on branch `pallavi`. These are synthetic teaching

datasets, not real business records. Scope: evaluation code, tests, evidence,

README, and presentation content. Application and ingestion fixes belong to

their respective owners.

## Current implementation status — 5 November 2026

The application has since been updated beyond the historical evaluation baseline documented below.

The current implementation uses a configured pipeline factory to initialize retrieval services for the Streamlit application. It supports PDF, chart, CSV and timestamped transcript evidence, exact CSV-based numerical calculations, metadata retrieval and OpenAI-based answer generation.

### Latest verification

| Check | Latest result |

|---|---:|

| Evaluation questions | 15 |

| Content matches | 15/15 |

| Complete citations | 15/15 |

| Strict evaluation passes | 15/15 |

| Automated tests | 51 passed, 1 warning |

| Live Streamlit questions manually checked | 6 |

Three additional assignment edge cases were manually verified:

- INR lakh to Indian rupee conversion.

- Correct transcript timestamp for unavailable customer acquisition cost.

- Conflicting revenue trend interpretation checked against verified CSV values.

Five live application screenshots are available in `docs/evaluation/screenshots/`, covering three successful cases and two missing-information cases.

These results describe the latest reported verification. The historical evaluation baseline and its original findings are retained below for transparency.

## Reproduce and inspect

From the repository root, use Python 3.11+:

```bash

python -m pip install pytest pandas pymupdf python-dotenv openai

python -m src.evaluation.evaluate

python -m pytest -q tests/test_evaluation.py

```

The CLI uses the configured pipeline factory to initialize the retrieval pipeline, consistent with the Streamlit application. It evaluates the current implementation using the configured services and records the results, including any errors encountered.

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

## Historical baseline — 4 November 2026

The following question results, scores, defects, and test logs describe the
4 November baseline. They are not the results of the current implementation.

### Question set and observed behavior

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

### Results and scoring

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

### Historical error analysis and handoff

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

### Historical test evidence

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

Five screenshots from the running Streamlit application demonstrate three successful cases and two missing-information cases.

| Case | Live-app screenshot | What it demonstrates |

|---|---|---|

| Highest revenue | [June revenue and profit](evaluation/screenshots/q1.png) | June revenue of 180 lakh INR and profit of 29 lakh INR |

| Profit margin | [May profit margin](evaluation/screenshots/q2.png) | Correct margin calculation of 13.79% |

| Margin comparison | [June versus May margin](evaluation/screenshots/q3.png) | Increase from 13.79% to 16.11%, or 2.32 percentage points |

| Missing evidence | [Customer acquisition cost](evaluation/screenshots/q4.png) | Correctly identifies unavailable verified customer acquisition cost and cites the transcript and report |

| Missing evidence | [City-wise revenue](evaluation/screenshots/q5.png) | Correctly abstains because the supplied data contains no city-level revenue figures |

These screenshots demonstrate the application's answers and displayed source evidence