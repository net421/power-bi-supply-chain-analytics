from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_ORDERS = 10_000
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(SEED)
dates = pd.date_range("2024-01-01", "2026-12-31", freq="D")
order_date = pd.to_datetime(rng.choice(dates, N_ORDERS))
month = order_date.month.to_numpy(); year = order_date.year.to_numpy()
q4 = np.isin(month, [10, 11, 12]); growth = (year - 2024) * 0.08
qty = np.maximum(1, np.round(rng.lognormal(2.1, .55, N_ORDERS) * (.9 + growth + q4 * .18))).astype(int)
incomplete = rng.random(N_ORDERS) < .03
qty_delivered = qty.copy()
qty_delivered[incomplete] = np.maximum(0, np.floor(qty[incomplete] * rng.uniform(.55, .95, incomplete.sum()))).astype(int)
late = rng.random(N_ORDERS) < .05
lead = rng.integers(3, 16, N_ORDERS)
promised = order_date + pd.to_timedelta(lead, unit="D")
delay = np.zeros(N_ORDERS, dtype=int); delay[late] = rng.integers(1, 6, late.sum())
delivery = promised.to_numpy() + pd.to_timedelta(delay, unit="D").to_numpy()
early = (~late) & (rng.random(N_ORDERS) < .35)
delivery[early] = promised.to_numpy()[early] - pd.to_timedelta(rng.integers(0, 3, early.sum()), unit="D").to_numpy()
orders = pd.DataFrame({
    "order_id": [f"SO{i:06d}" for i in range(1, N_ORDERS + 1)],
    "order_date": order_date.strftime("%Y-%m-%d"),
    "customer_id": [f"C{i:04d}" for i in rng.integers(1, 1001, N_ORDERS)],
    "product_id": [f"P{i:03d}" for i in rng.integers(1, 501, N_ORDERS)],
    "supplier_id": [f"S{i:02d}" for i in rng.integers(1, 51, N_ORDERS)],
    "warehouse_id": [f"W{i:02d}" for i in rng.integers(1, 9, N_ORDERS)],
    "quantity_ordered": qty, "quantity_delivered": qty_delivered,
    "unit_cost": np.round(rng.uniform(8, 250, N_ORDERS), 2),
    "promised_date": pd.to_datetime(promised).strftime("%Y-%m-%d"),
    "delivery_date": pd.to_datetime(delivery).strftime("%Y-%m-%d"),
    "quality_score": np.round(np.clip(rng.normal(.965, .035, N_ORDERS), .75, 1), 3),
    "handling_cost": np.round(qty * np.round(rng.uniform(8, 250, N_ORDERS), 2) * rng.uniform(.008, .025, N_ORDERS), 2),
})
orders.to_csv(OUT / "supply_chain_orders.csv", index=False)
products = pd.DataFrame({"product_id":[f"P{i:03d}" for i in range(1,501)],"product_name":[f"Product {i:03d}" for i in range(1,501)],"category":rng.choice(["Components","Finished Goods","Packaging","Raw Materials"],500),"subcategory":rng.choice(["A","B","C","D"],500),"unit_cost":np.round(rng.uniform(8,250,500),2)})
products.to_csv(OUT / "products.csv", index=False)
suppliers = pd.DataFrame({"supplier_id":[f"S{i:02d}" for i in range(1,51)],"supplier_name":[f"Supplier {i:02d}" for i in range(1,51)],"country":rng.choice(["Mexico","USA","Canada","Germany","China","Japan"],50),"lead_time_days":rng.integers(3,16,50),"reliability_score":np.round(rng.uniform(.82,.99,50),3)})
suppliers.to_csv(OUT / "suppliers.csv", index=False)
warehouses = pd.DataFrame({"warehouse_id":[f"W{i:02d}" for i in range(1,9)],"warehouse_name":[f"Warehouse {i:02d}" for i in range(1,9)],"region":["North","Northeast","Central","West","South","Southeast","Midwest","Pacific"],"capacity":rng.integers(50000,200000,8)})
warehouses.to_csv(OUT / "warehouses.csv", index=False)
print(f"Generated {len(orders):,} orders in {OUT}")
