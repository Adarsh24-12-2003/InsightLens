"""Verify chart captions describe the metric values in the trusted CSV."""

from pathlib import Path

import pytest

from src.ingestion.chart_processor import process_chart


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
CSV_PATH = DATA_DIR / "G3_sales_ground_truth.csv"


def test_revenue_caption_has_chart_specific_trend_and_verified_values():
    record = process_chart(DATA_DIR / "G3_revenue_chart.png", CSV_PATH)[0]

    assert record["metadata"]["title"] == "H1 2026 Revenue"
    assert record["metadata"]["axes"] == "X-axis: Month; Y-axis: Revenue (INR lakh)"
    assert "Declines occur from Feb to Mar, Apr to May." in record["metadata"]["trend"]
    assert '"Jun": 180' in record["metadata"]["verified_values"]
    assert record["metadata"]["source_type"] == "chart"


def test_profit_caption_has_its_own_trend_and_verified_values():
    record = process_chart(DATA_DIR / "G3_profit_chart.png", CSV_PATH)[0]

    assert record["metadata"]["title"] == "H1 2026 Profit"
    assert record["metadata"]["axes"] == "X-axis: Month; Y-axis: Profit (INR lakh)"
    assert "Profit ends at 29 lakh INR in Jun, up from 18 lakh INR in Jan." in record["metadata"]["trend"]
    assert '"Jun": 29' in record["metadata"]["verified_values"]
    assert record["metadata"]["source_type"] == "chart"


def test_unknown_chart_metric_is_rejected(tmp_path):
    chart_path = tmp_path / "G3_margin_chart.png"
    chart_path.touch()

    with pytest.raises(ValueError, match="Unsupported chart name"):
        process_chart(chart_path, CSV_PATH)
