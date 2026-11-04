"""Clean and prepare timestamped transcript segments for retrieval."""

from __future__ import annotations

import json
from pathlib import Path


def _format_timestamp(seconds: int) -> str:
    """Convert numeric seconds to mm:ss format."""
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(secs):02d}"


def process_transcript(json_path: str | Path) -> list[dict]:
    """Return transcript segment records with source metadata and timestamps."""
    json_path = Path(json_path)
    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    records: list[dict] = []
    for item in data:
        start_ts = _format_timestamp(int(item["start_sec"]))
        end_ts = _format_timestamp(int(item["end_sec"]))
        text = item.get("text", "").strip()
        if not text:
            continue

        chunk_text = (
            f"source_type=transcript; source_name={json_path.name}; start_ts={start_ts}; "
            f"end_ts={end_ts}; video_id={item.get('video_id', 'unknown')}; "
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
            "start_sec": int(item["start_sec"]),
            "end_sec": int(item["end_sec"]),
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
