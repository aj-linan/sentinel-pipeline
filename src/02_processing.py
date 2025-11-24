import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.mask import mask
import geopandas as gpd
from datetime import datetime
from scipy.stats import linregress
from shapely.geometry import mapping
from . import config

def load_aoi():
    print("Loading AOI...")
    aoi = gpd.read_file(config.AOI_PATH)
    return aoi.to_crs(config.TARGET_CRS)

def calculate_mean_ndvi(raster_path, aoi_geom):
    try:
        with rasterio.open(raster_path) as src:
            if aoi_geom.crs != src.crs:
                aoi_geom = aoi_geom.to_crs(src.crs)

            geoms = [mapping(aoi_geom.union_all())]
            out_image, _ = mask(src, geoms, crop=True)
            ndvi = out_image[0]

            # Filter nodata and invalid values
            valid_ndvi = ndvi[(ndvi != src.nodata) & np.isfinite(ndvi)]

            if valid_ndvi.size == 0:
                return np.nan

            return float(np.mean(valid_ndvi))
            
    except Exception as e:
        print(f"Error calculating NDVI for {raster_path.name}: {e}")
        return np.nan

def process_files(aoi):
    print("Processing NDVI files...")
    results = []
    files = [f for f in os.listdir(config.OUTPUT_DIR) if f.lower().endswith((".tif", ".tiff"))]
    
    if not files:
        print("No TIFF files found.")
        return pd.DataFrame()

    for file in files:
        try:
            # Extract date from filename (assuming format contains YYYYMMDD)
            parts = file.split("_")
            date_str = next((p for p in parts if len(p) == 8 and p.isdigit() and p.startswith("20")), None)
            
            if not date_str:
                continue

            date = datetime.strptime(date_str, "%Y%m%d").date()
            
            mean_ndvi = calculate_mean_ndvi(config.OUTPUT_DIR / file, aoi)
            
            if not np.isnan(mean_ndvi):
                results.append({"date": date, "mean_ndvi": mean_ndvi})
                
        except Exception:
            continue

    return pd.DataFrame(results).sort_values("date")

def analyze_and_plot(df):
    if df.empty:
        print("No data to analyze.")
        return

    # Smoothing
    df["ndvi_smoothed"] = df["mean_ndvi"].rolling(window=config.MOVING_AVERAGE_WINDOW, center=True).mean()

    # Trend Analysis
    df["date"] = pd.to_datetime(df["date"])
    days = (df["date"] - df["date"].min()).dt.days
    
    valid = df.dropna(subset=["mean_ndvi"])
    
    if len(valid) > 1:
        slope, intercept, r_val, _, _ = linregress(days[valid.index], valid["mean_ndvi"])
        trend = "increasing" if slope > 0 else "decreasing"
        print(f"Trend: {trend} (Slope: {slope:.6f}, R²: {r_val**2:.3f})")
    else:
        slope, intercept = 0, 0
        print("Insufficient data for trend analysis.")

    # Plotting
    plt.figure(figsize=(12,6))
    plt.plot(df["date"], df["mean_ndvi"], "o-", color="green", alpha=0.5, label="Original")
    plt.plot(df["date"], df["ndvi_smoothed"], "r-", linewidth=2, label="Smoothed")

    if len(valid) > 1:
        plt.plot(df["date"], intercept + slope * days, "b--", label="Trend")

    plt.title("NDVI Time Series - Parque Natural de la Breña")
    plt.xlabel("Date")
    plt.ylabel("Mean NDVI")
    plt.legend()
    plt.grid(True)

    output_plot = config.RESULTS_DIR / "ndvi_plot.png"
    plt.savefig(output_plot)
    print(f"Plot saved to {output_plot}")

    output_csv = config.RESULTS_DIR / "ndvi_data.csv"
    df.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv}")

def run():
    aoi = load_aoi()
    df = process_files(aoi)
    analyze_and_plot(df)

if __name__ == "__main__":
    run()
