# Cost KPIs

```dax
Cost to Serve = DIVIDE(SUM(fact_shipping[freight_cost]) + SUM(fact_orders[handling_cost]), DISTINCTCOUNT(fact_orders[order_id]), 0)

Freight Cost per Kg = DIVIDE(SUM(fact_shipping[freight_cost]), SUM(fact_shipping[weight_kg]), 0)

Cost to Serve by Mode = CALCULATE([Cost to Serve], ALLEXCEPT(dim_shipping_mode, dim_shipping_mode[mode_name]))

Freight Budget Variance % = VAR actual = SUM(fact_shipping[freight_cost]) VAR budget = SUM(fact_shipping[budgeted_cost]) RETURN DIVIDE(actual - budget, budget, 0)
```
