"""Check independent oracles, rejection of bad answers, and real exports."""

import csv
import json

import pytest

from src.evaluation.evaluate import build_cases, citation_matches, grade, run_evaluation, write_artifacts


@pytest.fixture
def cases():
    return build_cases()


def test_dataset_oracles_and_coverage(cases):
    assert len(cases) == 15
    assert len({c['id'] for c in cases}) == 15
    assert {c['category'] for c in cases} == {
        'numerical', 'chart-only', 'transcript-only', 'PDF-only', 'cross-modal', 'missing-evidence'
    }
    assert cases[3]['numbers'] == ['13.79']
    assert cases[4]['numbers'] == ['16.11']
    assert cases[5]['numbers'] == ['13.79', '16.11', '2.32']
    assert cases[10]['evidence'][0]['start_sec'] == 36
    assert cases[10]['evidence'][0]['end_sec'] == 58
    assert 'late May' in cases[11]['evidence'][0]['quote']


@pytest.mark.parametrize('answer', [
    'May profit margin was 20%.',  # Absolute profit confused with percentage.
    'May profit margin was 13.79 lakh.',  # Correct number, wrong unit.
    'May profit margin was 1379%.',  # Decimal placement.
])
def test_incorrect_numbers_or_units_fail(cases, answer):
    result = grade(cases[3], {'answer': answer, 'sources': [{'source': 'G3_sales_ground_truth.csv', 'row': 6}]})
    assert result['status'] == 'FAIL'


def test_correct_answer_needs_source_location(cases):
    response = {'answer': 'May profit margin was 13.79%.', 'sources': [{'source': 'G3_sales_ground_truth.csv'}]}
    assert grade(cases[3], response)['content_ok']
    assert not grade(cases[3], response)['citation_ok']
    response['sources'][0]['row'] = 6
    assert grade(cases[3], response)['status'] == 'PASS'


def test_wrong_or_missing_timestamp_is_rejected(cases):
    expected = cases[10]['evidence'][0]
    assert not citation_matches({'source': expected['file']}, expected)
    assert not citation_matches({'source': expected['file'], 'start_sec': 35, 'end_sec': 58}, expected)
    assert citation_matches({'source_filename': expected['file'], 'start_sec': 36, 'end_sec': 58}, expected)


def test_wrong_pdf_page_and_fabricated_filename_are_rejected(cases):
    expected = cases[11]['evidence'][0]
    assert not citation_matches({'source': expected['file'], 'page': 99}, expected)
    assert not citation_matches({'source': 'invented.pdf', 'page': 1}, expected)
    assert citation_matches({'source_name': expected['file'], 'page_number': 1}, expected)


def test_cross_modal_requires_all_evidence_types(cases):
    case = cases[12]
    response = {'answer': 'Following the promotion, June revenue rose from 145 to 180 lakh; this does not prove causality.',
                'sources': [{'source': 'G3_sales_ground_truth.csv', 'row': 7}]}
    result = grade(case, response)
    assert result['content_ok'] and result['numerical_ok']
    assert not result['citation_ok']


def test_unavailable_cac_must_not_be_invented(cases):
    result = grade(cases[13], {'answer': 'Customer acquisition cost was 500 INR.', 'sources': []})
    assert not result['content_ok']


def test_runtime_errors_remain_errors(cases):
    class Unavailable:
        def ask(self, question):
            raise ValueError('retrieval unavailable')
    results = run_evaluation(Unavailable())
    assert len(results) == 15
    assert all(r['status'] == 'FAIL' and r['actual_answer'] == '' for r in results)
    assert all(r['error'] == 'ValueError: retrieval unavailable' for r in results)


def test_real_pipeline_and_export(tmp_path):
    results = run_evaluation()
    assert results[0]['numerical_ok'] is True
    assert results[0]['actual_sources'] == '[{"source": "G3_sales_ground_truth.csv"}]'
    assert results[10]['error'].startswith('ValueError:')
    write_artifacts(results, tmp_path)
    with (tmp_path / 'evaluation_results.csv').open(encoding='utf-8', newline='') as handle:
        exported = list(csv.DictReader(handle))
    assert len(exported) == 15
    assert exported[0]['actual_answer'] == results[0]['actual_answer']
    manifest = json.loads((tmp_path / 'evaluation_manifest.json').read_text())
    assert len(manifest['sha256']) == 5
    assert manifest['questions'] == 15


def test_html_escapes_pipeline_text(tmp_path):
    class UnsafeText:
        def ask(self, question):
            return {'answer': '<script>alert(1)</script>', 'sources': []}
    write_artifacts(run_evaluation(UnsafeText()), tmp_path)
    document = (tmp_path / 'evaluation_evidence.html').read_text(encoding='utf-8')
    assert '<script>alert(1)</script>' not in document
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in document
