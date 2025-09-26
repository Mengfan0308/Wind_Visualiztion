#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hong Kong International Airport 2024 Wind Data Visualization - Simple Version
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
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import LineCollection
from datetime import datetime
import warnings
import sys
import locale

warnings.filterwarnings('ignore')

# Output system and local encoding
print(f"System encoding: {sys.stdout.encoding}")
print(f"Local encoding: {locale.getpreferredencoding()}")

# Configure matplotlib for optimal display and rendering - optimized for performance
plt.rcParams['font.sans-serif'] = ['Corbel', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titlesize'] = 'large'
plt.rcParams['axes.labelsize'] = 'medium'
plt.rcParams['xtick.labelsize'] = 'small'
plt.rcParams['ytick.labelsize'] = 'small'

# Performance optimization settings
plt.rcParams['agg.path.chunksize'] = 10000  # Reduce path rendering overhead
plt.rcParams['path.simplify'] = True        # Simplify paths for faster rendering
plt.rcParams['figure.max_open_warning'] = 0 # Disable figure limit warnings

# Set display backend for better window management
import matplotlib
import os

# Choose the best backend for Windows
if sys.platform.startswith('win'):
    try:
        matplotlib.use('TkAgg')
        print("🖥️ Using TkAgg backend for Windows")
    except ImportError:
        try:
            matplotlib.use('Qt5Agg')
            print("🖥️ Using Qt5Agg backend")
        except ImportError:
            print("⚠️ Using default backend")

class SimpleWindFlowerVisualizer:
    def __init__(self):
        """Initialize the visualizer with font caching for performance"""
        self.wind_direction_data = None
        self.wind_speed_data = None
        self.combined_data = None
        
        # Cache font properties for better performance
        self.bowlby_props = {'family': 'Bowlby One', 'weight': 'bold'}
        self.corbel_props = {'family': 'Corbel'}
        self.corbel_bold_props = {'family': 'Corbel', 'weight': 'bold'}
        self.corbel_italic_props = {'family': 'Corbel', 'style': 'italic'}
    
    def parse_xml_data(self, wind_dir_file, wind_speed_file):
        """Parse XML files and extract data"""
        print("📂 Parsing XML data files...")
        
        # Parse wind direction data
        tree_dir = ET.parse(wind_dir_file)
        root_dir = tree_dir.getroot()
        
        # Parse wind speed data
        tree_speed = ET.parse(wind_speed_file)
        root_speed = tree_speed.getroot()
        
        # Extract wind direction data
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
        
        # Extract wind speed data
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
        
        # Convert to DataFrame
        self.wind_direction_data = pd.DataFrame(dir_data, columns=['year', 'month', 'day', 'direction'])
        self.wind_speed_data = pd.DataFrame(speed_data, columns=['year', 'month', 'day', 'speed'])
        
        print(f"✅ Wind direction records: {len(self.wind_direction_data)}")
        print(f"✅ Wind speed records: {len(self.wind_speed_data)}")
        
        return self.wind_direction_data, self.wind_speed_data
    
    def preprocess_data(self):
        """Data preprocessing and cleaning"""
        print("🔧 Processing data preprocessing...")
        
        # Merge wind direction and speed data
        self.combined_data = pd.merge(
            self.wind_direction_data, 
            self.wind_speed_data,
            on=['year', 'month', 'day'],
            how='inner'
        )
        
        # Create date column
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
    
    def create_simple_wind_flower(self):
        """Create beautiful wind flower visualization with simple single rendering"""
        print("🌸 Creating beautiful wind flower visualization...")
        
        # Create figure with optimized settings and fixed design layout
        fig = plt.figure(figsize=(16, 16), facecolor='#0a0a0a', dpi=100)
        ax = plt.subplot(111, projection='polar', facecolor='#0a0a0a')
        
        # Set fixed, balanced margins for optimal design layout - NO auto adjustment
        fig.subplots_adjust(left=0.1, right=0.9, top=0.88, bottom=0.12)

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
                          color=circle_color, alpha=circle_alpha, linewidth=1.5)
            ax.add_patch(circle)

        # Add month labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for month in range(1, 13):
            radius_pos = month * 1.0 + 0.3
            ax.text(np.pi, radius_pos, month_names[month-1], 
                   ha='center', va='center', color='white', 
                   fontsize=12, fontproperties=self.corbel_bold_props,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

        # Set polar coordinate style
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # Set angle labels - optimized
        ax.set_thetagrids(np.arange(0, 360, 45), 
                         ['N', 'NE', 'E', 'SE', 
                          'S', 'SW', 'W', 'NW'],
                         fontsize=14, color='white', fontproperties=self.corbel_bold_props)
        
        # Set radius range and labels
        ax.set_ylim(0, 14)
        ax.set_yticks(np.arange(2, 14, 2))
        
        # Beautify grid
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        ax.set_facecolor('#0a0a0a')
        
        # Beautiful title - clean and focused
        title_text = 'Hong Kong International Airport 2024 Wind Rose Flower'

        plt.suptitle(title_text, fontsize=22, color='white', 
                    y=0.95, fontproperties=self.bowlby_props,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.8))

        # Add simple annotations and legends
        self._add_simple_annotations(fig, ax)
        
        # Artistic signature - optimized
        plt.figtext(0.98, 0.02, 
                   'PROGRAMMING FOR ARTISTS AND DESIGNERS',
                   fontsize=10, color='#FFD700', fontproperties=self.corbel_italic_props,
                   horizontalalignment='right', verticalalignment='bottom')

        # Save high-quality PNG
        output_filename = 'HKA_2024_Beautiful_Wind_Rose_Flower.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='none', 
                   pad_inches=0.5, transparent=False)
        print(f"💾 Perfect PNG saved as: {output_filename}")

        return fig, ax
    
    def _add_simple_annotations(self, fig, ax):
        """Add simple annotations and legends"""
        
        # Seasonal color definition
        season_palettes = {
            'Spring': ['#FFB3E6', '#FF80DF', '#FF4DD8', '#FF1AD1'],
            'Summer': ['#B3FFB3', '#80FF80', '#4DFF4D', '#1AFF1A'],
            'Autumn': ['#FFD1B3', '#FFBB80', '#FFA54D', '#FF8F1A'],
            'Winter': ['#B3E6FF', '#80D9FF', '#4DCCFF', '#1ABFFF']
        }
        
        # Monthly color mapping
        month_colors = {
            3: season_palettes['Spring'][2], 4: season_palettes['Spring'][3], 5: season_palettes['Spring'][0],
            6: season_palettes['Summer'][1], 7: season_palettes['Summer'][2], 8: season_palettes['Summer'][3],
            9: season_palettes['Autumn'][0], 10: season_palettes['Autumn'][1], 11: season_palettes['Autumn'][2],
            12: season_palettes['Winter'][3], 1: season_palettes['Winter'][0], 2: season_palettes['Winter'][1]
        }
        
        # Create annotation background (optimized for larger window)
        annotation_bg = Rectangle((0.01, 0.01), 0.35, 0.20, 
                                transform=fig.transFigure, 
                                facecolor='black', alpha=0.85, 
                                edgecolor='white', linewidth=1)
        fig.patches.append(annotation_bg)
        
        # Main title (with more top margin) - optimized
        plt.figtext(0.025, 0.185, 'Data Statistics & Visualization Guide', 
                   fontsize=14, color='#FFD700', fontproperties=self.bowlby_props)
        
        # Data statistics (increased line spacing)
        stats_line1 = f"• Total Records: {len(self.combined_data)}  • Direction Range: {self.combined_data['direction'].min():.0f}°-{self.combined_data['direction'].max():.0f}°"
        stats_line2 = f"• Speed Range: {self.combined_data['speed'].min():.1f}-{self.combined_data['speed'].max():.1f} km/h  • Average Speed: {self.combined_data['speed'].mean():.1f} km/h"
        
        plt.figtext(0.025, 0.155, stats_line1, fontsize=9, color='white', fontproperties=self.corbel_props)
        plt.figtext(0.025, 0.135, stats_line2, fontsize=9, color='white', fontproperties=self.corbel_props)
        
        # Visualization explanation (split into two lines to fit within frame) - optimized
        plt.figtext(0.025, 0.115, 'Visualization Principle: Concentric Circles=Months (Jan=Inner→Dec=Outer)', 
                   fontsize=9, color='white', fontproperties=self.corbel_props)
        plt.figtext(0.025, 0.100, 'Angle=Direction | Distance=Speed', 
                   fontsize=9, color='white', fontproperties=self.corbel_props)
        
        # Seasonal color system title - using regular text font
        plt.figtext(0.025, 0.082, 'Seasonal Color Gradient System', 
                   fontsize=11, color='white', fontproperties=self.corbel_bold_props)
        
        # Draw seasonal colors
        seasons_layout = [
            [('Spring', [3, 4, 5], 0.025, 0.065), ('Summer', [6, 7, 8], 0.19, 0.065)],
            [('Autumn', [9, 10, 11], 0.025, 0.040), ('Winter', [12, 1, 2], 0.19, 0.040)]
        ]
        
        # Month names for better readability
        month_names_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        
        for row in seasons_layout:
            for season_name, months, x_pos, y_pos in row:
                # Season gradient squares
                season_key = season_name
                if season_key in season_palettes:
                    colors = season_palettes[season_key]
                    main_color = colors[1]
                    season_rect = Rectangle((x_pos, y_pos-0.003), 0.012, 0.012, 
                                          transform=fig.transFigure,
                                          facecolor=main_color, alpha=0.8)
                    fig.patches.append(season_rect)
                
                # Season title (closer to the color square) - optimized
                plt.figtext(x_pos + 0.014, y_pos, season_name, 
                           fontsize=9, color='white', fontproperties=self.corbel_bold_props)
                
                # Month dots (closer spacing)
                month_x_start = x_pos + 0.07
                for i, month in enumerate(months):
                    month_color = month_colors[month]
                    month_circle = plt.Circle((month_x_start + i*0.022, y_pos+0.005), 0.004,
                                            transform=fig.transFigure,
                                            facecolor=month_color, alpha=0.8,
                                            edgecolor='white', linewidth=0.5)
                    fig.patches.append(month_circle)
                    
                    # Month labels (closer to circles, using Jan/Feb/Mar format) - optimized
                    plt.figtext(month_x_start + i*0.022, y_pos-0.007, month_names_map[month],
                               fontsize=7, color='white', ha='center', fontproperties=self.corbel_props)
        
        # Wind speed intensity legend (right top corner with improved spacing)
        speed_legend_elements = []
        speeds = [10, 15, 20, 25, 30]
        for speed in speeds:
            point_size = 20 + speed * 8
            speed_legend_elements.append(
                plt.scatter([], [], s=point_size, c='white', alpha=0.8, 
                          edgecolors='gray', label=f'{speed} km/h'))
        
        legend2 = ax.legend(handles=speed_legend_elements, 
                           title='Wind Speed', 
                           loc='upper right', bbox_to_anchor=(1.15, 1.0),
                           title_fontsize=11, fontsize=9,
                           facecolor='black', edgecolor='white', framealpha=0.9,
                           columnspacing=2.0, handletextpad=1.2, borderpad=1,
                           labelspacing=1.0)
        legend2.get_title().set_color('white')
        legend2.get_title().set_horizontalalignment('center')
        for text in legend2.get_texts():
            text.set_color('white')
        
        # Bottom note (with more bottom margin) - optimized
        plt.figtext(0.025, 0.025, 'Note: Dot size reflects wind speed intensity, color indicates month/season',
                   fontsize=8, color='#CCCCCC', fontproperties=self.corbel_italic_props)

# Main program
if __name__ == "__main__":
    # Initialize simple visualizer
    visualizer = SimpleWindFlowerVisualizer()
    
    # Data file paths
    wind_dir_file = "daily_HKA_PDIR_ALL - 副本.xml"
    wind_speed_file = "daily_HKA_WSPD_ALL - 副本.xml"
    
    try:
        # Parse and process data
        dir_data, speed_data = visualizer.parse_xml_data(wind_dir_file, wind_speed_file)
        combined_data = visualizer.preprocess_data()
        print("\n🎉 Data parsing and preprocessing completed!")
        
        # Create beautiful wind flower visualization
        fig, ax = visualizer.create_simple_wind_flower()
        
        # Show the visualization with controlled window size and stable layout
        print("\n🖥️ Opening visualization window...")
        
        # Get the current figure manager and set window properties BEFORE showing
        mngr = fig.canvas.manager
        if hasattr(mngr, 'window'):
            if hasattr(mngr.window, 'wm_geometry'):
                # For TkAgg backend - set window size, position and title
                mngr.window.wm_geometry('1200x1200+100+100')  # Smaller, more reasonable size
                mngr.window.wm_title('Hong Kong Airport 2024 Wind Rose Flower - Interactive View')
            elif hasattr(mngr.window, 'setGeometry'):
                # For Qt backend - set window geometry and title
                mngr.window.setGeometry(100, 100, 1200, 1200)  # Smaller, more reasonable size
                mngr.window.setWindowTitle('Hong Kong Airport 2024 Wind Rose Flower - Interactive View')
        
        # Set the axes limits to ensure full view from start
        ax.set_ylim(0, 14)
        
        plt.show()
        
        print("\n🌟 Beautiful wind flower visualization created!")
        print("This artistic data visualization displays Hong Kong International Airport's 2024 wind direction and speed patterns,")
        print("transforming scientific data into a beautiful flower pattern! 🌸✨")
        
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