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
print("Direction DataFrame shape:", df_dir.shape)
print("Speed DataFrame shape:", df_speed.shape)
print("\nFirst few rows of Direction data:")
print(df_dir.head())
print("\nFirst few rows of Speed data:")
print(df_speed.head())

# 3. 动态获取列名（假设第一列是日期，第二列是数据）
date_col_dir = df_dir.columns[0]
direction_col = df_dir.columns[1] if len(df_dir.columns) > 1 else df_dir.columns[0]

date_col_speed = df_speed.columns[0]
speed_col = df_speed.columns[1] if len(df_speed.columns) > 1 else df_speed.columns[0]

print(f"\nUsing columns - Direction: {direction_col}, Speed: {speed_col}")

# 4. 重命名列以便后续处理
df_dir_clean = df_dir[[date_col_dir, direction_col]].copy()
df_dir_clean.columns = ['Date', 'Direction']

df_speed_clean = df_speed[[date_col_speed, speed_col]].copy()
df_speed_clean.columns = ['Date', 'Speed']

# 5. 合并数据集
df = pd.merge(df_dir_clean, df_speed_clean, on='Date', how='inner')
print(f"\nMerged data shape: {df.shape}")

# 6. 转换日期列并筛选2024年数据
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
df_2024 = df[df['Date'].dt.year == 2024].copy()
print(f"2024 data shape: {df_2024.shape}")

# 7. 清理数据，移除缺失值
df_2024 = df_2024.dropna(subset=['Direction', 'Speed'])
print(f"After removing NaN values: {df_2024.shape}")

if df_2024.empty:
    print("Error: No valid data for 2024!")
    exit()

# 8. 提取月份
df_2024['Month'] = df_2024['Date'].dt.month

# 9. 处理风向数据
print(f"\nDirection data type: {df_2024['Direction'].dtype}")
print(f"Sample direction values: {df_2024['Direction'].head(10).tolist()}")

if df_2024['Direction'].dtype == 'object':
    direction_map = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    }
    df_2024['Direction_angle'] = df_2024['Direction'].map(direction_map)
    # 移除无法映射的方向值
    df_2024 = df_2024.dropna(subset=['Direction_angle'])
else:
    df_2024['Direction_angle'] = pd.to_numeric(df_2024['Direction'], errors='coerce')
    df_2024 = df_2024.dropna(subset=['Direction_angle'])
    df_2024['Direction_angle'] = df_2024['Direction_angle'] % 360

# 10. 处理风速数据
df_2024['Speed'] = pd.to_numeric(df_2024['Speed'], errors='coerce')
df_2024 = df_2024.dropna(subset=['Speed'])

print(f"Final cleaned data shape: {df_2024.shape}")
print(f"Data summary:\n{df_2024.describe()}")

if df_2024.empty:
    print("Error: No valid data after cleaning!")
    exit()

# 计算每个月的总风速
monthly_speed = df_2024.groupby('Month')['Speed'].sum().to_dict()
print(f"\nMonthly wind speeds: {monthly_speed}")

# 为每个月的风向数据创建"桶"（16个方位）
def get_direction_bucket(angle):
    buckets = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
               'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = int((angle + 11.25) % 360 / 22.5)
    return buckets[index]

df_2024['Direction_bucket'] = df_2024['Direction_angle'].apply(get_direction_bucket)

# 计算每个月中，各个风向的频率
monthly_wind_roses = {}
for month in range(1, 13):
    month_data = df_2024[df_2024['Month'] == month]
    if not month_data.empty:
        freq = month_data['Direction_bucket'].value_counts(normalize=True).to_dict()
        monthly_wind_roses[month] = freq
    else:
        monthly_wind_roses[month] = {}

print(f"\nWind rose data for each month: {len(monthly_wind_roses)} months")

# 确保所有月份都有数据，如果没有则填充空字典
for month in range(1, 13):
    if month not in monthly_wind_roses:
        monthly_wind_roses[month] = {}
    if month not in monthly_speed:
        monthly_speed[month] = 0

# 绘图部分（修复缩进问题）
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

# 定义颜色映射
direction_buckets = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
colors = plt.cm.plasma(np.linspace(0, 1, len(direction_buckets)))
color_map = dict(zip(direction_buckets, colors))

# 计算每个扇形的角度范围
num_months = 12
theta_offset = np.pi / num_months

# 确定扇形大小的缩放因子
max_total_speed = max(monthly_speed.values()) if monthly_speed.values() else 1
radii = [monthly_speed[m] / max_total_speed for m in range(1, 13)]

# 绘制每个月的扇形
for i, month in enumerate(range(1, 13)):
    theta_start = 2 * np.pi * (i / num_months) - theta_offset
    theta_end = 2 * np.pi * ((i+1) / num_months) - theta_offset
    theta_mid = (theta_start + theta_end) / 2

    wind_rose = monthly_wind_roses[month]
    current_radius = 0

    for direction, freq in wind_rose.items():
        delta_r = radii[i] * freq
        ax.bar(x=theta_mid, 
               height=delta_r, 
               width=(theta_end - theta_start), 
               bottom=current_radius, 
               color=color_map[direction],
               edgecolor='white', 
               linewidth=0.5,
               alpha=0.8)
        current_radius += delta_r

    label_radius = 1.05 * max(radii) if radii else 1.05
    ax.text(theta_mid, label_radius, str(month), 
            ha='center', va='center', fontsize=12, fontweight='bold')

# 美化图表
ax.set_xticks(np.linspace(0, 2*np.pi, 16, endpoint=False))
ax.set_xticklabels(direction_buckets)
ax.set_yticklabels([])
ax.spines['polar'].set_visible(False)
plt.title('Hong Kong Airport 2024 - Meteorological Organism\n(Sector Size: Total Monthly Wind Speed, Color: Wind Direction Frequency)', pad=20, fontsize=14)

# 添加图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color_map[dir], label=dir) for dir in direction_buckets]
ax.legend(handles=legend_elements, title='Wind Direction', bbox_to_anchor=(1.2, 1), loc='upper left')

plt.tight_layout()
plt.savefig('Meteorological_Organism_HKA_2024.png', dpi=300, bbox_inches='tight')
plt.show()