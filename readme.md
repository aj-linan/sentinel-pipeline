# Sentinel-2 NDVI Pipeline

This project automates the download, processing, and analysis of Sentinel-2 images to calculate NDVI (Normalized Difference Vegetation Index) for a user-defined area of interest (AOI) in a specified time period. In this specific use case, the AOI corresponds to the Parque Natural de la Breña y Marismas del Barbate in 2025.

## Project Structure

```text
├── input/
│   └── aoi.geojson       # Area of Interest (Parque Natural de la Breña)
├── ndvi/                 # Output folder for NDVI GeoTIFFs
├── results/              # Analysis results (plots, CSVs)
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

Run the full pipeline with a single command:

```bash
python -m src.00_pipeline
```

## Configuration

Edit `src/config.py` to modify:
- **Date Range**: `INITIAL_DATE`, `END_DATE`
- **AOI**: `AOI_FILENAME`
- **Cloud Cover**: `CLOUD_COVER_LIMIT`
- **Output Paths**: `DATA_DIR`, `OUTPUT_DIR`, `RESULTS_DIR`
