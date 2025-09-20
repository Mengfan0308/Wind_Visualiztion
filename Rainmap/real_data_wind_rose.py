# REAL DATA WIND ROSE - 香港机场2024年真实风数据可视化
# Programming for Artists and Designers - 简洁优雅的数据驱动设计
# 获取真实数据并生成月度风玫瑰构成图

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import matplotlib.patches as patches

print("🌪️  REAL DATA WIND ROSE COMPOSITION")
print("📍 Hong Kong International Airport 2024")
print("🎨 Programming for Artists and Designers\n")

class RealWindDataProcessor:
    """真实风数据处理器 - 简洁优雅的设计"""
    
    def __init__(self):
        self.directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                          'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        self.direction_angles = np.arange(0, 360, 22.5)
        
        # 简洁的季节配色
        self.colors = {
            'winter': ['#5DADE2', '#3498DB', '#2980B9'],  # 冬蓝
            'spring': ['#58D68D', '#27AE60', '#239B56'],  # 春绿
            'summer': ['#F1948A', '#E74C3C', '#C0392B'],  # 夏红
            'autumn': ['#F8C471', '#F39C12', '#E67E22']   # 秋橙
        }
        
        self.season_map = {
            1: 'winter', 2: 'winter', 3: 'spring', 4: 'spring', 
            5: 'spring', 6: 'summer', 7: 'summer', 8: 'summer',
            9: 'autumn', 10: 'autumn', 11: 'autumn', 12: 'winter'
        }

    def download_real_data(self):
        """下载香港机场真实风数据"""
        print("📡 正在下载真实风数据...")
        
        urls = {
            'direction': "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv",
            'speed': "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv"
        }
        
        datasets = {}
        for name, url in urls.items():
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    # 跳过前两行（通常是元数据）
                    df = pd.read_csv(StringIO(response.text), encoding='utf-8-sig', skiprows=2)
                    datasets[name] = df
                    print(f"✓ {name} 数据下载成功: {df.shape}")
                else:
                    print(f"✗ {name} 下载失败: {response.status_code}")
                    return None
            except Exception as e:
                print(f"✗ {name} 下载错误: {e}")
                return None
        
        return datasets

    def clean_and_merge_data(self, datasets):
        """清理并合并数据 - 简洁的数据处理"""
        print("\n🧹 正在清理和合并数据...")
        
        if not datasets:
            return None
            
        try:
            df_dir = datasets['direction']
            df_speed = datasets['speed']
            
            # 处理香港天文台的特殊格式
            def process_hko_data(df):
                # 查找年月日和数值列
                year_col = month_col = day_col = value_col = None
                
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'year' in col_lower or '年' in col:
                        year_col = col
                    elif 'month' in col_lower or '月' in col:
                        month_col = col
                    elif 'day' in col_lower or '日' in col:
                        day_col = col
                    elif 'value' in col_lower or '值' in col:
                        value_col = col
                
                if not all([year_col, month_col, day_col, value_col]):
                    raise ValueError(f"无法识别数据列: {df.columns.tolist()}")
                
                # 创建日期列
                df_clean = df.copy()
                df_clean = df_clean.dropna(subset=[year_col, month_col, day_col])
                
                # 构建日期字符串
                df_clean['Date'] = (
                    df_clean[year_col].astype(int).astype(str) + 
                    df_clean[month_col].astype(int).astype(str).str.zfill(2) + 
                    df_clean[day_col].astype(int).astype(str).str.zfill(2)
                )
                
                # 清理数值列（去除'***'等无效值）
                df_clean['Value'] = df_clean[value_col]
                df_clean = df_clean[df_clean['Value'] != '***']
                df_clean = df_clean.dropna(subset=['Value'])
                
                return df_clean[['Date', 'Value']]
            
            # 处理两个数据集
            df_dir_clean = process_hko_data(df_dir)
            df_dir_clean.columns = ['Date', 'Direction']
            
            df_speed_clean = process_hko_data(df_speed)
            df_speed_clean.columns = ['Date', 'Speed']
            
            # 合并数据
            df_merged = pd.merge(df_dir_clean, df_speed_clean, on='Date', how='inner')
            
            # 转换日期格式
            df_merged['Date'] = pd.to_datetime(df_merged['Date'], format='%Y%m%d', errors='coerce')
            df_merged = df_merged.dropna(subset=['Date'])
            
            # 筛选2024年数据
            df_2024 = df_merged[df_merged['Date'].dt.year == 2024].copy()
            
            if df_2024.empty:
                print("⚠️  未找到2024年数据，使用最新年份")
                latest_year = df_merged['Date'].dt.year.max()
                df_2024 = df_merged[df_merged['Date'].dt.year == latest_year].copy()
                print(f"使用 {latest_year} 年数据")
            
            # 处理风向数据 - 假设为角度数值
            df_2024['Direction_Angle'] = pd.to_numeric(df_2024['Direction'], errors='coerce')
            df_2024['Direction_Sector'] = df_2024['Direction_Angle'].apply(self._angle_to_direction)
            
            # 处理风速数据
            df_2024['Speed'] = pd.to_numeric(df_2024['Speed'], errors='coerce')
            
            # 清理无效数据
            df_2024 = df_2024.dropna(subset=['Direction_Sector', 'Speed'])
            df_2024['Month'] = df_2024['Date'].dt.month
            
            print(f"✓ 数据清理完成: {len(df_2024)} 条记录")
            print(f"数据年份: {df_2024['Date'].dt.year.unique()}")
            return df_2024
            
        except Exception as e:
            print(f"✗ 数据处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _angle_to_direction(self, angle):
        """角度转换为16方位"""
        if pd.isna(angle):
            return None
        sectors = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = int((angle + 11.25) % 360 / 22.5)
        return sectors[index]

    def analyze_monthly_patterns(self, df):
        """分析月度风模式 - 优雅的统计计算"""
        print("\n📊 正在分析月度风模式...")
        
        monthly_stats = {}
        
        for month in range(1, 13):
            month_data = df[df['Month'] == month]
            
            if not month_data.empty:
                # 风向频率统计
                direction_counts = month_data['Direction_Sector'].value_counts()
                direction_freq = direction_counts.reindex(self.directions, fill_value=0)
                direction_freq_pct = (direction_freq / len(month_data)) * 100
                
                # 每个方向的平均风速
                avg_speeds = {}
                for direction in self.directions:
                    dir_data = month_data[month_data['Direction_Sector'] == direction]
                    avg_speeds[direction] = dir_data['Speed'].mean() if len(dir_data) > 0 else 0
                
                monthly_stats[month] = {
                    'frequencies': direction_freq_pct.to_dict(),
                    'avg_speeds': avg_speeds,
                    'overall_avg_speed': month_data['Speed'].mean(),
                    'predominant_dir': direction_freq.idxmax(),
                    'season': self.season_map[month],
                    'total_days': len(month_data)
                }
                
                print(f"月份 {month:2d}: {monthly_stats[month]['predominant_dir']} "
                      f"({direction_freq_pct.max():.1f}%), "
                      f"平均: {monthly_stats[month]['overall_avg_speed']:.1f} km/h")
        
        return monthly_stats

    def create_elegant_wind_rose(self, stats, month, ax):
        """创建优雅的单月风玫瑰图"""
        frequencies = [stats['frequencies'][d] for d in self.directions]
        speeds = [stats['avg_speeds'][d] for d in self.directions]
        season = stats['season']
        
        # 设置极坐标样式
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_facecolor('white')
        
        # 绘制风玫瑰
        colors = self.colors[season]
        max_speed = max(speeds) if max(speeds) > 0 else 1
        
        for i, (freq, speed) in enumerate(zip(frequencies, speeds)):
            if freq > 0:
                angle = np.radians(self.direction_angles[i])
                width = np.radians(22.5)
                
                # 根据风速选择颜色
                color_idx = min(int((speed / max_speed) * (len(colors) - 1)), len(colors) - 1)
                color = colors[color_idx]
                
                # 绘制扇形
                wedge = patches.Wedge((0, 0), freq/100, 
                                    np.degrees(angle - width/2),
                                    np.degrees(angle + width/2),
                                    facecolor=color, alpha=0.8,
                                    edgecolor='white', linewidth=0.8)
                ax.add_patch(wedge)
        
        # 优雅的样式设置
        ax.set_ylim(0, max(frequencies)/100 * 1.1 if frequencies else 0.1)
        ax.set_rticks([])
        ax.set_thetagrids(range(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
                         fontsize=9, color='#34495E')
        ax.grid(True, alpha=0.2)
        
        # 月份标签
        month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        ax.text(0.5, -0.12, month_names[month-1], 
               transform=ax.transAxes, ha='center', va='top',
               fontsize=11, fontweight='bold', color='#2C3E50')
        
        # 统计信息
        ax.text(0.5, -0.22, f'{stats["overall_avg_speed"]:.1f} km/h', 
               transform=ax.transAxes, ha='center', va='top',
               fontsize=9, color='#7F8C8D')

    def create_composition(self, monthly_stats):
        """创建最终的构成作品"""
        print("\n🎨 正在创建最终作品...")
        
        # 创建画布
        fig = plt.figure(figsize=(16, 12), facecolor='#FDFDFE')
        fig.suptitle('HONG KONG AIRPORT WIND PATTERNS 2024\n月度风玫瑰构成图', 
                    fontsize=18, fontweight='bold', color='#2C3E50', y=0.94)
        
        # 季节标签
        season_info = [
            ('WINTER', '#3498DB', 0.125, [0.88, 0.19]),
            ('SPRING', '#27AE60', 0.125, [0.65]),  
            ('SUMMER', '#E74C3C', 0.125, [0.42]),
            ('AUTUMN', '#F39C12', 0.125, [0.19])
        ]
        
        for season, color, x, y_positions in season_info:
            for y in y_positions:
                fig.text(x, y, season, fontsize=12, fontweight='bold',
                        color=color, rotation=90, ha='center', va='center')
        
        # 绘制12个月的风玫瑰
        for month in range(1, 13):
            ax = fig.add_subplot(4, 3, month, projection='polar')
            if month in monthly_stats:
                self.create_elegant_wind_rose(monthly_stats[month], month, ax)
        
        # 简洁的说明
        description = (
            "数据来源: 香港天文台\n"
            "设计理念: 扇形长度 = 风向频率, 颜色深度 = 风速强度\n"
            "季节编码: 蓝(冬) · 绿(春) · 红(夏) · 橙(秋)"
        )
        
        fig.text(0.02, 0.02, description, fontsize=9, color='#7F8C8D',
                verticalalignment='bottom', fontfamily='monospace')
        
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, right=0.95, top=0.87, bottom=0.08)
        
        # 保存作品
        filename = 'Hong_Kong_Airport_Wind_Rose_2024_Real_Data.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor='#FDFDFE', edgecolor='none')
        
        print(f"✅ 真实数据作品已保存: {filename}")
        plt.show()
        
        return fig

def main():
    """主程序 - 简洁的执行流程"""
    processor = RealWindDataProcessor()
    
    # 1. 下载真实数据
    datasets = processor.download_real_data()
    
    # 2. 清理和处理数据
    df = processor.clean_and_merge_data(datasets)
    
    if df is not None:
        # 3. 分析月度模式
        monthly_stats = processor.analyze_monthly_patterns(df)
        
        # 4. 创建最终作品
        processor.create_composition(monthly_stats)
        
        print(f"\n🎉 完成！使用了 {len(df)} 条真实数据记录")
        print("🎨 这是一个完全基于真实数据的艺术可视化作品")
    else:
        print("❌ 数据获取失败，请检查网络连接")

if __name__ == "__main__":
    main()