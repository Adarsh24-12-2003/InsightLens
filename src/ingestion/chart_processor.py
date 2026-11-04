"""Extract chart metadata and structured captions from revenue/profit images."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _build_chart_caption(
    chart_name: str,
    chart_path: str | Path,
    csv_path: str | Path,
) -> dict:
    """Create a structured caption with chart content and verified values."""
    chart_path = Path(chart_path)
    csv_path = Path(csv_path)

    df = pd.read_csv(csv_path)
    metric_columns = {
        "revenue": ("revenue_lakh_inr", "Revenue"),
        "profit": ("profit_lakh_inr", "Profit"),
    }
    chart_key = chart_name.lower()
    if chart_key not in metric_columns:
        raise ValueError(f"Unsupported chart name: {chart_name}")

    metric_column, metric_label = metric_columns[chart_key]
    month_values = df["month"].astype(str).tolist()
    metric_values = pd.to_numeric(df[metric_column], errors="raise").tolist()
    changes = [
        (month_values[index - 1], month_values[index], metric_values[index] - metric_values[index - 1])
        for index in range(1, len(month_values))
    ]
    increases = [
        f"{start} to {end}" for start, end, change in changes if change > 0
    ]
    declines = [
        f"{start} to {end}" for start, end, change in changes if change < 0
    ]
    trend_parts = [
        f"{metric_label} ends at {metric_values[-1]} lakh INR in {month_values[-1]}, "
        f"up from {metric_values[0]} lakh INR in {month_values[0]}."
    ]
    if increases:
        trend_parts.append(f"Increases occur from {', '.join(increases)}.")
    if declines:
        trend_parts.append(f"Declines occur from {', '.join(declines)}.")
    trend = " ".join(trend_parts)

    caption = {
        "title": f"H1 2026 {metric_label}",
        "axes": f"X-axis: Month; Y-axis: {metric_label} (INR lakh)",
        "units": "INR lakh",
        "trend": trend,
        "values": dict(zip(month_values, metric_values)),
    }

    content = (
        f"source_type=chart; source_name={chart_path.name}; chart_name={chart_key}; "
        f"title='{caption['title']}'; axes='{caption['axes']}'; "
        f"units='{caption['units']}'; trend='{caption['trend']}'; "
        f"values={json.dumps(caption['values'], ensure_ascii=False)}; "
        f"content='The {metric_label.lower()} chart shows values for "
        f"{month_values[0]}-{month_values[-1]} 2026 using INR lakh units.'"
    )

    metadata = {
        "source_filename": chart_path.name,
        "source_name": chart_path.name,
        "source_type": "chart",
        "modality": "chart",
        "document_type": "chart_caption",
        "chart_name": chart_key,
        "title": caption["title"],
        "axes": caption["axes"],
        "units": caption["units"],
        "trend": trend,
        "original_file": str(chart_path),
        "verified_values": json.dumps(caption["values"], ensure_ascii=False),
    }

    return {
        "id": f"chart_{chart_key}",
        "text": content,
        "metadata": metadata,
    }


def process_chart(chart_path: str | Path, csv_path: str | Path) -> list[dict]:
    """Generate a structured caption record for a chart."""
    chart_path = Path(chart_path)
    chart_name = chart_path.stem.replace("G3_", "").replace("_chart", "")
    return [_build_chart_caption(chart_name, chart_path, csv_path)]
