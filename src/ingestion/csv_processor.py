"""Normalize and structure CSV sales data into searchable records."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def process_csv(csv_path: str | Path) -> list[dict]:
    """Read the sales CSV and return standardized row-level records."""
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    records: list[dict] = []
    for index, row in df.iterrows():
        month = str(row["month"]).strip()
        revenue = float(row["revenue_lakh_inr"])
        profit = float(row["profit_lakh_inr"])
        margin = round((profit / revenue) * 100, 2) if revenue else 0.0

        text = (
            "source_type=csv; source_name="
            f"{csv_path.name}; row_index={index}; month={month}; "
            f"revenue_lakh_inr={revenue}; profit_lakh_inr={profit}; "
            f"margin_percent={margin}; content='Month {month} revenue was {revenue} lakh INR "
            f"and profit was {profit} lakh INR.'"
        )

        metadata = {
            "source_filename": csv_path.name,
            "source_name": csv_path.name,
            "source_type": "csv",
            "modality": "tabular",
            "document_type": "csv_row",
            "month": month,
            "row_index": int(index),
            "revenue_lakh_inr": revenue,
            "profit_lakh_inr": profit,
            "margin_percent": margin,
            "original_file": str(csv_path),
        }

        records.append(
            {
                "id": f"csv_{csv_path.stem}_{index}_{month.lower()}",
                "text": text,
                "metadata": metadata,
            }
        )

    return records
