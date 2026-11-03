"""Calculate revenue and profit-margin metrics from monthly CSV data."""

import pandas as pd


class DataAnalyzer:
    """Look up monthly sales data and calculate business metrics."""

    def __init__(self, csv_path: str):
        """Load the sales records from ``csv_path``."""
        self.data = pd.read_csv(csv_path)

    def get_highest_revenue(self) -> dict:
        """Return the month and amount for the highest recorded revenue."""
        row = self.data.loc[self.data["revenue_lakh_inr"].idxmax()]

        return {
            "month": row["month"],
            "revenue": row["revenue_lakh_inr"]
        }

    def get_monthly_data(self, month: str) -> dict:
        """Return the row for ``month`` or an error when it is not present.

        Month matching ignores capitalization.
        """
        row = self.data[
            self.data["month"].str.lower() == month.lower()
        ]

        if row.empty:
            return {"error": f"No data found for {month}"}

        return row.iloc[0].to_dict()

    def calculate_profit_margin(self, month: str) -> dict:
        """Calculate a month's profit as a percentage of its revenue.

        The calculation divides profit by revenue and multiplies by 100.
        """
        result = self.get_monthly_data(month)

        if "error" in result:
            return result

        margin = (
            result["profit_lakh_inr"] / result["revenue_lakh_inr"]
        ) * 100

        return {
            "month": result["month"],
            "profit_margin": round(margin, 2)
        }

    def compare_profit_margins(
        self,
        first_month: str,
        second_month: str
    ) -> dict:
        """Compare two months and report the margin change from first to second.

        The difference is measured in percentage points. ``improved`` is true
        when the second month's margin is higher than the first month's.
        """
        first = self.calculate_profit_margin(first_month)
        second = self.calculate_profit_margin(second_month)

        if "error" in first:
            return first
        if "error" in second:
            return second

        difference = round(
            second["profit_margin"] - first["profit_margin"],
            2
        )

        return {
            "first_month": first["month"],
            "first_margin": first["profit_margin"],
            "second_month": second["month"],
            "second_margin": second["profit_margin"],
            "difference": difference,
            "improved": difference > 0
        }
