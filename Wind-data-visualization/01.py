#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
香港国际机场2024年风向风速数据可视化
"风之花朵" - 极坐标年轮图

日期：2025年9月21日
数据来源：香港国际机场气象数据
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Circle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class WindDataVisualizer:
    """香港机场风数据可视化类"""
    
    def __init__(self):
        self.wind_direction_data = None
        self.wind_speed_data = None
        self.combined_data = None
        
    def parse_xml_data(self, wind_dir_file, wind_speed_file):
        """解析XML文件并提取数据"""
        print("📂 正在解析XML数据文件...")
        
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
                    if year == 2024:  # 只处理2024年数据
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
                    if year == 2024:  # 只处理2024年数据
                        speed_data.append([year, month, day, speed])
                except (ValueError, TypeError):
                    continue
        
        # 转换为DataFrame
        self.wind_direction_data = pd.DataFrame(dir_data, columns=['year', 'month', 'day', 'direction'])
        self.wind_speed_data = pd.DataFrame(speed_data, columns=['year', 'month', 'day', 'speed'])
        
        print(f"✅ 风向数据记录数: {len(self.wind_direction_data)}")
        print(f"✅ 风速数据记录数: {len(self.wind_speed_data)}")
        
        return self.wind_direction_data, self.wind_speed_data
    
    def preprocess_data(self):
        """数据预处理和清洗"""
        print("🔧 正在进行数据预处理...")
        
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
        
        # 计算一年中的第几天（用于角度计算）
        self.combined_data['day_of_year'] = self.combined_data['date'].dt.dayofyear
        
        # 数据范围检查
        print(f"📊 数据概览:")
        print(f"   风向范围: {self.combined_data['direction'].min():.1f}° - {self.combined_data['direction'].max():.1f}°")
        print(f"   风速范围: {self.combined_data['speed'].min():.1f} - {self.combined_data['speed'].max():.1f} km/h")
        print(f"   时间范围: {self.combined_data['date'].min().strftime('%Y-%m-%d')} - {self.combined_data['date'].max().strftime('%Y-%m-%d')}")
        print(f"   总记录数: {len(self.combined_data)}")
        
        return self.combined_data
    
    def create_wind_flower(self, save_path="香港机场2024年风之花朵.png"):
        """创建"风之花朵"极坐标可视化"""
        print("🌸 正在创建风之花朵可视化...")
        
        # 设置图形大小和样式
        fig, ax = plt.subplots(figsize=(16, 16), subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # 定义季节色彩映射
        season_colors = {
            'spring': ['#FFE5E5', '#FFCCCC', '#FF9999', '#FF6666'],  # 春季：粉色系
            'summer': ['#E5F5E5', '#CCFFCC', '#99FF99', '#66FF66'],  # 夏季：绿色系
            'autumn': ['#FFF5E5', '#FFEBCC', '#FFD699', '#FFC266'],  # 秋季：橙色系
            'winter': ['#E5F0FF', '#CCE5FF', '#99D6FF', '#66C7FF']   # 冬季：蓝色系
        }
        
        # 为每个月定义颜色
        month_colors = []
        for month in range(1, 13):
            if month in [3, 4, 5]:  # 春季
                color_idx = (month - 3) % 4
                month_colors.append(season_colors['spring'][color_idx])
            elif month in [6, 7, 8]:  # 夏季
                color_idx = (month - 6) % 4
                month_colors.append(season_colors['summer'][color_idx])
            elif month in [9, 10, 11]:  # 秋季
                color_idx = (month - 9) % 4
                month_colors.append(season_colors['autumn'][color_idx])
            else:  # 冬季
                color_idx = (month - 12) % 4 if month == 12 else (month - 1) % 4
                month_colors.append(season_colors['winter'][color_idx])
        
        # 绘制每个月的数据
        for month in range(1, 13):
            month_data = self.combined_data[self.combined_data['month'] == month]
            
            if len(month_data) == 0:
                continue
                
            # 转换风向为弧度（风向是指风吹来的方向，需要转换为数学角度）
            # 气象风向：北=0°，东=90°，南=180°，西=270°
            # 数学角度：东=0°，北=90°，西=180°，南=270°
            wind_directions_rad = np.deg2rad(90 - month_data['direction'])
            
            # 风速归一化到适当的半径范围（每个月一个环）
            # 基础半径：每个月占用一定的环宽度
            base_radius = month * 0.8
            max_speed = self.combined_data['speed'].max()
            min_speed = self.combined_data['speed'].min()
            
            # 风速映射到半径增量
            radius_increment = 0.6 * (month_data['speed'] - min_speed) / (max_speed - min_speed)
            radii = base_radius + radius_increment
            
            # 绘制风向风速点
            scatter = ax.scatter(
                wind_directions_rad, 
                radii,
                c=month_colors[month-1],
                s=month_data['speed'] * 3,  # 点的大小也反映风速
                alpha=0.7,
                edgecolors='white',
                linewidth=0.5,
                label=f'{month}月'
            )
        
        # 添加同心圆环来表示月份
        for month in range(1, 13):
            circle = Circle((0, 0), month * 0.8, fill=False, 
                          color='white', alpha=0.3, linewidth=0.5)
            ax.add_patch(circle)
            
            # 添加月份标签
            ax.text(np.pi/2, month * 0.8 + 0.2, f'{month}月', 
                   ha='center', va='center', color='white', fontsize=10)
        
        # 设置极坐标图的样式
        ax.set_theta_zero_location('N')  # 北方为0度
        ax.set_theta_direction(-1)  # 顺时针
        
        # 设置角度标签（风向）
        ax.set_thetagrids(np.arange(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        
        # 设置半径范围
        ax.set_ylim(0, 13)
        ax.set_yticks(np.arange(2, 13, 2))
        ax.set_yticklabels([f'{int(i*0.8)}' for i in np.arange(2, 13, 2)], color='white')
        
        # 美化坐标轴
        ax.grid(True, alpha=0.3, color='white')
        ax.set_facecolor('black')
        
        # 设置标题
        plt.title('🌸 香港国际机场2024年风之花朵 🌸\nWind Rose Flower - Hong Kong International Airport 2024', 
                 fontsize=20, color='white', pad=30, fontweight='bold')
        
        # 添加风速图例
        speed_legend_elements = []
        for speed in [10, 15, 20, 25, 30]:
            speed_legend_elements.append(
                plt.scatter([], [], s=speed*3, c='white', alpha=0.7, 
                          edgecolors='gray', label=f'{speed} km/h'))
        
        legend1 = ax.legend(handles=speed_legend_elements, 
                           title='风速 Wind Speed', 
                           loc='upper right', bbox_to_anchor=(1.15, 1.0),
                           title_fontsize=12, fontsize=10,
                           facecolor='black', edgecolor='white')
        legend1.get_title().set_color('white')
        for text in legend1.get_texts():
            text.set_color('white')
        
        # 添加说明文字
        plt.figtext(0.5, 0.02, 
                   '每个同心圆代表一个月份，点的位置代表风向，距离中心的远近代表风速强度\n' +
                   'Each concentric circle represents a month, point position shows wind direction, distance from center shows wind speed',
                   ha='center', fontsize=12, color='white', style='italic')
        
        # 保存图像
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        print(f"💾 图像已保存为: {save_path}")
        
        # 显示图像
        plt.show()
        
        return fig, ax

# 初始化可视化器
visualizer = WindDataVisualizer()

# 解析数据文件
wind_dir_file = "daily_HKA_PDIR_ALL - 副本.xml"
wind_speed_file = "daily_HKA_WSPD_ALL - 副本.xml"

try:
    dir_data, speed_data = visualizer.parse_xml_data(wind_dir_file, wind_speed_file)
    combined_data = visualizer.preprocess_data()
    print("\n🎉 数据解析和预处理完成！")
    
    # 显示前几行数据作为验证
    print("\n📋 数据样本:")
    print(combined_data.head(10).to_string(index=False))
    
    # 创建风之花朵可视化
    print("\n" + "="*50)
    fig, ax = visualizer.create_wind_flower()
    
except FileNotFoundError as e:
    print(f"❌ 文件未找到: {e}")
    print("请确保XML文件在当前目录中")
except Exception as e:
    print(f"❌ 处理数据时出错: {e}")
    import traceback
    traceback.print_exc()
