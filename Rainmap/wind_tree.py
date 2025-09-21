# 风之分形树可视化 - 第一步：数据读取与清洗
# 读取2024年香港国际机场风速和风向数据

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

def load_wind_data():
    # 下载并读取风向和风速数据
    url_dir = 'https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv'
    url_spd = 'https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv'
    # 自动检测数据起始行，跳过多余表头
    import requests
    from io import StringIO
    def fetch_clean_csv(url):
        r = requests.get(url)
        lines = r.text.splitlines()
        print(f"First 10 lines of {url}:")
        for l in lines[:10]:
            print(l)
        # 宽松匹配Year/年
        header_idx = None
        for i, line in enumerate(lines):
            if ('Year' in line) or ('年' in line):
                header_idx = i
                print(f"Header found at line {i}: {line}")
                break
        if header_idx is None:
            raise ValueError('No header found in CSV')
        # 提取表头及数据部分
        data_lines = lines[header_idx:]
        csv_str = '\n'.join(data_lines)
        return pd.read_csv(StringIO(csv_str), encoding='utf-8')
    # 直接读取本地CSV文件，尝试多种编码
    dir_path = 'e:/PolyU/5913 Programming/daily_HKA_PDIR_ALL.csv'
    spd_path = 'e:/PolyU/5913 Programming/daily_HKA_WSPD_ALL.csv'
    
    def read_csv_with_encoding(filepath):
        encodings = ['utf-8-sig', 'gbk', 'gb2312', 'utf-8', 'latin1']
        for encoding in encodings:
            try:
                print(f"Trying to read {filepath} with encoding: {encoding}")
                df = pd.read_csv(filepath, encoding=encoding, skiprows=2)  # 跳过前两行标题
                print(f"Successfully read with encoding: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not read {filepath} with any encoding")
    
    df_dir = read_csv_with_encoding(dir_path)
    df_spd = read_csv_with_encoding(spd_path)
    
    print("Wind direction columns:", list(df_dir.columns))
    print("Wind speed columns:", list(df_spd.columns))
    print("First 5 rows of wind direction:")
    print(df_dir.head())
    print("First 5 rows of wind speed:")
    print(df_spd.head())
    # 用模糊匹配找到年份、风向、风速字段
    def find_col(cols, keywords):
        for k in keywords:
            for c in cols:
                if k in c:
                    return c
        return None
    year_col = find_col(df_dir.columns, ['Year', '年'])
    dir_col = find_col(df_dir.columns, ['Value', '數值'])
    spd_col = find_col(df_spd.columns, ['Value', '數值'])
    
    print(f"Found columns - Year: {year_col}, Direction: {dir_col}, Speed: {spd_col}")
    print(f"Year column data type: {df_dir[year_col].dtype}")
    print(f"Unique years in direction data: {df_dir[year_col].unique()}")
    print(f"Unique years in speed data: {df_spd[year_col].unique()}")
    
    # 只保留2024年数据，注意年份是字符串类型
    df_dir_2024 = df_dir[df_dir[year_col] == '2024']
    df_spd_2024 = df_spd[df_spd[year_col] == '2024']
    
    print(f"2024 data: direction={len(df_dir_2024)}, speed={len(df_spd_2024)}")
    
    # 合并为一个DataFrame
    min_len = min(len(df_dir_2024), len(df_spd_2024))
    df = pd.DataFrame({
        'day': range(1, min_len+1),
        'wind_dir': pd.to_numeric(df_dir_2024[dir_col].iloc[:min_len], errors='coerce'),
        'wind_spd': pd.to_numeric(df_spd_2024[spd_col].iloc[:min_len], errors='coerce')
    })
    df = df.dropna()
    print(f"Final data after cleaning: {len(df)} days")
    # 转为list of dicts，便于后续处理
    wind_data = df.to_dict(orient='records')
    return wind_data

def draw_wind_tree(wind_data):
    """绘制风之分形树"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(-50, 50)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('black')
    
    # 起始点和参数
    start_x, start_y = 0, 0
    current_x, current_y = start_x, start_y
    
    # 颜色映射：风向决定色相，风速决定明度
    colors = []
    for i, day_data in enumerate(wind_data):
        wind_dir = day_data['wind_dir']
        wind_spd = day_data['wind_spd']
        
        # 风向转换为角度（度转弧度）
        angle = math.radians(wind_dir)
        
        # 风速映射为分支长度（归一化到0.2-1.5）
        branch_length = 0.2 + (wind_spd / 35.0) * 1.3
        
        # 计算新的端点
        new_x = current_x + branch_length * math.sin(angle)
        new_y = current_y + branch_length * math.cos(angle)
        
        # 风向映射为颜色（HSV色彩空间）
        hue = wind_dir / 360.0
        saturation = 0.8
        value = 0.5 + (wind_spd / 35.0) * 0.5
        
        import colorsys
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # 绘制分支
        ax.plot([current_x, new_x], [current_y, new_y], 
                color=rgb, linewidth=1.5, alpha=0.7)
        
        # 更新当前位置
        current_x, current_y = new_x, new_y
    
    plt.title('Wind Tree - 2024 Hong Kong International Airport', 
              color='white', fontsize=16, pad=20)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    wind_data = load_wind_data()
    print(f"Loaded {len(wind_data)} days of wind data for 2024.")
    print("First 3 days:")
    for d in wind_data[:3]:
        print(d)
    
    # 绘制风之分形树
    draw_wind_tree(wind_data)
