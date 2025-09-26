#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hong Kong International Airport 2024 Wind Data Interactive Visualization
"Wind Flower" - Animation + Interactive Version

Features:
- Monthly animation showing data evolution
- Mouse hover for detailed information
- Seasonal color gradient system
- Play/Pause controls

Implementation: Plotly + Dash
Date: September 21, 2025
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import warnings
warnings.filterwarnings('ignore')

class InteractiveWindFlowerVisualizer:
    """Interactive Wind Flower Visualizer"""
    
    def __init__(self):
        self.wind_direction_data = None
        self.wind_speed_data = None
        self.combined_data = None
        self.app = None
        
    def parse_xml_data(self, wind_dir_file, wind_speed_file):
        """Parse XML files and extract data"""
        print("📂 Parsing XML data files...")
        
        # 解析风向数据
        tree_dir = ET.parse(wind_dir_file)
        root_dir = tree_dir.getroot()
        
        # 解析风速数据
        tree_speed = ET.parse(wind_speed_file)
        root_speed = tree_speed.getroot()
        
        # 提取风向数据
        dir_data = []
        for row in root_dir.findall(".//ss:Row", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}):
            cells = row.findall(".//ss:Cell/ss:Data", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"})
            if len(cells) >= 4:
                try:
                    year = int(cells[0].text)
                    month = int(cells[1].text)
                    day = int(cells[2].text)
                    direction = float(cells[3].text)
                    if year == 2024:
                        dir_data.append([year, month, day, direction])
                except (ValueError, TypeError):
                    continue
        
        # 提取风速数据
        speed_data = []
        for row in root_speed.findall(".//ss:Row", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}):
            cells = row.findall(".//ss:Cell/ss:Data", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"})
            if len(cells) >= 4:
                try:
                    year = int(cells[0].text)
                    month = int(cells[1].text)
                    day = int(cells[2].text)
                    speed = float(cells[3].text)
                    if year == 2024:
                        speed_data.append([year, month, day, speed])
                except (ValueError, TypeError):
                    continue
        
        # 转换为DataFrame
        self.wind_direction_data = pd.DataFrame(dir_data, columns=['year', 'month', 'day', 'direction'])
        self.wind_speed_data = pd.DataFrame(speed_data, columns=['year', 'month', 'day', 'speed'])
        
        print(f"✅ Wind direction records: {len(self.wind_direction_data)}")
        print(f"✅ Wind speed records: {len(self.wind_speed_data)}")
        
        return self.wind_direction_data, self.wind_speed_data
    
    def preprocess_data(self):
        """Data preprocessing and cleaning"""
        print("🔧 Processing data preprocessing...")
        
        # 合并风向和风速数据
        self.combined_data = pd.merge(
            self.wind_direction_data, 
            self.wind_speed_data,
            on=['year', 'month', 'day'],
            how='inner'
        )
        
        # 创建日期列
        self.combined_data['date'] = pd.to_datetime(
            self.combined_data[['year', 'month', 'day']]
        )
        
        # 计算季节
        def get_season(month):
            if month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            elif month in [9, 10, 11]:
                return 'Autumn'
            else:
                return 'Winter'
        
        self.combined_data['season'] = self.combined_data['month'].apply(get_season)
        
        # 添加颜色映射
        season_palettes = {
            'Spring': ['#FFB3E6', '#FF80DF', '#FF4DD8', '#FF1AD1'],
            'Summer': ['#B3FFB3', '#80FF80', '#4DFF4D', '#1AFF1A'],
            'Autumn': ['#FFD1B3', '#FFBB80', '#FFA54D', '#FF8F1A'],
            'Winter': ['#B3E6FF', '#80D9FF', '#4DCCFF', '#1ABFFF']
        }
        
        month_colors = {
            3: season_palettes['Spring'][2], 4: season_palettes['Spring'][3], 5: season_palettes['Spring'][0],
            6: season_palettes['Summer'][1], 7: season_palettes['Summer'][2], 8: season_palettes['Summer'][3],
            9: season_palettes['Autumn'][0], 10: season_palettes['Autumn'][1], 11: season_palettes['Autumn'][2],
            12: season_palettes['Winter'][3], 1: season_palettes['Winter'][0], 2: season_palettes['Winter'][1]
        }
        
        self.combined_data['color'] = self.combined_data['month'].map(month_colors)
        
        # 转换为极坐标
        self.combined_data['theta'] = 90 - self.combined_data['direction']  # 转换为数学角度
        self.combined_data['r'] = self.combined_data['month'] + \
                                 (self.combined_data['speed'] - self.combined_data['speed'].min()) / \
                                 (self.combined_data['speed'].max() - self.combined_data['speed'].min()) * 0.8
        
        # 添加悬停信息
        self.combined_data['hover_text'] = self.combined_data.apply(
            lambda row: f"Date: {row['date'].strftime('%Y-%m-%d')}<br>" +
                       f"Wind Direction: {row['direction']:.1f}°<br>" +
                       f"Wind Speed: {row['speed']:.1f} km/h<br>" +
                       f"Season: {row['season']}<br>" +
                       f"Month: {row['month']}",
            axis=1
        )
        
        print(f"📊 Data preprocessing completed, total records: {len(self.combined_data)}")
        return self.combined_data
    
    def create_interactive_app(self):
        """Create interactive Dash application"""
        
        # 初始化Dash应用
        self.app = dash.Dash(__name__)
        
        # 应用布局
        self.app.layout = html.Div([
            html.H1("Hong Kong International Airport 2024 Wind Rose Visualization", 
                   style={
                       'textAlign': 'center', 
                       'color': 'white', 
                       'backgroundColor': 'black',
                       'fontFamily': 'Bowlby One, Arial, sans-serif',
                       'fontSize': '22px',
                       'fontWeight': 'normal',
                       'padding': '20px',
                       'margin': '0'
                   }),
            
            # 紧凑控制面板
            html.Div([
                html.Div([
                    # Time Period 标签
                    html.Label("Time Period", 
                              style={'color': '#B3E6FF', 'fontSize': '10px', 'fontWeight': '500', 'marginBottom': '5px', 'display': 'block'}),
                    
                    # 时间滑块和按钮同行布局
                    html.Div([
                        # 时间滑块（占更大空间，延伸到接近右边）
                        html.Div([
                            dcc.Slider(
                                id='month-slider',
                                min=1,
                                max=12,
                                step=1,
                                value=12,
                                marks={i: f'{i}' for i in range(1, 13)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                        ], style={
                            'width': 'calc(100% - 240px)', 
                            'display': 'inline-block', 
                            'verticalAlign': 'middle',
                            'paddingRight': '15px'
                        }),
                        
                        # 控制按钮（紧贴在数字12的右边）
                        html.Div([
                            html.Button('▶ Play', id='play-button', n_clicks=0,
                                       style={
                                           'margin': '0 6px', 
                                           'padding': '4px 8px', 
                                           'fontSize': '9px',
                                           'backgroundColor': '#2E7D32',
                                           'color': 'white',
                                           'border': 'none',
                                           'borderRadius': '3px',
                                           'cursor': 'pointer'
                                       }),
                            html.Button('⏸ Pause', id='pause-button', n_clicks=0,
                                       style={
                                           'margin': '0 6px', 
                                           'padding': '4px 8px', 
                                           'fontSize': '9px',
                                           'backgroundColor': '#F57C00',
                                           'color': 'white',
                                           'border': 'none',
                                           'borderRadius': '3px',
                                           'cursor': 'pointer'
                                       }),
                            html.Button('⟲ Reset', id='reset-button', n_clicks=0,
                                       style={
                                           'margin': '0 6px', 
                                           'padding': '4px 8px', 
                                           'fontSize': '9px',
                                           'backgroundColor': '#5D4037',
                                           'color': 'white',
                                           'border': 'none',
                                           'borderRadius': '3px',
                                           'cursor': 'pointer'
                                       }),
                        ], style={
                            'width': '240px',
                            'display': 'inline-block', 
                            'verticalAlign': 'middle',
                            'textAlign': 'left',
                            'paddingLeft': '0px'
                        })
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'width': '100%'
                    })
                ], style={
                    'maxWidth': '1000px',
                    'margin': '0 auto',
                    'padding': '0 25px'
                })
            ], style={
                'backgroundColor': '#1A1A1A', 
                'padding': '15px 0',
                'borderBottom': '1px solid #333'
            }),
            
            # 主图表区域
            html.Div([
                # 图表小标题（左对齐，缩小字体）
                html.Div([
                    html.Div(id='chart-subtitle', children="Wind Flower - Display up to Month 12", 
                           style={
                               'color': '#B3E6FF', 
                               'fontSize': '12px', 
                               'marginBottom': '10px',
                               'marginLeft': '25px',
                               'textAlign': 'left',
                               'lineHeight': '1.4'
                           })
                ]),
                
                # 图表和内嵌注释
                html.Div([
                    dcc.Graph(id='wind-flower-plot', style={
                        'height': '720px',
                        'backgroundColor': 'transparent'
                    }),
                    
                    # 左下角注释框（内嵌在图表区域）
                    html.Div([
                        html.Div([
                            # 标题部分 - 黄色大标题
                            html.Div([
                                html.Span("Data Statistics & Visualization Guide", style={'color': '#FFD700', 'fontSize': '14px', 'fontWeight': 'bold'})
                            ], style={'marginBottom': '8px'}),
                            
                            # 数据统计 - 白色小字
                            html.Div([
                                html.Span("• Total Records: 366  • Direction Range: 10°-360°", style={'color': 'white', 'fontSize': '9px', 'display': 'block', 'marginBottom': '2px'}),
                                html.Span("• Speed Range: 7.9-32.0 km/h  • Average Speed: 15.5 km/h", style={'color': 'white', 'fontSize': '9px', 'display': 'block'})
                            ], style={'marginBottom': '6px'}),
                            
                            # 可视化原理说明 - 白色文字
                            html.Div([
                                html.Span("Visualization Principle: Concentric Circles=Months (Jan=Inner→Dec=Outer)", style={'color': 'white', 'fontSize': '9px', 'display': 'block', 'marginBottom': '2px'}),
                                html.Span("Angle=Direction | Distance=Speed", style={'color': 'white', 'fontSize': '9px', 'display': 'block'})
                            ], style={'marginBottom': '8px'}),
                            
                            # 季节色彩渐变系统标题 - 白色
                            html.Div([
                                html.Span("Seasonal Color Gradient System", style={'color': 'white', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ], style={'marginBottom': '6px'}),
                            
                            # 四季颜色图例 - 2x2网格布局
                            html.Div([
                                # 第一行：Spring 和 Summer
                                html.Div([
                                    # Spring
                                    html.Div([
                                        html.Div([
                                            html.Span("■", style={'color': '#FF69B4', 'fontSize': '12px', 'marginRight': '4px'}),
                                            html.Span("Spring", style={'color': 'white', 'fontSize': '10px', 'fontWeight': 'bold'})
                                        ], style={'marginBottom': '3px'}),
                                        html.Div([
                                            html.Span("●", style={'color': '#FF1493', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Mar", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#FF69B4', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Apr", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#FFB6C1', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("May", style={'color': 'white', 'fontSize': '8px'}),
                                        ])
                                    ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top'}),
                                    
                                    # Summer
                                    html.Div([
                                        html.Div([
                                            html.Span("■", style={'color': '#32CD32', 'fontSize': '12px', 'marginRight': '4px'}),
                                            html.Span("Summer", style={'color': 'white', 'fontSize': '10px', 'fontWeight': 'bold'})
                                        ], style={'marginBottom': '3px'}),
                                        html.Div([
                                            html.Span("●", style={'color': '#00FF00', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Jun", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#32CD32', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Jul", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#90EE90', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Aug", style={'color': 'white', 'fontSize': '8px'}),
                                        ])
                                    ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top', 'marginLeft': '4%'}),
                                ], style={'marginBottom': '4px'}),
                                
                                # 第二行：Autumn 和 Winter
                                html.Div([
                                    # Autumn
                                    html.Div([
                                        html.Div([
                                            html.Span("■", style={'color': '#FF8C00', 'fontSize': '12px', 'marginRight': '4px'}),
                                            html.Span("Autumn", style={'color': 'white', 'fontSize': '10px', 'fontWeight': 'bold'})
                                        ], style={'marginBottom': '3px'}),
                                        html.Div([
                                            html.Span("●", style={'color': '#FF4500', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Sep", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#FF8C00', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Oct", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#FFB84D', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Nov", style={'color': 'white', 'fontSize': '8px'}),
                                        ])
                                    ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top'}),
                                    
                                    # Winter
                                    html.Div([
                                        html.Div([
                                            html.Span("■", style={'color': '#1E90FF', 'fontSize': '12px', 'marginRight': '4px'}),
                                            html.Span("Winter", style={'color': 'white', 'fontSize': '10px', 'fontWeight': 'bold'})
                                        ], style={'marginBottom': '3px'}),
                                        html.Div([
                                            html.Span("●", style={'color': '#00BFFF', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Dec", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#1E90FF', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Jan", style={'color': 'white', 'fontSize': '8px', 'marginRight': '8px'}),
                                            html.Span("●", style={'color': '#87CEEB', 'fontSize': '8px', 'marginRight': '2px'}),
                                            html.Span("Feb", style={'color': 'white', 'fontSize': '8px'}),
                                        ])
                                    ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top', 'marginLeft': '4%'}),
                                ]),
                                
                                # Note说明
                                html.Div([
                                    html.Span("Note: Dot size reflects wind speed intensity, color indicates month/season", 
                                             style={'color': '#888', 'fontSize': '8px', 'fontStyle': 'italic'})
                                ], style={'marginTop': '6px'})
                            ]),
                            
                        ], style={
                            'position': 'absolute',
                            'bottom': '25px',
                            'left': '25px',
                            'width': '420px',
                            'height': '180px',
                            'backgroundColor': 'rgba(0, 0, 0, 0.9)',
                            'border': '0.5px solid #FFD700',
                            'borderRadius': '8px',
                            'padding': '12px 10px 24px 12px',
                            'fontFamily': 'Arial, sans-serif',
                            'zIndex': '1000',
                            'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.8)',
                            'overflow': 'hidden'
                        })
                    ], style={'position': 'relative'})
                ])
            ], style={
                'backgroundColor': '#0F0F0F',
                'padding': '10px 0 20px 0',
                'margin': '0'
            }),

            
            # 现代化底部注释
            html.Div([
                html.Span("✦ Dot size reflects wind speed intensity, color indicates month/season", 
                         style={
                             'color': '#888', 
                             'fontSize': '9px', 
                             'fontStyle': 'italic',
                             'fontWeight': '300'
                         })
            ], style={
                'position': 'fixed',
                'bottom': '15px',
                'left': '30px',
                'zIndex': '1000',
                'backgroundColor': 'rgba(0, 0, 0, 0.7)',
                'padding': '4px 8px',
                'borderRadius': '4px'
            }),
            
            dcc.Interval(
                id='animation-interval',
                interval=1000,  # 1秒更新一次
                n_intervals=0,
                disabled=True  # 默认禁用
            ),
            
            html.Div(id='animation-state', style={'display': 'none'}, children='stopped'),
            
        ], style={
            'backgroundColor': '#000000',
            'minHeight': '100vh',
            'fontFamily': 'Arial, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        })
        
        # 回调函数
        @self.app.callback(
            [Output('wind-flower-plot', 'figure'),
             Output('animation-interval', 'disabled'),
             Output('animation-state', 'children'),
             Output('month-slider', 'value'),
             Output('chart-subtitle', 'children')],
            [Input('month-slider', 'value'),
             Input('play-button', 'n_clicks'),
             Input('pause-button', 'n_clicks'),
             Input('reset-button', 'n_clicks'),
             Input('animation-interval', 'n_intervals')],
            prevent_initial_call=False
        )
        def update_plot(selected_month, play_clicks, pause_clicks, reset_clicks, n_intervals):
            
            ctx = dash.callback_context
            if not ctx.triggered:
                trigger = 'month-slider'
            else:
                trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # 动画状态管理
            current_state = 'stopped'
            animation_disabled = True
            current_month = selected_month
            
            if trigger == 'play-button':
                current_state = 'playing'
                animation_disabled = False
                if current_month >= 12:
                    current_month = 1
            elif trigger == 'pause-button':
                current_state = 'paused'
                animation_disabled = True
            elif trigger == 'reset-button':
                current_state = 'stopped'
                animation_disabled = True
                current_month = 1
            elif trigger == 'animation-interval':
                current_state = 'playing'
                animation_disabled = False
                current_month = min(current_month + 1, 12)
                if current_month >= 12:
                    animation_disabled = True
                    current_state = 'completed'
            
            # 筛选数据
            filtered_data = self.combined_data[self.combined_data['month'] <= current_month]
            
            # 计算统计信息
            total_records = len(filtered_data)
            avg_speed = filtered_data['speed'].mean() if len(filtered_data) > 0 else 0
            max_speed = filtered_data['speed'].max() if len(filtered_data) > 0 else 0
            dominant_direction = filtered_data['direction'].mode().iloc[0] if len(filtered_data) > 0 else 0
            
            # 创建极坐标图
            fig = go.Figure()
            
            # 添加数据点
            fig.add_trace(go.Scatterpolar(
                r=filtered_data['r'],
                theta=filtered_data['theta'],
                mode='markers',
                marker=dict(
                    size=filtered_data['speed'] / 2 + 5,  # 根据风速调整大小
                    color=filtered_data['color'],
                    opacity=0.8,
                    line=dict(width=1, color='white')
                ),
                text=filtered_data['hover_text'],
                hovertemplate='%{text}<extra></extra>',
                name='Wind Direction & Speed Data',
                showlegend=False
            ))
            
            # 添加同心圆环（月份参考）
            for month in range(1, 13):
                circle_r = [month] * 360
                circle_theta = list(range(360))
                fig.add_trace(go.Scatterpolar(
                    r=circle_r,
                    theta=circle_theta,
                    mode='lines',
                    line=dict(color='white', width=0.5, dash='dot'),
                    opacity=0.3,
                    hoverinfo='skip',
                    showlegend=False
                ))
            
            # 添加月份标签在180°线位置
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for month in range(1, 13):
                fig.add_trace(go.Scatterpolar(
                    r=[month],
                    theta=[180],  # 180°线位置
                    mode='text',
                    text=[month_names[month-1]],
                    textfont=dict(size=10, color='white'),
                    textposition='middle center',
                    hoverinfo='skip',
                    showlegend=False
                ))
            
            # 设置布局
            fig.update_layout(
                title="",  # 移除重复的标题
                title_font_size=20,
                title_font_color='white',
                paper_bgcolor='black',
                plot_bgcolor='black',
                polar=dict(
                    bgcolor='black',
                    radialaxis=dict(
                        visible=True,
                        range=[0, 14],
                        showline=True,
                        linecolor='white',
                        gridcolor='white',
                        gridwidth=0.5,
                        tick0=0,
                        dtick=2,
                        tickfont=dict(color='white', size=10),
                        showticklabels=False  # 隐藏径向轴刻度标签
                    ),
                    angularaxis=dict(
                        visible=True,
                        tickfont_size=12,
                        tickfont_color='white',
                        direction='counterclockwise',
                        rotation=90
                    )
                ),
                font=dict(color='white'),
                height=700,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            subtitle = f"Wind Flower - Display up to Month {current_month}<br>Data Points: {total_records} | Avg Speed: {avg_speed:.1f}km/h | Max Speed: {max_speed:.1f}km/h | Dominant Direction: {dominant_direction:.0f}°"
            return fig, animation_disabled, current_state, current_month, subtitle
        
        return self.app

# Main function
def main():
    """Main function"""
    print("🌸 Starting interactive Wind Flower visualization...")
    
    # Create visualizer
    visualizer = InteractiveWindFlowerVisualizer()
    
    # Parse data
    visualizer.parse_xml_data(
        'daily_HKA_PDIR_ALL - 副本.xml',
        'daily_HKA_WSPD_ALL - 副本.xml'
    )
    
    # Preprocess data
    visualizer.preprocess_data()
    
    # Create interactive application
    app = visualizer.create_interactive_app()
    
    print("\n🚀 Starting Web server...")
    print("📱 Please open in browser: http://127.0.0.1:8050")
    print("🎮 Features:")
    print("   • Drag slider to select display month")
    print("   • Click 'Play Animation' to see monthly evolution")
    print("   • Hover over data points for details")
    print("   • Point size represents wind speed, color represents season")
    
    # Run application
    app.run(debug=True, host='127.0.0.1', port=8050)

if __name__ == "__main__":
    main()