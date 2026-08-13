from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
orders = pd.read_csv(DATA / "supply_chain_orders.csv")
checks = {
    "orders_10000": len(orders) == 10000,
    "unique_order_id": orders.order_id.is_unique,
    "quantity_consistency": (orders.quantity_delivered <= orders.quantity_ordered).all(),
    "nonnegative_costs": (orders.unit_cost.ge(0) & orders.handling_cost.ge(0)).all(),
    "valid_dates": (pd.to_datetime(orders.delivery_date) >= pd.to_datetime(orders.order_date)).all(),
    "late_rate_band": .045 <= (pd.to_datetime(orders.delivery_date) > pd.to_datetime(orders.promised_date)).mean() <= .06,
    "incomplete_rate_band": .025 <= (orders.quantity_delivered < orders.quantity_ordered).mean() <= .04,
    "product_keys": orders.product_id.isin(pd.read_csv(DATA / "products.csv").product_id).all(),
    "supplier_keys": orders.supplier_id.isin(pd.read_csv(DATA / "suppliers.csv").supplier_id).all(),
    "warehouse_keys": orders.warehouse_id.isin(pd.read_csv(DATA / "warehouses.csv").warehouse_id).all(),
}
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL':4} {name}")
if not all(checks.values()):
    raise SystemExit(1)
