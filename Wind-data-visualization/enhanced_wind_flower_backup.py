#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hong Kong International Airport 2024 Wind Data Visualization - Enhanced Version (Simplified)
"Wind Flower" - Beautiful Polar Annual Ring Chart

Features:
- Seasonal color gradients
- Monthly ring distribution
- Artistic point cloud effects
- Single rendering system (no dual channels)

Date: September 25, 2025
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import LineCollection
from datetime import datetime
import warnings
import sys
import locale

warnings.filterwarnings('ignore')

# Output system and local encoding
print(f"System encoding: {sys.stdout.encoding}")
print(f"Local encoding: {locale.getpreferredencoding()}")

# Configure matplotlib for optimal display and rendering
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100  # Screen display DPI
plt.rcParams['savefig.dpi'] = 300  # Save file DPI
plt.rcParams['figure.constrained_layout.use'] = False  # Disable auto layout to prevent distortion
plt.rcParams['figure.autolayout'] = False  # Disable automatic layout adjustment
plt.rcParams['axes.titlesize'] = 'large'
plt.rcParams['axes.labelsize'] = 'medium'
plt.rcParams['xtick.labelsize'] = 'small'
plt.rcParams['ytick.labelsize'] = 'small'

# Set display backend for better window management
import matplotlib
import os

# Choose the best backend for Windows
if os.name == 'nt':  # Windows
    try:
        matplotlib.use('TkAgg')  # Best for Windows
        print("🖥️ Using TkAgg backend for Windows")
    except ImportError:
        try:
            matplotlib.use('Qt5Agg')
            print("🖥️ Using Qt5Agg backend")
        except ImportError:
            matplotlib.use('Agg')  # No display
            print("⚠️ Using Agg backend (no display)")
else:
    matplotlib.use('TkAgg')

class EnhancedWindFlowerVisualizer:
    """Enhanced Wind Flower Visualizer"""
    
    def __init__(self):
        self.wind_direction_data = None
        self.wind_speed_data = None
        self.combined_data = None
    
    def parse_xml_data(self, wind_dir_file, wind_speed_file):
        """Parse XML files and extract data"""
        print("📂 Parsing XML data files...")
        
        # 解析风向数据
        tree_dir = ET.parse(wind_dir_file)
        root_dir = tree_dir.getroot()
        
        # 解析风速数据
        tree_speed = ET.parse(wind_speed_file)
        root_speed = tree_speed.getroot()
        
        # 提取风向数据
        dir_data = []
        for row in root_dir.findall(".//ss:Row", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}):
            cells = row.findall(".//ss:Cell/ss:Data", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"})
            if len(cells) >= 4:
                try:
                    year = int(cells[0].text)
                    month = int(cells[1].text)
                    day = int(cells[2].text)
                    direction = float(cells[3].text)
                    if year == 2024:
                        dir_data.append([year, month, day, direction])
                except (ValueError, TypeError):
                    continue
        
        # 提取风速数据
        speed_data = []
        for row in root_speed.findall(".//ss:Row", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}):
            cells = row.findall(".//ss:Cell/ss:Data", {"ss": "urn:schemas-microsoft-com:office:spreadsheet"})
            if len(cells) >= 4:
                try:
                    year = int(cells[0].text)
                    month = int(cells[1].text)
                    day = int(cells[2].text)
                    speed = float(cells[3].text)
                    if year == 2024:
                        speed_data.append([year, month, day, speed])
                except (ValueError, TypeError):
                    continue
        
        # 转换为DataFrame
        self.wind_direction_data = pd.DataFrame(dir_data, columns=['year', 'month', 'day', 'direction'])
        self.wind_speed_data = pd.DataFrame(speed_data, columns=['year', 'month', 'day', 'speed'])
        
        print(f"✅ Wind direction records: {len(self.wind_direction_data)}")
        print(f"✅ Wind speed records: {len(self.wind_speed_data)}")
        
        return self.wind_direction_data, self.wind_speed_data
    
    def preprocess_data(self):
        """Data preprocessing and cleaning"""
        print("🔧 Processing data preprocessing...")
        
        # 合并风向和风速数据
        self.combined_data = pd.merge(
            self.wind_direction_data, 
            self.wind_speed_data,
            on=['year', 'month', 'day'],
            how='inner'
        )
        
        # 创建日期列
        self.combined_data['date'] = pd.to_datetime(
            self.combined_data[['year', 'month', 'day']]
        )
        
        # Calculate seasons
        def get_season(month):
            if month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            elif month in [9, 10, 11]:
                return 'Autumn'
            else:
                return 'Winter'
        
        self.combined_data['season'] = self.combined_data['month'].apply(get_season)
        
        print(f"📊 Data Overview:")
        print(f"   Wind Direction Range: {self.combined_data['direction'].min():.1f}° - {self.combined_data['direction'].max():.1f}°")
        print(f"   Wind Speed Range: {self.combined_data['speed'].min():.1f} - {self.combined_data['speed'].max():.1f} km/h")
        print(f"   Time Range: {self.combined_data['date'].min().strftime('%Y-%m-%d')} - {self.combined_data['date'].max().strftime('%Y-%m-%d')}")
        print(f"   Total Records: {len(self.combined_data)}")
        
        return self.combined_data
    
    def create_enhanced_annotation(self, fig, ax):
        """Create optimized graphical annotation area"""
        
        # Seasonal color definition
        season_palettes = {
            'Spring': ['#FFB3E6', '#FF80DF', '#FF4DD8', '#FF1AD1'],  # 樱花粉
            'Summer': ['#B3FFB3', '#80FF80', '#4DFF4D', '#1AFF1A'],  # 翠绿色
            'Autumn': ['#FFD1B3', '#FFBB80', '#FFA54D', '#FF8F1A'],  # 金橙色  
            'Winter': ['#B3E6FF', '#80D9FF', '#4DCCFF', '#1ABFFF']   # 冰蓝色
        }
        
        # Monthly color mapping
        month_colors = {
            3: season_palettes['Spring'][2], 4: season_palettes['Spring'][3], 5: season_palettes['Spring'][0],
            6: season_palettes['Summer'][1], 7: season_palettes['Summer'][2], 8: season_palettes['Summer'][3],
            9: season_palettes['Autumn'][0], 10: season_palettes['Autumn'][1], 11: season_palettes['Autumn'][2],
            12: season_palettes['Winter'][3], 1: season_palettes['Winter'][0], 2: season_palettes['Winter'][1]
        }
        
        # 创建精确适应内容的注释背景 - 进一步缩小右边距
        annotation_bg = plt.Rectangle((0.01, 0.01), 0.33, 0.16, 
                                    transform=fig.transFigure, 
                                    facecolor='black', alpha=0.85, 
                                    edgecolor='white', linewidth=1)
        fig.patches.append(annotation_bg)
        
        # Main title - Adjusted position for new framework
        plt.figtext(0.02, 0.15, 'Data Statistics & Visualization Guide', 
                   fontsize=14, fontweight='bold', color='#FFD700')
        
        # Data statistics section - Adjusted position
        stats_line1 = f"• Total Records: {len(self.combined_data)}  • Direction Range: {self.combined_data['direction'].min():.0f}°-{self.combined_data['direction'].max():.0f}°"
        stats_line2 = f"• Speed Range: {self.combined_data['speed'].min():.1f}-{self.combined_data['speed'].max():.1f} km/h  • Average Speed: {self.combined_data['speed'].mean():.1f} km/h"
        
        plt.figtext(0.02, 0.13, stats_line1, fontsize=9, color='white')
        plt.figtext(0.02, 0.12, stats_line2, fontsize=9, color='white')
        
        # Visualization explanation - Adjusted position
        plt.figtext(0.02, 0.10, 'Visualization Principle: Concentric Circles=Months (Jan=Inner→Dec=Outer) | Angle=Direction | Distance=Speed', 
                   fontsize=9, color='white')
        
        # Seasonal color system title - Adjusted position
        plt.figtext(0.02, 0.08, 'Seasonal Color Gradient System', 
                   fontsize=11, fontweight='bold', color='white')
        
        # Draw seasonal colors - Adjusted position for new framework
        seasons_layout = [
            [('Spring', [3, 4, 5], 0.02, 0.06), ('Summer', [6, 7, 8], 0.18, 0.06)],
            [('Autumn', [9, 10, 11], 0.02, 0.04), ('Winter', [12, 1, 2], 0.18, 0.04)]
        ]
        
        for row in seasons_layout:
            for season_name, months, x_pos, y_pos in row:
                # Season gradient squares
                season_key = season_name
                if season_key in season_palettes:
                    colors = season_palettes[season_key]
                    main_color = colors[1]
                    season_rect = plt.Rectangle((x_pos, y_pos-0.003), 0.012, 0.012, 
                                              transform=fig.transFigure,
                                              facecolor=main_color, alpha=0.8)
                    fig.patches.append(season_rect)
                
                # Season title
                plt.figtext(x_pos + 0.016, y_pos, season_name, 
                           fontsize=9, fontweight='bold', color='white')
                
                # Month dots - Horizontally arranged after season name
                month_x_start = x_pos + 0.08
                for i, month in enumerate(months):
                    month_color = month_colors[month]
                    month_circle = plt.Circle((month_x_start + i*0.025, y_pos+0.005), 0.004,
                                            transform=fig.transFigure,
                                            facecolor=month_color, alpha=0.8,
                                            edgecolor='white', linewidth=0.5)
                    fig.patches.append(month_circle)
                    
                    # Month labels
                    plt.figtext(month_x_start + i*0.025, y_pos-0.01, f'M{month}',
                               fontsize=7, color='white', ha='center')
        
        # Bottom note - Close to seasonal info, reduced spacing
        plt.figtext(0.02, 0.08, 'Note: Dot size reflects wind speed intensity, color indicates month/season',
                   fontsize=8, color='#CCCCCC', style='italic')
    
    def create_enhanced_wind_flower(self):
        """Create beautiful wind flower visualization"""
        print("🌸 Creating beautiful wind flower visualization...")
        
        # Create figure with optimized settings
        fig = plt.figure(figsize=(16, 16), facecolor='#0a0a0a', dpi=100)
        ax = plt.subplot(111, projection='polar', facecolor='#0a0a0a')

        # Define beautiful seasonal colors
        season_palettes = {
            'Spring': ['#FFB3E6', '#FF80DF', '#FF4DD8', '#FF1AD1'],  # Cherry blossom pink
            'Summer': ['#B3FFB3', '#80FF80', '#4DFF4D', '#1AFF1A'],  # Emerald green
            'Autumn': ['#FFD1B3', '#FFBB80', '#FFA54D', '#FF8F1A'],  # Golden orange  
            'Winter': ['#B3E6FF', '#80D9FF', '#4DCCFF', '#1ABFFF']   # Ice blue
        }

        # Create beautiful visualization for each data point
        for month in range(1, 13):
            month_data = self.combined_data[self.combined_data['month'] == month]
            
            if len(month_data) == 0:
                continue
            
            # Get season and corresponding colors
            season = month_data.iloc[0]['season']
            color_palette = season_palettes[season]
            color_idx = (month - 1) % 4
            main_color = color_palette[color_idx]
            
            # Convert wind direction to radians
            wind_directions_rad = np.deg2rad(90 - month_data['direction'])
            
            # Calculate radius position (monthly rings)
            base_radius = month * 1.0
            max_speed = self.combined_data['speed'].max()
            min_speed = self.combined_data['speed'].min()
            
            # Map wind speed to radius variation
            speed_normalized = (month_data['speed'] - min_speed) / (max_speed - min_speed)
            radii = base_radius + speed_normalized * 0.8
            
            # Create gradient effect points
            for i, (angle, radius, speed) in enumerate(zip(wind_directions_rad, radii, month_data['speed'])):
                # Adjust point size based on wind speed
                point_size = 20 + speed * 8
                
                # Add halo effect
                ax.scatter(angle, radius, s=point_size * 3, c=main_color, 
                          alpha=0.1, edgecolors='none')
                ax.scatter(angle, radius, s=point_size * 1.5, c=main_color, 
                          alpha=0.3, edgecolors='none')
                ax.scatter(angle, radius, s=point_size, c=main_color, 
                          alpha=0.8, edgecolors='white', linewidth=0.5)

        # Concentric rings
        for month in range(1, 13):
            circle_color = "#ffffff"
            circle_alpha = 0.02  
            
            # Main rings
            circle = Circle((0, 0), month * 1.0, fill=False, 
                          color=circle_color, alpha=circle_alpha, linewidth=1)
            ax.add_patch(circle)

        # Add month labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for month in range(1, 13):
            radius_pos = month * 1.0 + 0.3
            ax.text(np.pi, radius_pos, month_names[month-1], 
                   ha='center', va='center', color='white', 
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

        # Set polar coordinate style
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # Set angle labels
        ax.set_thetagrids(np.arange(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 
                          'S', 'SW', 'W', 'NW'],
                         fontsize=14, color='white', fontweight='bold')
        
        # Set radius range and labels
        ax.set_ylim(0, 14)
        ax.set_yticks(np.arange(2, 14, 2))
        
        # Beautify grid
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        ax.set_facecolor('#0a0a0a')
        
        # Beautiful title
        title_text = '🌸 Hong Kong International Airport 2024 Wind Rose Flower \n' + \
                    'Every petal tells a story of the sky'

        plt.suptitle(title_text, fontsize=20, color='white', 
                    y=0.95, fontweight='bold', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.8))

        # Add simple annotations and legends
        self.create_enhanced_annotation(fig, ax)
        
        # Artistic signature
        plt.figtext(0.98, 0.02, 
                   'PROGRAMMING FOR ARTISTS AND DESIGNERS',
                   fontsize=10, color='#FFD700', style='italic',
                   horizontalalignment='right', verticalalignment='bottom')

        # Save high-quality PNG
        output_filename = 'HKA_2024_Beautiful_Wind_Rose_Flower.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='none', 
                   pad_inches=0.5, transparent=False)
        print(f"💾 Perfect PNG saved as: {output_filename}")

        return fig, ax

# Main program
if __name__ == "__main__":
        
        for season, month_colors in season_month_mapping.items():
            for month, color in month_colors:
                season_legend_elements.append(
                    plt.scatter([], [], s=120, c=color, alpha=0.9, 
                              edgecolors='white', linewidth=1,
                              label=f'M{month} ({season.split()[0]})'))

        # Adjust legend positioning based on mode
        if mode == "display":
            bbox_anchor = (-0.12, 1.0)
            legend_fontsize = fontsize - 1
        else:
            bbox_anchor = (-0.15, 1.0)
            legend_fontsize = fontsize

        legend1 = ax.legend(handles=season_legend_elements, 
                           title='🌈 Monthly Color Guide', 
                           loc='upper left', bbox_to_anchor=bbox_anchor,
                           title_fontsize=legend_fontsize+1, fontsize=legend_fontsize, ncol=2,
                           facecolor='black', edgecolor='white', framealpha=0.9)
        legend1.get_title().set_color('white')
        for text in legend1.get_texts():
            text.set_color('white')

# Main program
if __name__ == "__main__":
        
        # Create beautiful visualization for each data point
        for month in range(1, 13):
            month_data = self.combined_data[self.combined_data['month'] == month]
            
            if len(month_data) == 0:
                continue
            
            # Get season and corresponding colors
            season = month_data.iloc[0]['season']
            color_palette = season_palettes[season]
            color_idx = (month - 1) % 4
            main_color = color_palette[color_idx]
            
            # Convert wind direction to radians
            wind_directions_rad = np.deg2rad(90 - month_data['direction'])
            
            # Calculate radius position (monthly rings)
            base_radius = month * 1.0
            max_speed = self.combined_data['speed'].max()
            min_speed = self.combined_data['speed'].min()
            
            # Map wind speed to radius variation
            speed_normalized = (month_data['speed'] - min_speed) / (max_speed - min_speed)
            radii = base_radius + speed_normalized * 0.8
            
            # Create gradient effect points
            for i, (angle, radius, speed) in enumerate(zip(wind_directions_rad, radii, month_data['speed'])):
                # Adjust point size based on wind speed
                point_size = 20 + speed * 8
                
                # Add halo effect
                ax.scatter(angle, radius, s=point_size * 3, c=main_color, 
                          alpha=0.1, edgecolors='none')
                ax.scatter(angle, radius, s=point_size * 1.5, c=main_color, 
                          alpha=0.3, edgecolors='none')
                ax.scatter(angle, radius, s=point_size, c=main_color, 
                          alpha=0.8, edgecolors='white', linewidth=0.5)
        
        # Concentric rings
        for month in range(1, 13):
            circle_color = "#ffffff"
            circle_alpha = 0.02  
            
            # Main rings
            circle = Circle((0, 0), month * 1.0, fill=False, 
                          color=circle_color, alpha=circle_alpha, linewidth=1)
            ax.add_patch(circle)
        
        # Add month labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for month in range(1, 13):
            radius_pos = month * 1.0 + 0.3
            ax.text(np.pi, radius_pos, month_names[month-1], 
                   ha='center', va='center', color='white', 
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Set polar coordinate style
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # Set angle labels
        ax.set_thetagrids(np.arange(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 
                          'S', 'SW', 'W', 'NW'],
                         fontsize=14, color='white', fontweight='bold')
        
        # Set radius range and labels
        ax.set_ylim(0, 14)
        ax.set_yticks(np.arange(2, 14, 2))
        
        
        # Beautify grid
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        ax.set_facecolor('#0a0a0a')
        
        # Beautiful title
        title_text = '🌸 Hong Kong International Airport 2024 Wind Rose Flower \n' + \
                    'Every petal tells a story of the sky'

        plt.suptitle(title_text, fontsize=24, color='white', 
                    y=0.95, fontweight='bold', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.8))
        
        # Create seasonal color legend
        season_legend_elements = []
        
        # Create detailed month-color mapping for each season
        season_month_mapping = {
            'Spring 🌸': [(3, '#FF4DD8'), (4, '#FF1AD1'), (5, '#FFB3E6')],
            'Summer 🌿': [(6, '#80FF80'), (7, '#4DFF4D'), (8, '#1AFF1A')],
            'Autumn 🍂': [(9, '#FFD1B3'), (10, '#FFBB80'), (11, '#FFA54D')],
            'Winter ❄️': [(12, '#1ABFFF'), (1, '#B3E6FF'), (2, '#80D9FF')]
        }
        
        for season, month_colors in season_month_mapping.items():
            for month, color in month_colors:
                season_legend_elements.append(
                    plt.scatter([], [], s=120, c=color, alpha=0.9, 
                              edgecolors='white', linewidth=1,
                              label=f'{month}月 ({season.split()[0]})'))
        
        legend1 = ax.legend(handles=season_legend_elements, 
                           title='🌈 Monthly Color Guide', 
                           loc='upper left', bbox_to_anchor=(-0.15, 1.0),
                           title_fontsize=12, fontsize=10, ncol=2,
                           facecolor='black', edgecolor='white', framealpha=0.9)
        legend1.get_title().set_color('white')
        for text in legend1.get_texts():
            text.set_color('white')
        
        # Wind speed intensity legend
        speed_legend_elements = []
        speeds = [10, 15, 20, 25, 30]
        for speed in speeds:
            point_size = 20 + speed * 8
            speed_legend_elements.append(
                plt.scatter([], [], s=point_size, c='white', alpha=0.8, 
                          edgecolors='gray', label=f'{speed} km/h'))
        
        legend2 = ax.legend(handles=speed_legend_elements, 
                           title='💨 风速强度 Wind Speed', 
                           loc='upper right', bbox_to_anchor=(1.1, 1.0),
                           title_fontsize=14, fontsize=12,
                           facecolor='black', edgecolor='white', framealpha=0.9)
        legend2.get_title().set_color('white')
        for text in legend2.get_texts():
            text.set_color('white')
        
        # Create optimized graphical annotation area
        self.create_enhanced_annotation(fig, ax)
        
        # Artistic signature
        plt.figtext(0.98, 0.02, 
                   'PROGRAMMING FOR ARTISTS AND DESIGNERS',
                   fontsize=10, color='#FFD700', style='italic',
                   horizontalalignment='right', verticalalignment='bottom')
        
        # Save high-quality image
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='none', 
                   pad_inches=0.5)
        print(f"💾 Beautiful image saved as: {save_path}")
        
        # Handle different display modes
        if display_mode in ["both", "display_only"]:
            print("\n" + "="*60)
            print("📺 DISPLAY MODE: Layout Difference Analysis")
            print("="*60)
            print("🔍 Why PNG and Window look different:")
            print("   • PNG: 300 DPI (6000x6000 pixels) - Ultra high quality")
            print("   • Window: 100 DPI (~1200x1200 pixels) - Screen optimized")
            print("   • Text/annotations scale differently at different DPIs")
            print("   • Window may be resized by your screen resolution")
            print("   • Absolute positioning causes relative size changes")
            print("\n✅ Solutions implemented:")
            print("   • PNG always uses optimal high-DPI rendering")
            print("   • Window uses screen-optimized settings")
            print("   • Both versions maintain the same data accuracy")
            print("="*60)
            
            try:
                # Create optimized display version
                print("\n📺 Creating optimized display version...")
                
                # Configure display settings
                if hasattr(fig.canvas, 'manager'):
                    try:
                        fig.canvas.manager.set_window_title('Wind Rose Flower - Display Optimized')
                    except:
                        pass
                
                # Adjust layout for display
                plt.tight_layout(pad=2.0)
                
                print("�️ Opening display window...")
                print("💡 Note: This version is optimized for your screen")
                print("📄 The saved PNG has the highest quality layout")
                
                # Show the figure
                plt.figure(fig.number)
                plt.show()
                
                print("✅ Display window closed successfully")
                
            except Exception as e:
                print(f"⚠️ Display error: {e}")
                print("📄 The PNG file was still saved successfully!")
        
        if display_mode == "display_only":
            print("🖼️ Display-only mode: Image not saved to file")
        
        return fig, ax

# Main program
if __name__ == "__main__":
    # Initialize enhanced visualizer
    visualizer = EnhancedWindFlowerVisualizer()
    
    # Data file paths
    wind_dir_file = "daily_HKA_PDIR_ALL - 副本.xml"
    wind_speed_file = "daily_HKA_WSPD_ALL - 副本.xml"
    
    try:
        # Parse and process data
        dir_data, speed_data = visualizer.parse_xml_data(wind_dir_file, wind_speed_file)
        combined_data = visualizer.preprocess_data()
        print("\n🎉 Data parsing and preprocessing completed!")
        
        # Create beautiful wind flower visualization
        

        
        fig, ax = visualizer.create_enhanced_wind_flower()
        
        # Show the visualization
        print("\n�️ Opening visualization window...")
        plt.tight_layout()
        plt.show()
        
        print("\n🌟 Beautiful wind flower visualization created!")
        print("This artistic data visualization displays Hong Kong International Airport's 2024 wind direction and speed patterns,")
        print("transforming scientific data into a beautiful flower pattern! 🌸✨")
        
        # Ensure clean exit
        print("\n✅ Program completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Please ensure XML files are in the current directory")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)