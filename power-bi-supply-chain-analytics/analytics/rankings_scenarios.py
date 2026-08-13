"""
Rankings and Scenario Analysis

Implements supplier rankings and what-if scenario analysis:
- Supplier Reliability Rank
- Top 5 Suppliers by OTIF
- What-If: OTIF Impact of Lead Time Reduction
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class RankingsScenarios:
    """
    Class for rankings and what-if scenario analysis.
    
    Equivalent to Power BI ranking functions and scenario parameters.
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize rankings and scenarios calculator.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = data_dir
        self.orders = None
        self.suppliers = None
        
    def load_data(self):
        """Load orders and suppliers data."""
        self.orders = pd.read_csv(
            os.path.join(self.data_dir, 'supply_chain_orders.csv'),
            parse_dates=['order_date', 'promised_date', 'delivery_date']
        )
        
        self.suppliers = pd.read_csv(
            os.path.join(self.data_dir, 'suppliers.csv')
        )
        
    def calculate_supplier_reliability_rank(self):
        """
        Calculate Supplier Reliability Rank.
        
        DAX Equivalent:
        Supplier Reliability Rank = 
            RANKX(
                ALL(Suppliers),
                [OTIF %],
                ,DESC
            )
        
        Returns:
            DataFrame: Suppliers with reliability scores and ranks
        """
        if self.orders is None:
            self.load_data()
            
        # Calculate OTIF by supplier
        supplier_otif = self.orders.groupby('supplier_id').apply(
            lambda df: pd.Series({
                'otif': ((df['delivery_date'] <= df['promised_date']) & 
                        (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100,
                'on_time_pct': (df['delivery_date'] <= df['promised_date']).mean() * 100,
                'in_full_pct': (df['quantity_delivered'] >= df['quantity_ordered']).mean() * 100,
                'total_orders': len(df),
                'avg_lead_time': (df['delivery_date'] - df['order_date']).dt.days.mean(),
                'avg_quality_score': df['quality_score'].mean()
            })
        ).reset_index()
        
        # Merge with supplier info
        supplier_otif = supplier_otif.merge(self.suppliers[['supplier_id', 'supplier_name', 'region']], 
                                            on='supplier_id')
        
        # Calculate composite reliability score
        supplier_otif['reliability_score'] = (
            supplier_otif['otif'] * 0.4 +
            supplier_otif['on_time_pct'] * 0.2 +
            supplier_otif['in_full_pct'] * 0.2 +
            supplier_otif['avg_quality_score'] * 20  # Scale quality to similar range
        ) / 100
        
        # Rank suppliers
        supplier_otif['reliability_rank'] = supplier_otif['reliability_score'].rank(ascending=False, method='min')
        supplier_otif['otif_rank'] = supplier_otif['otif'].rank(ascending=False, method='min')
        
        return supplier_otif.sort_values('reliability_rank')
    
    def get_top_5_suppliers_by_otif(self):
        """
        Get Top 5 Suppliers by OTIF.
        
        DAX Equivalent:
        Top 5 Suppliers = 
            TOPN(
                5,
                VALUES(Suppliers[supplier_id]),
                [OTIF %],
                DESC
            )
        
        Returns:
            DataFrame: Top 5 suppliers by OTIF
        """
        rankings = self.calculate_supplier_reliability_rank()
        return rankings.head(5)[['supplier_id', 'supplier_name', 'otif', 'reliability_score', 'reliability_rank']]
    
    def get_bottom_5_suppliers_by_otif(self):
        """
        Get Bottom 5 Suppliers by OTIF for improvement focus.
        
        Returns:
            DataFrame: Bottom 5 suppliers by OTIF
        """
        rankings = self.calculate_supplier_reliability_rank()
        return rankings.tail(5)[['supplier_id', 'supplier_name', 'otif', 'reliability_score', 'reliability_rank']]
    
    def simulate_lead_time_reduction(self, reduction_days=2):
        """
        What-If Analysis: OTIF Impact of Lead Time Reduction.
        
        Simulates the impact of reducing supplier lead times on OTIF.
        
        DAX Equivalent (using What-If parameter):
        OTIF with Reduced Lead Time = 
            CALCULATE(
                [OTIF %],
                FILTER(
                    Orders,
                    Orders[delivery_date] <= 
                        Orders[order_date] + (Orders[lead_time] - [Lead Time Reduction Parameter])
                )
            )
        
        Args:
            reduction_days: Number of days to reduce lead time
            
        Returns:
            dict: Current vs simulated OTIF metrics
        """
        if self.orders is None:
            self.load_data()
            
        # Current OTIF
        current_on_time = (self.orders['delivery_date'] <= self.orders['promised_date']).sum()
        current_in_full = (self.orders['quantity_delivered'] >= self.orders['quantity_ordered']).sum()
        current_otif = ((self.orders['delivery_date'] <= self.orders['promised_date']) & 
                       (self.orders['quantity_delivered'] >= self.orders['quantity_ordered'])).mean() * 100
        
        # Simulate reduced promised date (earlier promise = harder to meet)
        # This simulates what happens if we promise faster delivery
        simulated_promised_date = self.orders['promised_date'] - pd.Timedelta(days=reduction_days)
        simulated_on_time = (self.orders['delivery_date'] <= simulated_promised_date).sum()
        simulated_otif = ((self.orders['delivery_date'] <= simulated_promised_date) & 
                         (self.orders['quantity_delivered'] >= self.orders['quantity_ordered'])).mean() * 100
        
        # Calculate improvement (negative means it's harder to achieve)
        otif_improvement = simulated_otif - current_otif
        on_time_improvement = simulated_on_time - current_on_time
        
        return {
            'reduction_days': reduction_days,
            'current_otif': current_otif,
            'simulated_otif': simulated_otif,
            'otif_improvement_pp': otif_improvement,
            'current_on_time_count': current_on_time,
            'simulated_on_time_count': simulated_on_time,
            'additional_on_time_orders': on_time_improvement,
            'improvement_pct': (otif_improvement / current_otif) * 100 if current_otif > 0 else 0
        }
    
    def analyze_lead_time_scenarios(self):
        """
        Analyze multiple lead time reduction scenarios.
        
        Returns:
            DataFrame: Comparison of different lead time reduction scenarios
        """
        scenarios = []
        for reduction in [0, 1, 2, 3, 5, 7]:
            result = self.simulate_lead_time_reduction(reduction)
            scenarios.append(result)
        
        return pd.DataFrame(scenarios)
    
    def get_supplier_performance_by_region(self):
        """
        Get supplier performance breakdown by region.
        
        Returns:
            DataFrame: Regional supplier performance
        """
        rankings = self.calculate_supplier_reliability_rank()
        
        regional = rankings.groupby('region').agg({
            'otif': 'mean',
            'reliability_score': 'mean',
            'total_orders': 'sum',
            'reliability_rank': lambda x: x.min()  # Best rank in region
        }).reset_index()
        
        regional.columns = ['region', 'avg_otif', 'avg_reliability_score', 'total_orders', 'best_rank']
        
        return regional.sort_values('avg_otif', ascending=False)
    
    def get_supplier_category_analysis(self):
        """
        Analyze supplier performance by category.
        
        Returns:
            DataFrame: Performance by supplier category
        """
        if self.orders is None:
            self.load_data()
            
        # Merge orders with supplier category
        orders_with_cat = self.orders.merge(
            self.suppliers[['supplier_id', 'category']], 
            on='supplier_id'
        )
        
        category_perf = orders_with_cat.groupby('category').apply(
            lambda df: pd.Series({
                'otif': ((df['delivery_date'] <= df['promised_date']) & 
                        (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100,
                'total_orders': len(df),
                'avg_quantity': df['quantity_ordered'].mean(),
                'total_value': (df['unit_cost'] * df['quantity_ordered']).sum()
            })
        ).reset_index()
        
        return category_perf
    
    def get_all_rankings_and_scenarios(self):
        """
        Get all rankings and scenario analyses.
        
        Returns:
            dict: All rankings and scenarios
        """
        if self.orders is None:
            self.load_data()
            
        return {
            'supplier_rankings': self.calculate_supplier_reliability_rank(),
            'top_5_suppliers': self.get_top_5_suppliers_by_otif(),
            'bottom_5_suppliers': self.get_bottom_5_suppliers_by_otif(),
            'lead_time_scenarios': self.analyze_lead_time_scenarios(),
            'regional_analysis': self.get_supplier_performance_by_region(),
            'category_analysis': self.get_supplier_category_analysis(),
        }


def main():
    """Main function to demonstrate rankings and scenarios."""
    print("=" * 60)
    print("RANKINGS AND SCENARIO ANALYSIS")
    print("=" * 60)
    
    rs = RankingsScenarios()
    rs.load_data()
    
    print("\n" + "=" * 60)
    print("TOP 5 SUPPLIERS BY OTIF")
    print("=" * 60)
    top5 = rs.get_top_5_suppliers_by_otif()
    print(top5.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("BOTTOM 5 SUPPLIERS BY OTIF (Improvement Focus)")
    print("=" * 60)
    bottom5 = rs.get_bottom_5_suppliers_by_otif()
    print(bottom5.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("LEAD TIME REDUCTION SCENARIOS")
    print("=" * 60)
    scenarios = rs.analyze_lead_time_scenarios()
    print(scenarios.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("SUPPLIER PERFORMANCE BY REGION")
    print("=" * 60)
    regional = rs.get_supplier_performance_by_region()
    print(regional.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("SUPPLIER PERFORMANCE BY CATEGORY")
    print("=" * 60)
    category = rs.get_supplier_category_analysis()
    print(category.to_string(index=False))
    
    # Detailed what-if analysis
    print("\n" + "=" * 60)
    print("WHAT-IF ANALYSIS: Lead Time Reduction Impact")
    print("=" * 60)
    for reduction in [1, 2, 3, 5]:
        result = rs.simulate_lead_time_reduction(reduction)
        print(f"\n  Reducing lead time by {reduction} days:")
        print(f"    Current OTIF:     {result['current_otif']:.2f}%")
        print(f"    Simulated OTIF:   {result['simulated_otif']:.2f}%")
        print(f"    Improvement:      {result['otif_improvement_pp']:+.2f} pp ({result['improvement_pct']:.1f}%)")
        print(f"    Additional On-Time Orders: {result['additional_on_time_orders']:.0f}")
    
    print("\n" + "=" * 60)
    print("Rankings and Scenarios Complete!")
    print("=" * 60)
    
    return rs.get_all_rankings_and_scenarios()


if __name__ == "__main__":
    main()
