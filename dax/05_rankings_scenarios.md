# Rankings & Scenarios

```dax
Supplier Rank = RANKX(ALL(dim_supplier), CALCULATE([OTIF %]), , DESC, DENSE)

Top 5 Suppliers OTIF = CALCULATE([OTIF %], FILTER(ALL(dim_supplier), [Supplier Rank] <= 5))

OTIF Impact Scenario = VAR reduction = SELECTEDVALUE('Scenario'[Lead Time Reduction Days], 0) VAR adjusted = FILTER(ADDCOLUMNS(fact_orders, "Adjusted Delivery", fact_orders[delivery_date] - reduction), [Adjusted Delivery] <= fact_orders[promised_date]) RETURN DIVIDE(COUNTROWS(adjusted), COUNTROWS(fact_orders), 0)
```
