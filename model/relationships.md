# Star Schema Relationships

| Dimension | Fact | Cardinality | Key |
|---|---|---|---|
| dim_date | fact_orders | 1:* | date_key → order_date |
| dim_product | fact_orders | 1:* | product_key → product_id |
| dim_supplier | fact_orders | 1:* | supplier_key → supplier_id |
| dim_warehouse | fact_orders | 1:* | warehouse_key → warehouse_id |
| dim_date | fact_inventory | 1:* | date_key |
| dim_product | fact_inventory | 1:* | product_key |
| dim_warehouse | fact_inventory | 1:* | warehouse_key |
| dim_date | fact_shipping | 1:* | date_key |
| dim_warehouse | fact_shipping | 1:* role-playing origin/destination |
| dim_shipping_mode | fact_shipping | 1:* | mode_key |

Use single-direction relationships from dimensions to facts. Keep the two warehouse relationships role-playing/inactive as appropriate for the shipping analysis and activate them with `USERELATIONSHIP` where needed.
