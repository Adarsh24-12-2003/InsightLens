
import pandas as pd  # Load tools for working with CSV data.


class DataAnalyzer:  # Analyze business data from a CSV file.
    """Perform numerical analysis using verified CSV data."""

    def __init__(self, csv_path: str):  # Initialize the analyzer.
        self.data = pd.read_csv(csv_path)  # Read the CSV into a DataFrame.

    def get_highest_revenue(self) -> dict:  # Find the month with the most revenue.
        """Find the month with the highest revenue."""

        row = self.data.loc[  # Select the row with the highest revenue.
            self.data["revenue_lakh_inr"].idxmax()  # Find its row index.
        ]  # Store the selected row.

        return {  # Return the month and its revenue.
            "month": row["month"],  # Include the month name.
            "revenue": row["revenue_lakh_inr"]  # Include the revenue amount.
        }  # Finish the result.

    def get_monthly_data(self, month: str) -> dict:  # Get data for one month.
        """Get revenue and profit for a particular month."""

        row = self.data[  # Filter the rows to the requested month.
            self.data["month"].str.lower() == month.lower()  # Compare month names without case sensitivity.
        ]  # Store the matching rows.

        if row.empty:  # Check whether the month was found.
            return {"error": f"No data found for {month}"}  # Report the missing month.

        return row.iloc[0].to_dict()  # Return the first match as a dictionary.

    def calculate_profit_margin(self, month: str) -> dict:  # Calculate profit as a percentage of revenue.
        """Calculate profit margin for a particular month."""

        result = self.get_monthly_data(month)  # Get the month's revenue and profit.

        if "error" in result:  # Check whether the month lookup failed.
            return result  # Pass the error back to the caller.

        margin = (  # Compute profit divided by revenue as a percentage.
            result["profit_lakh_inr"]  # Use the month's profit.
            / result["revenue_lakh_inr"]  # Divide by its revenue.
        ) * 100  # Convert the ratio to a percentage.

        return {  # Return the month and its profit margin.
            "month": result["month"],  # Include the month name.
            "profit_margin": round(margin, 2)  # Round the margin to two decimal places.
        }  # Finish the result.
