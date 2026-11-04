"""Evaluate real answers against dataset-derived expectations; no model required.

Run with ``python -m src.evaluation.evaluate``. To evaluate connected retrieval,
call ``run_evaluation(pipeline)`` with a configured RAGPipeline instead.
"""

import argparse
import csv
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
CSV = "G3_sales_ground_truth.csv"
PDF = "G3_business_report.pdf"
VIDEO = "G3_video_transcript.json"


def build_cases(data_dir=RAW):
    """Build 15 oracles independently of production DataAnalyzer calculations."""
    import fitz
    data_dir = Path(data_dir)
    with (data_dir / CSV).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    sales = {r['month']: r for r in rows}
    segments = json.loads((data_dir / VIDEO).read_text(encoding="utf-8"))
    with fitz.open(data_dir / PDF) as doc:
        pages = [p.get_text() for p in doc]
    cases = []

    def add(category, question, expected, patterns, evidence, numbers=()):
        cases.append(dict(id=f"Q{len(cases)+1:02}", category=category, question=question,
                          expected_answer=expected, patterns=patterns, evidence=evidence,
                          numbers=[str(n) for n in numbers]))

    def csv_source(month):
        return dict(file=CSV, row=next(i+2 for i, r in enumerate(rows) if r['month'] == month))

    def transcript_source(index):
        s = segments[index]
        return dict(file=VIDEO, start_sec=s['start_sec'], end_sec=s['end_sec'], quote=s['text'])

    def margin(month):
        r = sales[month]
        return (Decimal(r['profit_lakh_inr']) / Decimal(r['revenue_lakh_inr']) * 100).quantize(Decimal('0.01'))

    for month, full in [('Jun', 'June'), ('May', 'May'), ('Mar', 'March')]:
        r = sales[month]
        revenue, profit = r['revenue_lakh_inr'], r['profit_lakh_inr']
        add('numerical', f'What were the revenue and profit in {full}?',
            f'{month}: revenue {revenue} lakh INR; profit {profit} lakh INR.',
            [month, 'revenue', 'profit', 'lakh'], [csv_source(month)], [revenue, profit])
    for month, full in [('May', 'May'), ('Jun', 'June')]:
        add('numerical', f'What was the profit margin in {full}?', f'{month}: {margin(month)}%.',
            [month, '%'], [csv_source(month)], [margin(month)])
    delta = margin('Jun') - margin('May')
    add('numerical', 'Did profit margin improve in June compared with May?',
        f'Yes: {margin("May")}% to {margin("Jun")}%, +{delta} percentage points.',
        ['improved', 'percentage points'], [csv_source('May'), csv_source('Jun')],
        [margin('May'), margin('Jun'), delta])
    chart = dict(file='G3_revenue_chart.png', chart='revenue')
    add('chart-only', 'Which month had the highest revenue?',
        'June, 180 lakh INR. Cite revenue chart; verify with CSV.',
        [r'\bjun(?:e)?\b', 'lakh'], [chart, csv_source('Jun')], [180])
    add('chart-only', 'Did the revenue chart rise steadily every month?',
        'No. Feb to Mar declined 130 to 125; Apr to May declined 150 to 145 lakh INR.',
        [r'\bno\b|not', 'mar', 'may', 'declin|decreas|fell'],
        [chart, csv_source('Mar'), csv_source('May')], [130, 125, 150, 145])
    add('chart-only', 'What does the profit chart show for June?', 'June profit: 29 lakh INR.',
        [r'\bjun(?:e)?\b', 'profit', 'lakh'],
        [dict(file='G3_profit_chart.png', chart='profit'), csv_source('Jun')], [29])
    add('transcript-only', 'When did distribution expand and by how many districts?',
        'April; two additional districts. Transcript 00:10-00:35.',
        ['april', r'two|2', 'district'], [transcript_source(0)])
    add('transcript-only', 'When did the promotion start? Include the video timestamp.',
        'Late May. Transcript 00:36-00:58.', ['late may'], [transcript_source(1)])
    page = next(i+1 for i, text in enumerate(pages) if 'promotion' in text.lower())
    pdf = dict(file=PDF, page=page, quote=pages[page-1].strip())
    add('PDF-only', 'What does the business report say about the promotion and June?',
        'A late-May promotion preceded stronger June revenue; causality is not established.',
        ['promotion', 'june', 'may'], [pdf])
    add('cross-modal', 'What happened after the late-May promotion?',
        'Revenue rose from May 145 to June 180 lakh INR (+35; 24.14%). This does not prove causality.',
        ['june', 'promotion', r'not.*(?:caus|prove)|cannot.*(?:caus|prove)|association|correlation'],
        [pdf, transcript_source(1), csv_source('Jun')], [145, 180])
    add('missing-evidence', 'What was the verified customer acquisition cost?',
        'Verified CAC is unavailable. Transcript 01:24-01:48.',
        [r'unavailable|not (?:have|available|verified|provided)|no verified|insufficient'], [transcript_source(3)])
    add('missing-evidence', 'Does the campaign prove efficient ROI?',
        'Cannot determine campaign efficiency or ROI without marketing costs. Transcript 00:59-01:23.',
        [r'cannot|insufficient|not.*(?:establish|determin|prov)|need', 'cost'], [transcript_source(2)])
    return cases


def citation_matches(actual, expected):
    name = next((actual[k] for k in ('source', 'source_filename', 'source_name') if actual.get(k)), '')
    if Path(str(name)).name != expected['file']:
        return False
    for key, aliases in [('row', ('row', 'row_number')), ('page', ('page', 'page_number')),
                         ('start_sec', ('start_sec',)), ('end_sec', ('end_sec',))]:
        if key in expected and not any(actual.get(alias) == expected[key] for alias in aliases):
            return False
    return True


def grade(case, response):
    """Conservative automated rubric; semantic model outputs need human review.

    Required numbers allow 0.01 absolute error; units are required patterns.
    Additional invented numbers are not detected by this lightweight rubric.
    """
    answer = str(response.get('answer', ''))
    content = all(re.search(p, answer, re.I) is not None for p in case['patterns'])
    observed = [Decimal(n.replace(',', '')) for n in re.findall(r'(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?(?![\w.])', answer)]
    numeric = all(any(abs(Decimal(n)-v) <= Decimal('0.01') for v in observed) for n in case['numbers'])
    missing = [json.dumps({k:v for k,v in e.items() if k != 'quote'}, sort_keys=True)
               for e in case['evidence'] if not any(citation_matches(s, e) for s in response.get('sources', []))]
    return dict(content_ok=content, numerical_ok=numeric if case['numbers'] else 'N/A',
                citation_ok=not missing, missing_information='; '.join(missing),
                status='PASS' if content and numeric and not missing else 'FAIL')


def run_evaluation(pipeline=None, data_dir=RAW):
    """Keep genuine responses and errors; never substitute oracle responses."""
    if pipeline is None:
        from src.retrieval.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
    results = []
    for case in build_cases(data_dir):
        error = ''
        try:
            response = pipeline.ask(case['question'])
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            response = dict(answer='', sources=[])
        results.append(dict(id=case['id'], category=case['category'], question=case['question'],
                            expected_answer=case['expected_answer'], actual_answer=response.get('answer', ''),
                            expected_evidence=json.dumps(case['evidence'], ensure_ascii=False),
                            actual_sources=json.dumps(response.get('sources', []), ensure_ascii=False),
                            **grade(case, response), error=error))
    return results


def write_artifacts(results, output_dir, data_dir=RAW):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'evaluation_results.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    manifest = dict(evaluated_at_utc=datetime.now(timezone.utc).isoformat(), questions=len(results),
                    strict_passes=sum(r['status'] == 'PASS' for r in results),
                    sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(data_dir).glob('G3_*'))})
    (output / 'evaluation_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    cards = []
    for r in results:
        fields = ''.join(f'<h3>{html.escape(k)}</h3><pre>{html.escape(str(v))}</pre>' for k,v in r.items() if k != 'expected_evidence')
        cards.append(f'<article id="{r["id"]}">{fields}</article>')
    document = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>Evaluation evidence</title>'
                '<style>body{font:18px Arial;margin:30px;background:#eef2f8;color:#17263c}article{background:white;padding:25px;margin:20px 0}h3{font-size:16px;margin-bottom:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px Consolas}</style>'
                '<h1>InsightLens: real evaluation outputs</h1><p>Recorded pipeline evidence; this is not the Streamlit UI.</p>'
                '<script>addEventListener("DOMContentLoaded",()=>{if(location.hash)document.querySelectorAll("article").forEach(e=>e.hidden=e.id!==location.hash.slice(1))})</script>'
                + ''.join(cards) + '</html>')
    (output / 'evaluation_evidence.html').write_text(document, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'docs/evaluation')
    args = parser.parse_args()
    results = run_evaluation()
    write_artifacts(results, args.output_dir)
    print(f"{len(results)} questions; {sum(r['content_ok'] for r in results)} content matches; "
          f"{sum(r['citation_ok'] for r in results)} complete citations; "
          f"{sum(r['status'] == 'PASS' for r in results)} strict passes")


if __name__ == '__main__':
    main()
