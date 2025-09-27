#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hong Kong International Airport 2024 Wind Data Visualization - Streamlit Version
"Wind Flower" - Interactive Web Application

Streamlit version for easier deployment to Streamlit Cloud
"""

import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class StreamlitWindFlowerVisualizer:
    """Streamlit Wind Flower Visualizer for easy deployment"""
    
    def __init__(self):
        # Season color palettes
        self.season_palettes = {
            'spring': ['#FFB3E6', '#FF8EE6', '#FF69E6', '#FF44E6', '#FF1FE6'],
            'summer': ['#B3FFB3', '#8EFF8E', '#69FF69', '#44FF44', '#1FFF1F'],  
            'autumn': ['#FFD1B3', '#FFBF8E', '#FFAD69', '#FF9B44', '#FF891F'],
            'winter': ['#B3E6FF', '#8EDDFF', '#69D4FF', '#44CBFF', '#1FC2FF']
        }
        
    def parse_xml_file(self, file_path):
        """Parse XML wind data file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            data = []
            for record in root.findall('.//record'):
                year = record.find('year')
                month = record.find('month') 
                day = record.find('day')
                value = record.find('value')
                
                if all(x is not None for x in [year, month, day, value]):
                    data.append({
                        'year': int(year.text),
                        'month': int(month.text),
                        'day': int(day.text), 
                        'value': float(value.text)
                    })
            
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error parsing {file_path}: {str(e)}")
            return pd.DataFrame()

    def get_season_color(self, month, intensity=0.8):
        """Get season-appropriate color"""
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'autumn'
        
        colors = self.season_palettes[season]
        color_idx = int(intensity * (len(colors) - 1))
        return colors[color_idx]

    def create_wind_flower_plot(self, df_direction, df_speed, target_month=None):
        """Create wind flower plot"""
        
        fig = go.Figure()
        
        # Filter data by month if specified
        if target_month:
            df_direction_filtered = df_direction[df_direction['month'] == target_month]
            df_speed_filtered = df_speed[df_speed['month'] == target_month]
        else:
            df_direction_filtered = df_direction
            df_speed_filtered = df_speed
        
        # Merge direction and speed data
        merged_data = pd.merge(
            df_direction_filtered[['year', 'month', 'day', 'value']], 
            df_speed_filtered[['year', 'month', 'day', 'value']], 
            on=['year', 'month', 'day'], 
            suffixes=('_dir', '_speed')
        )
        
        if merged_data.empty:
            st.warning("No data available for the selected month.")
            return fig
        
        # Convert wind direction to radians (meteorological to mathematical)
        angles_rad = np.radians(90 - merged_data['value_dir'])
        
        # Calculate radial distances (month position + speed offset)
        base_radius = merged_data['month'] * 0.8
        speed_offset = (merged_data['value_speed'] - merged_data['value_speed'].min()) / \
                      (merged_data['value_speed'].max() - merged_data['value_speed'].min()) * 0.6
        radial_distances = base_radius + speed_offset
        
        # Convert to Cartesian coordinates
        x_coords = radial_distances * np.cos(angles_rad)
        y_coords = radial_distances * np.sin(angles_rad)
        
        # Create color and size arrays
        colors = [self.get_season_color(month) for month in merged_data['month']]
        sizes = merged_data['value_speed'] / merged_data['value_speed'].max() * 15 + 5
        
        # Add main scatter plot
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.7,
                line=dict(width=0.5, color='white')
            ),
            text=[f"Date: {row['year']}-{row['month']:02d}-{row['day']:02d}<br>"
                 f"Direction: {row['value_dir']:.1f}°<br>"
                 f"Speed: {row['value_speed']:.1f} km/h"
                 for _, row in merged_data.iterrows()],
            hovertemplate='%{text}<extra></extra>',
            name='Wind Data'
        ))
        
        # Add concentric circles for months
        theta = np.linspace(0, 2*np.pi, 100)
        for month in range(1, 13):
            if target_month is None or month == target_month:
                r = month * 0.8
                x_circle = r * np.cos(theta)
                y_circle = r * np.sin(theta)
                
                fig.add_trace(go.Scatter(
                    x=x_circle,
                    y=y_circle,
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.3)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Add direction labels
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        
        for direction, angle in zip(directions, angles):
            angle_rad = np.radians(90 - angle)
            r = 10.5
            x_pos = r * np.cos(angle_rad)
            y_pos = r * np.sin(angle_rad)
            
            fig.add_annotation(
                x=x_pos, y=y_pos,
                text=direction,
                showarrow=False,
                font=dict(color='white', size=12, family='Arial'),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1
            )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"🌸 Hong Kong International Airport 2024 Wind Rose Flower" + 
                     (f" - Month {target_month}" if target_month else ""),
                x=0.5,
                font=dict(size=20, color='white', family='Arial Black')
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(10, 25, 47, 1)',
            paper_bgcolor='rgba(10, 25, 47, 1)',
            showlegend=False,
            width=800,
            height=800
        )
        
        # Set equal aspect ratio
        fig.update_xaxes(scaleanchor="y", scaleratio=1)
        
        return fig

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="HKA 2024 Wind Rose Flower",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stSelectbox > label {
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("🌸 Hong Kong International Airport 2024 Wind Rose Flower")
    st.markdown("*Interactive wind pattern visualization with seasonal colors*")
    
    # Initialize visualizer
    viz = StreamlitWindFlowerVisualizer()
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Month selection
        month_options = ["All Months"] + [f"Month {i}" for i in range(1, 13)]
        selected_month = st.selectbox(
            "Select Month to Display:",
            month_options,
            index=0
        )
        
        target_month = None if selected_month == "All Months" else int(selected_month.split()[1])
        
        st.markdown("---")
        st.markdown("### 📊 Legend")
        st.markdown("**Seasons:**")
        st.markdown("🌸 **Spring** (Mar-May): Pink")
        st.markdown("🌿 **Summer** (Jun-Aug): Green") 
        st.markdown("🍂 **Autumn** (Sep-Nov): Orange")
        st.markdown("❄️ **Winter** (Dec-Feb): Blue")
        
        st.markdown("**Visual Mapping:**")
        st.markdown("• **Angle**: Wind direction")
        st.markdown("• **Distance**: Month + wind speed")
        st.markdown("• **Size**: Wind speed intensity")
        st.markdown("• **Color**: Season")
    
    # Load data
    try:
        with st.spinner("Loading wind data..."):
            df_direction = viz.parse_xml_file('daily_HKA_PDIR_ALL - 副本.xml')
            df_speed = viz.parse_xml_file('daily_HKA_WSPD_ALL - 副本.xml')
        
        if df_direction.empty or df_speed.empty:
            st.error("Could not load wind data files. Please ensure XML files are in the same directory.")
            return
        
        # Create and display plot
        fig = viz.create_wind_flower_plot(df_direction, df_speed, target_month)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df_direction))
        
        with col2:
            avg_speed = df_speed['value'].mean()
            st.metric("Average Wind Speed", f"{avg_speed:.1f} km/h")
        
        with col3:
            max_speed = df_speed['value'].max()
            st.metric("Maximum Wind Speed", f"{max_speed:.1f} km/h")
        
        # Data table
        with st.expander("📋 View Raw Data"):
            merged_data = pd.merge(
                df_direction[['year', 'month', 'day', 'value']], 
                df_speed[['year', 'month', 'day', 'value']], 
                on=['year', 'month', 'day'], 
                suffixes=('_direction', '_speed')
            )
            
            if target_month:
                merged_data = merged_data[merged_data['month'] == target_month]
            
            st.dataframe(
                merged_data.rename(columns={
                    'value_direction': 'Wind Direction (°)',
                    'value_speed': 'Wind Speed (km/h)'
                }),
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error loading application: {str(e)}")
        st.info("Please ensure the XML data files are in the same directory as this script.")

if __name__ == "__main__":
    main()