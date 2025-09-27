# Hong Kong International Airport 2024 Wind Data Visualization

## 🌸 Project Overview

This project provides beautiful and interactive visualizations of wind data from Hong Kong International Airport (HKA) for the year 2024. The wind patterns are transformed into artistic "Wind Rose Flower" charts that combine scientific data analysis with aesthetic design.

## � Data Source & Location

- **Location**: Hong Kong International Airport (VHHH)
- **Geographic Coordinates**: 22°18′32″N 113°54′51″E  
- **Data Period**: January 1, 2024 - December 31, 2024 (366 days, including leap year)
- **Data Provider**: Hong Kong Observatory / Airport Meteorological Office

## 📊 Dataset Description

The project uses two primary datasets:

### Wind Direction Data (`daily_HKA_PDIR_ALL - 副本.xml`)
- **Records**: 366 daily measurements
- **Parameter**: Prevailing wind direction in degrees (0°-360°)
- **Range**: 10° - 360°
- **Format**: XML with year, month, day, and direction values

### Wind Speed Data (`daily_HKA_WSPD_ALL - 副本.xml`)
- **Records**: 366 daily measurements  
- **Parameter**: Average wind speed in km/h
- **Range**: 7.9 - 32.0 km/h
- **Average Speed**: ~15.5 km/h
- **Format**: XML with year, month, day, and speed values

## 🎨 Visualization Files

### 1. Static Wind Rose Flower (`HKA_2024_Wind Rose Flower.py`)

**Purpose**: Creates high-quality static wind rose visualizations with artistic flair.

**Features**:
- **Polar Coordinate System**: Wind direction mapped to angles, months to concentric circles
- **Seasonal Color Gradients**: 
  - Spring: Cherry blossom pink (`#FFB3E6` to `#FF1AD1`)
  - Summer: Emerald green (`#B3FFB3` to `#1AFF1A`) 
  - Autumn: Golden orange (`#FFD1B3` to `#FF8F1A`)
  - Winter: Ice blue (`#B3E6FF` to `#1ABFFF`)
- **Multi-layer Rendering**: Halo effects and gradient points for artistic appeal
- **Professional Typography**: Bowlby One and Corbel fonts
- **High-Resolution Output**: 300 DPI PNG export
- **Comprehensive Annotations**: Data statistics and visualization guide

**Output**: `HKA_2024_Beautiful_Wind_Rose_Flower.png`

### 2. Interactive Wind Flower (`HKA_2024_Interactive_Wind_Flower.py`)

**Purpose**: Web-based interactive dashboard for dynamic data exploration.

**Features**:
- **Monthly Animation**: Play/pause controls to see wind pattern evolution
- **Interactive Timeline**: Slider to select specific months (1-12)
- **Hover Details**: Mouse-over for detailed wind information
- **Responsive Design**: Modern dark theme with optimized layout
- **Real-time Statistics**: Dynamic data summaries
- **Control Panel**: Compact interface with 6px button spacing
- **Embedded Annotations**: Integrated legend and explanation system

**Technology Stack**:
- **Framework**: Dash + Plotly
- **Backend**: Python with pandas/numpy
- **Frontend**: HTML/CSS with modern styling
- **Port**: Runs on `http://127.0.0.1:8050`

## 🖼️ Generated Visualizations

### Wind Rose Flower Chart
The main output is a stunning polar chart that transforms meteorological data into flower-like patterns:

- **Concentric Rings**: Each ring represents a month (January=innermost, December=outermost)
- **Angular Position**: Wind direction (North=0°, East=90°, etc.)
- **Point Size**: Wind speed intensity (larger = stronger winds)
- **Color Coding**: Seasonal progression with smooth gradients
- **Visual Style**: Artistic point cloud with halo effects on dark background

## � Installation & Usage

### Prerequisites
```bash
pip install pandas numpy matplotlib plotly dash
```

### Running Static Version
```bash
python "HKA_2024_Wind Rose Flower.py"
```
- Generates high-resolution PNG image
- Opens interactive window for viewing
- Automatically saves to current directory

### Running Interactive Version
```bash
python "HKA_2024_Interactive_Wind_Flower.py"
```
- Starts web server on port 8050
- Open browser to `http://127.0.0.1:8050`
- Use controls to explore data interactively

## 📈 Data Analysis Insights

Based on the 2024 HKA wind data:

- **Total Records**: 366 complete daily measurements
- **Wind Direction Range**: 10° to 360° (full compass coverage)
- **Wind Speed Statistics**:
  - Minimum: 7.9 km/h
  - Maximum: 32.0 km/h  
  - Average: ~15.5 km/h
- **Seasonal Patterns**: Visualized through color-coded monthly progression
- **Temporal Distribution**: Full year coverage including leap day (Feb 29)

## � Technical Features

### Code Optimization
- **DRY Principle**: Unified XML parsing methods
- **Class-based Architecture**: Organized, maintainable code structure
- **Performance Optimized**: Efficient data processing and rendering
- **Internationalized**: All comments in English
- **Error Handling**: Robust parsing with exception management

### Visual Design
- **Color Psychology**: Seasonal colors reflect natural progressions
- **Typography Hierarchy**: Multiple font weights and sizes for clarity
- **Layout Optimization**: Carefully positioned annotations and legends
- **Responsive Margins**: Adaptive spacing (24px bottom margins, 6px button spacing)

## 📋 Project Structure

```
Wind-data-visualization/
├── HKA_2024_Wind Rose Flower.py              # Static visualization generator
├── HKA_2024_Interactive_Wind_Flower.py       # Interactive web dashboard
├── daily_HKA_PDIR_ALL - 副本.xml             # Wind direction dataset
├── daily_HKA_WSPD_ALL - 副本.xml             # Wind speed dataset
├── HKA_2024_Beautiful_Wind_Rose_Flower.png   # Generated static image
└── README.md                                  # This documentation
```

## 🌟 Use Cases

- **Meteorological Analysis**: Understanding seasonal wind patterns
- **Aviation Planning**: Wind data for flight operations
- **Environmental Studies**: Climate pattern analysis
- **Data Visualization Education**: Example of artistic data representation
- **Academic Research**: Hong Kong regional wind studies

## 📝 Notes

- Data represents daily averages, not instantaneous measurements
- Visualization emphasizes pattern recognition over precise measurement
- Interactive version provides detailed hover information for accuracy
- Color gradients are designed for accessibility and aesthetic appeal
- All timestamps are in Hong Kong Standard Time (UTC+8)

## 🌐 Online Deployment Options

### Why GitHub Can't Run Interactive Apps Directly

GitHub Pages only supports static websites (HTML/CSS/JS), not server-side Python applications like Dash. Interactive visualizations require a running Python server to process user interactions and generate dynamic content.

### Recommended Deployment Solutions

#### 1. Streamlit Cloud (Easiest)
- **Free hosting** for Streamlit applications
- **Direct GitHub integration** - just connect your repository
- **Automatic deployment** when you push changes
- **Public URL** for easy sharing

**Steps:**
1. Push your project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repository
4. Choose `streamlit_wind_flower.py` as the main file
5. Deploy and get your public URL!

#### 2. Heroku (Full Control)
- **Free tier available** (with limitations)
- **Supports both Dash and Streamlit** applications
- **Custom domain** support
- **Environment variables** for configuration

#### 3. Render.com (Modern Alternative)
- **Free tier with better performance** than Heroku
- **Automatic deployments** from GitHub
- **Built-in SSL certificates**
- **Zero-config deployment** for Python apps

### Quick Start: Streamlit Deployment
```bash
# Install Streamlit locally to test
pip install streamlit

# Run the Streamlit version
streamlit run streamlit_wind_flower.py

# Push to GitHub and deploy to Streamlit Cloud
git add .
git commit -m "Add Streamlit version for deployment"
git push origin main
```

Then visit [share.streamlit.io](https://share.streamlit.io) to deploy!

---

*This project demonstrates the intersection of scientific data analysis and artistic visualization, transforming raw meteorological measurements into beautiful, informative displays that can be shared worldwide through cloud deployment.*