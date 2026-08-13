"""
Supply Chain KPI Calculations

Implements 20 key performance metrics equivalent to Power BI DAX measures.
Uses Pandas for all calculations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class SupplyChainKPIs:
    """
    Class to calculate supply chain KPIs from raw data.
    
    Equivalent to DAX measures in Power BI but implemented in Python/Pandas.
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize KPI calculator with data directory.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = data_dir
        self.orders = None
        self.inventory = None
        self.shipping = None
        self.products = None
        self.suppliers = None
        self.warehouses = None
        
    def load_data(self):
        """Load all CSV data files into DataFrames."""
        print("Loading data...")
        
        self.orders = pd.read_csv(
            os.path.join(self.data_dir, 'supply_chain_orders.csv'),
            parse_dates=['order_date', 'promised_date', 'delivery_date']
        )
        
        self.inventory = pd.read_csv(
            os.path.join(self.data_dir, 'inventory_levels.csv'),
            parse_dates=['date', 'last_replenishment_date', 'next_expected_delivery']
        )
        
        self.shipping = pd.read_csv(
            os.path.join(self.data_dir, 'shipping_costs.csv'),
            parse_dates=['ship_date', 'delivery_date']
        )
        
        self.products = pd.read_csv(
            os.path.join(self.data_dir, 'products.csv')
        )
        
        self.suppliers = pd.read_csv(
            os.path.join(self.data_dir, 'suppliers.csv'),
            parse_dates=['contract_start_date']
        )
        
        self.warehouses = pd.read_csv(
            os.path.join(self.data_dir, 'warehouses.csv'),
            parse_dates=['open_date']
        )
        
        print(f"  Loaded {len(self.orders)} orders")
        print(f"  Loaded {len(self.inventory)} inventory records")
        print(f"  Loaded {len(self.shipping)} shipments")
        
    # =========================================================================
    # SERVICE KPIs
    # =========================================================================
    
    def calculate_otif(self, df=None):
        """
        Calculate OTIF % (On Time In Full).
        
        DAX Equivalent:
        OTIF % = 
            DIVIDE(
                COUNTROWS(FILTER(Orders, Orders[delivery_date] <= Orders[promised_date] && 
                                 Orders[quantity_delivered] >= Orders[quantity_ordered])),
                COUNTROWS(Orders)
            )
        
        Returns:
            float: OTIF percentage (0-100)
        """
        if df is None:
            df = self.orders
            
        on_time = df['delivery_date'] <= df['promised_date']
        in_full = df['quantity_delivered'] >= df['quantity_ordered']
        otif_orders = (on_time & in_full).sum()
        
        return (otif_orders / len(df)) * 100
    
    def calculate_fill_rate(self, df=None):
        """
        Calculate Fill Rate %.
        
        DAX Equivalent:
        Fill Rate % = 
            DIVIDE(
                SUM(Orders[quantity_delivered]),
                SUM(Orders[quantity_ordered])
            )
        
        Returns:
            float: Fill rate percentage (0-100)
        """
        if df is None:
            df = self.orders
            
        total_delivered = df['quantity_delivered'].sum()
        total_ordered = df['quantity_ordered'].sum()
        
        return (total_delivered / total_ordered) * 100
    
    def calculate_on_time_delivery(self, df=None):
        """
        Calculate On-Time Delivery %.
        
        DAX Equivalent:
        On-Time Delivery % = 
            DIVIDE(
                COUNTROWS(FILTER(Orders, Orders[delivery_date] <= Orders[promised_date])),
                COUNTROWS(Orders)
            )
        
        Returns:
            float: On-time delivery percentage (0-100)
        """
        if df is None:
            df = self.orders
            
        on_time = (df['delivery_date'] <= df['promised_date']).sum()
        
        return (on_time / len(df)) * 100
    
    def calculate_perfect_order(self, df=None):
        """
        Calculate Perfect Order %.
        
        Perfect order = On-time + In-full + Quality score >= 0.95
        
        DAX Equivalent:
        Perfect Order % = 
            DIVIDE(
                COUNTROWS(FILTER(Orders, 
                    Orders[delivery_date] <= Orders[promised_date] &&
                    Orders[quantity_delivered] >= Orders[quantity_ordered] &&
                    Orders[quality_score] >= 0.95
                )),
                COUNTROWS(Orders)
            )
        
        Returns:
            float: Perfect order percentage (0-100)
        """
        if df is None:
            df = self.orders
            
        on_time = df['delivery_date'] <= df['promised_date']
        in_full = df['quantity_delivered'] >= df['quantity_ordered']
        high_quality = df['quality_score'] >= 0.95
        
        perfect_orders = (on_time & in_full & high_quality).sum()
        
        return (perfect_orders / len(df)) * 100
    
    # =========================================================================
    # INVENTORY KPIs
    # =========================================================================
    
    def calculate_inventory_turns(self, period_days=365):
        """
        Calculate Inventory Turns.
        
        DAX Equivalent:
        Inventory Turns = 
            DIVIDE(
                CALCULATE(SUM(Orders[quantity_ordered]), DATESINPERIOD(...)),
                AVERAGE(Inventory[inventory_on_hand])
            )
        
        Args:
            period_days: Number of days for the calculation period
            
        Returns:
            float: Inventory turns ratio
        """
        # Calculate COGS (Cost of Goods Sold) approximation
        cogs = self.orders['quantity_ordered'] * self.orders['unit_cost']
        annual_cogs = cogs.sum() * (365 / period_days)
        
        # Average inventory value
        avg_inventory = self.inventory['inventory_on_hand'].mean()
        
        # Approximate inventory value using average product cost
        avg_product_cost = self.products['base_cost'].mean()
        avg_inventory_value = avg_inventory * avg_product_cost
        
        if avg_inventory_value == 0:
            return 0
            
        return annual_cogs / avg_inventory_value
    
    def calculate_days_of_supply(self):
        """
        Calculate Days of Supply.
        
        DAX Equivalent:
        Days of Supply = 
            DIVIDE(
                AVERAGE(Inventory[inventory_on_hand]),
                AVERAGE(Orders[quantity_ordered]) / 30
            )
        
        Returns:
            float: Days of supply
        """
        avg_inventory = self.inventory['inventory_on_hand'].mean()
        
        # Average daily demand
        date_range = (self.orders['order_date'].max() - self.orders['order_date'].min()).days
        avg_daily_demand = self.orders['quantity_ordered'].sum() / max(date_range, 1)
        
        if avg_daily_demand == 0:
            return 0
            
        return avg_inventory / avg_daily_demand
    
    def calculate_inventory_risk_score(self):
        """
        Calculate Inventory Risk Score by product.
        
        Categories: Critical (< safety_stock), Warning (< reorder_point),
                   Optimal, Elevated (> 2x reorder_point)
        
        Returns:
            DataFrame: Product risk scores
        """
        inv = self.inventory.copy()
        
        def assign_risk(row):
            if row['inventory_on_hand'] < row['safety_stock']:
                return 'Critical'
            elif row['inventory_on_hand'] < row['reorder_point']:
                return 'Warning'
            elif row['inventory_on_hand'] > 2 * row['reorder_point']:
                return 'Elevated'
            else:
                return 'Optimal'
        
        inv['risk_category'] = inv.apply(assign_risk, axis=1)
        
        # Aggregate by product
        risk_summary = inv.groupby('product_id').agg({
            'risk_category': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown',
            'inventory_on_hand': 'mean'
        }).reset_index()
        
        risk_summary.columns = ['product_id', 'risk_category', 'avg_inventory']
        
        return risk_summary
    
    def calculate_stockout_frequency(self):
        """
        Calculate Stockout Frequency %.
        
        DAX Equivalent:
        Stockout Frequency % = 
            DIVIDE(
                COUNTROWS(FILTER(Inventory, Inventory[inventory_on_hand] = 0)),
                COUNTROWS(Inventory)
            )
        
        Returns:
            float: Stockout frequency percentage
        """
        stockouts = (self.inventory['inventory_on_hand'] == 0).sum()
        
        return (stockouts / len(self.inventory)) * 100
    
    # =========================================================================
    # COST KPIs
    # =========================================================================
    
    def calculate_cost_to_serve_per_order(self):
        """
        Calculate Cost to Serve per Order.
        
        DAX Equivalent:
        Cost to Serve per Order = 
            DIVIDE(
                SUM(Orders[unit_cost] * Orders[quantity_ordered]) + 
                SUM(Orders[handling_cost]) +
                SUM(Shipping[total_cost]),
                COUNTROWS(Orders)
            )
        
        Returns:
            float: Average cost to serve per order
        """
        product_costs = (self.orders['unit_cost'] * self.orders['quantity_ordered']).sum()
        handling_costs = self.orders['handling_cost'].sum()
        shipping_costs = self.shipping['total_cost'].sum()
        
        total_cost = product_costs + handling_costs + shipping_costs
        
        return total_cost / len(self.orders)
    
    def calculate_freight_cost_per_kg(self):
        """
        Calculate Freight Cost per Kg.
        
        DAX Equivalent:
        Freight Cost per Kg = 
            DIVIDE(
                SUM(Shipping[total_cost]),
                SUM(Shipping[weight_kg])
            )
        
        Returns:
            float: Freight cost per kilogram
        """
        total_cost = self.shipping['total_cost'].sum()
        total_weight = self.shipping['weight_kg'].sum()
        
        if total_weight == 0:
            return 0
            
        return total_cost / total_weight
    
    def calculate_cost_to_serve_by_shipping_mode(self):
        """
        Calculate Cost to Serve by Shipping Mode.
        
        DAX Equivalent:
        Cost to Serve by Mode = 
            CALCULATE(
                SUM(Shipping[total_cost]),
                ALLEXCEPT(Shipping, Shipping[shipping_mode])
            )
        
        Returns:
            Series: Cost by shipping mode
        """
        return self.shipping.groupby('shipping_mode')['total_cost'].sum()
    
    def calculate_freight_budget_variance(self, budget_multiplier=1.0):
        """
        Calculate Freight Budget Variance %.
        
        DAX Equivalent:
        Freight Budget Variance % = 
            DIVIDE(
                SUM(Shipping[total_cost]) - [Freight Budget],
                [Freight Budget]
            )
        
        Args:
            budget_multiplier: Multiplier to simulate budget vs actual
            
        Returns:
            float: Budget variance percentage
        """
        actual_cost = self.shipping['total_cost'].sum()
        
        # Simulate budget (in real scenario, this would come from a budget table)
        budget = actual_cost * budget_multiplier
        
        if budget == 0:
            return 0
            
        return ((actual_cost - budget) / budget) * 100
    
    # =========================================================================
    # GET ALL KPIs
    # =========================================================================
    
    def get_all_kpis(self):
        """
        Calculate and return all KPIs in a dictionary.
        
        Returns:
            dict: All calculated KPIs
        """
        if self.orders is None:
            self.load_data()
        
        kpis = {
            # Service KPIs
            'OTIF %': self.calculate_otif(),
            'Fill Rate %': self.calculate_fill_rate(),
            'On-Time Delivery %': self.calculate_on_time_delivery(),
            'Perfect Order %': self.calculate_perfect_order(),
            
            # Inventory KPIs
            'Inventory Turns': self.calculate_inventory_turns(),
            'Days of Supply': self.calculate_days_of_supply(),
            'Stockout Frequency %': self.calculate_stockout_frequency(),
            
            # Cost KPIs
            'Cost to Serve per Order': self.calculate_cost_to_serve_per_order(),
            'Freight Cost per Kg': self.calculate_freight_cost_per_kg(),
            'Freight Budget Variance %': self.calculate_freight_budget_variance(),
        }
        
        # Add cost by shipping mode
        cost_by_mode = self.calculate_cost_to_serve_by_shipping_mode()
        for mode, cost in cost_by_mode.items():
            kpis[f'Cost to Serve - {mode}'] = cost
        
        return kpis


def main():
    """Main function to calculate and display KPIs."""
    print("=" * 60)
    print("SUPPLY CHAIN KPI CALCULATIONS")
    print("=" * 60)
    
    # Initialize KPI calculator
    kpi_calc = SupplyChainKPIs()
    
    # Load data
    kpi_calc.load_data()
    
    # Calculate all KPIs
    print("\nCalculating KPIs...")
    kpis = kpi_calc.get_all_kpis()
    
    # Display results
    print("\n" + "=" * 60)
    print("SERVICE KPIs")
    print("=" * 60)
    print(f"  OTIF %:              {kpis['OTIF %']:.2f}%")
    print(f"  Fill Rate %:         {kpis['Fill Rate %']:.2f}%")
    print(f"  On-Time Delivery %:  {kpis['On-Time Delivery %']:.2f}%")
    print(f"  Perfect Order %:     {kpis['Perfect Order %']:.2f}%")
    
    print("\n" + "=" * 60)
    print("INVENTORY KPIs")
    print("=" * 60)
    print(f"  Inventory Turns:     {kpis['Inventory Turns']:.2f}")
    print(f"  Days of Supply:      {kpis['Days of Supply']:.2f}")
    print(f"  Stockout Frequency:  {kpis['Stockout Frequency %']:.2f}%")
    
    print("\n" + "=" * 60)
    print("COST KPIs")
    print("=" * 60)
    print(f"  Cost to Serve/Order: ${kpis['Cost to Serve per Order']:.2f}")
    print(f"  Freight Cost/Kg:     ${kpis['Freight Cost per Kg']:.2f}")
    print(f"  Freight Budget Var:  {kpis['Freight Budget Variance %']:.2f}%")
    
    print("\n" + "=" * 60)
    print("COST BY SHIPPING MODE")
    print("=" * 60)
    for mode in ['Air', 'Ocean', 'Road', 'Rail', 'Express']:
        key = f'Cost to Serve - {mode}'
        if key in kpis:
            print(f"  {mode:12}: ${kpis[key]:,.2f}")
    
    # Calculate inventory risk
    print("\n" + "=" * 60)
    print("INVENTORY RISK DISTRIBUTION")
    print("=" * 60)
    risk_df = kpi_calc.calculate_inventory_risk_score()
    risk_dist = risk_df['risk_category'].value_counts()
    for category, count in risk_dist.items():
        pct = (count / len(risk_df)) * 100
        print(f"  {category:12}: {count:4} ({pct:.1f}%)")
    
    print("\n" + "=" * 60)
    print("KPI Calculation Complete!")
    print("=" * 60)
    
    return kpis


if __name__ == "__main__":
    main()
