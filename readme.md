# NDVI Analysis Pipeline 

This project automates the download, processing, and analysis of Sentinel-2 images to calculate NDVI (Normalized Difference Vegetation Index) for a user-defined area of interest (AOI) in a specified time period. In this specific use case, the AOI corresponds to the Parque Natural de la Breña y Marismas del Barbate in 2025.


## Project Structure

- `data/`
  - `parque_brena_recortado.geojson` - AOI in GeoJSON format.
  - `parque_brena_recortado.qmd` - Additional AOI document.
  - `Parque_natural_de_La_Breña_y_marismas_del_río_Barbate_mapa_limpio.png` - Reference map.
- `ndvi/`
  - Original NDVI files (`ndvi_*.tiff`).
  - `tiff_clipped/` - NDVI clipped to AOI (`clipped_ndvi_*.tiff`).
- `results/`
  - Generated results (plots, CSV files, etc.).
- `scripts/`
  - `01_download_data.py` - Downloads Sentinel-2 images and calculates NDVI.
  - `02_transform_data.py` - Clips NDVI images to the AOI.
  - `03_create_visualization.py` - Visualizes and analyzes NDVI time series.

## Workflow

1. **Download Sentinel-2 Images**  
   Run `scripts/01_download_data.py` to search and download images, and calculate NDVI.

2. **Clip NDVI Images**  
   Run `scripts/02_transform_data.py` to clip NDVI images to the AOI.

3. **Visualize NDVI Time Series**  
   Run `scripts/03_create_visualization.py` to analyze and plot the NDVI evolution over time.

### Workflow Details

- **STAC Catalog Connection**: Uses `pystac_client` to connect to a public STAC catalog for Sentinel-2 data.
- **AOI Handling**: Loads the AOI from a GeoJSON, merges geometries, and ensures proper CRS.
- **NDVI Calculation**: Uses `odc.stac.load` and `odc.geo` to compute NDVI as `(NIR - Red) / (NIR + Red)`.
- **GeoTIFF Export**: NDVI images are exported as Cloud Optimized GeoTIFFs (COG) for efficient storage and access.
- **Clipping**: Uses `rasterio` and `geopandas` to clip NDVI to AOI boundaries.
- **Time Series Analysis**: Reads clipped NDVI files, calculates mean NDVI per image, applies smoothing (rolling mean), and performs linear regression to identify trends.
- **Visualization**: Generates plots with original NDVI, smoothed NDVI, and trend lines; saves CSV with NDVI time series.

## Installation

It is recommended to use a virtual environment. Install dependencies with:

```bash
pip install -r requirements.txt
