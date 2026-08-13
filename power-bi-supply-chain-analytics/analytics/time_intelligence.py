"""
Time Intelligence Calculations

Implements time-based KPI calculations equivalent to Power BI DAX time intelligence:
- YTD (Year-to-Date)
- PY (Prior Year)
- YoY Growth
- MoM Change
- Rolling Averages
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class TimeIntelligence:
    """
    Class for time-based KPI calculations.
    
    Equivalent to DAX time intelligence functions in Power BI.
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize time intelligence calculator.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = data_dir
        self.orders = None
        
    def load_data(self):
        """Load orders data."""
        self.orders = pd.read_csv(
            os.path.join(self.data_dir, 'supply_chain_orders.csv'),
            parse_dates=['order_date', 'promised_date', 'delivery_date']
        )
        self.orders['year'] = self.orders['order_date'].dt.year
        self.orders['month'] = self.orders['order_date'].dt.month
        self.orders['quarter'] = self.orders['order_date'].dt.quarter
        self.orders['year_month'] = self.orders['order_date'].dt.to_period('M')
        
    def calculate_otif_ytd(self, end_date=None):
        """
        Calculate OTIF % Year-to-Date.
        
        DAX Equivalent:
        OTIF % YTD = 
            CALCULATE(
                [OTIF %],
                DATESYTD('Calendar'[Date])
            )
        
        Args:
            end_date: End date for YTD calculation (default: latest date in data)
            
        Returns:
            float: YTD OTIF percentage
        """
        if self.orders is None:
            self.load_data()
            
        if end_date is None:
            end_date = self.orders['order_date'].max()
            
        start_of_year = datetime(end_date.year, 1, 1)
        ytd_orders = self.orders[
            (self.orders['order_date'] >= start_of_year) & 
            (self.orders['order_date'] <= end_date)
        ]
        
        if len(ytd_orders) == 0:
            return 0
            
        on_time = ytd_orders['delivery_date'] <= ytd_orders['promised_date']
        in_full = ytd_orders['quantity_delivered'] >= ytd_orders['quantity_ordered']
        otif_orders = (on_time & in_full).sum()
        
        return (otif_orders / len(ytd_orders)) * 100
    
    def calculate_otif_py(self, reference_date=None):
        """
        Calculate OTIF % Prior Year.
        
        DAX Equivalent:
        OTIF % PY = 
            CALCULATE(
                [OTIF %],
                SAMEPERIODLASTYEAR('Calendar'[Date])
            )
        
        Args:
            reference_date: Reference date to calculate prior year from
            
        Returns:
            float: Prior year OTIF percentage
        """
        if self.orders is None:
            self.load_data()
            
        if reference_date is None:
            reference_date = self.orders['order_date'].max()
            
        # Get the same period last year
        start_date = datetime(reference_date.year - 1, 1, 1)
        end_date = datetime(reference_date.year - 1, 12, 31)
        
        py_orders = self.orders[
            (self.orders['order_date'] >= start_date) & 
            (self.orders['order_date'] <= end_date)
        ]
        
        if len(py_orders) == 0:
            return 0
            
        on_time = py_orders['delivery_date'] <= py_orders['promised_date']
        in_full = py_orders['quantity_delivered'] >= py_orders['quantity_ordered']
        otif_orders = (on_time & in_full).sum()
        
        return (otif_orders / len(py_orders)) * 100
    
    def calculate_otif_yoy_growth(self, reference_date=None):
        """
        Calculate OTIF % Year-over-Year Growth.
        
        DAX Equivalent:
        OTIF % YoY Growth = 
            [OTIF %] - [OTIF % PY]
        
        Args:
            reference_date: Reference date for comparison
            
        Returns:
            float: YoY growth in percentage points
        """
        current_otif = self.calculate_otif_ytd(reference_date)
        prior_otif = self.calculate_otif_py(reference_date)
        
        return current_otif - prior_otif
    
    def calculate_fill_rate_rolling_avg(self, window_months=3):
        """
        Calculate Fill Rate 3-Month Rolling Average.
        
        DAX Equivalent:
        Fill Rate 3M Rolling Avg = 
            AVERAGEX(
                DATESINPERIOD('Calendar'[Date], LASTDATE('Calendar'[Date]), -3, MONTH),
                [Fill Rate %]
            )
        
        Args:
            window_months: Number of months for rolling window
            
        Returns:
            DataFrame: Monthly fill rates with rolling average
        """
        if self.orders is None:
            self.load_data()
            
        # Calculate monthly fill rate
        monthly = self.orders.groupby('year_month').agg({
            'quantity_delivered': 'sum',
            'quantity_ordered': 'sum'
        }).reset_index()
        
        monthly['fill_rate'] = (monthly['quantity_delivered'] / monthly['quantity_ordered']) * 100
        
        # Calculate rolling average
        monthly['rolling_avg'] = monthly['fill_rate'].rolling(window=window_months, min_periods=1).mean()
        
        return monthly
    
    def calculate_cost_to_serve_mom_change(self):
        """
        Calculate Cost to Serve Month-over-Month Change.
        
        DAX Equivalent:
        Cost to Serve MoM Change = 
            [Cost to Serve] - 
            CALCULATE([Cost to Serve], PREVIOUSMONTH('Calendar'[Date]))
        
        Returns:
            DataFrame: Monthly cost to serve with MoM change
        """
        if self.orders is None:
            self.load_data()
            
        # Calculate monthly cost to serve
        monthly = self.orders.groupby('year_month').agg({
            'unit_cost': lambda x: (x * self.orders.loc[x.index, 'quantity_ordered']).sum(),
            'handling_cost': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        monthly.columns = ['year_month', 'product_cost', 'handling_cost', 'order_count']
        monthly['total_cost'] = monthly['product_cost'] + monthly['handling_cost']
        monthly['cost_per_order'] = monthly['total_cost'] / monthly['order_count']
        
        # Calculate MoM change
        monthly['prev_month_cost'] = monthly['cost_per_order'].shift(1)
        monthly['mom_change'] = monthly['cost_per_order'] - monthly['prev_month_cost']
        monthly['mom_change_pct'] = (monthly['mom_change'] / monthly['prev_month_cost']) * 100
        
        return monthly
    
    def get_monthly_otif_trend(self):
        """
        Calculate monthly OTIF trend for charting.
        
        Returns:
            DataFrame: Monthly OTIF percentages
        """
        if self.orders is None:
            self.load_data()
            
        monthly = self.orders.groupby('year_month').apply(
            lambda df: pd.Series({
                'otif': ((df['delivery_date'] <= df['promised_date']) & 
                        (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100,
                'on_time': (df['delivery_date'] <= df['promised_date']).mean() * 100,
                'in_full': (df['quantity_delivered'] >= df['quantity_ordered']).mean() * 100,
                'order_count': len(df)
            })
        ).reset_index()
        
        return monthly
    
    def get_quarterly_performance(self):
        """
        Calculate quarterly performance summary.
        
        Returns:
            DataFrame: Quarterly KPIs
        """
        if self.orders is None:
            self.load_data()
            
        self.orders['year_quarter'] = self.orders['order_date'].dt.to_period('Q')
        
        # Calculate OTIF for each quarter
        quarterly_metrics = self.orders.groupby(['year', 'quarter']).apply(
            lambda df: pd.Series({
                'otif': ((df['delivery_date'] <= df['promised_date']) & 
                        (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100,
                'order_count': len(df)
            })
        ).reset_index()
        
        return quarterly_metrics
    
    def get_all_time_intelligence(self):
        """
        Calculate all time intelligence metrics.
        
        Returns:
            dict: All time intelligence calculations
        """
        if self.orders is None:
            self.load_data()
            
        results = {
            'otif_ytd': self.calculate_otif_ytd(),
            'otif_py': self.calculate_otif_py(),
            'otif_yoy_growth': self.calculate_otif_yoy_growth(),
            'fill_rate_rolling': self.calculate_fill_rate_rolling_avg(),
            'cost_mom_change': self.calculate_cost_to_serve_mom_change(),
            'monthly_otif_trend': self.get_monthly_otif_trend(),
            'quarterly_performance': self.get_quarterly_performance(),
        }
        
        return results


def main():
    """Main function to demonstrate time intelligence calculations."""
    print("=" * 60)
    print("TIME INTELLIGENCE CALCULATIONS")
    print("=" * 60)
    
    ti = TimeIntelligence()
    ti.load_data()
    
    print("\n" + "=" * 60)
    print("YTD vs PRIOR YEAR COMPARISON")
    print("=" * 60)
    print(f"  OTIF % YTD:     {ti.calculate_otif_ytd():.2f}%")
    print(f"  OTIF % PY:      {ti.calculate_otif_py():.2f}%")
    print(f"  OTIF % YoY:     {ti.calculate_otif_yoy_growth():+.2f} pp")
    
    print("\n" + "=" * 60)
    print("FILL RATE ROLLING AVERAGE (3 Months)")
    print("=" * 60)
    rolling = ti.calculate_fill_rate_rolling_avg()
    print(rolling[['year_month', 'fill_rate', 'rolling_avg']].tail(6).to_string())
    
    print("\n" + "=" * 60)
    print("COST TO SERVE MOM CHANGE")
    print("=" * 60)
    mom = ti.calculate_cost_to_serve_mom_change()
    print(mom[['year_month', 'cost_per_order', 'mom_change', 'mom_change_pct']].tail(6).to_string())
    
    print("\n" + "=" * 60)
    print("MONTHLY OTIF TREND")
    print("=" * 60)
    trend = ti.get_monthly_otif_trend()
    print(trend[['year_month', 'otif', 'on_time', 'in_full', 'order_count']].tail(12).to_string())
    
    print("\n" + "=" * 60)
    print("QUARTERLY PERFORMANCE")
    print("=" * 60)
    quarterly = ti.get_quarterly_performance()
    print(quarterly[['year', 'quarter', 'otif', 'order_count']].to_string())
    
    print("\n" + "=" * 60)
    print("Time Intelligence Calculations Complete!")
    print("=" * 60)
    
    return ti.get_all_time_intelligence()


if __name__ == "__main__":
    main()
