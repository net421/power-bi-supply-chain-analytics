"""
Data Quality Checks

Validates generated data for completeness, accuracy, and consistency.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys


class DataQualityChecker:
    """Class to perform data quality validation checks."""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.data_dir = data_dir
        self.results = {}
        
    def load_data(self):
        """Load all data files."""
        print("Loading data files...")
        
        self.orders = pd.read_csv(
            os.path.join(self.data_dir, 'supply_chain_orders.csv'),
            parse_dates=['order_date', 'promised_date', 'delivery_date']
        )
        
        self.inventory = pd.read_csv(
            os.path.join(self.data_dir, 'inventory_levels.csv'),
            parse_dates=['date']
        )
        
        self.shipping = pd.read_csv(
            os.path.join(self.data_dir, 'shipping_costs.csv'),
            parse_dates=['ship_date', 'delivery_date']
        )
        
        self.products = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
        self.suppliers = pd.read_csv(os.path.join(self.data_dir, 'suppliers.csv'))
        self.warehouses = pd.read_csv(os.path.join(self.data_dir, 'warehouses.csv'))
        
        print(f"  ✓ Loaded {len(self.orders)} orders")
        print(f"  ✓ Loaded {len(self.inventory)} inventory records")
        print(f"  ✓ Loaded {len(self.shipping)} shipments")
        print(f"  ✓ Loaded {len(self.products)} products")
        print(f"  ✓ Loaded {len(self.suppliers)} suppliers")
        print(f"  ✓ Loaded {len(self.warehouses)} warehouses")
        
    def check_record_counts(self):
        """Check if record counts meet requirements."""
        print("\n" + "="*60)
        print("RECORD COUNT VALIDATION")
        print("="*60)
        
        checks = {
            'Orders (expected ~10,000)': len(self.orders) >= 9500 and len(self.orders) <= 10500,
            'Inventory (expected ~24,000)': len(self.inventory) >= 23000 and len(self.inventory) <= 25000,
            'Shipping (expected ~8,500)': len(self.shipping) >= 8000 and len(self.shipping) <= 9000,
            'Products (expected ~500)': len(self.products) >= 490 and len(self.products) <= 510,
            'Suppliers (expected ~50)': len(self.suppliers) >= 49 and len(self.suppliers) <= 51,
            'Warehouses (expected ~8)': len(self.warehouses) >= 7 and len(self.warehouses) <= 9,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                all_passed = False
        
        self.results['record_counts'] = all_passed
        return all_passed
    
    def check_column_completeness(self):
        """Check if all required columns exist."""
        print("\n" + "="*60)
        print("COLUMN COMPLETENESS VALIDATION")
        print("="*60)
        
        required_columns = {
            'orders': ['order_id', 'order_date', 'customer_id', 'product_id', 'supplier_id', 
                      'warehouse_id', 'quantity_ordered', 'quantity_delivered', 'unit_cost',
                      'promised_date', 'delivery_date', 'quality_score', 'handling_cost'],
            'inventory': ['date', 'product_id', 'warehouse_id', 'inventory_on_hand',
                         'inventory_in_transit', 'safety_stock', 'reorder_point'],
            'shipping': ['shipment_id', 'order_id', 'ship_date', 'delivery_date',
                        'origin_warehouse', 'destination_region', 'shipping_mode',
                        'weight_kg', 'total_cost'],
            'products': ['product_id', 'product_name', 'category', 'base_cost'],
            'suppliers': ['supplier_id', 'supplier_name', 'region', 'lead_time_days'],
            'warehouses': ['warehouse_id', 'warehouse_name', 'region', 'capacity_units']
        }
        
        all_passed = True
        for table, required_cols in required_columns.items():
            df = getattr(self, table)
            missing = set(required_cols) - set(df.columns)
            
            if missing:
                print(f"  ✗ FAIL: {table} - Missing columns: {missing}")
                all_passed = False
            else:
                print(f"  ✓ PASS: {table} - All required columns present")
        
        self.results['column_completeness'] = all_passed
        return all_passed
    
    def check_null_values(self):
        """Check for unexpected null values."""
        print("\n" + "="*60)
        print("NULL VALUE VALIDATION")
        print("="*60)
        
        critical_columns = {
            'orders': ['order_id', 'order_date', 'product_id', 'quantity_ordered', 'quantity_delivered'],
            'inventory': ['date', 'product_id', 'warehouse_id', 'inventory_on_hand'],
            'shipping': ['shipment_id', 'order_id', 'total_cost', 'weight_kg']
        }
        
        all_passed = True
        for table, cols in critical_columns.items():
            df = getattr(self, table)
            has_nulls = False
            
            for col in cols:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    print(f"  ✗ FAIL: {table}.{col} has {null_count} null values")
                    has_nulls = True
                    all_passed = False
            
            if not has_nulls:
                print(f"  ✓ PASS: {table} - No nulls in critical columns")
        
        self.results['null_values'] = all_passed
        return all_passed
    
    def check_data_patterns(self):
        """Check if data follows expected patterns."""
        print("\n" + "="*60)
        print("DATA PATTERN VALIDATION")
        print("="*60)
        
        all_passed = True
        
        # Check delivery delays (~5%)
        late_orders = (self.orders['delivery_date'] > self.orders['promised_date']).sum()
        late_pct = late_orders / len(self.orders) * 100
        delay_check = 3 <= late_pct <= 7  # Allow some variance
        print(f"  {'✓' if delay_check else '✗'} Delivery delay rate: {late_pct:.1f}% (expected ~5%)")
        if not delay_check:
            all_passed = False
        
        # Check incomplete deliveries (~3%)
        incomplete = (self.orders['quantity_delivered'] < self.orders['quantity_ordered']).sum()
        incomplete_pct = incomplete / len(self.orders) * 100
        incomplete_check = 1 <= incomplete_pct <= 5
        print(f"  {'✓' if incomplete_check else '✗'} Incomplete delivery rate: {incomplete_pct:.1f}% (expected ~3%)")
        if not incomplete_check:
            all_passed = False
        
        # Check date ranges
        order_min = self.orders['order_date'].min()
        order_max = self.orders['order_date'].max()
        date_range_check = order_min.year == 2023 and order_max.year == 2024
        print(f"  {'✓' if date_range_check else '✗'} Order date range: {order_min.date()} to {order_max.date()}")
        if not date_range_check:
            all_passed = False
        
        # Check positive values
        negative_costs = (self.orders['unit_cost'] < 0).sum() + (self.shipping['total_cost'] < 0).sum()
        cost_check = negative_costs == 0
        print(f"  {'✓' if cost_check else '✗'} No negative costs found")
        if not cost_check:
            all_passed = False
        
        # Check quantity logic
        over_delivered = (self.orders['quantity_delivered'] > self.orders['quantity_ordered'] * 1.1).sum()
        qty_check = over_delivered == 0
        print(f"  {'✓' if qty_check else '✗'} No unrealistic over-deliveries")
        if not qty_check:
            all_passed = False
        
        self.results['data_patterns'] = all_passed
        return all_passed
    
    def check_seasonality(self):
        """Check for Q4 seasonality pattern."""
        print("\n" + "="*60)
        print("SEASONALITY VALIDATION")
        print("="*60)
        
        # Group orders by quarter
        self.orders['quarter'] = self.orders['order_date'].dt.quarter
        
        q1_avg = self.orders[self.orders['quarter'] == 1]['order_id'].count()
        q4_avg = self.orders[self.orders['quarter'] == 4]['order_id'].count()
        
        # Q4 should have more orders than Q1
        seasonality_check = q4_avg > q1_avg * 1.3  # At least 30% more
        print(f"  Q1 orders: {q1_avg}, Q4 orders: {q4_avg}")
        print(f"  {'✓' if seasonality_check else '✗'} Q4 peak detected (Q4 > Q1 * 1.3)")
        
        self.results['seasonality'] = seasonality_check
        return seasonality_check
    
    def check_referential_integrity(self):
        """Check foreign key relationships."""
        print("\n" + "="*60)
        print("REFERENTIAL INTEGRITY VALIDATION")
        print("="*60)
        
        all_passed = True
        
        # Check product references
        order_products = set(self.orders['product_id'].unique())
        valid_products = set(self.products['product_id'].unique())
        invalid_products = order_products - valid_products
        product_check = len(invalid_products) == 0
        print(f"  {'✓' if product_check else '✗'} All order products exist in product master")
        if not product_check:
            all_passed = False
        
        # Check supplier references
        order_suppliers = set(self.orders['supplier_id'].unique())
        valid_suppliers = set(self.suppliers['supplier_id'].unique())
        invalid_suppliers = order_suppliers - valid_suppliers
        supplier_check = len(invalid_suppliers) == 0
        print(f"  {'✓' if supplier_check else '✗'} All order suppliers exist in supplier master")
        if not supplier_check:
            all_passed = False
        
        # Check warehouse references
        order_warehouses = set(self.orders['warehouse_id'].unique())
        valid_warehouses = set(self.warehouses['warehouse_id'].unique())
        invalid_warehouses = order_warehouses - valid_warehouses
        warehouse_check = len(invalid_warehouses) == 0
        print(f"  {'✓' if warehouse_check else '✗'} All order warehouses exist in warehouse master")
        if not warehouse_check:
            all_passed = False
        
        self.results['referential_integrity'] = all_passed
        return all_passed
    
    def run_all_checks(self):
        """Run all validation checks."""
        print("\n" + "="*60)
        print("DATA QUALITY VALIDATION REPORT")
        print("="*60)
        
        self.load_data()
        
        results = [
            self.check_record_counts(),
            self.check_column_completeness(),
            self.check_null_values(),
            self.check_data_patterns(),
            self.check_seasonality(),
            self.check_referential_integrity()
        ]
        
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        all_passed = all(results)
        
        if all_passed:
            print("\n✅ ALL VALIDATION CHECKS PASSED!")
            print("Data is ready for analytics and dashboard generation.")
        else:
            print("\n⚠️ SOME VALIDATION CHECKS FAILED")
            print("Please review the failures above and regenerate data if needed.")
        
        return all_passed


def main():
    """Main function to run data quality checks."""
    checker = DataQualityChecker()
    passed = checker.run_all_checks()
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
