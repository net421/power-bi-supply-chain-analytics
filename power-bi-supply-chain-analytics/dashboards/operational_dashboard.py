"""
Operational Dashboard

Dashboard 2 - Operational Analysis:
- Table: Late Orders Detail
- Heatmap: OTIF by Product Category × Warehouse
- Scatter plot: Fill Rate vs Days of Supply
- Waterfall: Stockout Root Causes
- Slicers: Date, Supplier, Warehouse, Product
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def render_operational_dashboard(data, kpi_calc, time_intel, filters):
    """Render the operational dashboard."""
    
    st.header("⚙️ Operational Analysis")
    st.markdown("Detailed operational metrics for supply chain management and execution")
    
    # Apply filters to orders
    orders = data['orders'].copy()
    
    # Date filter
    if len(filters['date_range']) == 2:
        orders = orders[
            (orders['order_date'] >= pd.Timestamp(filters['date_range'][0])) &
            (orders['order_date'] <= pd.Timestamp(filters['date_range'][1]))
        ]
    
    st.markdown("---")
    
    # Row 1: Late Orders Table
    st.subheader("📋 Late Orders Detail")
    
    # Identify late orders
    late_orders = orders[orders['delivery_date'] > orders['promised_date']].copy()
    late_orders['days_late'] = (late_orders['delivery_date'] - late_orders['promised_date']).dt.days
    late_orders['order_value'] = late_orders['unit_cost'] * late_orders['quantity_ordered']
    
    # Select columns for display
    late_display = late_orders[[
        'order_id', 'order_date', 'customer_id', 'product_id', 
        'supplier_id', 'warehouse_id', 'promised_date', 'delivery_date',
        'days_late', 'quantity_ordered', 'quantity_delivered', 'order_value'
    ]].sort_values('days_late', ascending=False)
    
    # Show top 20 late orders
    st.dataframe(
        late_display.head(20).style.format({
            'order_date': '{:%Y-%m-%d}',
            'promised_date': '{:%Y-%m-%d}',
            'delivery_date': '{:%Y-%m-%d}',
            'order_value': '${:,.2f}'
        }),
        use_container_width=True,
        height=400
    )
    
    st.caption(f"Showing top 20 of {len(late_display)} late orders")
    
    st.markdown("---")
    
    # Row 2: Heatmap and Scatter
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 OTIF Heatmap: Category × Warehouse")
        
        # Merge orders with products to get category
        orders_with_cat = orders.merge(
            data['products'][['product_id', 'category']],
            on='product_id',
            how='left'
        )
        
        # Calculate OTIF by category and warehouse
        heatmap_data = orders_with_cat.groupby(['category', 'warehouse_id']).apply(
            lambda df: ((df['delivery_date'] <= df['promised_date']) & 
                       (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100
        ).reset_index()
        heatmap_data.columns = ['Category', 'Warehouse', 'OTIF']
        
        # Pivot for heatmap
        heatmap_pivot = heatmap_data.pivot(index='Category', columns='Warehouse', values='OTIF')
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            text_auto='.1f',
            color_continuous_scale='RdYlGn',
            range_color=[70, 100],
            labels={'x': 'Warehouse', 'y': 'Category', 'color': 'OTIF %'}
        )
        
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        st.subheader("📊 Fill Rate vs Days of Supply")
        
        # Calculate fill rate and days of supply by product
        product_metrics = orders.groupby('product_id').agg({
            'quantity_delivered': 'sum',
            'quantity_ordered': 'sum'
        }).reset_index()
        product_metrics['fill_rate'] = (
            product_metrics['quantity_delivered'] / product_metrics['quantity_ordered'] * 100
        )
        
        # Get inventory data for days of supply
        inv_latest = data['inventory'].groupby('product_id').agg({
            'inventory_on_hand': 'last',
            'date': 'max'
        }).reset_index()
        
        # Merge
        product_scatter = product_metrics.merge(inv_latest, on='product_id', how='left')
        
        # Calculate average daily demand
        date_range = (orders['order_date'].max() - orders['order_date'].min()).days + 1
        product_scatter['avg_daily_demand'] = product_scatter['quantity_ordered'] / date_range
        product_scatter['days_of_supply'] = (
            product_scatter['inventory_on_hand'] / product_scatter['avg_daily_demand'].replace(0, 1)
        )
        
        # Remove outliers
        product_scatter = product_scatter[
            (product_scatter['days_of_supply'] < 200) & 
            (product_scatter['days_of_supply'] > 0)
        ]
        
        fig_scatter = px.scatter(
            product_scatter,
            x='days_of_supply',
            y='fill_rate',
            size='quantity_ordered',
            color='fill_rate',
            color_continuous_scale='RdYlGn',
            hover_name='product_id',
            hover_data=['quantity_ordered', 'inventory_on_hand'],
            labels={
                'days_of_supply': 'Days of Supply',
                'fill_rate': 'Fill Rate %'
            },
            title='Product Performance Matrix'
        )
        
        # Add reference lines
        fig_scatter.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
        fig_scatter.add_vline(x=30, line_dash="dash", line_color="orange", annotation_text="Min DOS: 30")
        fig_scatter.add_vline(x=60, line_dash="dash", line_color="blue", annotation_text="Max DOS: 60")
        
        fig_scatter.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Stockout Analysis and Inventory Risk
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Stockout Root Causes")
        
        # Analyze stockouts from inventory data
        inv = data['inventory'].copy()
        inv['is_stockout'] = inv['inventory_on_hand'] == 0
        inv['is_below_safety'] = inv['inventory_on_hand'] < inv['safety_stock']
        inv['is_below_reorder'] = inv['inventory_on_hand'] < inv['reorder_point']
        
        # Count by cause
        stockout_causes = pd.DataFrame({
            'Cause': ['Critical Stockout', 'Below Safety Stock', 'Below Reorder Point'],
            'Count': [
                inv['is_stockout'].sum(),
                inv['is_below_safety'].sum() - inv['is_stockout'].sum(),
                inv['is_below_reorder'].sum() - inv['is_below_safety'].sum()
            ]
        })
        
        # Create waterfall chart
        fig_waterfall = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative"],
            x=stockout_causes['Cause'],
            textposition="outside",
            text=stockout_causes['Count'],
            y=stockout_causes['Count'],
            connector={"line": {"color": "#666"}},
            decreasing={"marker": {"color": "#E63946"}},
            increasing={"marker": {"color": "#457B9D"}}
        ))
        
        fig_waterfall.update_layout(
            height=400,
            title="Stockout Incidents by Severity",
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Inventory Risk Distribution")
        
        # Calculate risk categories
        risk_data = kpi_calc.calculate_inventory_risk_score()
        risk_dist = risk_data.groupby('risk_category').size().reset_index(name='count')
        risk_dist['percentage'] = (risk_dist['count'] / risk_dist['count'].sum()) * 100
        
        # Color mapping
        color_map = {
            'Critical': '#E63946',
            'Warning': '#F18F01',
            'Optimal': '#2A9D8F',
            'Elevated': '#264653'
        }
        
        fig_pie = px.pie(
            risk_dist,
            names='risk_category',
            values='percentage',
            color='risk_category',
            color_discrete_map=color_map,
            hole=0.4,
            labels={'risk_category': 'Risk Level', 'percentage': '% of Products'}
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400, showlegend=True)
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Row 4: Detailed Metrics Table
    st.subheader("📊 Detailed Performance Metrics")
    
    # Create summary table by supplier
    supplier_perf = orders.groupby('supplier_id').agg({
        'order_id': 'count',
        'quantity_delivered': 'sum',
        'quantity_ordered': 'sum',
        'unit_cost': lambda x: (x * orders.loc[x.index, 'quantity_ordered']).sum(),
        'quality_score': 'mean'
    }).reset_index()
    
    supplier_perf.columns = ['Supplier ID', 'Orders', 'Qty Delivered', 'Qty Ordered', 'Total Value', 'Avg Quality']
    supplier_perf['Fill Rate'] = (supplier_perf['Qty Delivered'] / supplier_perf['Qty Ordered']) * 100
    
    # Calculate OTIF
    supplier_otif = orders.groupby('supplier_id').apply(
        lambda df: ((df['delivery_date'] <= df['promised_date']) & 
                   (df['quantity_delivered'] >= df['quantity_ordered'])).mean() * 100
    ).reset_index()
    supplier_otif.columns = ['Supplier ID', 'OTIF']
    
    supplier_perf = supplier_perf.merge(supplier_otif, on='Supplier ID')
    supplier_perf = supplier_perf.sort_values('OTIF', ascending=False)
    
    # Format and display
    st.dataframe(
        supplier_perf.style.format({
            'Fill Rate': '{:.1f}%',
            'OTIF': '{:.1f}%',
            'Avg Quality': '{:.2f}',
            'Total Value': '${:,.2f}'
        }),
        use_container_width=True,
        height=300
    )
    
    # Insights section
    st.markdown("---")
    st.subheader("💡 Operational Insights")
    
    insights = []
    
    # Late order analysis
    late_pct = (len(late_orders) / len(orders)) * 100 if len(orders) > 0 else 0
    if late_pct > 10:
        insights.append(f"🚨 **High Delay Rate:** {late_pct:.1f}% of orders are delayed - investigate root causes")
    elif late_pct > 5:
        insights.append(f"⚠️ **Moderate Delays:** {late_pct:.1f}% delay rate - monitor closely")
    else:
        insights.append(f"✅ **Good On-Time Performance:** Only {late_pct:.1f}% delays")
    
    # Stockout analysis
    stockout_count = inv['is_stockout'].sum()
    if stockout_count > 100:
        insights.append(f"🚨 **Critical Stockouts:** {stockout_count} stockout incidents detected")
    elif stockout_count > 50:
        insights.append(f"⚠️ **Stockout Alert:** {stockout_count} stockout incidents - review safety stock levels")
    else:
        insights.append(f"✅ **Stock Levels Healthy:** Only {stockout_count} stockout incidents")
    
    # Category performance
    if len(heatmap_pivot) > 0:
        worst_cat = heatmap_pivot.mean().idxmin()
        worst_otif = heatmap_pivot.mean().min()
        if worst_otif < 85:
            insights.append(f"⚠️ **Category Focus:** {worst_cat} has lowest OTIF ({worst_otif:.1f}%)")
    
    for insight in insights:
        st.markdown(insight)
