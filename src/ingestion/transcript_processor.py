"""Clean and prepare timestamped transcript segments for retrieval."""

from __future__ import annotations

import json
from pathlib import Path


def _format_timestamp(seconds: int) -> str:
    """Convert numeric seconds to mm:ss format."""
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02d}:{secs:02d}"


def process_transcript(json_path: str | Path) -> list[dict]:
    """Return transcript segment records with source metadata and timestamps."""

    json_path = Path(json_path)

    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("Transcript must be a JSON list")

    records: list[dict] = []

    for item in data:

        if not isinstance(item, dict):
            raise ValueError("Each transcript segment must be a JSON object")

        if "start_sec" not in item:
            raise ValueError("missing start_sec")

        if "end_sec" not in item:
            raise ValueError("missing end_sec")

        start_sec = item["start_sec"]
        end_sec = item["end_sec"]

        if (
            not isinstance(start_sec, int)
            or isinstance(start_sec, bool)
            or not isinstance(end_sec, int)
            or isinstance(end_sec, bool)
        ):
            raise ValueError("Timestamps must be integer seconds")

        if start_sec < 0 or end_sec <= start_sec:
            raise ValueError("invalid time range")

        text = item.get("text", "")

        if not isinstance(text, str):
            raise ValueError("Transcript text must be a string")

        text = text.strip()

        if not text:
            continue

        start_ts = _format_timestamp(start_sec)
        end_ts = _format_timestamp(end_sec)

        chunk_text = (
            f"source_type=transcript; source_name={json_path.name}; "
            f"start_ts={start_ts}; end_ts={end_ts}; "
            f"video_id={item.get('video_id', 'unknown')}; "
            f"content='{text}'"
        )

        metadata = {
            "source_filename": json_path.name,
            "source_name": json_path.name,
            "source_type": "transcript",
            "modality": "transcript",
            "document_type": "transcript_segment",
            "video_id": item.get("video_id", "unknown"),
            "start_time": start_ts,
            "end_time": end_ts,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "start_sec": start_sec,
            "end_sec": end_sec,
            "original_file": str(json_path),
        }

        records.append(
            {
                "id": f"transcript_{start_ts}_{end_ts}",
                "text": chunk_text,
                "metadata": metadata,
            }
        )

    return records