# Sentinel-2 NDVI Pipeline

This project automates the download, processing, and analysis of Sentinel-2 images to calculate NDVI (Normalized Difference Vegetation Index) for a user-defined area of interest (AOI) in a specified time period. In this specific use case, the AOI corresponds to the Parque Natural de la Breña y Marismas del Barbate in 2025.

## Project Structure

```text
├── data/
│   ├── input/
│   │   └── aoi.geojson   # Area of Interest (Parque Natural de la Breña)
│   ├── ndvi/             # Output folder for NDVI GeoTIFFs
│   └── results/          # Analysis results (plots, CSVs)
├── src/
│   ├── 00_pipeline.py    # Main entry point
│   ├── 01_download.py    # Download & NDVI calculation module
│   ├── 02_processing.py  # Analysis & visualization module
│   └── config.py         # Configuration parameters
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Features

- **Automated Download**: Connects to Earth Search STAC API to find Sentinel-2 images.
- **NDVI Calculation**: Computes NDVI on-the-fly and saves as Cloud Optimized GeoTIFFs.
- **Time-Series Analysis**: Calculates mean NDVI for the AOI over time.
- **Trend Detection**: Performs linear regression to identify vegetation trends.
- **Visualization**: Generates smoothed time-series plots.

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Full Pipeline

Execute all steps (download, NDVI calculation, and analysis) with a single command:

```bash
python -m src.00_pipeline
```

### Run Individual Modules

You can also run each module independently:

#### Download and Calculate NDVI
Downloads Sentinel-2 imagery from Earth Search STAC API and calculates NDVI:

```bash
python -m src.01_download
```

**What it does:**
- Connects to [Earth Search STAC API](https://earth-search.aws.element84.com/v1) (AWS Element 84)
- Searches for Sentinel-2 Level-2A images matching your AOI, date range, and cloud cover criteria
- Downloads only the required bands (Red and NIR)
- Calculates NDVI on-the-fly: `(NIR - Red) / (NIR + Red)`
- Saves results as Cloud Optimized GeoTIFFs in `data/ndvi/`
- Skips already downloaded images automatically

#### Process and Analyze
Analyzes existing NDVI files and generates visualizations:

```bash
python -m src.02_processing
```

**What it does:**
- Loads all NDVI GeoTIFFs from `data/ndvi/`
- Calculates mean NDVI for the AOI over time
- Performs linear regression to detect vegetation trends
- Generates smoothed time-series plots
- Saves results to `data/results/`

## Configuration

Edit `src/config.py` to customize the pipeline behavior:

### Data Source Parameters

- **`STAC_API_URL`**: STAC catalog endpoint (default: Earth Search AWS)
  - Uses [Element 84's Earth Search](https://www.element84.com/earth-search/) - a free STAC API providing access to Sentinel-2 and Landsat data hosted on AWS
- **`COLLECTION`**: Satellite collection ID (default: `"sentinel-2-l2a"`)
  - L2A = atmospherically corrected surface reflectance

### Search Filters

- **`INITIAL_DATE`** / **`END_DATE`**: Date range for image search (format: `"YYYY-MM-DD"`)
- **`CLOUD_COVER_LIMIT`**: Maximum cloud cover percentage (default: `0.2` = 20%)
  - Lower values = clearer images but fewer results
  - Range: 0.0 (0%) to 1.0 (100%)

### Area of Interest

- **`AOI_FILENAME`**: GeoJSON file with your area of interest (default: `"aoi.geojson"`)
- **`AOI_PATH`**: Full path to AOI file (auto-generated from `DATA_DIR` + `AOI_FILENAME`)

### Output Paths

- **`DATA_DIR`**: Input data folder (default: `data/input/`)
- **`OUTPUT_DIR`**: NDVI GeoTIFFs output (default: `data/ndvi/`)
- **`RESULTS_DIR`**: Analysis results (default: `data/results/`)

### Processing Parameters

- **`TARGET_CRS`**: Coordinate reference system for analysis (default: `"EPSG:32630"` - UTM Zone 30N)
- **`MOVING_AVERAGE_WINDOW`**: Smoothing window for time-series plots (default: `3`)
