# Step 1: Data Acquisition and Cleaning for Ridge Plot (2024 Hong Kong Airport Wind)
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar

# URLs for wind direction and wind speed data
url_dir = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv"
url_spd = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv"

# Read CSVs (auto-detect encoding)
# 读取风向和风速数据，跳过前两行，第三行为真正表头
try:
    df_dir = pd.read_csv(url_dir, encoding='utf-8-sig', skiprows=2, header=0)
except Exception:
    df_dir = pd.read_csv(url_dir, encoding='utf-8', skiprows=2, header=0)
try:
    df_spd = pd.read_csv(url_spd, encoding='utf-8-sig', skiprows=2, header=0)
except Exception:
    df_spd = pd.read_csv(url_spd, encoding='utf-8', skiprows=2, header=0)
# 只保留第二行表头
if isinstance(df_dir.columns, pd.MultiIndex):
    df_dir.columns = df_dir.columns.get_level_values(-1)
if isinstance(df_spd.columns, pd.MultiIndex):
    df_spd.columns = df_spd.columns.get_level_values(-1)

# Debug: print columns and first few rows to check actual headers
print('df_dir columns:', df_dir.columns)
print(df_dir.head())
print('df_spd columns:', df_spd.columns)
print(df_spd.head())

# Debug: 打印所有列名的repr，定位不可见字符
print('df_dir columns repr:', [repr(col) for col in df_dir.columns])
print('df_spd columns repr:', [repr(col) for col in df_spd.columns])

# 去除所有列名的前后空格，保证后续处理不出错
df_dir.columns = df_dir.columns.str.strip()
df_spd.columns = df_spd.columns.str.strip()

# 统一清理所有列名，全部转英文
for df_ in [df_dir, df_spd]:
    df_.columns = df_.columns.str.strip()
    col_map = {
        '年/Year': 'Year',
        '月/Month': 'Month',
        '日/Day': 'Day',
        df_.columns[3]: 'Value'  # 第四列为Value
    }
    df_.rename(columns=col_map, inplace=True)
# 分别重命名为Value_dir和Value_spd
df_dir.rename(columns={'Value': 'Value_dir'}, inplace=True)
df_spd.rename(columns={'Value': 'Value_spd'}, inplace=True)

# 只保留需要的列
keep_cols_dir = ['Year', 'Month', 'Day', 'Value_dir']
keep_cols_spd = ['Year', 'Month', 'Day', 'Value_spd']
df_dir = df_dir[keep_cols_dir]
df_spd = df_spd[keep_cols_spd]

# 转换Year/Month/Day为整数
for col in ['Year', 'Month', 'Day']:
    df_dir[col] = pd.to_numeric(df_dir[col], errors='coerce')
    df_spd[col] = pd.to_numeric(df_spd[col], errors='coerce')

# 去除无效行
for df_ in [df_dir, df_spd]:
    df_.dropna(subset=['Year', 'Month', 'Day'], inplace=True)
    df_['Year'] = df_['Year'].astype(int)
    df_['Month'] = df_['Month'].astype(int)
    df_['Day'] = df_['Day'].astype(int)

# 只保留英文列名后的数据清洗
# 将Value_dir和Value_spd转为数值
for col in ['Value_dir']:
    df_dir[col] = pd.to_numeric(df_dir[col], errors='coerce')
for col in ['Value_spd']:
    df_spd[col] = pd.to_numeric(df_spd[col], errors='coerce')
# 去除无效行
df_dir = df_dir.dropna(subset=['Year', 'Month', 'Day', 'Value_dir'])
df_spd = df_spd.dropna(subset=['Year', 'Month', 'Day', 'Value_spd'])
# 转换为整数
df_dir['Year'] = df_dir['Year'].astype(int)
df_dir['Month'] = df_dir['Month'].astype(int)
df_dir['Day'] = df_dir['Day'].astype(int)
df_spd['Year'] = df_spd['Year'].astype(int)
df_spd['Month'] = df_spd['Month'].astype(int)
df_spd['Day'] = df_spd['Day'].astype(int)
# 只保留2024年
df_dir = df_dir[df_dir['Year'] == 2024]
df_spd = df_spd[df_spd['Year'] == 2024]

# Merge on Year, Month, Day
df = pd.merge(df_dir, df_spd, on=['Year', 'Month', 'Day'], suffixes=('_dir', '_spd'))

# Keep only relevant columns and rename for clarity
df = df[['Year', 'Month', 'Day', 'Value_dir', 'Value_spd']]
df.columns = ['Year', 'Month', 'Day', 'Wind_Direction', 'Wind_Speed']

# Drop rows with missing or invalid data
df = df.dropna(subset=['Wind_Direction', 'Wind_Speed'])
df = df[(df['Wind_Direction'] >= 0) & (df['Wind_Direction'] <= 360)]
df = df[(df['Wind_Speed'] >= 0)]

# Add a date column for convenience
df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

# Preview cleaned data
print(df.head())

# Step 2: Ridge Plot Visualization (Wind Speed Distribution by Month)

# Prepare data for ridge plot: each row = one day, columns: Month (name), Wind_Speed
# Add English month name for better plot labels
month_names = [calendar.month_abbr[m] for m in df['Month']]
df['Month_Eng'] = month_names

# Sort months for correct order in plot
df['Month_Eng'] = pd.Categorical(df['Month_Eng'], categories=calendar.month_abbr[1:], ordered=True)

# Create ridge plot using Plotly Express
fig = px.violin(
    df,
    y="Month_Eng",
    x="Wind_Speed",
    orientation="h",
    color="Month_Eng",
    category_orders={"Month_Eng": list(calendar.month_abbr[1:])},
    box=True, # show boxplot inside violin
    points="all", # show all data points
    hover_data=["Date", "Wind_Direction"],
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig.update_traces(meanline_visible=True, width=3, opacity=0.8)
fig.update_layout(
    title="2024 Hong Kong International Airport Wind Speed Ridge Plot",
    xaxis_title="Wind Speed (km/h)",
    yaxis_title="Month",
    legend_title="Month",
    template="simple_white",
    height=700,
    width=1000,
    font=dict(family="Arial", size=14),
    showlegend=False
)

fig.show()
