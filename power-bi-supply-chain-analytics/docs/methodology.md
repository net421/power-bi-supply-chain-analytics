# Methodology

## KPI Calculation Methodology

This document describes the calculation methodology for all 20 supply chain KPIs implemented in this project.

---

## Service KPIs

### 1. OTIF % (On Time In Full)

**Definition**: Percentage of orders delivered on or before the promised date AND with complete quantity.

**Formula**:
```
OTIF % = (Count of On-Time & In-Full Orders / Total Orders) × 100
```

**Business Logic**:
- On-Time: delivery_date ≤ promised_date
- In-Full: quantity_delivered ≥ quantity_ordered
- Both conditions must be true for OTIF

**Target**: ≥ 90%

---

### 2. Fill Rate %

**Definition**: Percentage of ordered quantity that was successfully delivered.

**Formula**:
```
Fill Rate % = (Total Quantity Delivered / Total Quantity Ordered) × 100
```

**Business Logic**:
- Aggregates across all orders
- Can exceed 100% if over-deliveries occur

**Target**: ≥ 95%

---

### 3. On-Time Delivery %

**Definition**: Percentage of orders delivered on or before the promised date.

**Formula**:
```
On-Time Delivery % = (Count of On-Time Orders / Total Orders) × 100
```

**Business Logic**:
- Only considers delivery timing, not quantity
- Always ≥ OTIF % (less restrictive)

**Target**: ≥ 92%

---

### 4. Perfect Order %

**Definition**: Percentage of orders that are on-time, in-full, AND have high quality score.

**Formula**:
```
Perfect Order % = (Count of Perfect Orders / Total Orders) × 100
```

**Business Logic**:
- On-Time: delivery_date ≤ promised_date
- In-Full: quantity_delivered ≥ quantity_ordered
- High Quality: quality_score ≥ 0.95
- All three conditions must be true

**Target**: ≥ 85%

---

## Inventory KPIs

### 5. Inventory Turns

**Definition**: Number of times inventory is sold and replaced over a period.

**Formula**:
```
Inventory Turns = Annual COGS / Average Inventory Value
```

**Business Logic**:
- COGS approximated as quantity_ordered × unit_cost
- Annualized if period < 365 days
- Higher turns indicate efficient inventory management

**Target**: Industry-dependent (typically 6-12x)

---

### 6. Days of Supply

**Definition**: Average number of days current inventory will last based on demand rate.

**Formula**:
```
Days of Supply = Average Inventory On-Hand / Average Daily Demand
```

**Business Logic**:
- Lower values risk stockouts
- Higher values tie up capital
- Optimal range typically 30-60 days

**Target**: 30-60 days

---

### 7. Inventory Risk Score

**Definition**: Categorical risk assessment based on inventory levels vs targets.

**Categories**:
- **Critical**: inventory_on_hand < safety_stock
- **Warning**: safety_stock ≤ inventory_on_hand < reorder_point
- **Optimal**: reorder_point ≤ inventory_on_hand ≤ 2× reorder_point
- **Elevated**: inventory_on_hand > 2× reorder_point

**Business Logic**:
- Helps prioritize replenishment actions
- Critical items need immediate attention

---

### 8. Stockout Frequency %

**Definition**: Percentage of inventory records showing zero stock.

**Formula**:
```
Stockout Frequency % = (Count of Zero Stock Records / Total Records) × 100
```

**Business Logic**:
- Measures inventory availability
- Lower is better

**Target**: < 2%

---

## Cost KPIs

### 9. Cost to Serve per Order

**Definition**: Average total cost to fulfill one customer order.

**Formula**:
```
Cost to Serve/Order = (Product Costs + Handling Costs + Shipping Costs) / Total Orders
```

**Business Logic**:
- Includes all fulfillment costs
- Used for profitability analysis

**Target**: Minimize while maintaining service levels

---

### 10. Freight Cost per Kg

**Definition**: Average shipping cost per kilogram of product.

**Formula**:
```
Freight Cost/Kg = Total Freight Cost / Total Weight Shipped
```

**Business Logic**:
- Efficiency metric for logistics
- Varies by shipping mode

**Target**: Minimize through mode optimization

---

### 11. Cost to Serve by Shipping Mode

**Definition**: Total cost breakdown by transportation method.

**Formula**:
```
Cost by Mode = SUM(total_cost) GROUP BY shipping_mode
```

**Business Logic**:
- Identifies cost drivers
- Supports mode selection decisions

---

### 12. Freight Budget Variance %

**Definition**: Difference between actual and budgeted freight costs.

**Formula**:
```
Budget Variance % = ((Actual Cost - Budget) / Budget) × 100
```

**Business Logic**:
- Positive = Over budget
- Negative = Under budget
- Acceptable range: ±5%

**Target**: Within ±5% of budget

---

## Time Intelligence KPIs

### 13. OTIF % YTD (Year-to-Date)

**Definition**: OTIF calculated from start of current year to current date.

**Formula**:
```
OTIF YTD = OTIF for orders where order_date >= Jan 1 of current year
```

**Business Logic**:
- Tracks annual performance
- Resets each calendar year

---

### 14. OTIF % PY (Prior Year)

**Definition**: OTIF for the same period in the previous year.

**Formula**:
```
OTIF PY = OTIF for orders in prior calendar year
```

**Business Logic**:
- Baseline for YoY comparison
- Enables trend analysis

---

### 15. OTIF % YoY Growth

**Definition**: Year-over-year change in OTIF performance.

**Formula**:
```
YoY Growth = OTIF YTD - OTIF PY
```

**Business Logic**:
- Measured in percentage points
- Positive = Improvement

**Target**: Positive growth

---

### 16. Fill Rate 3-Month Rolling Average

**Definition**: Average fill rate over trailing 3 months.

**Formula**:
```
Rolling Avg = AVERAGE(fill_rate for months t, t-1, t-2)
```

**Business Logic**:
- Smooths monthly volatility
- Reveals underlying trends

---

### 17. Cost to Serve MoM Change

**Definition**: Month-over-month change in cost per order.

**Formula**:
```
MoM Change = Current Month Cost - Previous Month Cost
MoM Change % = (MoM Change / Previous Month Cost) × 100
```

**Business Logic**:
- Identifies cost trends
- Early warning for issues

---

## Rankings & Scenario KPIs

### 18. Supplier Reliability Rank

**Definition**: Ranked ordering of suppliers by composite reliability score.

**Formula**:
```
Reliability Score = (OTIF × 0.4) + (On-Time × 0.2) + (In-Full × 0.2) + (Quality × 0.2)
Rank = RANKX(ALL(Suppliers), Reliability Score, DESC)
```

**Business Logic**:
- Composite of multiple metrics
- Rank 1 = Best performer

---

### 19. Top 5 Suppliers by OTIF

**Definition**: Five suppliers with highest OTIF percentages.

**Formula**:
```
Top 5 = TOPN(5, Suppliers, OTIF, DESC)
```

**Business Logic**:
- Recognizes best performers
- Identifies preferred partners

---

### 20. What-If: Lead Time Reduction Impact

**Definition**: Simulated OTIF improvement from reducing supplier lead times.

**Formula**:
```
Simulated Promised Date = Original Promised Date - Reduction Days
Simulated OTIF = OTIF using simulated dates
Impact = Simulated OTIF - Current OTIF
```

**Business Logic**:
- Supports investment decisions
- Quantifies benefit of process improvements

---

## Data Assumptions

1. **Calendar**: Standard Gregorian calendar
2. **Fiscal Year**: Same as calendar year (Jan-Dec)
3. **Working Days**: Not explicitly modeled; all days treated equally
4. **Currency**: All costs in USD
5. **Time Zones**: All dates in same time zone

---

## Calculation Notes

- All percentages expressed as 0-100 scale
- Null values excluded from calculations
- Division by zero returns 0
- Rounding: 2 decimal places for percentages, 0 for counts
