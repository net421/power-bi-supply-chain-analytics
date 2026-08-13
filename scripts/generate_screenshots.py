"""
Generate static dashboard screenshots as PNG files.
Uses Plotly directly - no browser needed.
Run: python scripts/generate_screenshots.py
"""
import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboards", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
COLORS = {"navy":"#0F2B3C","blue":"#1B6CA8","gold":"#D4A843","green":"#2ECC71","red":"#E74C3C","amber":"#F39C12","light_bg":"#F8F9FA"}
BANNER_TEXT = "Supply Chain Analytics | Python Equivalent of Power BI | github.com/net421"

def load_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    orders = pd.read_csv(os.path.join(data_dir, "supply_chain_orders.csv"))
    orders["order_date"] = pd.to_datetime(orders["order_date"]); orders["promised_date"] = pd.to_datetime(orders["promised_date"]); orders["delivery_date"] = pd.to_datetime(orders["delivery_date"])
    products_path = os.path.join(data_dir, "products.csv"); products = pd.read_csv(products_path) if os.path.exists(products_path) else None
    shipping_path = os.path.join(data_dir, "shipping_costs.csv"); shipping = pd.read_csv(shipping_path) if os.path.exists(shipping_path) else None
    return orders, products, shipping

def calculate_kpis(orders):
    on_time = orders["delivery_date"] <= orders["promised_date"]; in_full = orders["quantity_delivered"] >= orders["quantity_ordered"]
    return {"OTIF %":(on_time & in_full).mean()*100,"Fill Rate %":orders["quantity_delivered"].sum()/orders["quantity_ordered"].sum()*100,"On-Time %":on_time.mean()*100,"Cost to Serve":orders["handling_cost"].sum()/orders["order_id"].nunique()}

def add_banner(fig):
    fig.add_annotation(text=BANNER_TEXT,xref="paper",yref="paper",x=.5,y=-.08,showarrow=False,font=dict(size=10,color=COLORS["navy"]),opacity=.7); return fig

def generate_kpi_cards(kpis):
    fig=make_subplots(rows=1,cols=4,specs=[[{"type":"indicator"}]*4],subplot_titles=["OTIF","Fill Rate","On-Time Delivery","Cost to Serve"])
    vals=[(kpis["OTIF %"],"%",COLORS["navy"]),(kpis["Fill Rate %"],"%",COLORS["blue"]),(kpis["On-Time %"],"%",COLORS["green"]),(kpis["Cost to Serve"],"$",COLORS["gold"])]
    for i,(v,s,c) in enumerate(vals,1):
        fig.add_trace(go.Indicator(mode="number",value=v,number={"suffix":s if s=="%" else "","prefix":"" if s=="%" else "$","font":{"size":40,"color":c}},title={"text":("OTIF %" if i==1 else "Fill Rate" if i==2 else "On-Time Delivery" if i==3 else "Cost to Serve")} ),row=1,col=i)
    fig.update_layout(height=300,width=1400,paper_bgcolor=COLORS["light_bg"],title_text="Executive KPI Summary",title_font=dict(size=18,color=COLORS["navy"]),margin=dict(l=50,r=50,t=80,b=50)); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"01_executive_kpi_cards.png"),scale=2); print("OK 01_executive_kpi_cards.png")

def generate_otif_trend(orders):
    x=orders.copy(); x["month"]=x.order_date.dt.to_period("M").astype(str); x["is_otif"]=(x.delivery_date<=x.promised_date)&(x.quantity_delivered>=x.quantity_ordered); y=x.groupby("month").is_otif.mean().reset_index()
    fig=px.line(y,x="month",y="is_otif",title="Monthly OTIF % Trend",markers=True); fig.update_traces(line=dict(color=COLORS["blue"],width=3),marker=dict(size=8,color=COLORS["gold"])); fig.update_layout(height=500,width=1400,yaxis_title="OTIF %",xaxis_title="Month",paper_bgcolor=COLORS["light_bg"],plot_bgcolor="white",title_font=dict(size=18,color=COLORS["navy"]),margin=dict(l=60,r=40,t=80,b=60)); fig.update_yaxes(range=[0,1.05]); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"02_otif_monthly_trend.png"),scale=2); print("OK 02_otif_monthly_trend.png")

def generate_top_suppliers(orders):
    x=orders.groupby("supplier_id").apply(lambda z:((z.delivery_date<=z.promised_date)&(z.quantity_delivered>=z.quantity_ordered)).mean()).reset_index(); x.columns=["supplier_id","otif"]; x=x.sort_values("otif").tail(10)
    fig=px.bar(x,x="otif",y="supplier_id",orientation="h",color="otif",color_continuous_scale="RdYlGn",title="Top 10 Suppliers by OTIF %"); fig.update_layout(height=500,width=1400,xaxis_title="OTIF %",yaxis_title="",paper_bgcolor=COLORS["light_bg"],plot_bgcolor="white",title_font=dict(size=18,color=COLORS["navy"]),showlegend=False,margin=dict(l=100,r=40,t=80,b=60)); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"03_top_suppliers_otif.png"),scale=2); print("OK 03_top_suppliers_otif.png")

def generate_heatmap(orders,products):
    if products is None:return
    x=orders.merge(products[["product_id","category"]],on="product_id",how="left"); x["is_otif"]=(x.delivery_date<=x.promised_date)&(x.quantity_delivered>=x.quantity_ordered); p=x.groupby(["category","warehouse_id"]).is_otif.mean().reset_index().pivot(index="category",columns="warehouse_id",values="is_otif")
    fig=px.imshow(p,color_continuous_scale="RdYlGn",title="OTIF % by Product Category × Warehouse",labels=dict(color="OTIF %")); fig.update_layout(height=500,width=1400,paper_bgcolor=COLORS["light_bg"],title_font=dict(size=18,color=COLORS["navy"]),margin=dict(l=100,r=40,t=80,b=60)); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"04_heatmap_otif_category_warehouse.png"),scale=2); print("OK 04_heatmap_otif_category_warehouse.png")

def generate_cost_by_mode(shipping):
    if shipping is None:return
    x=shipping.groupby("mode").agg(freight_cost=("freight_cost","sum"),weight_kg=("weight_kg","sum")).reset_index(); x["cost_per_kg"]=x.freight_cost/x.weight_kg
    fig=px.bar(x,x="mode",y="cost_per_kg",color="mode",title="Freight Cost per Kg by Shipping Mode"); fig.update_layout(height=500,width=1400,yaxis_title="Cost per Kg ($)",xaxis_title="Shipping Mode",paper_bgcolor=COLORS["light_bg"],plot_bgcolor="white",title_font=dict(size=18,color=COLORS["navy"]),showlegend=False,margin=dict(l=60,r=40,t=80,b=60)); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"05_cost_per_kg_by_mode.png"),scale=2); print("OK 05_cost_per_kg_by_mode.png")

def generate_waterfall(shipping):
    if shipping is None:return
    budget=shipping.budgeted_cost.sum(); actual=shipping.freight_cost.sum(); variance=actual-budget
    fig=go.Figure(go.Waterfall(x=["Budget","Variance","Actual"],y=[budget,variance,actual],measure=["absolute","relative","total"])); fig.update_layout(title="Freight Budget vs Actual",height=500,width=1400,yaxis_title="Cost ($)",paper_bgcolor=COLORS["light_bg"],title_font=dict(size=18,color=COLORS["navy"]),margin=dict(l=60,r=40,t=80,b=60)); add_banner(fig); fig.write_image(os.path.join(SCREENSHOT_DIR,"06_freight_budget_waterfall.png"),scale=2); print("OK 06_freight_budget_waterfall.png")

def main():
    orders,products,shipping=load_data(); kpis=calculate_kpis(orders); generate_kpi_cards(kpis); generate_otif_trend(orders); generate_top_suppliers(orders); generate_heatmap(orders,products); generate_cost_by_mode(shipping); generate_waterfall(shipping); print("All screenshots generated successfully")
if __name__=="__main__":main()
