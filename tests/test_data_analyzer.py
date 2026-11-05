
"""Test CSV lookups and sales calculations."""

from src.analysis.data_analyzer import DataAnalyzer


def test_highest_revenue():
    analyzer = DataAnalyzer("data/raw/G3_sales_ground_truth.csv")

    result = analyzer.get_highest_revenue()

    assert result == {
        "month": "Jun",
        "revenue": 180
    }


def test_monthly_data():
    analyzer = DataAnalyzer("data/raw/G3_sales_ground_truth.csv")

    result = analyzer.get_monthly_data("May")

    assert result["revenue_lakh_inr"] == 145
    assert result["profit_lakh_inr"] == 20


def test_profit_margin():
    analyzer = DataAnalyzer("data/raw/G3_sales_ground_truth.csv")

    result = analyzer.calculate_profit_margin("May")

    assert result["profit_margin"] == 13.79


def test_compare_profit_margins():
    analyzer = DataAnalyzer(
        "data/raw/G3_sales_ground_truth.csv"
    )

    result = analyzer.compare_profit_margins("May", "Jun")

    assert result["first_month"] == "May"
    assert result["first_margin"] == 13.79
    assert result["second_month"] == "Jun"
    assert result["second_margin"] == 16.11
    assert result["difference"] == 2.32
    assert result["improved"] is True


def test_compare_profit_margins_invalid_month():
    analyzer = DataAnalyzer("data/raw/G3_sales_ground_truth.csv")

    result = analyzer.compare_profit_margins("December", "May")

    assert result == {"error": "No data found for December"}


def test_invalid_month():
    analyzer = DataAnalyzer("data/raw/G3_sales_ground_truth.csv")

    result = analyzer.get_monthly_data("December")

    assert "error" in result
