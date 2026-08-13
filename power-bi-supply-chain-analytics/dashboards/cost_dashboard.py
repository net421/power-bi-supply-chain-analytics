"""
Cost Analysis Dashboard

Dashboard 3 - Cost Analysis:
- Waterfall: Freight Budget Variance
- Bar chart: Cost per Kg by Mode
- Line chart: Freight Cost Trend
- Matrix: Cost to Serve by Supplier × Lane
- Decomposition: Total Freight Cost breakdown
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def render_cost_dashboard(data, kpi_calc, time_intel):
    """Render the cost analysis dashboard."""
    
    st.header("💰 Cost Analysis")
    st.markdown("Detailed freight and logistics cost analysis for budget management")
    
    shipping = data['shipping'].copy()
    orders = data['orders'].copy()
    
    # Calculate key cost metrics
    total_freight = shipping['total_cost'].sum()
    avg_cost_per_kg = kpi_calc.calculate_freight_cost_per_kg()
    budget_variance = kpi_calc.calculate_freight_budget_variance(budget_multiplier=0.95)  # Assume 95% budget target
    
    st.markdown("---")
    
    # Row 1: KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📦 Total Freight Cost",
            value=f"${total_freight:,.0f}"
        )
    
    with col2:
        st.metric(
            label="⚖️ Avg Cost per Kg",
            value=f"${avg_cost_per_kg:.2f}"
        )
    
    with col3:
        st.metric(
            label="📊 Budget Variance",
            value=f"{budget_variance:+.1f}%",
            delta=None
        )
    
    with col4:
        shipments_count = len(shipping)
        st.metric(
            label="🚚 Total Shipments",
            value=f"{shipments_count:,}"
        )
    
    st.markdown("---")
    
    # Row 2: Waterfall and Cost by Mode
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Freight Budget Variance Waterfall")
        
        # Simulate budget components
        base_freight = shipping['base_freight_cost'].sum()
        fuel_surcharge = shipping['fuel_surcharge'].sum()
        handling_fees = shipping['handling_fee'].sum()
        insurance = shipping['insurance_cost'].sum()
        
        # Budget (assume 95% of actual as target)
        budget = total_freight * 0.95
        variance = total_freight - budget
        
        # Create waterfall data
        categories = ['Base Freight', 'Fuel Surcharge', 'Handling', 'Insurance', 'Budget Gap', 'Total']
        values = [base_freight, fuel_surcharge, handling_fees, insurance, variance, total_freight]
        measures = ['absolute', 'absolute', 'absolute', 'absolute', 'relative', 'total']
        colors = ['#457B9D', '#E63946', '#F18F01', '#2A9D8F', '#E63946' if variance > 0 else '#2A9D8F', '#264653']
        
        fig_waterfall = go.Figure(go.Waterfall(
            orientation="v",
            measure=measures,
            x=categories,
            text=[f"${v:,.0f}" for v in values],
            y=values,
            connector={"line": {"color": "#666"}},
            marker={"color": colors},
            decreasing={"marker": {"color": "#E63946"}},
            increasing={"marker": {"color": "#457B9D"}}
        ))
        
        fig_waterfall.update_layout(
            height=400,
            title="Freight Cost Composition vs Budget",
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    with col2:
        st.subheader("⚖️ Cost per Kg by Shipping Mode")
        
        # Calculate cost per kg by mode
        cost_by_mode = shipping.groupby('shipping_mode').agg({
            'total_cost': 'sum',
            'weight_kg': 'sum'
        }).reset_index()
        cost_by_mode['cost_per_kg'] = cost_by_mode['total_cost'] / cost_by_mode['weight_kg']
        
        fig_bar = px.bar(
            cost_by_mode.sort_values('cost_per_kg'),
            x='shipping_mode',
            y='cost_per_kg',
            color='cost_per_kg',
            color_continuous_scale='YlOrRd',
            text_auto='$.2f',
            labels={
                'shipping_mode': 'Shipping Mode',
                'cost_per_kg': 'Cost per Kg ($)'
            },
            title='Efficiency Comparison by Mode'
        )
        
        fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside")
        fig_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Trend and Decomposition
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Freight Cost Trend")
        
        # Monthly trend
        shipping['month'] = shipping['ship_date'].dt.to_period('M')
        monthly_costs = shipping.groupby('month').agg({
            'total_cost': 'sum',
            'weight_kg': 'sum',
            'shipment_id': 'count'
        }).reset_index()
        monthly_costs.columns = ['month', 'total_cost', 'total_weight', 'shipment_count']
        monthly_costs['cost_per_kg'] = monthly_costs['total_cost'] / monthly_costs['total_weight']
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=monthly_costs['month'].astype(str),
            y=monthly_costs['total_cost'],
            mode='lines+markers',
            name='Total Cost',
            line=dict(color='#E63946', width=2),
            fill='tozeroy',
            fillcolor='rgba(230, 57, 70, 0.1)'
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=monthly_costs['month'].astype(str),
            y=monthly_costs['cost_per_kg'],
            mode='lines+markers',
            name='Cost/Kg',
            line=dict(color='#457B9D', width=2, dash='dash'),
            yaxis='y2'
        ))
        
        fig_trend.update_layout(
            height=400,
            title='Monthly Freight Cost Trend',
            xaxis_title='Month',
            yaxis=dict(title='Total Cost ($)', side='left'),
            yaxis2=dict(title='Cost/Kg ($)', side='right', overlaying='y', anchor='x'),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Freight Cost Decomposition")
        
        # Cost breakdown by region and mode
        cost_decomp = shipping.groupby(['destination_region', 'shipping_mode']).agg({
            'total_cost': 'sum'
        }).reset_index()
        
        # Create sunburst chart
        fig_sunburst = px.sunburst(
            cost_decomp,
            path=['destination_region', 'shipping_mode'],
            values='total_cost',
            color='total_cost',
            color_continuous_scale='YlOrRd',
            title='Cost Distribution by Region & Mode'
        )
        
        fig_sunburst.update_layout(height=400)
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    st.markdown("---")
    
    # Row 4: Cost Matrix
    st.subheader("📊 Cost to Serve Matrix: Supplier × Lane")
    
    # Create supplier-lane matrix
    # Lane = destination region
    supplier_lane = shipping.merge(
        orders[['order_id', 'supplier_id']],
        on='order_id',
        how='left'
    )
    
    # Aggregate by supplier and region
    matrix_data = supplier_lane.groupby(['supplier_id', 'destination_region']).agg({
        'total_cost': 'sum',
        'weight_kg': 'sum',
        'shipment_id': 'count'
    }).reset_index()
    matrix_data.columns = ['Supplier', 'Lane', 'Total Cost', 'Weight', 'Shipments']
    matrix_data['Cost per Shipment'] = matrix_data['Total Cost'] / matrix_data['Shipments']
    
    # Pivot for heatmap
    matrix_pivot = matrix_data.pivot(index='Supplier', columns='Lane', values='Total Cost')
    
    fig_matrix = px.imshow(
        matrix_pivot,
        text_auto='.0f',
        color_continuous_scale='YlOrRd',
        labels={'x': 'Destination Lane', 'y': 'Supplier', 'color': 'Cost ($)'}
    )
    
    fig_matrix.update_layout(height=500)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.markdown("---")
    
    # Row 5: Carrier Performance
    st.subheader("🚚 Carrier Performance Analysis")
    
    carrier_perf = shipping.groupby('carrier').agg({
        'total_cost': 'sum',
        'weight_kg': 'sum',
        'on_time': 'mean',
        'shipment_id': 'count'
    }).reset_index()
    carrier_perf.columns = ['Carrier', 'Total Cost', 'Total Weight', 'On-Time Rate', 'Shipments']
    carrier_perf['Cost per Kg'] = carrier_perf['Total Cost'] / carrier_perf['Total Weight']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_carrier_cost = px.bar(
            carrier_perf.sort_values('Total Cost', ascending=False),
            x='Carrier',
            y='Total Cost',
            color='On-Time Rate',
            color_continuous_scale='RdYlGn',
            text_auto='.0f',
            title='Carrier Spend vs Performance',
            labels={'Total Cost': 'Total Cost ($)', 'On-Time Rate': 'On-Time %'}
        )
        fig_carrier_cost.update_layout(height=400)
        st.plotly_chart(fig_carrier_cost, use_container_width=True)
    
    with col2:
        fig_carrier_scatter = px.scatter(
            carrier_perf,
            x='Shipments',
            y='Cost per Kg',
            size='Total Cost',
            color='On-Time Rate',
            color_continuous_scale='RdYlGn',
            hover_name='Carrier',
            text='Carrier',
            title='Carrier Efficiency Matrix',
            labels={
                'Shipments': 'Number of Shipments',
                'Cost per Kg': 'Cost per Kg ($)'
            }
        )
        fig_carrier_scatter.update_traces(textposition='top center')
        fig_carrier_scatter.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_carrier_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Insights section
    st.subheader("💡 Cost Insights")
    
    insights = []
    
    # Budget variance insight
    if abs(budget_variance) > 5:
        if budget_variance > 0:
            insights.append(f"🚨 **Budget Overrun:** Freight costs {budget_variance:.1f}% over budget")
        else:
            insights.append(f"✅ **Under Budget:** Freight costs {abs(budget_variance):.1f}% under budget")
    else:
        insights.append(f"✅ **On Budget:** Freight costs within acceptable variance ({budget_variance:+.1f}%)")
    
    # Most expensive mode
    if len(cost_by_mode) > 0:
        most_expensive = cost_by_mode.loc[cost_by_mode['cost_per_kg'].idxmax()]
        cheapest = cost_by_mode.loc[cost_by_mode['cost_per_kg'].idxmin()]
        insights.append(f"💡 **Mode Efficiency:** {most_expensive['shipping_mode']} is most expensive at ${most_expensive['cost_per_kg']:.2f}/kg vs {cheapest['shipping_mode']} at ${cheapest['cost_per_kg']:.2f}/kg")
    
    # Top spending region
    region_costs = shipping.groupby('destination_region')['total_cost'].sum()
    top_region = region_costs.idxmax()
    top_region_cost = region_costs.max()
    insights.append(f"🌍 **Top Spending:** {top_region} accounts for ${(top_region_cost/total_freight)*100:.1f}% of freight costs")
    
    # Carrier recommendation
    best_carrier = carrier_perf.loc[carrier_perf['On-Time Rate'].idxmax()]
    if best_carrier['On-Time Rate'] > 0.95:
        insights.append(f"⭐ **Top Performer:** {best_carrier['Carrier']} has {best_carrier['On-Time Rate']*100:.1f}% on-time rate")
    
    for insight in insights:
        st.markdown(insight)
    
    # Recommendations
    st.markdown("### 📋 Recommendations")
    
    recommendations = []
    
    # Mode optimization
    if len(cost_by_mode) > 1:
        high_cost_modes = cost_by_mode[cost_by_mode['cost_per_kg'] > avg_cost_per_kg * 1.5]
        if len(high_cost_modes) > 0:
            modes_list = ', '.join(high_cost_modes['shipping_mode'].tolist())
            recommendations.append(f"🔄 Consider shifting volume from {modes_list} to more economical modes")
    
    # Carrier consolidation
    if len(carrier_perf) > 5:
        recommendations.append("🤝 Consider consolidating carriers for better volume discounts")
    
    # Regional optimization
    high_cost_regions = region_costs[region_costs > region_costs.mean() * 1.5]
    if len(high_cost_regions) > 0:
        recommendations.append(f"🗺️ Review logistics strategy for high-cost regions: {', '.join(high_cost_regions.index.tolist())}")
    
    for rec in recommendations:
        st.markdown(rec)
