# Validation Results

Local deterministic generation run (seed 42):

- Orders: **10,000**
- Unique order IDs: **PASS**
- Delivered ≤ ordered: **PASS**
- Non-negative unit/handling costs: **PASS**
- Delivery date ≥ order date: **PASS**
- Delayed delivery rate: **5.33%** — within 4.5–6.0% target band
- Incomplete delivery rate: **3.32%** — within 2.5–4.0% target band
- Product foreign keys: **PASS**
- Supplier foreign keys: **PASS**
- Warehouse foreign keys: **PASS**

Run locally with:

```bash
python scripts/generate_supply_chain_data.py
python validation/data_quality_checks.py
```
