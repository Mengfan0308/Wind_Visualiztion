# MONTHLY WIND ROSE COMPOSITION - 月度风玫瑰构成图
# Programming for Artists and Designers - 香港机场2024风数据时间对比可视化
# 设计理念: 通过网格构成展现月度/季度风模式的差异与变化

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

print("=== MONTHLY WIND ROSE COMPOSITION ===")
print("设计目标: 清晰展现2024年各月风模式的时间变化")
print("构成理念: 4x3网格布局 + 现代风玫瑰图 + 季节色彩编码\n")

class MonthlyWindRoseComposer:
    """月度风玫瑰构成设计器"""
    
    def __init__(self):
        """初始化设计参数"""
        # 16方向定义
        self.directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                          'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        self.direction_angles = np.arange(0, 360, 22.5)
        
        # 季节配色方案 - 现代设计风格
        self.seasonal_colors = {
            'spring': ['#27AE60', '#2ECC71', '#58D68D'],  # 春季绿色系
            'summer': ['#E74C3C', '#EC7063', '#F1948A'],  # 夏季红色系  
            'autumn': ['#F39C12', '#F8C471', '#FAD5A5'],  # 秋季橙色系
            'winter': ['#3498DB', '#5DADE2', '#85C1E9']   # 冬季蓝色系
        }
        
        # 月份到季节的映射
        self.month_to_season = {
            1: 'winter', 2: 'winter', 3: 'spring',
            4: 'spring', 5: 'spring', 6: 'summer', 
            7: 'summer', 8: 'summer', 9: 'autumn',
            10: 'autumn', 11: 'autumn', 12: 'winter'
        }
        
        print("✓ 16方向风玫瑰系统初始化完成")
        print("✓ 季节配色方案加载完成")
    
    def create_sample_wind_data(self):
        """创建具有季节特征的示例风数据"""
        print("\n=== 创建季节性风模式示例数据 ===")
        
        wind_data = []
        start_date = datetime(2024, 1, 1)
        
        for i in range(366):  # 2024年是闰年
            date = start_date + timedelta(days=i)
            month = date.month
            
            # 模拟香港的季风模式
            if month in [6, 7, 8]:  # 夏季：偏南风为主
                dominant_directions = ['S', 'SSW', 'SW', 'SE', 'SSE']
                weights = [0.3, 0.25, 0.2, 0.15, 0.1]
                base_speed = 15
            elif month in [12, 1, 2]:  # 冬季：偏北风为主  
                dominant_directions = ['N', 'NNE', 'NE', 'NW', 'NNW']
                weights = [0.35, 0.25, 0.2, 0.12, 0.08]
                base_speed = 12
            elif month in [3, 4, 5]:  # 春季：变化较大
                dominant_directions = ['E', 'ENE', 'ESE', 'SE', 'NE']
                weights = [0.25, 0.2, 0.2, 0.2, 0.15]
                base_speed = 13
            else:  # 秋季：偏东风
                dominant_directions = ['E', 'ESE', 'SE', 'ENE', 'NE']
                weights = [0.3, 0.25, 0.2, 0.15, 0.1]
                base_speed = 11
            
            # 随机选择方向（基于季节概率）
            direction = np.random.choice(dominant_directions, p=weights)
            
            # 添加随机性
            if np.random.random() < 0.2:  # 20%概率选择其他方向
                direction = np.random.choice(self.directions)
            
            # 生成风速（考虑季节和随机因子）
            speed_variation = np.random.normal(0, 3)
            speed = max(1, base_speed + speed_variation)
            
            # 台风季节偶尔出现高风速
            if month in [7, 8, 9] and np.random.random() < 0.05:
                speed *= np.random.uniform(2, 3)
            
            wind_data.append({
                'date': date,
                'direction': direction,
                'speed': min(speed, 45)  # 限制最大风速
            })
        
        print(f"✓ 生成366天的季节性风数据")
        return wind_data
    
    def analyze_monthly_patterns(self, wind_data):
        """分析月度风模式"""
        print("\n=== 分析月度风模式 ===")
        
        df = pd.DataFrame(wind_data)
        df['month'] = df['date'].dt.month
        
        monthly_stats = {}
        
        for month in range(1, 13):
            month_data = df[df['month'] == month]
            
            # 计算风向频率
            direction_freq = month_data['direction'].value_counts()
            direction_freq = direction_freq.reindex(self.directions, fill_value=0)
            direction_freq_pct = direction_freq / len(month_data) * 100
            
            # 计算每个方向的平均风速
            avg_speeds = {}
            for direction in self.directions:
                dir_data = month_data[month_data['direction'] == direction]
                avg_speeds[direction] = dir_data['speed'].mean() if len(dir_data) > 0 else 0
            
            # 计算统计信息
            monthly_stats[month] = {
                'direction_frequencies': direction_freq_pct.to_dict(),
                'average_speeds': avg_speeds,
                'total_days': len(month_data),
                'avg_speed_overall': month_data['speed'].mean(),
                'max_speed': month_data['speed'].max(),
                'predominant_direction': direction_freq.idxmax(),
                'season': self.month_to_season[month]
            }
            
            print(f"月份 {month:2d}: 主导风向 {monthly_stats[month]['predominant_direction']} "
                  f"(频率: {direction_freq_pct.max():.1f}%), "
                  f"平均风速: {monthly_stats[month]['avg_speed_overall']:.1f} km/h")
        
        return monthly_stats
    
    def create_single_wind_rose(self, month_stats, month_num, ax):
        """创建单个月份的现代风玫瑰图"""
        direction_freqs = month_stats['direction_frequencies']
        avg_speeds = month_stats['average_speeds']
        season = month_stats['season']
        
        # 获取季节配色
        colors = self.seasonal_colors[season]
        
        # 转换为极坐标数据
        angles_rad = np.radians(self.direction_angles)
        frequencies = [direction_freqs[d] for d in self.directions]
        speeds = [avg_speeds[d] for d in self.directions]
        
        # 标准化风速用于颜色映射
        max_speed = max(speeds) if max(speeds) > 0 else 1
        normalized_speeds = [s/max_speed for s in speeds]
        
        # 绘制风玫瑰图
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # 绘制扇形区域
        for i, (angle, freq, norm_speed) in enumerate(zip(angles_rad, frequencies, normalized_speeds)):
            if freq > 0:  # 只绘制有数据的方向
                # 根据风速选择颜色深度
                color_idx = min(int(norm_speed * len(colors)), len(colors)-1)
                color = colors[color_idx]
                
                # 计算扇形的角度范围
                width = np.radians(22.5)  # 每个方向占22.5度
                
                # 绘制扇形
                wedge = patches.Wedge((0, 0), freq/100, 
                                    np.degrees(angle - width/2), 
                                    np.degrees(angle + width/2),
                                    facecolor=color, alpha=0.8, 
                                    edgecolor='white', linewidth=0.5)
                ax.add_patch(wedge)
        
        # 设置极坐标图样式
        ax.set_ylim(0, max(frequencies)/100 * 1.1 if frequencies else 0.1)
        ax.set_rticks([])  # 移除径向刻度
        ax.set_thetagrids(range(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('white')
        
        # 添加月份标签
        month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        ax.text(0.5, -0.15, f'{month_names[month_num-1]}', 
               transform=ax.transAxes, ha='center', va='top',
               fontsize=12, fontweight='bold', color='#2C3E50')
        
        # 添加统计信息
        ax.text(0.5, -0.25, f'Avg: {month_stats["avg_speed_overall"]:.1f} km/h', 
               transform=ax.transAxes, ha='center', va='top',
               fontsize=9, color='#7F8C8D')
    
    def create_composition(self, monthly_stats):
        """创建12个月的网格构成图"""
        print("\n=== 创建月度风玫瑰构成图 ===")
        
        # 创建4x3网格布局
        fig = plt.figure(figsize=(16, 12), facecolor='#F8F9FA')
        fig.suptitle('MONTHLY WIND PATTERNS COMPOSITION\n香港国际机场 2024年风模式时间构成图', 
                    fontsize=20, fontweight='bold', color='#2C3E50', y=0.95)
        
        # 添加季节分区标识
        season_positions = {
            'WINTER': (0.125, 0.88),
            'SPRING': (0.125, 0.65), 
            'SUMMER': (0.125, 0.42),
            'AUTUMN': (0.125, 0.19)
        }
        
        season_colors_label = {
            'WINTER': '#3498DB',
            'SPRING': '#27AE60', 
            'SUMMER': '#E74C3C',
            'AUTUMN': '#F39C12'
        }
        
        for season, pos in season_positions.items():
            fig.text(pos[0], pos[1], season, fontsize=14, fontweight='bold',
                    color=season_colors_label[season], rotation=90, 
                    ha='center', va='center')
        
        # 创建12个子图
        for month in range(1, 13):
            row = (month - 1) // 3
            col = (month - 1) % 3
            
            # 创建极坐标子图
            ax = fig.add_subplot(4, 3, month, projection='polar')
            
            # 绘制该月的风玫瑰图
            self.create_single_wind_rose(monthly_stats[month], month, ax)
        
        # 添加图例
        legend_elements = []
        for season, colors in self.seasonal_colors.items():
            for i, color in enumerate(colors):
                intensity = ['Low', 'Medium', 'High'][i]
                legend_elements.append(patches.Rectangle((0,0),1,1, 
                                     facecolor=color, alpha=0.8,
                                     label=f'{season.title()} {intensity}'))
        
        fig.legend(handles=legend_elements[-3:], title='Wind Speed Intensity',
                  loc='center', bbox_to_anchor=(0.02, 0.5), fontsize=10)
        
        # 添加说明文字
        explanation = (
            "设计说明:\n"
            "• 每个极坐标图代表一个月的风向分布\n"
            "• 扇形长度 = 该方向的风频率\n"
            "• 颜色深度 = 该方向的平均风速\n"
            "• 季节分组显示年度风模式变化\n"
            "• 网格构成强调时间层次的对比关系"
        )
        
        fig.text(0.02, 0.02, explanation, fontsize=9, color='#7F8C8D',
                verticalalignment='bottom', fontfamily='monospace')
        
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, right=0.95, top=0.88, bottom=0.12)
        
        # 保存作品
        filename = 'Monthly_Wind_Rose_Composition_HKA_2024.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor='#F8F9FA', edgecolor='none')
        
        print(f"✓ 构成图已保存: {filename}")
        plt.show()
        
        return fig

def create_design_summary():
    """创建设计方案总结"""
    print("\n" + "="*70)
    print("    MONTHLY WIND ROSE COMPOSITION - 设计方案总结")
    print("="*70)
    
    print("\n🎯 设计目标:")
    print("  ✓ 清晰展现12个月的风模式差异")
    print("  ✓ 通过网格构成强化时间对比关系") 
    print("  ✓ 现代设计美学与数据可视化结合")
    print("  ✓ 简单明了的视觉语言表达复杂数据")
    
    print("\n📊 可视化策略:")
    print("  ✓ 4x3网格布局 - 清晰的时间组织")
    print("  ✓ 极坐标风玫瑰图 - 直观的方向表达")
    print("  ✓ 季节配色编码 - 增强时间识别")
    print("  ✓ 双重数据映射 - 频率(长度) + 速度(颜色)")
    
    print("\n🎨 构成美学:")
    print("  ✓ 统一的网格系统创造秩序感")
    print("  ✓ 季节色彩渐变体现时间流动")
    print("  ✓ 现代极简风格突出数据本质")
    print("  ✓ 对称与变化的平衡关系")
    
    print("\n💡 设计价值:")
    print("  ✓ 一眼看出季节风模式的转换")
    print("  ✓ 对比发现月度间的微妙差异")
    print("  ✓ 理解香港气候的年度周期规律")
    print("  ✓ 数据艺术化的成功实践")

if __name__ == "__main__":
    # 运行完整的设计方案
    composer = MonthlyWindRoseComposer()
    
    # 创建示例数据
    wind_data = composer.create_sample_wind_data()
    
    # 分析月度模式
    monthly_stats = composer.analyze_monthly_patterns(wind_data)
    
    # 创建构成图
    composer.create_composition(monthly_stats)
    
    # 输出设计总结
    create_design_summary()
    
    print("\n✨ 新的设计方案演示完成！")
    print("这个方案通过网格构成和时间对比，让您清晰地看到:")
    print("• 每个月的独特风模式特征")
    print("• 季节之间的转换和差异") 
    print("• 全年风向分布的整体规律")
    print("• 简洁现代的设计美学表达")