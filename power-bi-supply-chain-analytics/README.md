# Power BI Supply Chain Analytics - Python Implementation

A comprehensive Python-based supply chain analytics platform that replicates Power BI functionality using Pandas, Plotly, and Streamlit. This project demonstrates professional data analytics skills with complete KPI calculations, interactive dashboards, and data validation.

## 📋 Table of Contents

- [Business Problem](#business-problem)
- [Project Architecture](#project-architecture)
- [20 Key Metrics (DAX → Python)](#20-key-metrics-dax--python)
- [Installation & Setup](#installation--setup)
- [Execution Instructions](#execution-instructions)
- [Data Validation](#data-validation)
- [Skills Demonstrated](#skills-demonstrated)

---

## 🎯 Business Problem

Supply chain managers need real-time visibility into:
- **Service Performance**: Are we meeting customer delivery commitments?
- **Inventory Health**: Do we have optimal stock levels across warehouses?
- **Cost Efficiency**: Are freight and logistics costs within budget?
- **Supplier Performance**: Which suppliers are reliable partners?

This project provides a complete analytics solution equivalent to Power BI dashboards, enabling data-driven decisions for supply chain optimization.

---

## 🏗️ Project Architecture

```
power-bi-supply-chain-analytics/
├── data/
│   ├── generate_data.py          # Synthetic data generator
│   ├── supply_chain_orders.csv   # 10,000 orders
│   ├── inventory_levels.csv      # 24,000 daily records
│   ├── shipping_costs.csv        # 8,500 shipments
│   ├── suppliers.csv             # 50 suppliers
│   ├── products.csv              # 500 products
│   └── warehouses.csv            # 8 warehouses
├── analytics/
│   ├── kpi_calculations.py       # 12 core KPIs
│   ├── time_intelligence.py      # YTD, YoY, MoM calculations
│   └── rankings_scenarios.py     # Rankings & what-if analysis
├── dashboards/
│   ├── app.py                    # Main Streamlit app
│   ├── executive_dashboard.py    # Executive overview
│   ├── operational_dashboard.py  # Operational details
│   └── cost_dashboard.py         # Cost analysis
├── validation/
│   ├── data_quality_checks.py    # Data validation
│   └── kpi_verification.py       # KPI tests
├── docs/
│   ├── data_dictionary.md        # Data definitions
│   ├── methodology.md            # Calculation methods
│   └── deployment_guide.md       # Deployment instructions
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📊 20 Key Metrics (DAX → Python)

### Service KPIs (4)

| # | Metric | DAX Equivalent | Python Implementation |
|---|--------|----------------|----------------------|
| 1 | **OTIF %** | `DIVIDE(COUNTROWS(FILTER(Orders, delivery<=promised && delivered>=ordered)), COUNTROWS(Orders))` | `(on_time & in_full).sum() / len(df) * 100` |
| 2 | **Fill Rate %** | `DIVIDE(SUM(quantity_delivered), SUM(quantity_ordered))` | `df['quantity_delivered'].sum() / df['quantity_ordered'].sum() * 100` |
| 3 | **On-Time Delivery %** | `DIVIDE(COUNTROWS(FILTER(Orders, delivery<=promised)), COUNTROWS(Orders))` | `(df['delivery_date'] <= df['promised_date']).sum() / len(df) * 100` |
| 4 | **Perfect Order %** | `DIVIDE(COUNTROWS(FILTER(Orders, on_time && in_full && quality>=0.95)), COUNTROWS(Orders))` | `(on_time & in_full & high_quality).sum() / len(df) * 100` |

### Inventory KPIs (4)

| # | Metric | DAX Equivalent | Python Implementation |
|---|--------|----------------|----------------------|
| 5 | **Inventory Turns** | `DIVIDE(CALCULATE(SUM(quantity_ordered), DATESINPERIOD), AVERAGE(inventory_on_hand))` | `annual_cogs / avg_inventory_value` |
| 6 | **Days of Supply** | `DIVIDE(AVERAGE(inventory_on_hand), AVERAGE(quantity_ordered)/30)` | `avg_inventory / avg_daily_demand` |
| 7 | **Inventory Risk Score** | `SWITCH(TRUE(), inventory<safety_stock, "Critical", ...)` | `apply(assign_risk, axis=1)` |
| 8 | **Stockout Frequency %** | `DIVIDE(COUNTROWS(FILTER(Inventory, inventory_on_hand=0)), COUNTROWS(Inventory))` | `(inventory==0).sum() / len(inventory) * 100` |

### Cost KPIs (4)

| # | Metric | DAX Equivalent | Python Implementation |
|---|--------|----------------|----------------------|
| 9 | **Cost to Serve/Order** | `DIVIDE(SUM(unit_cost*qty) + SUM(handling) + SUM(shipping), COUNTROWS(Orders))` | `total_cost / len(orders)` |
| 10 | **Freight Cost/Kg** | `DIVIDE(SUM(Shipping[total_cost]), SUM(Shipping[weight_kg]))` | `shipping['total_cost'].sum() / shipping['weight_kg'].sum()` |
| 11 | **Cost by Shipping Mode** | `CALCULATE(SUM(total_cost), ALLEXCEPT(Shipping, shipping_mode))` | `groupby('shipping_mode')['total_cost'].sum()` |
| 12 | **Freight Budget Variance %** | `DIVIDE(actual - budget, budget)` | `((actual - budget) / budget) * 100` |

### Time Intelligence (5)

| # | Metric | DAX Equivalent | Python Implementation |
|---|--------|----------------|----------------------|
| 13 | **OTIF % YTD** | `CALCULATE([OTIF %], DATESYTD('Calendar'[Date]))` | Filter by year-to-date, then calculate OTIF |
| 14 | **OTIF % PY** | `CALCULATE([OTIF %], SAMEPERIODLASTYEAR('Calendar'[Date]))` | Filter by prior year, then calculate OTIF |
| 15 | **OTIF % YoY Growth** | `[OTIF %] - [OTIF % PY]` | `current_otif - prior_otif` |
| 16 | **Fill Rate 3M Rolling Avg** | `AVERAGEX(DATESINPERIOD(..., -3, MONTH), [Fill Rate])` | `rolling(window=3).mean()` |
| 17 | **Cost to Serve MoM Change** | `[Cost] - CALCULATE([Cost], PREVIOUSMONTH)` | `current - shift(1)` |

### Rankings & Scenarios (3)

| # | Metric | DAX Equivalent | Python Implementation |
|---|--------|----------------|----------------------|
| 18 | **Supplier Reliability Rank** | `RANKX(ALL(Suppliers), [OTIF %], , DESC)` | `rank(ascending=False, method='min')` |
| 19 | **Top 5 Suppliers by OTIF** | `TOPN(5, VALUES(Suppliers), [OTIF %], DESC)` | `nlargest(5, 'otif')` |
| 20 | **What-If: Lead Time Impact** | Parameter + `CALCULATE([OTIF], FILTER(...))` | Simulate reduced promised dates |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- pip package manager

### Step 1: Clone Repository
```bash
cd /workspace
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Generate Synthetic Data
```bash
python data/generate_data.py
```

This creates:
- `supply_chain_orders.csv` - 10,000 orders with realistic patterns
- `inventory_levels.csv` - 24,000 daily inventory records
- `shipping_costs.csv` - 8,500 shipment records
- `suppliers.csv` - 50 supplier master records
- `products.csv` - 500 product master records
- `warehouses.csv` - 8 warehouse master records

### Step 4: Validate Data Quality
```bash
python validation/data_quality_checks.py
```

### Step 5: Verify KPI Calculations
```bash
python validation/kpi_verification.py
```

---

## 📌 Execution Instructions

### Run Individual Analytics Scripts

```bash
# Calculate all KPIs
python analytics/kpi_calculations.py

# Calculate time intelligence metrics
python analytics/time_intelligence.py

# Run rankings and scenarios
python analytics/rankings_scenarios.py
```

### Launch Interactive Dashboards

```bash
# Start the Streamlit application
streamlit run dashboards/app.py
```

The dashboard will open at `http://localhost:8501` with three tabs:
1. **Executive Overview** - Strategic KPIs and trends
2. **Operational Analysis** - Detailed operational metrics
3. **Cost Analysis** - Freight and logistics cost breakdown

---

## ✅ Data Validation

### Data Quality Checks
The `validation/data_quality_checks.py` script validates:

| Check | Description | Expected Result |
|-------|-------------|-----------------|
| Record Counts | Verify dataset sizes | Orders: ~10K, Inventory: ~24K, Shipping: ~8.5K |
| Column Completeness | All required columns present | 100% coverage |
| Null Values | No nulls in critical fields | 0 nulls |
| Delivery Delays | ~5% late deliveries | 3-7% range |
| Incomplete Deliveries | ~3% partial shipments | 1-5% range |
| Seasonality | Q4 peak pattern | Q4 > Q1 × 1.3 |
| Referential Integrity | Foreign key relationships | 100% valid references |

### KPI Verification Tests
The `validation/kpi_verification.py` script tests:

| Test | Validation Logic |
|------|------------------|
| OTIF Range | 80-100% |
| Fill Rate Logic | 90-100% |
| On-Time ≥ OTIF | Logical relationship |
| Perfect ≤ OTIF | Subset relationship |
| Inventory Turns | Positive value |
| Days of Supply | 1-365 days |
| Cost Values | All positive |
| Supplier Ranking | Sequential ranks |
| Time Intelligence | Valid percentages |

---

## 🎓 Skills Demonstrated

### Technical Skills
- **Python Programming**: Clean, modular code with docstrings
- **Pandas**: Advanced data manipulation and aggregation
- **Plotly**: Interactive visualizations (charts, maps, heatmaps)
- **Streamlit**: Web application development
- **Data Engineering**: ETL pipeline, data generation, validation

### Analytics Skills
- **KPI Development**: Translating business metrics to code
- **Time Intelligence**: YTD, YoY, MoM, rolling averages
- **Statistical Analysis**: Trend analysis, variance calculation
- **Data Modeling**: Star schema implementation

### Business Skills
- **Supply Chain Domain Knowledge**: OTIF, fill rate, inventory turns
- **Dashboard Design**: Executive, operational, and cost views
- **Data Storytelling**: Insights and recommendations

---

## 📸 Dashboard Screenshots

### Executive Dashboard
- KPI cards with YoY comparisons
- OTIF trend line (YTD vs Prior Year)
- Gauge chart for Days of Supply
- Top 10 suppliers bar chart
- Regional freight cost visualization

### Operational Dashboard
- Late orders detail table
- OTIF heatmap (Category × Warehouse)
- Fill Rate vs Days of Supply scatter
- Stockout root cause waterfall
- Inventory risk distribution pie chart

### Cost Dashboard
- Freight budget variance waterfall
- Cost per Kg by shipping mode
- Monthly freight cost trend
- Sunburst cost decomposition
- Carrier performance matrix

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Data files not found
```bash
# Solution: Generate data first
python data/generate_data.py
```

**Issue**: Module import errors
```bash
# Solution: Ensure you're in the project directory
cd power-bi-supply-chain-analytics
python -m analytics.kpi_calculations
```

**Issue**: Port already in use
```bash
# Solution: Use different port
streamlit run dashboards/app.py --server.port 8502
```

---

## 📄 License

This project is created for portfolio demonstration purposes.

---

## 👤 Author

Created as a professional portfolio piece demonstrating end-to-end supply chain analytics capabilities equivalent to Power BI implementations.
