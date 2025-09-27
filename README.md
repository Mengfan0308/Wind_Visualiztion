# Hong Kong International Airport 2024 Wind Data Visualization

## Project Overview

This project visualizes daily wind direction and speed data for Hong Kong International Airport (VHHH) in 2024, providing both static and interactive wind rose flower charts. The data is sourced from the Hong Kong Observatory/Airport Meteorological Office and covers the entire leap year (366 days).

## Data Description

- **Wind Direction Data**: `daily_HKA_PDIR_ALL - 副本.xml`  
  - 366 records, 0°-360°, XML format
- **Wind Speed Data**: `daily_HKA_WSPD_ALL - 副本.xml`  
  - 366 records, 7.9-32.0 km/h, average ~15.5 km/h, XML format

## Visualization Tools

- `HKA_2024_Wind Rose Flower.py`  
  Generates high-resolution static wind rose flower charts (seasonal gradient colors, polar coordinates, professional annotations and typography), outputs as PNG images.
- `HKA_2024_Interactive_Wind_Flower.py`  
  Dash+Plotly web dashboard, supports monthly animation, hover details, and real-time statistics.

## Quick Start

1. Install dependencies
   pip install pandas numpy matplotlib plotly dash
  
2. Generate static image
   python "HKA_2024_Wind Rose Flower.py"
 
3. Launch interactive dashboard
   python "HKA_2024_Interactive_Wind_Flower.py"
   # Open your browser at http://127.0.0.1:8050


## Project Structure

Wind_data_visualiztion/
├── HKA_2024_Wind Rose Flower.py
├── HKA_2024_Interactive_Wind_Flower.py
├── daily_HKA_PDIR_ALL - 副本.xml
├── daily_HKA_WSPD_ALL - 副本.xml
├── HKA_2024_Beautiful_Wind_Rose_Flower.png
└── README.md
