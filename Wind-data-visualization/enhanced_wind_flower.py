#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
香港国际机场2024年风向风速数据可视化 - 增强版
"风之花朵" - 精美极坐标年轮图

特色功能：
- 季节色彩渐变
- 月份环状分布
- 艺术化点云效果
- 专业的图例和标注

日期：2025年9月21日
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import LineCollection
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持和高质量渲染
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

class EnhancedWindFlowerVisualizer:
    """增强版风之花朵可视化器"""
    
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
        
        print(f"📊 数据概览:")
        print(f"   风向范围: {self.combined_data['direction'].min():.1f}° - {self.combined_data['direction'].max():.1f}°")
        print(f"   风速范围: {self.combined_data['speed'].min():.1f} - {self.combined_data['speed'].max():.1f} km/h")
        print(f"   时间范围: {self.combined_data['date'].min().strftime('%Y-%m-%d')} - {self.combined_data['date'].max().strftime('%Y-%m-%d')}")
        print(f"   总记录数: {len(self.combined_data)}")
        
        return self.combined_data
    
    def create_enhanced_wind_flower(self, save_path="香港机场2024年精美风之花朵.png"):
        """创建增强版风之花朵可视化"""
        print("🌸 正在创建精美风之花朵可视化...")
        
        # 创建图形
        fig = plt.figure(figsize=(20, 20), facecolor='#0a0a0a')
        ax = plt.subplot(111, projection='polar', facecolor='#0a0a0a')
        
        # 定义精美的季节色彩
        season_palettes = {
            'Spring': ['#FFB3E6', '#FF80DF', '#FF4DD8', '#FF1AD1'],  # 樱花粉
            'Summer': ['#B3FFB3', '#80FF80', '#4DFF4D', '#1AFF1A'],  # 翠绿色
            'Autumn': ['#FFD1B3', '#FFBB80', '#FFA54D', '#FF8F1A'],  # 金橙色  
            'Winter': ['#B3E6FF', '#80D9FF', '#4DCCFF', '#1ABFFF']   # 冰蓝色
        }
        
        # 为每个数据点创建精美的可视化
        for month in range(1, 13):
            month_data = self.combined_data[self.combined_data['month'] == month]
            
            if len(month_data) == 0:
                continue
            
            # 获取季节和对应颜色
            season = month_data.iloc[0]['season']
            color_palette = season_palettes[season]
            color_idx = (month - 1) % 4
            main_color = color_palette[color_idx]
            
            # 转换风向为弧度
            wind_directions_rad = np.deg2rad(90 - month_data['direction'])
            
            # 计算半径位置（月份环）
            base_radius = month * 1.0
            max_speed = self.combined_data['speed'].max()
            min_speed = self.combined_data['speed'].min()
            
            # 风速映射到半径变化
            speed_normalized = (month_data['speed'] - min_speed) / (max_speed - min_speed)
            radii = base_radius + speed_normalized * 0.8
            
            # 创建渐变效果的点
            for i, (angle, radius, speed) in enumerate(zip(wind_directions_rad, radii, month_data['speed'])):
                # 点的大小根据风速调整
                point_size = 20 + speed * 8
                
                # 添加光晕效果
                ax.scatter(angle, radius, s=point_size * 3, c=main_color, 
                          alpha=0.1, edgecolors='none')
                ax.scatter(angle, radius, s=point_size * 1.5, c=main_color, 
                          alpha=0.3, edgecolors='none')
                ax.scatter(angle, radius, s=point_size, c=main_color, 
                          alpha=0.8, edgecolors='white', linewidth=0.5)
        
        # 添加精美的同心圆环
        for month in range(1, 13):
            circle_color = '#ffffff'
            circle_alpha = 0.15
            
            # 主圆环
            circle = Circle((0, 0), month * 1.0, fill=False, 
                          color=circle_color, alpha=circle_alpha, linewidth=1)
            ax.add_patch(circle)
        
        # 添加月份标签（更加精美）
        month_names = ['1月', '2月', '3月', '4月', '5月', '6月', 
                      '7月', '8月', '9月', '10月', '11月', '12月']
        
        for month in range(1, 13):
            radius_pos = month * 1.0 + 0.3
            ax.text(np.pi/2, radius_pos, month_names[month-1], 
                   ha='center', va='center', color='white', 
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # 设置极坐标样式
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # 设置角度标签
        ax.set_thetagrids(np.arange(0, 360, 45), 
                         ['北 N', '东北 NE', '东 E', '东南 SE', 
                          '南 S', '西南 SW', '西 W', '西北 NW'],
                         fontsize=14, color='white', fontweight='bold')
        
        # 设置半径范围和标签
        ax.set_ylim(0, 14)
        ax.set_yticks(np.arange(2, 14, 2))
        ax.set_yticklabels([f'{i}月环' for i in np.arange(2, 14, 2)], 
                          color='white', fontsize=10)
        
        # 美化网格
        ax.grid(True, alpha=0.2, color='white', linestyle='--')
        ax.set_facecolor('#0a0a0a')
        
        # 精美标题
        title_text = '🌸 香港国际机场2024年风之花朵 🌸\n' + \
                    'Wind Rose Flower - Hong Kong International Airport 2024\n' + \
                    '每片花瓣诉说着天空的故事'
        
        plt.suptitle(title_text, fontsize=24, color='white', 
                    y=0.95, fontweight='bold', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.8))
        
        # 创建季节色彩图例
        season_legend_elements = []
        for season, colors in season_palettes.items():
            season_legend_elements.append(
                plt.scatter([], [], s=100, c=colors[1], alpha=0.8, 
                          edgecolors='white', label=f'{season}'))
        
        legend1 = ax.legend(handles=season_legend_elements, 
                           title='🌻 季节色彩 Seasonal Colors', 
                           loc='upper left', bbox_to_anchor=(-0.1, 1.0),
                           title_fontsize=14, fontsize=12,
                           facecolor='black', edgecolor='white', framealpha=0.9)
        legend1.get_title().set_color('white')
        for text in legend1.get_texts():
            text.set_color('white')
        
        # 风速强度图例
        speed_legend_elements = []
        speeds = [10, 15, 20, 25, 30]
        for speed in speeds:
            point_size = 20 + speed * 8
            speed_legend_elements.append(
                plt.scatter([], [], s=point_size, c='white', alpha=0.8, 
                          edgecolors='gray', label=f'{speed} km/h'))
        
        legend2 = ax.legend(handles=speed_legend_elements, 
                           title='💨 风速强度 Wind Speed', 
                           loc='upper right', bbox_to_anchor=(1.1, 1.0),
                           title_fontsize=14, fontsize=12,
                           facecolor='black', edgecolor='white', framealpha=0.9)
        legend2.get_title().set_color('white')
        for text in legend2.get_texts():
            text.set_color('white')
        
        # 数据统计信息
        stats_text = f"""
数据统计 Data Statistics:
• 总记录数 Total Records: {len(self.combined_data)}
• 风向范围 Wind Direction: {self.combined_data['direction'].min():.0f}° - {self.combined_data['direction'].max():.0f}°
• 风速范围 Wind Speed: {self.combined_data['speed'].min():.1f} - {self.combined_data['speed'].max():.1f} km/h
• 平均风速 Average Speed: {self.combined_data['speed'].mean():.1f} km/h

可视化说明 Visualization Guide:
• 每个同心圆代表一个月份
• 点的角度表示风向，距离中心远近表示风速
• 颜色按季节分布：春粉、夏绿、秋橙、冬蓝
• 点的大小也反映风速强度
        """
        
        plt.figtext(0.02, 0.02, stats_text.strip(), 
                   fontsize=11, color='white', 
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.8),
                   verticalalignment='bottom')
        
        # 艺术签名
        plt.figtext(0.98, 0.02, 
                   'Designed with ❤️ by GitHub Copilot\nPROGRAMMING FOR ARTISTS AND DESIGNERS',
                   fontsize=10, color='#FFD700', style='italic',
                   horizontalalignment='right', verticalalignment='bottom')
        
        # 保存高质量图像
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='none', 
                   pad_inches=0.5)
        print(f"💾 精美图像已保存为: {save_path}")
        
        # 显示图像
        plt.show()
        
        return fig, ax

# 主程序
if __name__ == "__main__":
    # 初始化增强版可视化器
    visualizer = EnhancedWindFlowerVisualizer()
    
    # 数据文件路径
    wind_dir_file = "daily_HKA_PDIR_ALL - 副本.xml"
    wind_speed_file = "daily_HKA_WSPD_ALL - 副本.xml"
    
    try:
        # 解析和处理数据
        dir_data, speed_data = visualizer.parse_xml_data(wind_dir_file, wind_speed_file)
        combined_data = visualizer.preprocess_data()
        print("\n🎉 数据解析和预处理完成！")
        
        # 创建精美的风之花朵可视化
        print("\n" + "="*60)
        fig, ax = visualizer.create_enhanced_wind_flower()
        
        print("\n🌟 精美的风之花朵可视化创建完成！")
        print("这个艺术化的数据可视化展现了香港国际机场2024年的风向风速模式，")
        print("将科学数据转化为了美丽的花朵图案！ 🌸✨")
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        print("请确保XML文件在当前目录中")
    except Exception as e:
        print(f"❌ 处理数据时出错: {e}")
        import traceback
        traceback.print_exc()