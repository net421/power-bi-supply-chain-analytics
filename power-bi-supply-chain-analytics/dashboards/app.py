"""
Supply Chain Analytics Dashboards - Main App

Main Streamlit application that orchestrates all dashboards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.kpi_calculations import SupplyChainKPIs
from analytics.time_intelligence import TimeIntelligence
from analytics.rankings_scenarios import RankingsScenarios

# Page configuration
st.set_page_config(
    page_title="Supply Chain Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    """Load all data files."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    try:
        orders = pd.read_csv(
            os.path.join(data_dir, 'supply_chain_orders.csv'),
            parse_dates=['order_date', 'promised_date', 'delivery_date']
        )
        inventory = pd.read_csv(
            os.path.join(data_dir, 'inventory_levels.csv'),
            parse_dates=['date']
        )
        shipping = pd.read_csv(
            os.path.join(data_dir, 'shipping_costs.csv'),
            parse_dates=['ship_date', 'delivery_date']
        )
        products = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        suppliers = pd.read_csv(os.path.join(data_dir, 'suppliers.csv'))
        warehouses = pd.read_csv(os.path.join(data_dir, 'warehouses.csv'))
        
        return {
            'orders': orders,
            'inventory': inventory,
            'shipping': shipping,
            'products': products,
            'suppliers': suppliers,
            'warehouses': warehouses
        }
    except FileNotFoundError as e:
        st.error(f"Data files not found. Please run generate_data.py first. Error: {e}")
        return None


def init_kpi_calculators(data):
    """Initialize KPI calculators with loaded data."""
    kpi_calc = SupplyChainKPIs()
    kpi_calc.orders = data['orders']
    kpi_calc.inventory = data['inventory']
    kpi_calc.shipping = data['shipping']
    kpi_calc.products = data['products']
    kpi_calc.suppliers = data['suppliers']
    kpi_calc.warehouses = data['warehouses']
    
    time_intel = TimeIntelligence()
    time_intel.orders = data['orders']
    
    rankings = RankingsScenarios()
    rankings.orders = data['orders']
    rankings.suppliers = data['suppliers']
    
    return kpi_calc, time_intel, rankings


def render_sidebar(data):
    """Render sidebar with filters."""
    st.sidebar.header("🔍 Filters")
    
    # Date filter
    min_date = data['orders']['order_date'].min()
    max_date = data['orders']['order_date'].max()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Supplier filter
    suppliers = ['All'] + sorted(data['suppliers']['supplier_name'].unique().tolist())
    selected_supplier = st.sidebar.selectbox("Supplier", suppliers)
    
    # Warehouse filter
    warehouses = ['All'] + sorted(data['warehouses']['warehouse_name'].unique().tolist())
    selected_warehouse = st.sidebar.selectbox("Warehouse", warehouses)
    
    # Product category filter
    categories = ['All'] + sorted(data['products']['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Product Category", categories)
    
    # Shipping mode filter
    modes = ['All'] + sorted(data['shipping']['shipping_mode'].unique().tolist())
    selected_mode = st.sidebar.selectbox("Shipping Mode", modes)
    
    return {
        'date_range': date_range,
        'supplier': selected_supplier,
        'warehouse': selected_warehouse,
        'category': selected_category,
        'mode': selected_mode
    }


def apply_filters(data, filters):
    """Apply filters to data."""
    orders = data['orders'].copy()
    
    # Date filter
    if len(filters['date_range']) == 2:
        orders = orders[
            (orders['order_date'] >= pd.Timestamp(filters['date_range'][0])) &
            (orders['order_date'] <= pd.Timestamp(filters['date_range'][1]))
        ]
    
    # Supplier filter
    if filters['supplier'] != 'All':
        supplier_id = data['suppliers'][
            data['suppliers']['supplier_name'] == filters['supplier']
        ]['supplier_id'].values[0]
        orders = orders[orders['supplier_id'] == supplier_id]
    
    # Warehouse filter
    if filters['warehouse'] != 'All':
        warehouse_id = data['warehouses'][
            data['warehouses']['warehouse_name'] == filters['warehouse']
        ]['warehouse_id'].values[0]
        orders = orders[orders['warehouse_id'] == warehouse_id]
    
    # Product category filter
    if filters['category'] != 'All':
        product_ids = data['products'][
            data['products']['category'] == filters['category']
        ]['product_id'].values
        orders = orders[orders['product_id'].isin(product_ids)]
    
    return orders


def main():
    """Main application."""
    # Header
    st.title("📊 Supply Chain Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    data = load_data()
    if data is None:
        st.warning("⚠️ Please generate data first by running: `python data/generate_data.py`")
        st.stop()
    
    # Initialize calculators
    kpi_calc, time_intel, rankings = init_kpi_calculators(data)
    
    # Render sidebar
    filters = render_sidebar(data)
    
    # Apply filters
    filtered_orders = apply_filters(data, filters)
    temp_orders = kpi_calc.orders.copy()
    kpi_calc.orders = filtered_orders
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.subheader("📑 Navigation")
    page = st.sidebar.radio(
        "Select Dashboard:",
        ["Executive Overview", "Operational Analysis", "Cost Analysis"]
    )
    
    # Display selected dashboard
    if page == "Executive Overview":
        from dashboards.executive_dashboard import render_executive_dashboard
        render_executive_dashboard(data, kpi_calc, time_intel, rankings)
    elif page == "Operational Analysis":
        from dashboards.operational_dashboard import render_operational_dashboard
        render_operational_dashboard(data, kpi_calc, time_intel, filters)
    elif page == "Cost Analysis":
        from dashboards.cost_dashboard import render_cost_dashboard
        render_cost_dashboard(data, kpi_calc, time_intel)
    
    # Restore original data
    kpi_calc.orders = temp_orders
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #7f8c8d;'>
            <p>Supply Chain Analytics Dashboard | Built with Python, Pandas, Plotly & Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
