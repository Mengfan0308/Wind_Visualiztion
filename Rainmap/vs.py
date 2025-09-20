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

# Clean and standardize dataframes
def clean_dataframe(df, data_type):
    """Clean and standardize dataframes"""
    if df is None or df.empty:
        return None
    
    print(f"\nCleaning {data_type} data...")
    
    # Find date column and data column
    date_col = None
    data_col = None
    
    for col in df.columns:
        sample_data = df[col].dropna().astype(str).head(10)
        date_pattern = sample_data.str.match(r'^\d{8}$')
        if date_pattern.any():
            date_col = col
            print(f"Found date column: {col}")
        
        try:
            numeric_data = pd.to_numeric(df[col], errors='coerce')
            if not numeric_data.isna().all() and col != date_col:
                data_col = col
                print(f"Found data column: {col}")
        except:
            pass
    
    if date_col is None or data_col is None:
        print(f"⚠️ Cannot identify date or data columns for {data_type}")
        return None
    
    clean_df = df[[date_col, data_col]].copy()
    clean_df.columns = ['Date', 'Value']
    clean_df = clean_df.dropna()
    
    print(f"✓ {data_type} cleaned, data count: {len(clean_df)}")
    return clean_df

# Clean data
df_direction_clean = clean_dataframe(df_direction, "Wind Direction")
df_speed_clean = clean_dataframe(df_speed, "Wind Speed")

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

if df_2024['Direction'].dtype == 'object':
    df_2024['Direction_Angle'] = df_2024['Direction'].map(direction_mapping)
    df_2024 = df_2024.dropna(subset=['Direction_Angle'])
else:
    df_2024['Direction_Angle'] = pd.to_numeric(df_2024['Direction'], errors='coerce')
    df_2024['Direction_Angle'] = df_2024['Direction_Angle'] % 360
    df_2024 = df_2024.dropna(subset=['Direction_Angle'])

# Process wind speed data
df_2024['Speed'] = pd.to_numeric(df_2024['Speed'], errors='coerce')
df_2024 = df_2024.dropna(subset=['Speed'])

print("✓ Basic data preprocessing complete!")

# =================================
# Step 3: Calculate Layer 1 Data with Dynamic Angular Allocation
# =================================
print("\n=== Step 3: Calculate Layer 1 Data with Dynamic Angular Allocation ===")

def calculate_monthly_vector_resultant(month_data):
    """
    Calculate the resultant vector for a month's wind data
    Each day's wind is treated as a vector (direction=angle, magnitude=speed)
    Returns: resultant_angle (degrees), resultant_magnitude, avg_speed
    """
    if month_data.empty:
        return 0, 0, 0
    
    # Convert wind direction and speed to vector components
    angles_rad = np.radians(month_data['Direction_Angle'])
    speeds = month_data['Speed']
    
    # Calculate x and y components of wind vectors
    x_components = speeds * np.sin(angles_rad)  # East component
    y_components = speeds * np.cos(angles_rad)  # North component
    
    # Sum all vectors
    sum_x = np.sum(x_components)
    sum_y = np.sum(y_components)
    
    # Calculate resultant vector
    resultant_magnitude = np.sqrt(sum_x**2 + sum_y**2)
    resultant_angle_rad = np.arctan2(sum_x, sum_y)
    resultant_angle_deg = np.degrees(resultant_angle_rad) % 360
    
    # Calculate average speed for length scaling
    avg_speed = np.mean(speeds)
    
    return resultant_angle_deg, resultant_magnitude, avg_speed

# Calculate data for all 12 months
print("1. Calculating monthly statistics...")

monthly_stats = {}
for month in range(1, 13):
    month_data = df_2024[df_2024['Month'] == month].copy()
    
    if not month_data.empty:
        resultant_angle, resultant_magnitude, avg_speed = calculate_monthly_vector_resultant(month_data)
        
        # Calculate space requirement based on multiple factors
        direction_diversity = len(month_data['Direction_Angle'].unique())  # Number of different wind directions
        wind_activity = avg_speed * len(month_data)  # Total wind activity
        
        monthly_stats[month] = {
            'resultant_angle': resultant_angle,
            'resultant_magnitude': resultant_magnitude,
            'avg_speed': avg_speed,
            'data_count': len(month_data),
            'direction_diversity': direction_diversity,
            'wind_activity': wind_activity,
            'space_requirement': wind_activity  # This will determine angular space
        }
        
        print(f"Month {month:2d}: Avg Speed={avg_speed:5.1f}, "
              f"Days={len(month_data)}, "
              f"Directions={direction_diversity}, "
              f"Activity={wind_activity:7.1f}")
    else:
        monthly_stats[month] = {
            'resultant_angle': 0,
            'resultant_magnitude': 0,
            'avg_speed': 0,
            'data_count': 0,
            'direction_diversity': 0,
            'wind_activity': 0,
            'space_requirement': 1  # Minimum space
        }
        print(f"Month {month:2d}: No data")

print("\n2. Calculating dynamic angular allocation...")

# Calculate total space requirement
total_space = sum([stats['space_requirement'] for stats in monthly_stats.values()])
total_angle = 360  # degrees

# Calculate angular allocation for each month
cumulative_angle = 0
month_angles = {}

for month in range(1, 13):
    space_req = monthly_stats[month]['space_requirement']
    
    # Calculate the angular space for this month
    angular_space = (space_req / total_space) * total_angle
    
    # Ensure minimum angular space (at least 15 degrees)
    angular_space = max(angular_space, 15)
    
    # Calculate the center angle for this month
    center_angle = cumulative_angle + (angular_space / 2)
    
    month_angles[month] = {
        'center_angle': center_angle % 360,
        'angular_space': angular_space,
        'start_angle': cumulative_angle % 360,
        'end_angle': (cumulative_angle + angular_space) % 360
    }
    
    cumulative_angle += angular_space
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print(f"{month_names[month-1]}: "
          f"Center={center_angle:6.1f}°, "
          f"Space={angular_space:5.1f}°, "
          f"Activity={space_req:7.1f}")

# Normalize if total exceeds 360
if cumulative_angle > 360:
    print(f"\n⚠️ Total angle exceeds 360° ({cumulative_angle:.1f}°), normalizing...")
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

print("\n3. Preparing final stem parameters...")

# Calculate final parameters for Layer 1 visualization
stem_params = {}
max_avg_speed = max([data['avg_speed'] for data in monthly_stats.values()] + [1])

for month in range(1, 13):
    stats = monthly_stats[month]
    angles = month_angles[month]
    
    # Calculate stem length (normalized by max average speed)
    if max_avg_speed > 0:
        stem_length = 0.3 + (stats['avg_speed'] / max_avg_speed) * 0.7  # Range: 0.3 to 1.0
    else:
        stem_length = 0.3
    
    # Use the dynamically allocated center angle
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
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print(f"{month_names[month-1]}: "
          f"Angle={stem_angle:6.1f}°, "
          f"Length={stem_length:4.2f}, "
          f"Space={angles['angular_space']:5.1f}°")

print("\n✓ Step 3 Complete - Dynamic angular allocation ready!")

# Continue with Layer 0 and Layer 1 drawing...
# (Rest of the code remains the same for now)

# =================================
# Step 4: Calculate Layer 0 Centroid and Draw Layer 1
# =================================
print("\n=== Step 4: Calculate Layer 0 Centroid and Draw Layer 1 ===")

def calculate_centroid(stem_params):
    """
    Calculate the centroid (Layer 0) based on Layer 1 stem endpoints
    The centroid is determined by the weighted center of all stem endpoints
    """
    # Calculate endpoints of all stems
    endpoints_x = []
    endpoints_y = []
    weights = []
    
    for month, params in stem_params.items():
        if params['data_count'] > 0:  # Only consider months with data
            angle_rad = params['angle_rad']
            length = params['length']
            
            # Calculate endpoint coordinates
            x = length * np.sin(angle_rad)
            y = length * np.cos(angle_rad)
            
            endpoints_x.append(x)
            endpoints_y.append(y)
            
            # Weight by wind activity (stronger influence for more active months)
            weights.append(params['wind_activity'])
    
    if not endpoints_x:
        return 0, 0  # Default center if no data
    
    # Calculate weighted centroid
    weights = np.array(weights)
    total_weight = np.sum(weights)
    
    if total_weight > 0:
        centroid_x = np.sum(np.array(endpoints_x) * weights) / total_weight
        centroid_y = np.sum(np.array(endpoints_y) * weights) / total_weight
    else:
        centroid_x = np.mean(endpoints_x)
        centroid_y = np.mean(endpoints_y)
    
    return centroid_x, centroid_y

# Calculate the centroid
print("1. Calculating centroid position...")
centroid_x, centroid_y = calculate_centroid(stem_params)
centroid_radius = np.sqrt(centroid_x**2 + centroid_y**2)
centroid_angle = np.arctan2(centroid_x, centroid_y)

print(f"Centroid position: x={centroid_x:.3f}, y={centroid_y:.3f}")
print(f"Centroid polar: radius={centroid_radius:.3f}, angle={np.degrees(centroid_angle):.1f}°")

# Create the visualization
print("\n2. Creating visualization...")

# Setup figure
plt.style.use('default')
fig, ax = plt.subplots(figsize=(16, 16), subplot_kw=dict(projection='polar'))
ax.set_facecolor('#fafafa')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.grid(False)
ax.set_xticklabels([])
ax.set_yticklabels([])

print("3. Drawing Layer 0: The Nexus...")

# Layer 0: Draw the nexus (convergence region)
ax.scatter([centroid_angle], [centroid_radius], 
           c='#2c3e50', s=800, alpha=0.8, marker='o', 
           edgecolors='white', linewidth=2, zorder=10)

print("4. Drawing Layer 1: Primary Stems with Dynamic Spacing...")

# Layer 1: Draw the 12 primary stems
month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# Draw stems from centroid to their endpoints
for month, params in stem_params.items():
    if params['data_count'] > 0:
        angle_rad = params['angle_rad']
        length = params['length']
        angular_space = params['angular_space']
        
        # Draw the stem
        stem_angles = [centroid_angle, angle_rad]
        stem_radii = [centroid_radius, length]
        
        # Vary stem thickness based on angular space (more space = thicker stem)
        stem_thickness = 3 + (angular_space / 40) * 3  # Range: 3-6
        
        ax.plot(stem_angles, stem_radii, 
                color='#34495e', linewidth=stem_thickness, alpha=0.8, 
                solid_capstyle='round', zorder=5)
        
        # Add month label at stem endpoint
        label_radius = length + 0.15
        ax.text(angle_rad, label_radius, month_names[month-1], 
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='#2c3e50', 
                rotation=np.degrees(angle_rad)-90 if angle_rad > np.pi/2 and angle_rad < 3*np.pi/2 else np.degrees(angle_rad)+90,
                zorder=15)
        
        # Add endpoint marker (size based on activity level)
        marker_size = 80 + (params['wind_activity'] / max([p['wind_activity'] for p in stem_params.values()])) * 120
        ax.scatter([angle_rad], [length], 
                   c='#34495e', s=marker_size, alpha=0.9, marker='o', 
                   edgecolors='white', linewidth=1, zorder=8)

print("5. Adding compass directions...")

# Add compass directions for reference
compass_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
compass_angles = [0, 45, 90, 135, 180, 225, 270, 315]

for direction, angle in zip(compass_directions, compass_angles):
    angle_rad = np.radians(angle)
    compass_radius = 1.4
    
    ax.text(angle_rad, compass_radius, direction, 
            ha='center', va='center', fontsize=10, 
            color='#7f8c8d', alpha=0.7, family='monospace')

# Add reference circles
for radius in [0.5, 1.0]:
    circle = plt.Circle((0, 0), radius, fill=False, 
                       color='#bdc3c7', alpha=0.3, linewidth=0.5)
    ax.add_patch(circle)

# Set axis limits
ax.set_ylim(0, 1.6)

print("6. Adding title and descriptions...")

# Add title
fig.suptitle('METEOROLOGICAL DANDELION - Dynamic Angular Allocation\nHong Kong International Airport 2024', 
             fontsize=18, fontweight='bold', color='#2c3e50', y=0.95)

# Add description
fig.text(0.5, 0.88, 
         'Layer 0: Data-driven Centroid | Layer 1: Chronologically Ordered Stems with Activity-based Spacing', 
         ha='center', va='center', fontsize=12, style='italic', color='#7f8c8d')

# Add technical details
fig.text(0.02, 0.02, 
         'Dynamic Angular Allocation: Month sequence preserved, angular space ∝ wind activity\n'
         'Layer 0: Centroid weighted by monthly wind activity\n'
         'Layer 1: 12 Primary Stems - Sequential order, Length ∝ Avg wind speed, Space ∝ Total wind activity\n'
         f'Centroid Position: ({centroid_x:.3f}, {centroid_y:.3f})\n\n'
         'Next: Layer 2 (Secondary Tendrils) - 16 wind directions per month',
         fontsize=9, color='#7f8c8d', verticalalignment='bottom', family='monospace')

print("7. Saving visualization...")

# Save the current layer
plt.tight_layout()
output_filename = 'Meteorological_Dandelion_DynamicAngular_HKA_2024.png'
plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
            facecolor='#fafafa', edgecolor='none')

print(f"✓ Dynamic angular allocation visualization saved as: {output_filename}")

# Display the plot
plt.show()

print("\n✓ Step 4 Complete!")
print(f"\nDynamic Angular Allocation Summary:")
print(f"- Months arranged in chronological order around the circle")
print(f"- Angular space for each month determined by wind activity level")
print(f"- High-activity months get more space for future Layer 2 tendrils")
print(f"- Centroid weighted by monthly wind activity")
print(f"- Ready for Layer 2 calculation (Secondary Tendrils)")

print(f"\n=== Ready for Step 5: Calculate and Draw Layer 2 ===")
print("The dynamic angular allocation provides optimal space for wind direction tendrils!")