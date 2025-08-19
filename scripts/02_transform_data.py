# Author: Albert Linan Maho

import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
from pathlib import Path

# Define the base path as two levels above the current script location
base_path = Path(__file__).parent.parent.resolve()
print(f"[INFO] Base path set to: {base_path}")

# Path to your AOI
aoi_path = base_path / "data" / "parque_brena_recortado.geojson"
print(f"[INFO] AOI path: {aoi_path}")

# Folder with the original NDVI images
input_folder = base_path / "ndvi"
print(f"[INFO] Input folder for NDVI images: {input_folder}")

# Folder where the clipped images will be stored
output_folder = input_folder / "tiff_clipped"
output_folder.mkdir(exist_ok=True)
print(f"[INFO] Output folder created (if not existing): {output_folder}")

# -------------------------------
# Load AOI
# -------------------------------
print("[STEP 1] Loading AOI...")
aoi = gpd.read_file(aoi_path)
aoi = aoi.to_crs("EPSG:4326")  # Ensure AOI is in WGS84
geojson_aoi = [mapping(aoi.union_all())]  # Convert AOI to mask format
print(f"[INFO] AOI loaded successfully with {len(aoi)} geometries")

# -------------------------------
# Clip images
# -------------------------------
print("[STEP 2] Starting clipping process...")
num_processed = 0
num_failed = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tif") or filename.lower().endswith(".tiff"):
        input_path = input_folder / filename
        print(f"\n[PROCESSING] File: {filename}")

        try:
            with rasterio.open(input_path) as src:
                # Reproject AOI if needed
                if aoi.crs != src.crs:
                    print("[INFO] AOI CRS differs from raster CRS, reprojecting AOI...")
                    aoi = aoi.to_crs(src.crs)
                    geojson_aoi = [mapping(aoi.union_all())]  # Update geometry
                
                # Clip the raster
                print("[INFO] Clipping raster...")
                out_image, out_transform = mask(src, geojson_aoi, crop=True)
                out_meta = src.meta.copy()
                
                # Update metadata
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                # Save the clipped raster
                output_path = output_folder / f"clipped_{filename}"
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                
                print(f"[SUCCESS] Clipped image saved: {output_path}")
                num_processed += 1

        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")
            num_failed += 1

print("\n=== PROCESS SUMMARY ===")
print(f"Total processed: {num_processed}")
print(f"Total failed: {num_failed}")
print("Clipping process finished.")
