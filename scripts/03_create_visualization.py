# Author: Albert Linan Maho

import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.mask import mask
import geopandas as gpd
from datetime import datetime
from scipy.stats import linregress
from pathlib import Path
from shapely.geometry import mapping

# -------------------------------
# CONFIGURATION
# -------------------------------
# Base path = parent of the parent of the current script
base_path = Path(__file__).parent.parent.resolve()
print(f"[INFO] Base path: {base_path}")

ndvi_folder = base_path / "ndvi" / "tiff_clipped"
print(f"[INFO] NDVI input folder: {ndvi_folder}")

aoi_path = base_path / "data" / "parque_brena_recortado.geojson"
print(f"[INFO] AOI path: {aoi_path}")

# -------------------------------
# Load AOI
# -------------------------------
print("[STEP 1] Loading AOI...")
aoi = gpd.read_file(aoi_path)
aoi = aoi.to_crs(epsg=32630)  # Adjust CRS if necessary
print(f"[INFO] AOI loaded with {len(aoi)} geometries. CRS: {aoi.crs}")

# -------------------------------
# Function to calculate mean NDVI
# -------------------------------
def calculate_mean_ndvi(raster_path, aoi_geom):
    """Clip raster by AOI and calculate mean NDVI."""
    try:
        with rasterio.open(raster_path) as src:
            if aoi_geom.crs != src.crs:
                print("[INFO] Reprojecting AOI to match raster CRS")
                aoi_geom = aoi_geom.to_crs(src.crs)

            geoms = [mapping(aoi_geom.union_all())]
            out_image, _ = mask(src, geoms, crop=True)
            ndvi = out_image[0]

            ndvi = ndvi[ndvi != src.nodata]
            if ndvi.size == 0:
                print(f"[WARNING] No valid NDVI values found in {raster_path}")
                return np.nan

            return float(np.nanmean(ndvi))
    except Exception as e:
        print(f"[ERROR] Failed to calculate mean NDVI for {raster_path}: {e}")
        return np.nan

# -------------------------------
# 3. Process raster files
# -------------------------------
print("[STEP 2] Processing NDVI rasters...")
results = []
num_processed, num_failed = 0, 0

for file in os.listdir(ndvi_folder):
    if file.lower().endswith((".tif", ".tiff")):
        raster_path = ndvi_folder / file
        print(f"\n[PROCESSING] File: {file}")

        try:
            # Extract date from filename
            date_str = file.split("_")[4]  # Adjust if filename format changes
            date = datetime.strptime(date_str, "%Y%m%d").date()
            print(f"[INFO] Extracted date: {date}")
        except Exception as e:
            print(f"[ERROR] Could not extract date from {file}: {e}")
            num_failed += 1
            continue

        mean_ndvi = calculate_mean_ndvi(raster_path, aoi)
        results.append({"date": date, "mean_ndvi": mean_ndvi})
        num_processed += 1

print(f"\n[SUMMARY] Processed: {num_processed}, Failed: {num_failed}")

df = pd.DataFrame(results).sort_values("date")

# -------------------------------
# 4. Moving average smoothing
# -------------------------------
print("[STEP 3] Applying moving average smoothing...")
window = 3  # Number of images to average
df["ndvi_smoothed"] = df["mean_ndvi"].rolling(window=window, center=True).mean()

# -------------------------------
# 5. Linear trend analysis
# -------------------------------
print("[STEP 4] Calculating linear trend...")
df["date"] = pd.to_datetime(df["date"])
days_since_start = (df["date"] - df["date"].min()).dt.days

slope, intercept, r_value, p_value, std_err = linregress(days_since_start, df["mean_ndvi"])
trend = "increasing" if slope > 0 else "decreasing"

print(f"[RESULT] NDVI trend: {trend}")
print(f"[RESULT] Slope: {slope:.6f} NDVI/day")
print(f"[RESULT] R²: {r_value**2:.3f}")

# -------------------------------
# 6. Plotting
# -------------------------------
print("[STEP 5] Plotting time series...")
plt.figure(figsize=(12,6))
plt.plot(df["date"], df["mean_ndvi"], marker="o", linestyle="-", color="green", alpha=0.5, label="Original NDVI")
plt.plot(df["date"], df["ndvi_smoothed"], color="red", linewidth=2, label=f"Smoothed NDVI ({window} images)")

# Trend line
trend_line = intercept + slope * days_since_start
plt.plot(df["date"], trend_line, color="blue", linestyle="--", label="Linear trend")

plt.title("NDVI Time Series - Parque Natural de la Breña", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Mean NDVI", fontsize=12)
plt.legend()
plt.grid(True)

output_plot = base_path / "results" / "temporal_series_ndvi_smoothed.png"
plt.savefig(output_plot)
plt.show()
print(f"[INFO] Plot saved as {output_plot}")

# -------------------------------
# 7. Save results
# -------------------------------
output_csv = base_path / "results" / "temporal_series_ndvi_smoothed.csv"
df.to_csv(output_csv, index=False)
print(f"[INFO] Time series saved as {output_csv}")

