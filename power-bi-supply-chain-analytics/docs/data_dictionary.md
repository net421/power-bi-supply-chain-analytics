# Data Dictionary

## Overview
This document defines all data entities, columns, and relationships in the Supply Chain Analytics dataset.

---

## Master Data Tables

### suppliers.csv (50 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| supplier_id | String | Unique supplier identifier | SUP_001 |
| supplier_name | String | Supplier company name | Supplier 1 |
| region | String | Geographic region | North America |
| category | String | Supplier category | Raw Materials |
| lead_time_days | Integer | Standard lead time in days | 14 |
| reliability_score | Float | Historical reliability (0-1) | 0.95 |
| contract_start_date | Date | Contract start date | 2023-01-15 |
| payment_terms_days | Integer | Payment terms in days | 30 |
| min_order_quantity | Integer | Minimum order quantity | 100 |
| quality_certification | String | Quality certifications | ISO9001 |

### products.csv (500 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| product_id | String | Unique product identifier | PRD_0001 |
| product_name | String | Product name | Product 1 |
| category | String | Product category | Electronics |
| subcategory | String | Product subcategory | Standard |
| uom | String | Unit of measure | units |
| unit_weight_kg | Float | Weight per unit in kg | 2.5 |
| unit_volume_m3 | Float | Volume per unit in m³ | 0.01 |
| base_cost | Float | Base cost per unit | 150.00 |
| selling_price | Float | Selling price per unit | 299.99 |
| reorder_point | Integer | Reorder point quantity | 200 |
| safety_stock | Integer | Safety stock level | 100 |
| shelf_life_days | Integer | Shelf life (-1 = none) | 365 |
| hazardous | Boolean | Hazardous material flag | False |
| supplier_id | String | Primary supplier FK | SUP_001 |

### warehouses.csv (8 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| warehouse_id | String | Unique warehouse identifier | WH_01 |
| warehouse_name | String | Warehouse name | Warehouse A |
| region | String | Geographic region | North |
| type | String | Facility type | Distribution Center |
| capacity_units | Integer | Storage capacity | 50000 |
| latitude | Float | GPS latitude | 40.7128 |
| longitude | Float | GPS longitude | -74.0060 |
| operating_cost_daily | Float | Daily operating cost | 12500.00 |
| automation_level | String | Automation level | High |
| open_date | Date | Facility opening date | 2022-06-01 |

---

## Transactional Tables

### supply_chain_orders.csv (10,000 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| order_id | String | Unique order identifier | ORD_000001 |
| order_date | Date | Order placement date | 2024-03-15 |
| customer_id | String | Customer identifier | CUST_0123 |
| product_id | String | Product FK | PRD_0001 |
| supplier_id | String | Supplier FK | SUP_001 |
| warehouse_id | String | Fulfillment warehouse FK | WH_01 |
| quantity_ordered | Integer | Quantity ordered | 50 |
| quantity_delivered | Integer | Quantity delivered | 50 |
| unit_cost | Float | Cost per unit | 150.00 |
| promised_date | Date | Promised delivery date | 2024-03-25 |
| delivery_date | Date | Actual delivery date | 2024-03-24 |
| quality_score | Float | Quality score (0-1) | 0.95 |
| handling_cost | Float | Handling cost | 7.50 |

**Key Metrics Derived:**
- OTIF: delivery_date <= promised_date AND quantity_delivered >= quantity_ordered
- On-Time: delivery_date <= promised_date
- In-Full: quantity_delivered >= quantity_ordered
- Perfect Order: OTIF AND quality_score >= 0.95

### inventory_levels.csv (24,000 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | Date | Inventory snapshot date | 2024-03-15 |
| product_id | String | Product FK | PRD_0001 |
| warehouse_id | String | Warehouse FK | WH_01 |
| inventory_on_hand | Integer | Current stock level | 450 |
| inventory_in_transit | Integer | Stock in transit | 100 |
| safety_stock | Integer | Safety stock target | 100 |
| reorder_point | Integer | Reorder trigger point | 250 |
| last_replenishment_date | Date | Last restock date | 2024-03-01 |
| next_expected_delivery | Date | Next expected delivery | 2024-03-20 |

**Key Metrics Derived:**
- Days of Supply: inventory_on_hand / avg_daily_demand
- Stockout: inventory_on_hand = 0
- Risk Level: Based on vs safety_stock and reorder_point

### shipping_costs.csv (8,500 records)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| shipment_id | String | Unique shipment identifier | SHP_000001 |
| order_id | String | Related order FK | ORD_000001 |
| ship_date | Date | Shipment dispatch date | 2024-03-16 |
| delivery_date | Date | Delivery completion date | 2024-03-24 |
| origin_warehouse | String | Origin warehouse FK | WH_01 |
| destination_region | String | Destination region | Europe |
| shipping_mode | String | Transport mode | Air |
| service_level | String | Service level | Standard |
| weight_kg | Float | Shipment weight in kg | 125.5 |
| distance_km | Float | Distance in kilometers | 5500 |
| base_freight_cost | Float | Base freight charge | 312.50 |
| fuel_surcharge | Float | Fuel surcharge | 62.50 |
| handling_fee | Float | Handling fee | 25.00 |
| insurance_cost | Float | Insurance premium | 9.38 |
| total_cost | Float | Total shipping cost | 409.38 |
| carrier | String | Shipping carrier | FedEx |
| tracking_number | String | Tracking reference | TRK123456789 |
| on_time | Boolean | Delivered on time | True |

---

## Relationships

```
suppliers (supplier_id) ──┬── orders (supplier_id)
                          │
products (product_id) ────┼── orders (product_id)
                          │
warehouses (warehouse_id) ─┴── orders (warehouse_id)
                          │
                          ├── inventory_levels (warehouse_id, product_id)
                          │
                          └── shipping_costs (origin_warehouse)

orders (order_id) ────────┬── shipping_costs (order_id)
                          │
customers (customer_id) ──┴── orders (customer_id)
```

---

## Data Generation Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| NUM_ORDERS | 10,000 | Total orders generated |
| NUM_INVENTORY_RECORDS | 24,000 | Daily inventory snapshots |
| NUM_SHIPMENTS | 8,500 | Total shipments |
| NUM_SUPPLIERS | 50 | Unique suppliers |
| NUM_PRODUCTS | 500 | Unique products |
| NUM_WAREHOUSES | 8 | Distribution centers |
| DATE_RANGE | 2023-01-01 to 2024-12-31 | Two years of data |
| DELAY_RATE | ~5% | Late deliveries |
| INCOMPLETE_RATE | ~3% | Partial shipments |
| Q4_PEAK_MULTIPLIER | 1.5x | Seasonal demand increase |
| ANNUAL_GROWTH | 5% | Year-over-year growth |

---

## Data Quality Rules

1. **Referential Integrity**: All foreign keys must reference valid master records
2. **Date Logic**: order_date <= promised_date <= delivery_date
3. **Quantity Logic**: quantity_delivered <= quantity_ordered (with exceptions for over-delivery)
4. **Positive Values**: All costs, weights, and quantities must be positive
5. **No Nulls**: Critical fields cannot be null
