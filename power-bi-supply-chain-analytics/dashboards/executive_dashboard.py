"""
Executive Dashboard

Dashboard 1 - Executive Overview:
- KPI cards (OTIF, Fill Rate, Cost to Serve, Inventory Turns)
- Trend line: OTIF % YTD vs Prior Year
- Gauge chart: Days of Supply
- Bar chart: Top 10 Suppliers by OTIF
- Map: Freight Cost by Region
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def render_executive_dashboard(data, kpi_calc, time_intel, rankings):
    """Render the executive dashboard."""
    
    st.header("📈 Executive Overview")
    st.markdown("Key performance indicators and strategic metrics for supply chain leadership")
    
    # Calculate KPIs
    otif = kpi_calc.calculate_otif()
    fill_rate = kpi_calc.calculate_fill_rate()
    cost_to_serve = kpi_calc.calculate_cost_to_serve_per_order()
    inventory_turns = kpi_calc.calculate_inventory_turns()
    days_of_supply = kpi_calc.calculate_days_of_supply()
    on_time_delivery = kpi_calc.calculate_on_time_delivery()
    perfect_order = kpi_calc.calculate_perfect_order()
    
    # KPI Cards Row 1
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_otif = time_intel.calculate_otif_yoy_growth()
        st.metric(
            label="🎯 OTIF %",
            value=f"{otif:.1f}%",
            delta=f"{delta_otif:+.1f} pp YoY"
        )
    
    with col2:
        st.metric(
            label="📦 Fill Rate %",
            value=f"{fill_rate:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="💰 Cost to Serve",
            value=f"${cost_to_serve:,.0f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="🔄 Inventory Turns",
            value=f"{inventory_turns:.1f}x",
            delta=None
        )
    
    # KPI Cards Row 2
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="⏱️ On-Time Delivery %",
            value=f"{on_time_delivery:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            label="✨ Perfect Order %",
            value=f"{perfect_order:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="📅 Days of Supply",
            value=f"{days_of_supply:.1f} days",
            delta=None
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 OTIF Trend: YTD vs Prior Year")
        
        # Get monthly OTIF trend
        monthly_trend = time_intel.get_monthly_otif_trend()
        monthly_trend['year'] = monthly_trend['year_month'].dt.year
        monthly_trend['month'] = monthly_trend['year_month'].dt.month
        
        # Create comparison chart
        fig_trend = go.Figure()
        
        # Current year
        current_year = monthly_trend[monthly_trend['year'] == 2024]
        fig_trend.add_trace(go.Scatter(
            x=current_year['year_month'],
            y=current_year['otif'],
            mode='lines+markers',
            name='2024 YTD',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))
        
        # Prior year
        prior_year = monthly_trend[monthly_trend['year'] == 2023]
        fig_trend.add_trace(go.Scatter(
            x=prior_year['year_month'],
            y=prior_year['otif'],
            mode='lines+markers',
            name='2023 PY',
            line=dict(color='#A23B72', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            height=400,
            xaxis_title="Month",
            yaxis_title="OTIF %",
            yaxis_range=[70, 100],
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.subheader("📏 Days of Supply")
        
        # Gauge chart for Days of Supply
        optimal_min = 30
        optimal_max = 60
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=days_of_supply,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Days of Supply", 'font': {'size': 18}},
            delta={'reference': optimal_max, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 120], 'tickwidth': 1, 'tickcolor': "#666"},
                'bar': {'color': "#2E86AB" if optimal_min <= days_of_supply <= optimal_max else "#F18F01"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#666",
                'steps': [
                    {'range': [0, optimal_min], 'color': "#FFE5D9"},
                    {'range': [optimal_min, optimal_max], 'color': "#D8F3DC"},
                    {'range': [optimal_max, 120], 'color': "#FFCDB2"}
                ],
            }
        ))
        
        fig_gauge.update_layout(height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Suppliers by OTIF")
        
        supplier_rankings = rankings.calculate_supplier_reliability_rank()
        top_10 = supplier_rankings.nlargest(10, 'otif')
        
        fig_suppliers = go.Figure()
        fig_suppliers.add_trace(go.Bar(
            y=top_10['supplier_name'],
            x=top_10['otif'],
            orientation='h',
            marker=dict(
                color=top_10['otif'],
                colorscale='RdYlGn',
                cmin=80,
                cmax=100
            ),
            hovertemplate='<b>%{y}</b><br>OTIF: %{x:.1f}%<extra></extra>'
        ))
        
        fig_suppliers.update_layout(
            height=400,
            xaxis_title="OTIF %",
            xaxis_range=[70, 100],
            showlegend=False,
            margin=dict(l=150, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig_suppliers, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Freight Cost by Region")
        
        # Aggregate shipping costs by region
        regional_costs = data['shipping'].groupby('destination_region').agg({
            'total_cost': 'sum',
            'shipment_id': 'count'
        }).reset_index()
        regional_costs.columns = ['Region', 'Total Cost', 'Shipment Count']
        
        # Create choropleth map (using location names)
        fig_map = px.choropleth(
            regional_costs,
            locations=['USA', 'DEU', 'CHN', 'BRA'],  # Simplified mapping
            locationmode='ISO-3',
            color='Total Cost',
            hover_name='Region',
            color_continuous_scale='YlOrRd',
            title='Freight Cost Distribution',
            labels={'Total Cost': 'Cost ($)'}
        )
        
        fig_map.update_layout(
            height=400,
            geo=dict(showframe=False, projection={'type': 'natural earth'})
        )
        
        # Alternative: Bar chart if map doesn't work well
        fig_bar = px.bar(
            regional_costs,
            x='Region',
            y='Total Cost',
            color='Total Cost',
            color_continuous_scale='YlOrRd',
            text_auto='.2s',
            labels={'Total Cost': 'Cost ($)', 'Region': 'Destination'}
        )
        
        fig_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Additional insights
    st.markdown("---")
    st.subheader("📋 Executive Summary")
    
    # Generate summary insights
    insights = []
    
    if otif >= 90:
        insights.append("✅ **Service Excellence:** OTIF above 90% target")
    elif otif >= 80:
        insights.append("⚠️ **Service Alert:** OTIF below 90% target - review supplier performance")
    else:
        insights.append("🚨 **Critical:** OTIF significantly below target - immediate action required")
    
    if days_of_supply < 30:
        insights.append("⚠️ **Inventory Risk:** Days of supply below optimal range")
    elif days_of_supply > 60:
        insights.append("⚠️ **Overstock Risk:** Excess inventory tying up capital")
    else:
        insights.append("✅ **Inventory Health:** Days of supply in optimal range")
    
    if fill_rate >= 95:
        insights.append("✅ **Fulfillment:** Strong fill rate performance")
    else:
        insights.append("⚠️ **Fulfillment Gap:** Fill rate below 95% target")
    
    for insight in insights:
        st.markdown(insight)
