# Inventory KPIs

```dax
Inventory Turns = DIVIDE(SUM(fact_orders[quantity_delivered]), AVERAGE(fact_inventory[quantity_on_hand]), 0)

Days of Supply = DIVIDE(AVERAGE(fact_inventory[quantity_on_hand]), DIVIDE(SUM(fact_orders[quantity_delivered]), 365, 0), 0)

Inventory Risk Score = VAR dos = [Days of Supply] RETURN SWITCH(TRUE(), dos < 15, "Critical - Stockout Risk", dos < 24, "Warning - Low Stock", dos <= 36, "Optimal", dos <= 45, "Elevated - Overstock", "Critical - Overstock")

Stockout Frequency % = DIVIDE(COUNTROWS(FILTER(fact_inventory, fact_inventory[quantity_on_hand] = 0)), COUNTROWS(fact_inventory), 0)
```
