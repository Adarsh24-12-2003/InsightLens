"""Verify transcript timestamps are validated before indexing."""

import json

import pytest

from src.ingestion.transcript_processor import process_transcript


def _write_transcript(tmp_path, segment):
    path = tmp_path / "transcript.json"
    path.write_text(json.dumps([segment]), encoding="utf-8")
    return path


def test_transcript_preserves_valid_timestamp_metadata(tmp_path):
    path = _write_transcript(
        tmp_path,
        {"start_sec": 36, "end_sec": 58, "text": "Revenue increased."},
    )

    record = process_transcript(path)[0]

    assert record["metadata"]["start_time"] == "00:36"
    assert record["metadata"]["end_time"] == "00:58"
    assert record["metadata"]["start_sec"] == 36
    assert record["metadata"]["end_sec"] == 58


@pytest.mark.parametrize(
    ("segment", "message"),
    [
        ({"end_sec": 20, "text": "Missing start."}, "missing start_sec"),
        ({"start_sec": 20, "end_sec": 20, "text": "Zero length."}, "invalid time range"),
        ({"start_sec": 21, "end_sec": 20, "text": "Reversed."}, "invalid time range"),
        ({"start_sec": -1, "end_sec": 20, "text": "Negative."}, "invalid time range"),
        ({"start_sec": "10", "end_sec": 20, "text": "Not normalized."}, "integer seconds"),
    ],
)
def test_invalid_transcript_timestamps_are_rejected(tmp_path, segment, message):
    path = _write_transcript(tmp_path, segment)

    with pytest.raises(ValueError, match=message):
        process_transcript(path)


def test_non_list_transcript_is_rejected(tmp_path):
    path = tmp_path / "transcript.json"
    path.write_text(json.dumps({"start_sec": 0}), encoding="utf-8")

    with pytest.raises(ValueError, match="JSON list"):
        process_transcript(path)
