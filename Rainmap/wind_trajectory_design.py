# WIND TRAJECTORY - 数据驱动设计方案
# Programming for Artists and Designers - 香港机场2024风数据可视化
# Author: 学生作品 | Date: 2024

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

print("=== WIND TRAJECTORY: 数据驱动设计方案 ===")
print("课程：PROGRAMMING FOR ARTISTS AND DESIGNERS")
print("数据源：香港国际机场2024年风数据")
print("设计理念：让风数据在画布上绘制自己的轨迹\n")

# =================================
# 1. 数据驱动设计核心算法
# =================================

class WindTrajectoryArtist:
    """风轨迹艺术生成器 - 数据驱动的艺术创作工具"""
    
    def __init__(self, canvas_size=(1000, 1000)):
        """初始化画布和参数"""
        self.canvas_size = canvas_size
        self.center_x = canvas_size[0] // 2
        self.center_y = canvas_size[1] // 2
        
        # 当前轨迹位置
        self.current_x = self.center_x
        self.current_y = self.center_y
        
        # 存储完整轨迹路径
        self.trajectory_points = [(self.current_x, self.current_y)]
        self.daily_vectors = []
        
        # 设计参数
        self.speed_scale = 2.5  # 风速到像素的缩放比例
        self.min_line_width = 0.5
        self.max_line_width = 3.0
        
        print(f"✓ 画布初始化: {canvas_size[0]}x{canvas_size[1]} 像素")
        print(f"✓ 起始中心点: ({self.center_x}, {self.center_y})")
    
    def wind_to_movement_vector(self, wind_direction_deg, wind_speed_kmh):
        """
        核心算法：将风数据转换为移动向量
        
        数据驱动规则：
        - 风向角度 → 移动方向（数学坐标系，0°=北，顺时针）
        - 风速 → 移动距离（km/h 缩放到像素）
        """
        # 转换角度：气象角度(北=0°,顺时针) → 数学角度(东=0°,逆时针)
        math_angle_rad = np.radians(90 - wind_direction_deg)
        
        # 计算移动向量（像素）
        dx = wind_speed_kmh * self.speed_scale * np.cos(math_angle_rad)
        dy = wind_speed_kmh * self.speed_scale * np.sin(math_angle_rad)
        
        return dx, dy
    
    def date_to_seasonal_color(self, date_obj):
        """
        数据驱动色彩：将日期转换为季节性颜色
        
        色彩映射：
        春季 (3-5月): 新绿色调
        夏季 (6-8月): 暖红色调  
        秋季 (9-11月): 金橙色调
        冬季 (12-2月): 冷蓝色调
        """
        month = date_obj.month
        day_of_year = date_obj.timetuple().tm_yday
        
        # 定义季节色彩
        spring_color = np.array([46, 204, 113]) / 255  # #2ecc71
        summer_color = np.array([231, 76, 60]) / 255   # #e74c3c  
        autumn_color = np.array([243, 156, 18]) / 255  # #f39c12
        winter_color = np.array([52, 152, 219]) / 255  # #3498db
        
        # 基于月份的季节映射
        if 3 <= month <= 5:  # 春季
            base_color = spring_color
            season_progress = (day_of_year - 60) / 92  # 3月1日到5月31日
        elif 6 <= month <= 8:  # 夏季
            base_color = summer_color
            season_progress = (day_of_year - 152) / 92  # 6月1日到8月31日
        elif 9 <= month <= 11:  # 秋季
            base_color = autumn_color
            season_progress = (day_of_year - 244) / 91  # 9月1日到11月30日
        else:  # 冬季 (12, 1, 2月)
            base_color = winter_color
            if month == 12:
                season_progress = (day_of_year - 335) / 90
            else:  # 1月或2月
                season_progress = (day_of_year + 31) / 90
        
        # 季节内的微调（增加渐变变化）
        season_progress = np.clip(season_progress, 0, 1)
        brightness_variation = 0.8 + 0.4 * season_progress  # 0.8-1.2的亮度变化
        
        return base_color * brightness_variation
    
    def wind_speed_to_line_width(self, wind_speed_kmh):
        """数据驱动线宽：风速 → 线条粗细"""
        # 假设风速范围 0-40 km/h
        normalized_speed = np.clip(wind_speed_kmh / 40.0, 0, 1)
        line_width = self.min_line_width + normalized_speed * (self.max_line_width - self.min_line_width)
        return line_width
    
    def add_daily_wind_step(self, date_obj, wind_direction_deg, wind_speed_kmh):
        """
        添加一天的风数据步骤
        这是核心的数据驱动绘制函数
        """
        # 1. 计算移动向量
        dx, dy = self.wind_to_movement_vector(wind_direction_deg, wind_speed_kmh)
        
        # 2. 更新位置
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        # 3. 计算视觉属性
        color = self.date_to_seasonal_color(date_obj)
        line_width = self.wind_speed_to_line_width(wind_speed_kmh)
        
        # 4. 存储轨迹数据
        daily_data = {
            'date': date_obj,
            'start_pos': (self.current_x, self.current_y),
            'end_pos': (new_x, new_y),
            'wind_direction': wind_direction_deg,
            'wind_speed': wind_speed_kmh,
            'movement_vector': (dx, dy),
            'color': color,
            'line_width': line_width
        }
        
        self.daily_vectors.append(daily_data)
        self.trajectory_points.append((new_x, new_y))
        
        # 5. 更新当前位置
        self.current_x = new_x
        self.current_y = new_y
        
        return daily_data

# =================================
# 2. 示例：使用模拟数据演示算法
# =================================

def create_sample_wind_data():
    """创建示例风数据用于算法演示"""
    print("\n=== 创建模拟风数据用于算法演示 ===")
    
    # 生成2024年全年的模拟风数据
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(366)]  # 2024是闰年
    
    # 模拟真实的季节性风模式
    wind_data = []
    for i, date in enumerate(dates):
        month = date.month
        
        # 季节性风向模式（香港主要受季风影响）
        if 4 <= month <= 9:  # 夏季风：偏南风
            base_direction = 180 + np.random.normal(0, 45)
        else:  # 冬季风：偏北风
            base_direction = 0 + np.random.normal(0, 45)
        
        direction = base_direction % 360
        
        # 季节性风速模式
        if month in [6, 7, 8]:  # 夏季台风季节
            speed = np.random.lognormal(2.5, 0.7)  # 更高的风速
        else:
            speed = np.random.lognormal(2.0, 0.5)  # 正常风速
        
        speed = np.clip(speed, 1, 40)  # 限制在合理范围
        
        wind_data.append({
            'date': date,
            'direction': direction,
            'speed': speed
        })
    
    print(f"✓ 生成了 {len(wind_data)} 天的模拟风数据")
    return wind_data

def visualize_trajectory_algorithm():
    """可视化轨迹生成算法"""
    print("\n=== 可视化轨迹算法演示 ===")
    
    # 1. 创建轨迹艺术家
    artist = WindTrajectoryArtist(canvas_size=(800, 800))
    
    # 2. 获取模拟数据
    wind_data = create_sample_wind_data()
    
    # 3. 处理每日风数据
    print("正在处理366天的风数据...")
    for i, day_data in enumerate(wind_data):
        if i % 50 == 0:  # 进度显示
            print(f"处理进度: {i+1}/366 天")
        
        artist.add_daily_wind_step(
            day_data['date'],
            day_data['direction'],
            day_data['speed']
        )
    
    print("✓ 所有风数据处理完成")
    
    # 4. 绘制最终轨迹艺术作品
    print("正在生成艺术作品...")
    
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 800)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 绘制轨迹路径
    for i, daily_data in enumerate(artist.daily_vectors):
        start_x, start_y = daily_data['start_pos']
        end_x, end_y = daily_data['end_pos']
        color = daily_data['color']
        line_width = daily_data['line_width']
        
        # 计算透明度（远离起点的轨迹更透明）
        distance_from_center = np.sqrt((end_x - artist.center_x)**2 + (end_y - artist.center_y)**2)
        max_distance = np.sqrt(2) * 400  # 画布对角线的一半
        alpha = 0.7 - 0.4 * (distance_from_center / max_distance)
        alpha = np.clip(alpha, 0.1, 0.8)
        
        ax.plot([start_x, end_x], [start_y, end_y], 
                color=color, linewidth=line_width, alpha=alpha,
                solid_capstyle='round')
    
    # 添加中心点标记
    ax.scatter([artist.center_x], [artist.center_y], 
               c='white', s=100, alpha=0.9, marker='o', 
               edgecolors='yellow', linewidth=2, zorder=10)
    
    # 添加标题和说明
    fig.suptitle('WIND TRAJECTORY - 数据驱动艺术设计\n香港机场2024年风数据轨迹可视化', 
                 fontsize=16, color='white', y=0.95)
    
    plt.figtext(0.02, 0.02, 
                '数据驱动规则:\n'
                '• 风向 → 移动方向\n'
                '• 风速 → 移动距离 & 线条粗细\n'
                '• 季节 → 颜色渐变\n'
                '• 累积轨迹 → 有机艺术图案\n\n'
                '春绿 → 夏红 → 秋橙 → 冬蓝',
                fontsize=10, color='white', family='monospace')
    
    plt.tight_layout()
    
    # 保存示例作品
    filename = 'Wind_Trajectory_Algorithm_Demo.png'
    plt.savefig(filename, dpi=300, facecolor='black', edgecolor='none')
    print(f"✓ 算法演示图像已保存: {filename}")
    
    plt.show()
    
    # 5. 输出统计信息
    print("\n=== 轨迹统计信息 ===")
    print(f"总移动距离: {len(artist.daily_vectors)} 步")
    
    final_distance = np.sqrt((artist.current_x - artist.center_x)**2 + 
                           (artist.current_y - artist.center_y)**2)
    print(f"最终距离中心: {final_distance:.1f} 像素")
    
    avg_speed = np.mean([d['wind_speed'] for d in artist.daily_vectors])
    print(f"平均风速: {avg_speed:.1f} km/h")
    
    return artist

# =================================
# 3. 设计方案总结
# =================================

def print_design_summary():
    """打印完整的数据驱动设计方案总结"""
    print("\n" + "="*60)
    print("    WIND TRAJECTORY - 数据驱动设计方案总结")
    print("="*60)
    
    print("\n🎨 设计理念:")
    print("  将自然界的风数据转化为艺术轨迹，让数据自己创作艺术作品")
    
    print("\n📊 数据映射关系:")
    print("  风向角度 (0-360°) → 移动方向角度")
    print("  风速 (km/h) → 移动距离 + 线条粗细")
    print("  日期/季节 → 颜色渐变 (春绿→夏红→秋橙→冬蓝)")
    print("  累积路径 → 有机艺术图案")
    
    print("\n🔧 核心算法:")
    print("  1. 从画布中心 (0,0) 开始")
    print("  2. 每日根据风向风速计算移动向量")  
    print("  3. 累积绘制连续轨迹路径")
    print("  4. 应用季节色彩和视觉增强")
    
    print("\n🎯 艺术目标:")
    print("  创造一幅完全由真实风数据驱动的抽象艺术作品")
    print("  展现数据可视化与艺术表达的完美结合")
    print("  体现香港2024年风模式的自然美学")
    
    print("\n✅ 下一步实现:")
    print("  1. 获取真实香港机场风数据")
    print("  2. 实现完整的轨迹绘制引擎")  
    print("  3. 添加高级视觉效果和美化")
    print("  4. 生成最终艺术作品")

if __name__ == "__main__":
    # 运行完整的设计方案演示
    print_design_summary()
    
    # 演示数据驱动算法
    artist = visualize_trajectory_algorithm()
    
    print("\n✨ 数据驱动设计方案演示完成!")
    print("这个方案将真实的风数据转化为独特的艺术轨迹。")
    print("每一条线、每一个颜色、每一个移动都由真实数据决定。")
    print("这就是数据驱动设计的魅力所在！")