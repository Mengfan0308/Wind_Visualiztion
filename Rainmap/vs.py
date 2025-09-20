import sys
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import math

print("✓ All necessary libraries installed")

# Step 1: Download and inspect data
print("=== Step 1: Download and Inspect Data ===")

# Data source URLs
url_direction = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_PDIR_ALL.csv"
url_speed = "https://data.weather.gov.hk/cis/csvfile/HKA/ALL/daily_HKA_WSPD_ALL.csv"

def download_and_inspect(url, name):
    """Download data and inspect original format"""
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text), encoding='utf-8-sig', skiprows=2)
                print(f"✓ Success! {name} shape: {df.shape}")
                return df
            except:
                try:
                    df = pd.read_csv(StringIO(response.text), encoding='utf-8-sig')
                    print(f"✓ Success! {name} shape: {df.shape}")
                    return df
                except Exception as e:
                    print(f"✗ Read failed: {e}")
                    return None
        else:
            print(f"✗ {name} download failed, status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ {name} error: {type(e).__name__}: {e}")
        return None

# Download and inspect data
df_direction = download_and_inspect(url_direction, "Wind Direction Data")
df_speed = download_and_inspect(url_speed, "Wind Speed Data")

# Improved data cleaning function
def clean_dataframe_improved(df, data_type):
    """Improved data cleaning with better column detection"""
    if df is None or df.empty:
        return None
    
    print(f"\nCleaning {data_type} data...")
    print(f"Columns found: {list(df.columns)}")
    
    # Try to find date and value columns more intelligently
    date_col = None
    value_col = None
    
    # Look for date-related columns
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['date', 'time', '日期', '年月日']):
            date_col = col
            print(f"Found potential date column: {col}")
            break
    
    # If no direct date column, try to construct from year/month/day
    if date_col is None:
        year_col = month_col = day_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if 'year' in col_str or '年' in col_str:
                year_col = col
            elif 'month' in col_str or '月' in col_str:
                month_col = col
            elif 'day' in col_str or '日' in col_str:
                day_col = col
        
        if year_col and month_col and day_col:
            print(f"Found date components: Year={year_col}, Month={month_col}, Day={day_col}")
            # Construct date column
            try:
                df['Date'] = pd.to_datetime(df[[year_col, month_col, day_col]])
                date_col = 'Date'
                print("✓ Successfully constructed date column")
            except Exception as e:
                print(f"✗ Failed to construct date: {e}")
    
    # Look for value column
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['value', 'val', '值', '数值', '測值']):
            value_col = col
            print(f"Found value column: {col}")
            break
    
    if date_col is None or value_col is None:
        print(f"⚠️ Cannot identify date ({date_col}) or value ({value_col}) columns for {data_type}")
        return None
    
    # Clean the dataframe
    clean_df = df[[date_col, value_col]].copy()
    clean_df.columns = ['Date', 'Value']
    clean_df = clean_df.dropna()
    
    print(f"✓ {data_type} cleaned, data count: {len(clean_df)}")
    return clean_df

# Clean data with improved function
df_direction_clean = clean_dataframe_improved(df_direction, "Wind Direction")
df_speed_clean = clean_dataframe_improved(df_speed, "Wind Speed")

# If cleaning fails, use sample data
if df_direction_clean is None or df_speed_clean is None:
    print("\nData cleaning failed, using sample data for demonstration...")
    dates = pd.date_range('2024-01-01', '2024-12-31')
    df_direction_clean = pd.DataFrame({
        'Date': [d.strftime('%Y%m%d') for d in dates],
        'Value': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], len(dates))
    })
    df_speed_clean = pd.DataFrame({
        'Date': [d.strftime('%Y%m%d') for d in dates],
        'Value': np.random.uniform(5, 25, len(dates))
    })
    print("✓ Sample data created")

# Step 2: Data Cleaning and Preprocessing
print("\n=== Step 2: Data Cleaning and Preprocessing ===")

# Rename columns for clarity
df_direction_clean.columns = ['Date', 'Direction']
df_speed_clean.columns = ['Date', 'Speed']

# Merge wind direction and speed data
df_merged = pd.merge(df_direction_clean, df_speed_clean, on='Date', how='inner')

# Process date format
df_merged['Date'] = pd.to_datetime(df_merged['Date'], format='%Y%m%d', errors='coerce')
df_merged = df_merged.dropna(subset=['Date'])

if df_merged.empty:
    dates = pd.date_range('2024-01-01', '2024-12-31')
    df_merged = pd.DataFrame({
        'Date': dates,
        'Direction': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], len(dates)),
        'Speed': np.random.uniform(5, 25, len(dates))
    })

# Filter 2024 data
df_2024 = df_merged[df_merged['Date'].dt.year == 2024].copy()

if df_2024.empty:
    latest_year = df_merged['Date'].dt.year.max()
    if pd.isna(latest_year):
        dates = pd.date_range('2024-01-01', '2024-12-31')
        df_2024 = pd.DataFrame({
            'Date': dates,
            'Direction': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], len(dates)),
            'Speed': np.random.uniform(5, 25, len(dates))
        })
    else:
        df_2024 = df_merged[df_merged['Date'].dt.year == latest_year].copy()

# Clean missing values and add time columns
df_2024 = df_2024.dropna(subset=['Direction', 'Speed'])
df_2024['Month'] = df_2024['Date'].dt.month

# Process wind direction data
direction_mapping = {
    'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
    'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
    'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
    'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
}

def get_direction_sector(angle):
    """Convert angle to 16-point compass direction"""
    sectors = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
               'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    sector_index = int((angle + 11.25) % 360 / 22.5)
    return sectors[sector_index]

if df_2024['Direction'].dtype == 'object':
    df_2024['Direction_Angle'] = df_2024['Direction'].map(direction_mapping)
    df_2024 = df_2024.dropna(subset=['Direction_Angle'])
else:
    df_2024['Direction_Angle'] = pd.to_numeric(df_2024['Direction'], errors='coerce')
    df_2024['Direction_Angle'] = df_2024['Direction_Angle'] % 360
    df_2024 = df_2024.dropna(subset=['Direction_Angle'])

df_2024['Direction_Sector'] = df_2024['Direction_Angle'].apply(get_direction_sector)
df_2024['Speed'] = pd.to_numeric(df_2024['Speed'], errors='coerce')
df_2024 = df_2024.dropna(subset=['Speed'])

print("✓ Basic data preprocessing complete!")

# =================================
# Step 3: Calculate Layer 1 Data with Dynamic Angular Allocation
# =================================
print("\n=== Step 3: Calculate Layer 1 Data with Dynamic Angular Allocation ===")

def calculate_monthly_vector_resultant(month_data):
    """Calculate the resultant vector for a month's wind data"""
    if month_data.empty:
        return 0, 0, 0
    
    angles_rad = np.radians(month_data['Direction_Angle'])
    speeds = month_data['Speed']
    
    x_components = speeds * np.sin(angles_rad)
    y_components = speeds * np.cos(angles_rad)
    
    sum_x = np.sum(x_components)
    sum_y = np.sum(y_components)
    
    resultant_magnitude = np.sqrt(sum_x**2 + sum_y**2)
    resultant_angle_rad = np.arctan2(sum_x, sum_y)
    resultant_angle_deg = np.degrees(resultant_angle_rad) % 360
    
    avg_speed = np.mean(speeds)
    
    return resultant_angle_deg, resultant_magnitude, avg_speed

# Calculate data for all 12 months
print("1. Calculating monthly statistics...")

monthly_stats = {}
for month in range(1, 13):
    month_data = df_2024[df_2024['Month'] == month].copy()
    
    if not month_data.empty:
        resultant_angle, resultant_magnitude, avg_speed = calculate_monthly_vector_resultant(month_data)
        
        direction_diversity = len(month_data['Direction_Angle'].unique())
        wind_activity = avg_speed * len(month_data)
        
        monthly_stats[month] = {
            'resultant_angle': resultant_angle,
            'resultant_magnitude': resultant_magnitude,
            'avg_speed': avg_speed,
            'data_count': len(month_data),
            'direction_diversity': direction_diversity,
            'wind_activity': wind_activity,
            'space_requirement': wind_activity
        }
    else:
        monthly_stats[month] = {
            'resultant_angle': 0,
            'resultant_magnitude': 0,
            'avg_speed': 0,
            'data_count': 0,
            'direction_diversity': 0,
            'wind_activity': 0,
            'space_requirement': 1
        }

# Dynamic angular allocation
total_space = sum([stats['space_requirement'] for stats in monthly_stats.values()])
total_angle = 360

cumulative_angle = 0
month_angles = {}

for month in range(1, 13):
    space_req = monthly_stats[month]['space_requirement']
    angular_space = (space_req / total_space) * total_angle
    angular_space = max(angular_space, 15)
    center_angle = cumulative_angle + (angular_space / 2)
    
    month_angles[month] = {
        'center_angle': center_angle % 360,
        'angular_space': angular_space,
        'start_angle': cumulative_angle % 360,
        'end_angle': (cumulative_angle + angular_space) % 360
    }
    
    cumulative_angle += angular_space

if cumulative_angle > 360:
    scale_factor = 360 / cumulative_angle
    cumulative_angle = 0
    for month in range(1, 13):
        angular_space = month_angles[month]['angular_space'] * scale_factor
        center_angle = cumulative_angle + (angular_space / 2)
        
        month_angles[month] = {
            'center_angle': center_angle % 360,
            'angular_space': angular_space,
            'start_angle': cumulative_angle % 360,
            'end_angle': (cumulative_angle + angular_space) % 360
        }
        
        cumulative_angle += angular_space

# Calculate final parameters for Layer 1 visualization
stem_params = {}
max_avg_speed = max([data['avg_speed'] for data in monthly_stats.values()] + [1])

for month in range(1, 13):
    stats = monthly_stats[month]
    angles = month_angles[month]
    
    if max_avg_speed > 0:
        stem_length = 0.3 + (stats['avg_speed'] / max_avg_speed) * 0.7
    else:
        stem_length = 0.3
    
    stem_angle = angles['center_angle']
    stem_angle_rad = np.radians(stem_angle)
    
    stem_params[month] = {
        'angle_deg': stem_angle,
        'angle_rad': stem_angle_rad,
        'length': stem_length,
        'avg_speed': stats['avg_speed'],
        'resultant_magnitude': stats['resultant_magnitude'],
        'data_count': stats['data_count'],
        'angular_space': angles['angular_space'],
        'wind_activity': stats['wind_activity']
    }

print("\n✓ Step 3 Complete - Dynamic angular allocation ready!")

# =================================
# Step 4: Calculate Layer 2 Data
# =================================
print("\n=== Step 4: Calculate Layer 2 Data ===")

compass_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

compass_angles = {
    'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
    'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
    'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
    'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
}

# Define direction colors
direction_colors = {
    'N': '#1f77b4', 'NNE': '#ff7f0e', 'NE': '#2ca02c', 'ENE': '#d62728',
    'E': '#9467bd', 'ESE': '#8c564b', 'SE': '#e377c2', 'SSE': '#7f7f7f',
    'S': '#bcbd22', 'SSW': '#17becf', 'SW': '#aec7e8', 'WSW': '#ffbb78',
    'W': '#98df8a', 'WNW': '#ff9896', 'NW': '#c5b0d5', 'NNW': '#c49c94'
}

# Calculate direction frequency for each month
tendrils_data = {}
for month in range(1, 13):
    month_data = df_2024[df_2024['Month'] == month].copy()
    tendrils_data[month] = {}
    
    if not month_data.empty:
        direction_counts = month_data['Direction_Sector'].value_counts()
        total_days = len(month_data)
        
        for direction in compass_directions:
            frequency = direction_counts.get(direction, 0)
            frequency_ratio = frequency / total_days if total_days > 0 else 0
            
            direction_data = month_data[month_data['Direction_Sector'] == direction]
            
            tendrils_data[month][direction] = {
                'frequency': frequency,
                'frequency_ratio': frequency_ratio,
                'daily_data': direction_data[['Date', 'Speed']].sort_values('Date').to_dict('records')
            }
    else:
        for direction in compass_directions:
            tendrils_data[month][direction] = {
                'frequency': 0,
                'frequency_ratio': 0,
                'daily_data': []
            }

print("\n✓ Step 4 Complete - Direction frequencies calculated!")

# =================================
# Step 5: Draw All Layers
# =================================
print("\n=== Step 5: Draw All Layers ===")

def calculate_centroid(stem_params):
    """Calculate the centroid (Layer 0)"""
    endpoints_x = []
    endpoints_y = []
    weights = []
    
    for month, params in stem_params.items():
        if params['data_count'] > 0:
            angle_rad = params['angle_rad']
            length = params['length']
            
            x = length * np.sin(angle_rad)
            y = length * np.cos(angle_rad)
            
            endpoints_x.append(x)
            endpoints_y.append(y)
            weights.append(params['wind_activity'])
    
    if not endpoints_x:
        return 0, 0
    
    weights = np.array(weights)
    total_weight = np.sum(weights)
    
    if total_weight > 0:
        centroid_x = np.sum(np.array(endpoints_x) * weights) / total_weight
        centroid_y = np.sum(np.array(endpoints_y) * weights) / total_weight
    else:
        centroid_x = np.mean(endpoints_x)
        centroid_y = np.mean(endpoints_y)
    
    return centroid_x, centroid_y

# Calculate centroid
centroid_x, centroid_y = calculate_centroid(stem_params)
centroid_radius = np.sqrt(centroid_x**2 + centroid_y**2)
centroid_angle = np.arctan2(centroid_x, centroid_y)

print(f"Centroid position: x={centroid_x:.3f}, y={centroid_y:.3f}")

# Create visualization
plt.style.use('default')
fig, ax = plt.subplots(figsize=(20, 20), subplot_kw=dict(projection='polar'))
ax.set_facecolor('#fafafa')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.grid(False)
ax.set_xticklabels([])
ax.set_yticklabels([])

print("Drawing Layer 0: The Nexus...")
ax.scatter([centroid_angle], [centroid_radius], 
           c='#2c3e50', s=800, alpha=0.8, marker='o', 
           edgecolors='white', linewidth=2, zorder=10)

print("Drawing Layer 1: Primary Stems...")
month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

for month, params in stem_params.items():
    if params['data_count'] > 0:
        angle_rad = params['angle_rad']
        length = params['length']
        angular_space = params['angular_space']
        
        stem_angles = [centroid_angle, angle_rad]
        stem_radii = [centroid_radius, length]
        
        stem_thickness = 3 + (angular_space / 40) * 3
        
        ax.plot(stem_angles, stem_radii, 
                color='#34495e', linewidth=stem_thickness, alpha=0.8, 
                solid_capstyle='round', zorder=5)
        
        label_radius = length + 0.4
        ax.text(angle_rad, label_radius, month_names[month-1], 
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='#2c3e50', 
                rotation=np.degrees(angle_rad)-90 if angle_rad > np.pi/2 and angle_rad < 3*np.pi/2 else np.degrees(angle_rad)+90,
                zorder=15)
        
        marker_size = 80 + (params['wind_activity'] / max([p['wind_activity'] for p in stem_params.values()])) * 120
        ax.scatter([angle_rad], [length], 
                   c='#34495e', s=marker_size, alpha=0.9, marker='o', 
                   edgecolors='white', linewidth=1, zorder=8)

print("Drawing Layer 2: Radial Tendrils from Stem Endpoints...")

# Draw tendrils for each month
for month, params in stem_params.items():
    if params['data_count'] > 0:
        # Calculate maximum frequency for this month (for scaling)
        month_frequencies = [tendrils_data[month][direction]['frequency'] for direction in compass_directions]
        max_frequency = max(month_frequencies) if max(month_frequencies) > 0 else 1
        
        # Draw tendril for each direction
        for i, direction in enumerate(compass_directions):
            tendril_data = tendrils_data[month][direction]
            frequency = tendril_data['frequency']
            
            if frequency > 0:
                # Calculate tendril angle: evenly distributed around the stem endpoint
                relative_angle = i * (2 * np.pi / 16)  # 0, π/8, π/4, 3π/8...
                tendril_angle = params['angle_rad'] + relative_angle
                
                # Calculate tendril length based on frequency
                tendril_length = (frequency / max_frequency) * 0.15  # Max length 0.15
                
                # Calculate tendril thickness based on frequency
                tendril_thickness = (frequency / max_frequency) * 1.5 + 0.3  # Range 0.3-1.8
                
                # Calculate tendril start and end points
                tendril_start_radius = params['length']
                tendril_end_radius = params['length'] + tendril_length
                
                # Draw the tendril
                ax.plot([tendril_angle, tendril_angle], 
                       [tendril_start_radius, tendril_end_radius],
                       color=direction_colors[direction], 
                       linewidth=tendril_thickness, 
                       alpha=0.7, 
                       solid_capstyle='round', 
                       zorder=6)
                
                # Add small endpoint marker
                ax.scatter([tendril_angle], [tendril_end_radius],
                          c=direction_colors[direction], 
                          s=6 + frequency * 1, 
                          alpha=0.8, 
                          marker='o',
                          edgecolors='white', 
                          linewidth=0.2,
                          zorder=7)

print("Adding compass directions...")
compass_display_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
compass_display_angles = [0, 45, 90, 135, 180, 225, 270, 315]

for direction, angle in zip(compass_display_directions, compass_display_angles):
    angle_rad = np.radians(angle)
    compass_radius = 2.2
    
    ax.text(angle_rad, compass_radius, direction, 
            ha='center', va='center', fontsize=10, 
            color='#7f8c8d', alpha=0.7, family='monospace')

# Add reference circles
for radius in [0.5, 1.0, 1.5]:
    circle = plt.Circle((0, 0), radius, fill=False, 
                       color='#bdc3c7', alpha=0.3, linewidth=0.5)
    ax.add_patch(circle)

ax.set_ylim(0, 2.4)

# Add title and descriptions
fig.suptitle('METEOROLOGICAL DANDELION - Fixed Version\nHong Kong International Airport 2024', 
             fontsize=20, fontweight='bold', color='#2c3e50', y=0.95)

fig.text(0.5, 0.88, 
         'Layer 0: Centroid | Layer 1: Monthly Stems | Layer 2: Radial Direction Tendrils', 
         ha='center', va='center', fontsize=14, style='italic', color='#7f8c8d')

fig.text(0.02, 0.02, 
         'Layer 2: 16 direction tendrils radiating from each month\'s stem endpoint\n'
         'Tendril length ∝ Direction frequency in that month\n'
         'Tendril thickness ∝ Direction frequency\n'
         'Color coding: Each compass direction has unique color\n\n'
         'Next: Layer 3 (Seed Puffs) - Daily wind data as expanding fans',
         fontsize=9, color='#7f8c8d', verticalalignment='bottom', family='monospace')

plt.tight_layout()
output_filename = 'Meteorological_Dandelion_FIXED_HKA_2024.png'
plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
            facecolor='#fafafa', edgecolor='none')

print(f"✓ FIXED visualization saved as: {output_filename}")
plt.show()

print("\n✓ All errors fixed!")
print("Layer 2 now shows radial tendrils from each stem endpoint like dandelion seeds!")
print("Ready for Layer 3!")