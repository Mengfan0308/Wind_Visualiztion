# METEOROLOGICAL DANDELION - 重新开始的艺术之旅
# Programming for Artists and Designers - 香港机场2024风数据蒲公英可视化
# 从Layer 0开始：简洁优雅的有机设计

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import platform

# 设置中文字体支持 - 修复方块字符问题
if platform.system() == 'Windows':
    # Windows系统优先使用微软雅黑
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong']
    plt.rcParams['font.family'] = 'sans-serif'
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'PingFang SC']
else:  # Linux
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

print("🌼 METEOROLOGICAL DANDELION - New Journey")
print("📍 Hong Kong International Airport 2024")
print("🎨 Organic Art Design from Layer 0\n")

class MeteorologicalDandelion:
    """Meteorological Dandelion - Elegant Organic Visualization"""
    
    def __init__(self):
        self.directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                          'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        
        # 有机色彩调色板
        self.palette = {
            'core': '#2C3E50',        # 深蓝灰 - 稳定的核心
            'stems': '#34495E',       # 蓝灰 - 月度茎干
            'tendrils': '#7F8C8D',    # 浅灰 - 方向触须
            'seeds': '#ECF0F1',       # 浅白 - 日数据种子
            'accent': '#E74C3C'       # 红色 - 强调色
        }
        
        print("✓ Dandelion system initialization complete")
        print("✓ Organic color palette loaded")

    def get_real_wind_data(self):
        """获取真实风数据 - 简化版本"""
        print("\n🌪️ Fetching real wind data...")
        
        try:
            # 使用之前成功的数据获取逻辑
            urls = {
                'direction': "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv",
                'speed': "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv"
            }
            
            datasets = {}
            for name, url in urls.items():
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    df = pd.read_csv(StringIO(response.text), encoding='utf-8-sig', skiprows=2)
                    datasets[name] = df
                    print(f"✓ {name} 数据获取成功")
                else:
                    raise Exception(f"数据下载失败: {response.status_code}")
            
            # 简化的数据处理
            df_processed = self._process_hko_data(datasets)
            print(f"✓ Data processing complete: {len(df_processed)} records")
            return df_processed
            
        except Exception as e:
            print(f"⚠️ 真实数据获取失败: {e}")
            print("🎨 使用艺术化的模拟数据...")
            return self._create_artistic_wind_data()

    def _process_hko_data(self, datasets):
        """处理香港天文台数据"""
        def clean_hko_df(df):
            # 找到年月日和数值列
            year_col = next((col for col in df.columns if '年' in col or 'year' in col.lower()), None)
            month_col = next((col for col in df.columns if '月' in col or 'month' in col.lower()), None)
            day_col = next((col for col in df.columns if '日' in col or 'day' in col.lower()), None)
            value_col = next((col for col in df.columns if '值' in col or 'value' in col.lower()), None)
            
            if not all([year_col, month_col, day_col, value_col]):
                raise ValueError("无法识别数据列")
            
            df_clean = df.dropna(subset=[year_col, month_col, day_col])
            df_clean['Date'] = (
                df_clean[year_col].astype(int).astype(str) + 
                df_clean[month_col].astype(int).astype(str).str.zfill(2) + 
                df_clean[day_col].astype(int).astype(str).str.zfill(2)
            )
            df_clean['Value'] = df_clean[value_col]
            df_clean = df_clean[df_clean['Value'] != '***'].dropna(subset=['Value'])
            
            return df_clean[['Date', 'Value']]
        
        # 处理风向和风速数据
        df_dir = clean_hko_df(datasets['direction'])
        df_speed = clean_hko_df(datasets['speed'])
        df_dir.columns = ['Date', 'Direction']
        df_speed.columns = ['Date', 'Speed']
        
        # 合并并筛选2024年数据
        df_merged = pd.merge(df_dir, df_speed, on='Date', how='inner')
        df_merged['Date'] = pd.to_datetime(df_merged['Date'], format='%Y%m%d')
        df_2024 = df_merged[df_merged['Date'].dt.year == 2024].copy()
        
        if df_2024.empty:
            latest_year = df_merged['Date'].dt.year.max()
            df_2024 = df_merged[df_merged['Date'].dt.year == latest_year].copy()
        
        # 转换风向角度为方向
        df_2024['Direction_Angle'] = pd.to_numeric(df_2024['Direction'], errors='coerce')
        df_2024['Direction_Sector'] = df_2024['Direction_Angle'].apply(self._angle_to_direction)
        df_2024['Speed'] = pd.to_numeric(df_2024['Speed'], errors='coerce')
        df_2024 = df_2024.dropna(subset=['Direction_Sector', 'Speed'])
        df_2024['Month'] = df_2024['Date'].dt.month
        
        return df_2024

    def _angle_to_direction(self, angle):
        """角度转16方位"""
        if pd.isna(angle):
            return None
        index = int((angle + 11.25) % 360 / 22.5)
        return self.directions[index]

    def _create_artistic_wind_data(self):
        """创建艺术化的风数据（备用方案）"""
        dates = pd.date_range('2024-01-01', '2024-12-31')
        wind_data = []
        
        for date in dates:
            month = date.month
            # 季节性风向模式
            if 6 <= month <= 8:  # 夏季：偏南风
                direction = np.random.choice(['S', 'SSW', 'SW', 'SE'], p=[0.4, 0.3, 0.2, 0.1])
            elif month in [12, 1, 2]:  # 冬季：偏北风
                direction = np.random.choice(['N', 'NNE', 'NE', 'NNW'], p=[0.4, 0.3, 0.2, 0.1])
            else:  # 春秋季：偏东风
                direction = np.random.choice(['E', 'ENE', 'ESE', 'NE'], p=[0.4, 0.25, 0.25, 0.1])
            
            speed = np.random.lognormal(2.3, 0.6)  # 艺术化的风速分布
            speed = np.clip(speed, 1, 35)
            
            wind_data.append({
                'Date': date,
                'Direction_Sector': direction,
                'Speed': speed,
                'Month': month,
                'Direction_Angle': self.directions.index(direction) * 22.5
            })
        
        return pd.DataFrame(wind_data)

    def calculate_layer0_centroid(self, df):
        """Calculate Layer 0: Core Center of Dandelion"""
        print("\n🎯 Calculating Layer 0: Dandelion Core...")
        
        # 计算月度向量合成
        monthly_vectors = {}
        for month in range(1, 13):
            month_data = df[df['Month'] == month]
            if not month_data.empty:
                # 计算该月的风向量合成
                angles_rad = np.radians(month_data['Direction_Angle'])
                speeds = month_data['Speed']
                
                # 向量合成
                x_sum = np.sum(speeds * np.sin(angles_rad))
                y_sum = np.sum(speeds * np.cos(angles_rad))
                
                # 月度合成向量
                magnitude = np.sqrt(x_sum**2 + y_sum**2)
                angle = np.degrees(np.arctan2(x_sum, y_sum)) % 360
                
                monthly_vectors[month] = {
                    'magnitude': magnitude,
                    'angle': angle,
                    'x': x_sum,
                    'y': y_sum,
                    'avg_speed': speeds.mean(),
                    'data_count': len(month_data)
                }
        
        # 计算年度重心（所有月份向量的加权中心）
        total_weight = sum(v['magnitude'] for v in monthly_vectors.values())
        if total_weight > 0:
            centroid_x = sum(v['x'] for v in monthly_vectors.values()) / len(monthly_vectors)
            centroid_y = sum(v['y'] for v in monthly_vectors.values()) / len(monthly_vectors)
        else:
            centroid_x = centroid_y = 0
        
        # 转换为极坐标
        centroid_magnitude = np.sqrt(centroid_x**2 + centroid_y**2)
        centroid_angle = np.degrees(np.arctan2(centroid_x, centroid_y)) % 360
        
        print(f"✓ Dandelion core position: Magnitude={centroid_magnitude:.2f}, Angle={centroid_angle:.1f}°")
        
        return {
            'centroid': {
                'x': centroid_x,
                'y': centroid_y,
                'magnitude': centroid_magnitude,
                'angle': centroid_angle
            },
            'monthly_vectors': monthly_vectors
        }

    def calculate_layer1_stems(self, layer0_data, df):
        """Recalculate Layer 1: Precise Mapping of Monthly Stems"""
        print("\n🌱 Recalculating Layer 1: Monthly Stems...")
        
        centroid = layer0_data['centroid']
        
        # Calculate monthly precise data
        stems_data = {}
        monthly_avg_speeds = {}
        monthly_vector_sums = {}
        
        # Step 1: Calculate monthly average speed and vector sum
        for month in range(1, 13):
            month_data = df[df['Month'] == month].copy()
            
            if not month_data.empty:
                # A. Calculate monthly average wind speed (for length mapping)
                avg_speed = month_data['Speed'].mean()
                monthly_avg_speeds[month] = avg_speed
                
                # B. Calculate monthly wind data vector sum (for angle mapping)
                angles_rad = np.radians(month_data['Direction_Angle'])
                speeds = month_data['Speed']
                
                # Treat each day's wind data as vector, calculate sum
                x_sum = np.sum(speeds * np.sin(angles_rad))
                y_sum = np.sum(speeds * np.cos(angles_rad))
                
                # Direction angle of resultant vector
                resultant_angle = np.degrees(np.arctan2(x_sum, y_sum)) % 360
                resultant_magnitude = np.sqrt(x_sum**2 + y_sum**2)
                
                monthly_vector_sums[month] = {
                    'angle': resultant_angle,
                    'magnitude': resultant_magnitude,
                    'x_sum': x_sum,
                    'y_sum': y_sum
                }
                
                print(f"Month {month:2d}: Avg Speed {avg_speed:.1f} km/h, Dominant Dir {resultant_angle:.1f}°")
            else:
                monthly_avg_speeds[month] = 0
                monthly_vector_sums[month] = {
                    'angle': 0,
                    'magnitude': 0,
                    'x_sum': 0,
                    'y_sum': 0
                }
        
        # Step 2: Calculate stem parameters
        max_avg_speed = max(monthly_avg_speeds.values()) if monthly_avg_speeds.values() else 1
        
        for month in range(1, 13):
            avg_speed = monthly_avg_speeds[month]
            vector_sum = monthly_vector_sums[month]
            
            # Data Mapping A: Length = Monthly average wind speed relative ratio
            base_length = 0.3  # Minimum length
            max_length = 1.2   # Maximum length
            if max_avg_speed > 0:
                stem_length = base_length + (avg_speed / max_avg_speed) * (max_length - base_length)
            else:
                stem_length = base_length
            
            # Data Mapping B: Angle = Monthly wind data vector resultant direction
            stem_angle = vector_sum['angle']
            
            # Uniform stem thickness (as per design requirement)
            stem_thickness = 2.5  # Uniform thickness
            
            # Calculate stem endpoint coordinates (from convergence center)
            stem_angle_rad = np.radians(stem_angle)
            end_x = stem_length * np.sin(stem_angle_rad)
            end_y = stem_length * np.cos(stem_angle_rad)
            
            stems_data[month] = {
                'length': stem_length,
                'thickness': stem_thickness,
                'angle': stem_angle,
                'angle_rad': stem_angle_rad,
                'end_x': end_x,
                'end_y': end_y,
                'avg_speed': avg_speed,
                'vector_magnitude': vector_sum['magnitude'],
                'data_basis': {
                    'avg_speed_ratio': avg_speed / max_avg_speed if max_avg_speed > 0 else 0,
                    'resultant_vector': vector_sum
                }
            }
        
        print(f"✓ Recalculated 12 monthly stems:")
        print(f"  - Longest stem: {max(s['length'] for s in stems_data.values()):.2f} (month with highest avg speed)")
        print(f"  - Shortest stem: {min(s['length'] for s in stems_data.values()):.2f}")
        print(f"  - Angle distribution: Determined by monthly wind data vector resultants (non-uniform)")
        
        return stems_data

    def visualize_layer01(self, layer0_data, stems_data):
        """Visualize Layer 0 + Layer 1: Dandelion Core and Stems"""
        print("\n🎨 Drawing Layer 0 + Layer 1: Core and Stems...")
        
        # Create elegant canvas
        fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))
        ax.set_facecolor('#FAFAFA')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        centroid = layer0_data['centroid']
        monthly_vectors = layer0_data['monthly_vectors']
        
        # Layer 1: 绘制月度主线
        print("Drawing Layer 1: Monthly Stems (Reimplemented)...")
        for month, stem in stems_data.items():
            # 从核心到茎干端点的连接
            centroid_angle_rad = np.radians(centroid['angle'])
            centroid_radius = centroid['magnitude'] / 1000
            
            stem_angle_rad = np.radians(stem['angle'])
            stem_end_radius = stem['length']
            
            # 绘制茎干
            ax.plot([centroid_angle_rad, stem_angle_rad], 
                   [centroid_radius, stem_end_radius],
                   color=self.palette['stems'], 
                   linewidth=stem['thickness'], 
                   alpha=0.8, 
                   solid_capstyle='round',
                   zorder=5)
            
            # 茎干端点标记 - 基于向量合力强度
            end_size = 30 + stem['vector_magnitude'] / 500  # 动态大小基于向量合力
            ax.scatter([stem_angle_rad], [stem_end_radius], 
                      s=end_size, c=self.palette['stems'], 
                      alpha=0.9, marker='o', 
                      edgecolors='white', linewidth=1.5, zorder=8)
            
            # 月份标签
            month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            label_radius = stem_end_radius + 0.15
            ax.text(stem_angle_rad, label_radius, month_names[month-1],
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color=self.palette['core'],
                   rotation=np.degrees(stem_angle_rad)-90 if stem_angle_rad > np.pi/2 and stem_angle_rad < 3*np.pi/2 else np.degrees(stem_angle_rad)+90,
                   zorder=15)
            
            # 风速信息
            ax.text(stem_angle_rad, label_radius - 0.08, 
                   f'{stem["avg_speed"]:.1f}km/h',
                   ha='center', va='center', fontsize=7,
                   color=self.palette['tendrils'], alpha=0.8,
                   rotation=np.degrees(stem_angle_rad)-90 if stem_angle_rad > np.pi/2 and stem_angle_rad < 3*np.pi/2 else np.degrees(stem_angle_rad)+90,
                   zorder=14)
        
        # Layer 0: Draw dandelion core (above stems)
        print("Drawing Layer 0: Dandelion Core...")
        centroid_angle_rad = np.radians(centroid['angle'])
        centroid_radius = centroid['magnitude'] / 1000
        
        # 核心圆圈 - 多层次设计
        core_sizes = [150, 100, 50]
        core_alphas = [0.3, 0.6, 1.0]
        core_colors = [self.palette['tendrils'], self.palette['stems'], self.palette['core']]
        
        for size, alpha, color in zip(core_sizes, core_alphas, core_colors):
            ax.scatter([centroid_angle_rad], [centroid_radius], 
                      s=size, c=color, alpha=alpha, 
                      edgecolors='white', linewidth=2, zorder=12)
        
        # 添加核心信息
        ax.text(centroid_angle_rad, centroid_radius, 
               'CORE', 
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', zorder=16)
        
        # 设置坐标轴样式
        max_radius = max(stem['length'] for stem in stems_data.values())
        ax.set_ylim(0, max_radius * 1.3)
        ax.set_thetagrids(range(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
                         fontsize=10, color=self.palette['stems'])
        ax.set_rticks([])
        ax.grid(True, alpha=0.2)
        
        # Title and description
        fig.suptitle('METEOROLOGICAL DANDELION - Layer 0 + 1\nCore and Monthly Stems (Reimplemented)', 
                    fontsize=18, fontweight='bold', color=self.palette['core'], y=0.95)
        
        plt.figtext(0.02, 0.02, 
                   'Layer 0: Dandelion Core (Annual Wind Center)\n'
                   'Layer 1: Monthly Stems (Precise Data Mapping)\n'
                   '• Stem Length ∝ Monthly Average Wind Speed\n'
                   '• Stem Angle = Monthly Wind Vector Resultant Direction\n'
                   '• Uniform Thickness Design (2.5px)\n'
                   '• Endpoint Coordinates for Layer 2 Foundation\n\n'
                   'Next: Layer 2 Direction Tendrils',
                   fontsize=9, color=self.palette['tendrils'], 
                   verticalalignment='bottom', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save artwork
        filename = 'Meteorological_Dandelion_Layer01_HKA_2024.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor='#FAFAFA', edgecolor='none')
        
        print(f"✅ Layer 0+1 saved: {filename}")
        plt.show()
        
        return fig

def main():
    """Main Program - Layer 0 + Layer 1"""
    dandelion = MeteorologicalDandelion()
    
    # 1. Get wind data
    df = dandelion.get_real_wind_data()
    
    # 2. Calculate Layer 0 core
    layer0_data = dandelion.calculate_layer0_centroid(df)
    
    # 3. Recalculate Layer 1 monthly stems
    stems_data = dandelion.calculate_layer1_stems(layer0_data, df)
    
    # 4. Visualize Layer 0 + Layer 1
    dandelion.visualize_layer01(layer0_data, stems_data)
    
    print(f"\n🌼 Layer 0 + Layer 1 Complete!")
    print("✨ Dandelion core and stem structure established")
    print("🎯 Core position: {:.1f}°".format(layer0_data['centroid']['angle']))
    print("🌱 Stem count: 12 monthly branches")
    print("🚀 Ready for Layer 2: Direction Tendrils?")

if __name__ == "__main__":
    main()