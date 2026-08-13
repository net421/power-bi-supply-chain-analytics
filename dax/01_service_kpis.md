# Service KPIs

```dax
OTIF % = DIVIDE(COUNTROWS(FILTER(fact_orders, fact_orders[delivery_date] <= fact_orders[promised_date] && fact_orders[quantity_delivered] >= fact_orders[quantity_ordered])), COUNTROWS(fact_orders), 0)

Fill Rate % = DIVIDE(SUM(fact_orders[quantity_delivered]), SUM(fact_orders[quantity_ordered]), 0)

On-Time Delivery % = DIVIDE(COUNTROWS(FILTER(fact_orders, fact_orders[delivery_date] <= fact_orders[promised_date])), COUNTROWS(fact_orders), 0)

Perfect Order % = DIVIDE(COUNTROWS(FILTER(fact_orders, fact_orders[delivery_date] <= fact_orders[promised_date] && fact_orders[quantity_delivered] >= fact_orders[quantity_ordered] && fact_orders[quality_score] >= 0.95)), COUNTROWS(fact_orders), 0)
```
