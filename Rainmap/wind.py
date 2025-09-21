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
                    print(f"✓ {name} data fetched successfully")
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
        """Layer 1: 主线 (Primary Stems | 代表"月")
        
        视觉表现：12条深灰色的、粗细统一的细线
        数据映射A（长度）：主线长度为该月的平均风速
        数据映射B（角度分布）：主线的发射角度由该月所有风数据的向量合力方向决定
        """
        print("\n🌱 Layer 1: 计算月度主线...")
        
        stems_data = {}
        monthly_speeds = []  # 用于归一化
        
        # 计算每个月的数据
        for month in range(1, 13):
            month_data = df[df['Month'] == month].copy()
            
            if not month_data.empty:
                # 数据映射A：长度 = 月平均风速
                avg_speed = month_data['Speed'].mean()
                monthly_speeds.append(avg_speed)
                
                # 数据映射B：角度 = 月风数据向量合力方向
                angles_rad = np.radians(month_data['Direction_Angle'])
                speeds = month_data['Speed']
                
                # 计算向量合力
                x_component = np.sum(speeds * np.sin(angles_rad))
                y_component = np.sum(speeds * np.cos(angles_rad))
                resultant_angle = np.degrees(np.arctan2(x_component, y_component)) % 360
                
                print(f"月份 {month:2d}: 平均风速 {avg_speed:.1f} km/h, 主导方向 {resultant_angle:.1f}°")
                
                stems_data[month] = {
                    'avg_speed': avg_speed,
                    'angle': resultant_angle,
                    'angle_rad': np.radians(resultant_angle)
                }
            else:
                monthly_speeds.append(0)
                stems_data[month] = {
                    'avg_speed': 0,
                    'angle': 0,
                    'angle_rad': 0
                }
        
        # 归一化长度：最大风速月份的主线最长
        max_speed = max(monthly_speeds) if monthly_speeds else 1
        min_length, max_length = 0.3, 1.2  # 主线长度范围
        
        for month in range(1, 13):
            avg_speed = stems_data[month]['avg_speed']
            
            # 按比例确定长度
            if max_speed > 0:
                normalized_length = avg_speed / max_speed
                stem_length = min_length + normalized_length * (max_length - min_length)
            else:
                stem_length = min_length
            
            stems_data[month].update({
                'length': stem_length,
                'thickness': 2.5,  # 统一粗细
            })
        
        print(f"✓ 12条主线计算完成：")
        print(f"  - 最长主线: {max(s['length'] for s in stems_data.values()):.2f}")
        print(f"  - 最短主线: {min(s['length'] for s in stems_data.values()):.2f}")
        print(f"  - 角度分布: 非均匀（由月度风向量决定）")
        
        return stems_data

    def calculate_layer2_tendrils(self, layer1_data, df):
        """Layer 2: 须须 (Secondary Tendrils | 代表"风向")
        
        视觉表现：从主线（Layer 1）的末端发出的、与主线粗细一致的线
        数据映射A（角度）：须须的发射角度严格遵循真实地理方位（16个方位）
        数据映射B（长度）：须须长度 ∝ 该风向在该月出现的频率（天数）
        """
        print("\n🌿 Layer 2: 计算风向须须...")
        
        # 定义16个绝对罗盘方向 (0°=N, 90°=E, 180°=S, 270°=W)
        directions_16 = {
            'N': 0,      'NNE': 22.5,  'NE': 45,     'ENE': 67.5,
            'E': 90,     'ESE': 112.5, 'SE': 135,    'SSE': 157.5,
            'S': 180,    'SSW': 202.5, 'SW': 225,    'WSW': 247.5,
            'W': 270,    'WNW': 292.5, 'NW': 315,    'NNW': 337.5
        }
        
        tendrils_data = {}
        
        # 为每个月计算16个风向的须须
        for month in range(1, 13):
            month_data = df[df['Month'] == month].copy()
            month_tendrils = {}
            
            if not month_data.empty:
                # 统计该月每个风向的出现天数
                direction_counts = {}
                for direction_name, direction_angle in directions_16.items():
                    # 计算该风向在本月的出现频率
                    tolerance = 11.25  # ±11.25°容差
                    lower_bound = (direction_angle - tolerance) % 360
                    upper_bound = (direction_angle + tolerance) % 360
                    
                    if lower_bound < upper_bound:
                        count = len(month_data[
                            (month_data['Direction_Angle'] >= lower_bound) & 
                            (month_data['Direction_Angle'] < upper_bound)
                        ])
                    else:  # 跨越0°边界
                        count = len(month_data[
                            (month_data['Direction_Angle'] >= lower_bound) | 
                            (month_data['Direction_Angle'] < upper_bound)
                        ])
                    
                    direction_counts[direction_name] = count
                
                # 找出最大出现天数用于归一化
                max_count = max(direction_counts.values()) if direction_counts.values() else 1
                active_directions = sum(1 for count in direction_counts.values() if count > 0)
                max_direction = max(direction_counts.items(), key=lambda x: x[1])
                
                print(f"月份 {month:2d}: {active_directions}/16个方向活跃, 最多: {max_direction[0]} ({max_direction[1]}天)")
                
                # 为每个风向生成须须
                for direction_name, direction_angle in directions_16.items():
                    count = direction_counts[direction_name]
                    
                    if count > 0:  # 只为出现过的风向生成须须
                        # 数据映射B：长度 ∝ 该风向出现频率
                        min_length, max_length = 0.1, 0.4
                        normalized_frequency = count / max_count if max_count > 0 else 0
                        tendril_length = min_length + normalized_frequency * (max_length - min_length)
                        
                        # 数据映射A：角度 = 绝对罗盘方向
                        tendril_angle = direction_angle
                        
                        # 须须粗细与主线一致
                        tendril_thickness = 2.5
                        
                        month_tendrils[direction_name] = {
                            'length': tendril_length,
                            'thickness': tendril_thickness,
                            'angle': tendril_angle,
                            'angle_rad': np.radians(tendril_angle),
                            'frequency': count,
                            'frequency_ratio': normalized_frequency
                        }
                    else:
                        # 未出现的风向不生成须须
                        month_tendrils[direction_name] = {
                            'length': 0,
                            'thickness': 0,
                            'angle': direction_angle,
                            'angle_rad': np.radians(direction_angle),
                            'frequency': 0,
                            'frequency_ratio': 0
                        }
            else:
                # 该月无数据
                for direction_name, direction_angle in directions_16.items():
                    month_tendrils[direction_name] = {
                        'length': 0,
                        'thickness': 0,
                        'angle': direction_angle,
                        'angle_rad': np.radians(direction_angle),
                        'frequency': 0,
                        'frequency_ratio': 0
                    }
            
            tendrils_data[month] = month_tendrils
        
        # 统计总体信息
        total_tendrils = sum(
            sum(1 for t in month_tendrils.values() if t['frequency'] > 0)
            for month_tendrils in tendrils_data.values()
        )
        
        print(f"✓ 须须计算完成：")
        print(f"  - 16个方向 × 12个月 = 192个潜在须须")
        print(f"  - 实际生成须须数量: {total_tendrils}个")
        print(f"  - 长度映射: 风向出现频率")
        print(f"  - 角度映射: 绝对罗盘方向")
        
        return tendrils_data

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

    def visualize_layer012(self, layer0_data, layer1_data, layer2_data):
        """可视化Layer 0+1+2: 完整的气象蒲公英"""
        print("\n🎨 绘制完整蒲公英: Layer 0+1+2...")
        
        # 创建画布
        fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))
        ax.set_facecolor('#FAFAFA')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # 获取核心数据
        centroid = layer0_data['centroid']
        convergence_radius = 0.2  # 核心位置
        convergence_angle_rad = np.radians(centroid['angle'])
        
        # Layer 1: 绘制12条月度主线
        print("绘制Layer 1: 月度主线...")
        for month, stem in layer1_data.items():
            # 从核心到主线端点
            stem_angle_rad = stem['angle_rad']
            stem_end_radius = convergence_radius + stem['length']  # 主线终点位置
            
            # 绘制主线
            ax.plot([convergence_angle_rad, stem_angle_rad],
                   [convergence_radius, stem_end_radius],
                   color=self.palette['stems'], 
                   linewidth=stem['thickness'], 
                   alpha=0.8, 
                   solid_capstyle='round',
                   zorder=5)
            
            # 主线端点标记
            ax.scatter([stem_angle_rad], [stem_end_radius], 
                      s=50, c=self.palette['stems'], 
                      alpha=0.9, marker='o', 
                      edgecolors='white', linewidth=1.5, zorder=8)
        
        # Layer 2: 绘制风向须须
        print("绘制Layer 2: 风向须须...")
        for month, month_tendrils in layer2_data.items():
            # 获取对应主线数据
            stem = layer1_data[month]
            stem_angle_rad = stem['angle_rad']
            stem_end_radius = convergence_radius + stem['length']  # 与Layer 1保持一致
            
            for direction_name, tendril in month_tendrils.items():
                if tendril['frequency'] > 0:  # 只绘制有数据的须须
                    
                    # 须须从主线端点开始，指向绝对罗盘方向
                    start_radius = stem_end_radius
                    start_angle_rad = stem_angle_rad
                    
                    end_radius = start_radius + tendril['length']
                    end_angle_rad = tendril['angle_rad']  # 绝对罗盘方向
                    
                    # 绘制须须
                    alpha_value = 0.6 + 0.3 * tendril['frequency_ratio']  # 基于频率的透明度
                    ax.plot([start_angle_rad, end_angle_rad],
                           [start_radius, end_radius],
                           color=self.palette['tendrils'], 
                           linewidth=tendril['thickness'], 
                           alpha=alpha_value,
                           solid_capstyle='round',
                           zorder=3)
                    
                    # 须须端点标记（仅显著须须）
                    if tendril['frequency'] >= 3:
                        marker_size = 10 + tendril['frequency'] * 1.5
                        ax.scatter([end_angle_rad], [end_radius], 
                                  s=marker_size, c=self.palette['tendrils'], 
                                  alpha=0.7, marker='o', 
                                  edgecolors='white', linewidth=0.5, zorder=6)
        
        # Layer 0: 绘制核心
        print("绘制Layer 0: 核心...")
        ax.scatter([convergence_angle_rad], [convergence_radius],
                  s=200, c=self.palette['core'], 
                  alpha=1.0, marker='o', 
                  edgecolors='white', linewidth=3, zorder=10)
        
        # 设置图表样式
        ax.set_ylim(0, 2.0)
        ax.set_thetagrids(range(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
                         fontsize=10, color=self.palette['stems'])
        ax.set_rticks([])
        ax.grid(True, alpha=0.2)
        
        # 标题和说明
        fig.suptitle('气象蒲公英 - 完整版本\n香港国际机场 2024年风数据', 
                    fontsize=18, fontweight='bold', color=self.palette['core'], y=0.95)
        
        plt.figtext(0.02, 0.02, 
                   'Layer 0: 核心 (年度风力中心)\n'
                   'Layer 1: 主线 (12个月, 长度∝平均风速, 角度=合力方向)\n'
                   'Layer 2: 须须 (16个风向, 长度∝出现频率, 角度=绝对方位)\n\n'
                   '设计原则: 数据驱动的有机形态',
                   fontsize=9, color=self.palette['tendrils'], 
                   verticalalignment='bottom', fontfamily='monospace')
        
        plt.tight_layout()
        
        # 保存图片
        filename = 'Meteorological_Dandelion_Layers012_CORRECTED_HKA_2024.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"✅ Layer 0+1+2已保存: {filename}")
        
        return filename

def main():
    """Main Program - Layer 0 + Layer 1 + Layer 2"""
    dandelion = MeteorologicalDandelion()
    
    # 1. Get wind data
    df = dandelion.get_real_wind_data()
    
    # 2. Calculate Layer 0 core
    layer0_data = dandelion.calculate_layer0_centroid(df)
    
    # 3. Calculate Layer 1 monthly stems
    layer1_data = dandelion.calculate_layer1_stems(layer0_data, df)
    
    # 4. Calculate Layer 2 direction tendrils
    layer2_data = dandelion.calculate_layer2_tendrils(layer1_data, df)
    
    # 5. Visualize complete Layer 0 + Layer 1 + Layer 2
    dandelion.visualize_layer012(layer0_data, layer1_data, layer2_data)
    
    print(f"\n🌼 Layer 0 + Layer 1 + Layer 2 Complete!")
    print("✨ Complete dandelion structure with tendrils established")
    print("🎯 Core position: {:.1f}°".format(layer0_data['centroid']['angle']))
    print("🌱 Stem count: 12 monthly branches")
    print("🌿 Tendril count: 192 direction tendrils (16 × 12)")
    print("🚀 Ready for Layer 3: Seed Puffs?")

if __name__ == "__main__":
    main()