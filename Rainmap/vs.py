import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 1. 加载数据
url_dir = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv"
url_speed = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv"

df_dir = pd.read_csv(url_dir)
df_speed = pd.read_csv(url_speed)

# 2. 检查数据结构和列名
print("Direction DataFrame Columns:", df_dir.columns.tolist())
print("Speed DataFrame Columns:", df_speed.columns.tolist())
print(df_dir.head())
print(df_speed.head())

# 假设列名是 ['Date', 'Direction'] 和 ['Date', 'Speed']
# 3. 合并数据集
df = pd.merge(df_dir, df_speed, on='Date', how='inner') # 确保日期匹配

# 4. 转换日期列并筛选2024年数据
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') # 根据实际日期格式调整
df_2024 = df[df['Date'].dt.year == 2024].copy()

# 5. 提取月份
df_2024['Month'] = df_2024['Date'].dt.month

# 6. 处理风向数据：如果风向是字符串（如'N', 'NE'），将其转换为角度
# 这是一个关键步骤，决定了后续可视化能否成功
if df_2024['Direction'].dtype == 'object':
    direction_map = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    }
    df_2024['Direction_angle'] = df_2024['Direction'].map(direction_map)
else:
    # 如果已经是角度，确保在0-360度之间
    df_2024['Direction_angle'] = df_2024['Direction'] % 360

print(df_2024.head())



# 计算每个月的总风速
monthly_speed = df_2024.groupby('Month')['Speed'].sum().to_dict()

# 为每个月的风向数据创建“桶”（16个方位）
# 将360度分为16个扇形，每个扇形22.5度
def get_direction_bucket(angle):
    buckets = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
               'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = int((angle + 11.25) % 360 / 22.5) # 加11.25使边界对齐
    return buckets[index]

df_2024['Direction_bucket'] = df_2024['Direction_angle'].apply(get_direction_bucket)

# 计算每个月中，各个风向的频率
monthly_wind_roses = {}
for month in range(1, 13):
    month_data = df_2024[df_2024['Month'] == month]
    # 计算16个方向的风频
    freq = month_data['Direction_bucket'].value_counts(normalize=True).to_dict()
    monthly_wind_roses[month] = freq




    # 1. 设置画布和极坐标轴
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N') # 让0度（北）在顶部
ax.set_theta_direction(-1) # 让角度顺时针方向增长

# 2. 定义颜色映射
# 为16个风向分配颜色，从北(蓝色)顺时针变化到西北(紫色)
direction_buckets = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
colors = plt.cm.plasma(np.linspace(0, 1, len(direction_buckets)))
color_map = dict(zip(direction_buckets, colors))

# 3. 计算每个扇形的角度范围
# 总圆周为2π，12个月，每个月的扇形弧度为 2π / 12
num_months = 12
theta_offset = np.pi / num_months # 半个扇形的角度偏移，用于居中

# 4. 确定扇形大小的缩放因子
# 我们将最大总风速的月份对应的扇形半径设为1，其他按比例缩放。
max_total_speed = max(monthly_speed.values())
radii = [monthly_speed[m] / max_total_speed for m in range(1, 13)]

# 5. 绘制每个月的扇形
for i, month in enumerate(range(1, 13)):
    # 计算当前扇形开始和结束的角度（弧度）
    theta_start = 2 * np.pi * (i / num_months) - theta_offset
    theta_end = 2 * np.pi * ((i+1) / num_months) - theta_offset
    theta_mid = (theta_start + theta_end) / 2 # 扇形中线的角度，用于放置月份标签

    # 获取当前月的风频数据
    wind_rose = monthly_wind_roses[month]
    current_radius = 0 # 从圆心开始绘制

    # 在这个扇区内，根据风频绘制不同颜色的子扇形
    for direction, freq in wind_rose.items():
        # 计算当前风向子扇形的半径增量
        delta_r = radii[i] * freq # 总半径 * 该风向的频率
        # 绘制子扇形
        ax.bar(x=theta_mid, 
               height=delta_r, 
               width=(theta_end - theta_start), 
               bottom=current_radius, 
               color=color_map[direction],
               edgecolor='white', 
               linewidth=0.5,
               alpha=0.8)
        # 更新当前半径
        current_radius += delta_r

    # 添加月份标签 (放在扇形外侧)
    label_radius = 1.05 * max(radii) # 标签位置略大于最大半径
    ax.text(theta_mid, label_radius, str(month), 
            ha='center', va='center', fontsize=12, fontweight='bold')

# 6. 美化图表
ax.set_xticks(np.linspace(0, 2*np.pi, 16, endpoint=False)) # 设置16个方位刻度
ax.set_xticklabels(direction_buckets)
ax.set_yticklabels([]) # 隐藏径向刻度标签
ax.spines['polar'].set_visible(False) # 隐藏极坐标 spines
plt.title('Hong Kong Airport 2024 - Meteorological Organism\n(Sector Size: Total Monthly Wind Speed, Color: Wind Direction Frequency)', pad=20, fontsize=14)

# 7. 添加图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color_map[dir], label=dir) for dir in direction_buckets]
ax.legend(handles=legend_elements, title='Wind Direction', bbox_to_anchor=(1.2, 1), loc='upper left')

plt.tight_layout()
plt.savefig('Meteorological_Organism_HKA_2024.png', dpi=300, bbox_inches='tight')
plt.show()