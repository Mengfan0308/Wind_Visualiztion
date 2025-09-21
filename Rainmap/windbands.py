# PROGRAMMING FOR ARTISTS AND DESIGNERS - 风之音波抽象条带可视化
# 结合风速/风向数据、py5绘图、课程基础知识与设计美学

import pandas as pd
import math
import py5

# 1. 读取和处理数据
def load_wind_data():
	# 读取2024年风速和风向数据
	url_dir = 'https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv'
	url_spd = 'https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv'
	df_dir = pd.read_csv(url_dir, encoding='utf-8')
	df_spd = pd.read_csv(url_spd, encoding='utf-8')
	# 只保留2024年数据
	df_dir = df_dir[df_dir['年/Year'] == 2024]
	df_spd = df_spd[df_spd['年/Year'] == 2024]
	# 合并
	df = pd.DataFrame({
		'day': range(1, len(df_dir)+1),
		'wind_dir': pd.to_numeric(df_dir['數值/Value'], errors='coerce'),
		'wind_spd': pd.to_numeric(df_spd['數值/Value'], errors='coerce')
	})
	df = df.dropna()
	return df

# 2. 颜色映射函数（HSB色彩空间）
def wind_to_color(wind_dir, wind_spd, spd_min=0, spd_max=30):
	# 风向0-360度映射色相(0-255)，风速映射明度(80-255)
	h = int((wind_dir % 360) / 360 * 255)
	b = int(80 + (wind_spd - spd_min) / (spd_max - spd_min) * 175)
	return py5.color(h, 180, b, 180)  # 半透明

# 3. 条带绘制函数
def draw_band(data, y_base, amp, color_func):
	py5.begin_shape()
	for i, row in data.iterrows():
		x = py5.remap(i, 0, len(data)-1, 60, py5.width-60)
		# 主条带：正弦+风速扰动
		y = y_base + math.sin(i*0.04) * 20 + row['wind_spd'] * amp
		c = color_func(row['wind_dir'], row['wind_spd'])
		py5.stroke(c)
		py5.stroke_weight(2)
		py5.no_fill()
		py5.vertex(x, y)
	py5.end_shape()

# 4. py5主循环
def setup():
	global wind_data
	py5.size(1200, 600)
	py5.background(245)
	py5.color_mode(py5.HSB, 255)
	wind_data = load_wind_data()

def draw():
	py5.background(245)
	# 主条带
	draw_band(wind_data, y_base=py5.height//2, amp=2.5, color_func=wind_to_color)
	# 可添加辅助条带、渐变、叠加等

py5.run_sketch()
