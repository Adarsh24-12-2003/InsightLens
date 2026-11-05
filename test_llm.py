"""Verify OpenAI answer generation offline; never require real credentials."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from src.retrieval.llm import LLMService


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key-not-a-secret')
    monkeypatch.delenv('OPENAI_MODEL', raising=False)
    with patch('src.retrieval.llm.load_dotenv'), patch('src.retrieval.llm.OpenAI') as client:
        client.return_value.responses.create.return_value = SimpleNamespace(output_text='June revenue was 180 lakh INR.')
        yield LLMService(), client


def test_missing_api_key_fails_before_client_creation(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with patch('src.retrieval.llm.load_dotenv'), patch('src.retrieval.llm.OpenAI') as client:
        with pytest.raises(ValueError, match='OPENAI_API_KEY'):
            LLMService()
        client.assert_not_called()


def test_default_model_and_api_key(service):
    llm, client = service
    assert llm.model == 'gpt-4.1-mini'
    client.assert_called_once_with(api_key='test-key-not-a-secret')


def test_model_is_configurable(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setenv('OPENAI_MODEL', 'custom-model')
    with patch('src.retrieval.llm.load_dotenv'), patch('src.retrieval.llm.OpenAI'):
        assert LLMService().model == 'custom-model'


def test_responses_api_preserves_evidence_and_grounding_instructions(service):
    llm, _ = service
    context = [{'text': 'June revenue was 180 lakh INR.',
                'metadata': {'source': 'G3_business_report.pdf', 'page_number': 1}}]
    assert llm.generate_answer('What was June revenue?', context) == 'June revenue was 180 lakh INR.'
    args = llm.client.responses.create.call_args.kwargs
    assert args['model'] == 'gpt-4.1-mini'
    assert args['store'] is False
    assert 'What was June revenue?' in args['input']
    assert 'G3_business_report.pdf' in args['input']
    assert '"page_number": 1' in args['input']
    assert 'June revenue was 180 lakh INR.' in args['input']
    assert 'ONLY the retrieved context' in args['instructions']
    assert 'Never invent facts' in args['instructions']
    assert 'If the evidence is insufficient' in args['instructions']
    assert 'timestamps' in args['instructions']


def test_empty_context_abstains_without_api_call(service):
    llm, _ = service
    assert 'could not find relevant information' in llm.generate_answer('Unknown fact?', [])
    llm.client.responses.create.assert_not_called()


@pytest.mark.parametrize('text', ['', '   ', None])
def test_empty_response_has_clear_fallback(service, text):
    llm, _ = service
    llm.client.responses.create.return_value = SimpleNamespace(output_text=text)
    assert 'could not generate an answer' in llm.generate_answer('Question?', [{'text': 'Evidence', 'metadata': {}}])


def test_service_errors_are_not_fabricated_answers(service):
    llm, _ = service
    llm.client.responses.create.side_effect = RuntimeError('service unavailable')
    with pytest.raises(RuntimeError, match='service unavailable'):
        llm.generate_answer('Question?', [{'text': 'Evidence', 'metadata': {}}])
