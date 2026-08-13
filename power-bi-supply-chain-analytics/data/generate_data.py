"""
Supply Chain Data Generator

Generates synthetic supply chain data with realistic patterns:
- Seasonality (Q4 peaks)
- 5% annual growth trend
- 5% delivery delays
- 3% incomplete deliveries
- Realistic cost variability
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
NUM_ORDERS = 10000
NUM_INVENTORY_RECORDS = 24000
NUM_SHIPMENTS = 8500
NUM_SUPPLIERS = 50
NUM_PRODUCTS = 500
NUM_WAREHOUSES = 8

# Date range: 2 years of data
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)
DATE_RANGE = pd.date_range(start=START_DATE, end=END_DATE, freq='D')


def generate_suppliers(n_suppliers=NUM_SUPPLIERS):
    """Generate supplier master data."""
    supplier_ids = [f"SUP_{str(i).zfill(3)}" for i in range(1, n_suppliers + 1)]
    
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    categories = ['Raw Materials', 'Components', 'Packaging', 'Finished Goods']
    
    suppliers = pd.DataFrame({
        'supplier_id': supplier_ids,
        'supplier_name': [f"Supplier {i}" for i in range(1, n_suppliers + 1)],
        'region': np.random.choice(regions, n_suppliers),
        'category': np.random.choice(categories, n_suppliers),
        'lead_time_days': np.random.randint(5, 30, n_suppliers),
        'reliability_score': np.random.uniform(0.7, 0.99, n_suppliers).round(3),
        'contract_start_date': pd.to_datetime(np.random.choice(DATE_RANGE[:-365], n_suppliers)),
        'payment_terms_days': np.random.choice([30, 45, 60, 90], n_suppliers),
        'min_order_quantity': np.random.randint(10, 500, n_suppliers),
        'quality_certification': np.random.choice(['ISO9001', 'ISO14001', 'Six Sigma', 'None'], n_suppliers),
    })
    
    return suppliers


def generate_products(n_products=NUM_PRODUCTS, n_suppliers=NUM_SUPPLIERS):
    """Generate product master data."""
    product_ids = [f"PRD_{str(i).zfill(4)}" for i in range(1, n_products + 1)]
    
    categories = ['Electronics', 'Machinery', 'Consumer Goods', 'Industrial', 'Automotive']
    subcategories = ['Standard', 'Premium', 'Economy', 'Custom']
    uoms = ['units', 'kg', 'liters', 'boxes', 'pallets']
    
    products = pd.DataFrame({
        'product_id': product_ids,
        'product_name': [f"Product {i}" for i in range(1, n_products + 1)],
        'category': np.random.choice(categories, n_products),
        'subcategory': np.random.choice(subcategories, n_products),
        'uom': np.random.choice(uoms, n_products),
        'unit_weight_kg': np.random.uniform(0.1, 50, n_products).round(2),
        'unit_volume_m3': np.random.uniform(0.001, 2, n_products).round(3),
        'base_cost': np.random.uniform(10, 500, n_products).round(2),
        'selling_price': np.random.uniform(20, 1000, n_products).round(2),
        'reorder_point': np.random.randint(50, 500, n_products),
        'safety_stock': np.random.randint(20, 200, n_products),
        'shelf_life_days': np.random.choice([30, 60, 90, 180, 365, -1], n_products),  # -1 = no expiry
        'hazardous': np.random.choice([True, False], n_products, p=[0.1, 0.9]),
        'supplier_id': np.random.choice([f"SUP_{str(i).zfill(3)}" for i in range(1, n_suppliers + 1)], n_products),
    })
    
    return products


def generate_warehouses(n_warehouses=NUM_WAREHOUSES):
    """Generate warehouse master data."""
    warehouse_ids = [f"WH_{str(i).zfill(2)}" for i in range(1, n_warehouses + 1)]
    
    regions = ['North', 'South', 'East', 'West', 'Central']
    types = ['Distribution Center', 'Fulfillment Center', 'Cold Storage', 'Cross-dock']
    
    warehouses = pd.DataFrame({
        'warehouse_id': warehouse_ids,
        'warehouse_name': [f"Warehouse {chr(65+i)}" for i in range(n_warehouses)],
        'region': np.random.choice(regions, n_warehouses),
        'type': np.random.choice(types, n_warehouses),
        'capacity_units': np.random.randint(10000, 100000, n_warehouses),
        'latitude': np.random.uniform(25, 48, n_warehouses).round(4),
        'longitude': np.random.uniform(-125, -70, n_warehouses).round(4),
        'operating_cost_daily': np.random.uniform(5000, 20000, n_warehouses).round(2),
        'automation_level': np.random.choice(['High', 'Medium', 'Low'], n_warehouses),
        'open_date': pd.to_datetime(np.random.choice(DATE_RANGE[:-730], n_warehouses)),
    })
    
    return warehouses


def generate_orders(n_orders=NUM_ORDERS, 
                    n_products=NUM_PRODUCTS, 
                    n_suppliers=NUM_SUPPLIERS,
                    n_warehouses=NUM_WAREHOUSES):
    """
    Generate order data with realistic patterns:
    - Seasonality (Q4 peaks)
    - 5% delivery delays
    - 3% incomplete deliveries
    """
    product_ids = [f"PRD_{str(i).zfill(4)}" for i in range(1, n_products + 1)]
    supplier_ids = [f"SUP_{str(i).zfill(3)}" for i in range(1, n_suppliers + 1)]
    warehouse_ids = [f"WH_{str(i).zfill(2)}" for i in range(1, n_warehouses + 1)]
    customer_ids = [f"CUST_{str(i).zfill(4)}" for i in range(1, 1001)]
    
    # Generate order dates with seasonality and trend
    base_dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    
    # Create weighted probability for order dates (higher in Q4)
    weights = []
    for date in base_dates:
        weight = 1.0
        # Q4 peak (Oct-Dec)
        if date.month in [10, 11, 12]:
            weight = 1.5
        # Q1 dip (Jan-Feb)
        elif date.month in [1, 2]:
            weight = 0.8
        # 5% annual growth trend
        if date.year == 2024:
            weight *= 1.05
        
        weights.append(weight)
    
    weights = np.array(weights) / sum(weights)
    
    # Sample order dates
    order_dates = np.random.choice(base_dates, size=n_orders, p=weights)
    order_dates = pd.to_datetime(order_dates)
    
    orders = []
    for i in range(n_orders):
        order_id = f"ORD_{str(i+1).zfill(6)}"
        order_date = order_dates[i]
        
        product_id = np.random.choice(product_ids)
        supplier_id = np.random.choice(supplier_ids)
        warehouse_id = np.random.choice(warehouse_ids)
        customer_id = np.random.choice(customer_ids)
        
        quantity_ordered = np.random.randint(1, 100)
        
        # 3% incomplete deliveries
        if np.random.random() < 0.03:
            quantity_delivered = int(quantity_ordered * np.random.uniform(0.5, 0.95))
        else:
            quantity_delivered = quantity_ordered
        
        # Base cost with variability
        unit_cost = round(np.random.uniform(10, 500) * np.random.uniform(0.9, 1.1), 2)
        handling_cost = round(unit_cost * 0.05 * np.random.uniform(0.8, 1.2), 2)
        
        # Lead time based on supplier reliability
        base_lead_time = np.random.randint(3, 14)
        
        # Promised date
        promised_date = order_date + timedelta(days=base_lead_time)
        
        # 5% delivery delays
        if np.random.random() < 0.05:
            delay_days = np.random.randint(1, 10)
            delivery_date = promised_date + timedelta(days=delay_days)
        else:
            # Some early deliveries
            if np.random.random() < 0.2:
                early_days = np.random.randint(0, 3)
                delivery_date = promised_date - timedelta(days=early_days)
            else:
                delivery_date = promised_date
        
        # Quality score (higher for on-time, full deliveries)
        if delivery_date <= promised_date and quantity_delivered == quantity_ordered:
            quality_score = round(np.random.uniform(0.85, 1.0), 2)
        else:
            quality_score = round(np.random.uniform(0.6, 0.9), 2)
        
        orders.append({
            'order_id': order_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'customer_id': customer_id,
            'product_id': product_id,
            'supplier_id': supplier_id,
            'warehouse_id': warehouse_id,
            'quantity_ordered': quantity_ordered,
            'quantity_delivered': quantity_delivered,
            'unit_cost': unit_cost,
            'promised_date': promised_date.strftime('%Y-%m-%d'),
            'delivery_date': delivery_date.strftime('%Y-%m-%d'),
            'quality_score': quality_score,
            'handling_cost': handling_cost,
        })
    
    return pd.DataFrame(orders)


def generate_inventory(n_records=NUM_INVENTORY_RECORDS,
                       n_products=NUM_PRODUCTS,
                       n_warehouses=NUM_WAREHOUSES):
    """Generate daily inventory levels."""
    product_ids = [f"PRD_{str(i).zfill(4)}" for i in range(1, n_products + 1)]
    warehouse_ids = [f"WH_{str(i).zfill(2)}" for i in range(1, n_warehouses + 1)]
    
    # Generate combinations of products and warehouses
    combinations = []
    for wh in warehouse_ids:
        for prod in product_ids[:n_products // n_warehouses]:  # Distribute products across warehouses
            combinations.append((prod, wh))
    
    # Calculate records per combination
    records_per_combo = n_records // len(combinations)
    
    inventory_records = []
    for product_id, warehouse_id in combinations:
        # Random start date for each combination
        start_idx = np.random.randint(0, len(DATE_RANGE) - records_per_combo)
        dates = DATE_RANGE[start_idx:start_idx + records_per_combo]
        
        # Base inventory level
        base_level = np.random.randint(100, 1000)
        
        for date in dates:
            # Add some randomness and trends
            seasonal_factor = 1.0
            if date.month in [10, 11, 12]:
                seasonal_factor = 0.7  # Lower inventory due to high sales
            elif date.month in [1, 2]:
                seasonal_factor = 1.3  # Higher inventory after holidays
            
            noise = np.random.normal(0, base_level * 0.1)
            inventory_on_hand = max(0, int(base_level * seasonal_factor + noise))
            
            # Inventory in transit
            inventory_in_transit = np.random.randint(0, base_level // 2)
            
            # Safety stock
            safety_stock = np.random.randint(20, 200)
            
            # Reorder point
            reorder_point = safety_stock + np.random.randint(50, 300)
            
            inventory_records.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product_id,
                'warehouse_id': warehouse_id,
                'inventory_on_hand': inventory_on_hand,
                'inventory_in_transit': inventory_in_transit,
                'safety_stock': safety_stock,
                'reorder_point': reorder_point,
                'last_replenishment_date': (date - timedelta(days=np.random.randint(1, 30))).strftime('%Y-%m-%d'),
                'next_expected_delivery': (date + timedelta(days=np.random.randint(1, 14))).strftime('%Y-%m-%d'),
            })
    
    return pd.DataFrame(inventory_records)


def generate_shipping_costs(n_shipments=NUM_SHIPMENTS,
                            n_warehouses=NUM_WAREHOUSES):
    """Generate shipping cost data."""
    warehouse_ids = [f"WH_{str(i).zfill(2)}" for i in range(1, n_warehouses + 1)]
    
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    modes = ['Air', 'Ocean', 'Road', 'Rail', 'Express']
    service_levels = ['Standard', 'Expedited', 'Same Day', 'Next Day']
    
    shipments = []
    for i in range(n_shipments):
        shipment_id = f"SHP_{str(i+1).zfill(6)}"
        
        # Weight affects cost
        weight_kg = np.random.uniform(1, 5000)
        distance_km = np.random.uniform(100, 10000)
        
        mode = np.random.choice(modes, p=[0.15, 0.25, 0.35, 0.15, 0.10])
        
        # Cost calculation based on mode, weight, and distance
        base_rate_per_kg_km = {
            'Air': 0.005,
            'Ocean': 0.0005,
            'Road': 0.001,
            'Rail': 0.0008,
            'Express': 0.01
        }
        
        base_cost = base_rate_per_kg_km[mode] * weight_kg * distance_km
        
        # Add fuel surcharge and other fees
        fuel_surcharge = base_cost * np.random.uniform(0.1, 0.25)
        handling_fee = np.random.uniform(10, 100)
        insurance = base_cost * np.random.uniform(0.01, 0.03)
        
        total_cost = base_cost + fuel_surcharge + handling_fee + insurance
        
        ship_date = pd.to_datetime(np.random.choice(DATE_RANGE))
        delivery_date = ship_date + timedelta(days=np.random.randint(1, 30))
        
        shipments.append({
            'shipment_id': shipment_id,
            'order_id': f"ORD_{str(np.random.randint(1, NUM_ORDERS+1)).zfill(6)}",
            'ship_date': ship_date.strftime('%Y-%m-%d'),
            'delivery_date': delivery_date.strftime('%Y-%m-%d'),
            'origin_warehouse': np.random.choice(warehouse_ids),
            'destination_region': np.random.choice(regions),
            'shipping_mode': mode,
            'service_level': np.random.choice(service_levels),
            'weight_kg': round(weight_kg, 2),
            'distance_km': round(distance_km, 2),
            'base_freight_cost': round(base_cost, 2),
            'fuel_surcharge': round(fuel_surcharge, 2),
            'handling_fee': round(handling_fee, 2),
            'insurance_cost': round(insurance, 2),
            'total_cost': round(total_cost, 2),
            'carrier': np.random.choice(['FedEx', 'UPS', 'DHL', 'Maersk', 'Local Carrier']),
            'tracking_number': f"TRK{np.random.randint(100000000, 999999999)}",
            'on_time': np.random.choice([True, False], p=[0.92, 0.08]),
        })
    
    return pd.DataFrame(shipments)


def main():
    """Main function to generate all datasets."""
    print("Starting data generation...")
    
    # Create output directory
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate master data
    print("Generating suppliers...")
    suppliers = generate_suppliers()
    suppliers.to_csv(os.path.join(output_dir, 'suppliers.csv'), index=False)
    print(f"  Created {len(suppliers)} suppliers")
    
    print("Generating products...")
    products = generate_products()
    products.to_csv(os.path.join(output_dir, 'products.csv'), index=False)
    print(f"  Created {len(products)} products")
    
    print("Generating warehouses...")
    warehouses = generate_warehouses()
    warehouses.to_csv(os.path.join(output_dir, 'warehouses.csv'), index=False)
    print(f"  Created {len(warehouses)} warehouses")
    
    # Generate transactional data
    print("Generating orders...")
    orders = generate_orders()
    orders.to_csv(os.path.join(output_dir, 'supply_chain_orders.csv'), index=False)
    print(f"  Created {len(orders)} orders")
    
    print("Generating inventory levels...")
    inventory = generate_inventory()
    inventory.to_csv(os.path.join(output_dir, 'inventory_levels.csv'), index=False)
    print(f"  Created {len(inventory)} inventory records")
    
    print("Generating shipping costs...")
    shipping = generate_shipping_costs()
    shipping.to_csv(os.path.join(output_dir, 'shipping_costs.csv'), index=False)
    print(f"  Created {len(shipping)} shipments")
    
    print("\nData generation complete!")
    print(f"Output directory: {output_dir}")
    
    # Print summary statistics
    print("\n=== Data Summary ===")
    print(f"Orders date range: {orders['order_date'].min()} to {orders['order_date'].max()}")
    print(f"OTIF Rate: {(orders['delivery_date'] <= orders['promised_date']) & (orders['quantity_delivered'] >= orders['quantity_ordered'])}")
    otif = ((orders['delivery_date'] <= orders['promised_date']) & 
            (orders['quantity_delivered'] >= orders['quantity_ordered'])).mean()
    print(f"  OTIF: {otif:.2%}")
    
    delay_rate = (orders['delivery_date'] > orders['promised_date']).mean()
    print(f"  Delay Rate: {delay_rate:.2%}")
    
    incomplete_rate = (orders['quantity_delivered'] < orders['quantity_ordered']).mean()
    print(f"  Incomplete Delivery Rate: {incomplete_rate:.2%}")


if __name__ == "__main__":
    main()
