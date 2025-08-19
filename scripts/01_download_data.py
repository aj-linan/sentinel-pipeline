# Author: Albert Linan Maho

import geopandas as gpd
from pystac_client import Client
from odc.stac import load
import odc.geo
import os
from pathlib import Path

# -------------------------------
# Connect to catalog
# -------------------------------
def connect_to_stac_catalog(url="https://earth-search.aws.element84.com/v1"):
    """
    Connects to a public STAC catalog.
    
    Args:
        url (str): The STAC catalog URL.
        
    Returns:
        pystac_client.Client: A STAC client object.
    """
    print(f"Connecting to STAC catalog at: {url}")
    return Client.open(url)

# -------------------------------
# Search sentinel data
# -------------------------------
def search_sentinel_data(client, aoi_path, collection, date_range, cloud_cover_limit=0.2):
    """
    Search for Sentinel-2 images matching the specified criteria.
    
    Args:
        client (pystac_client.Client): The STAC client.
        aoi_path (str): Path to the GeoJSON file defining the Area of Interest (AOI).
        collection (str): Collection ID, e.g., 'sentinel-2-l2a'.
        date_range (str): Date range in format 'YYYY-MM-DD/YYYY-MM-DD'.
        cloud_cover_limit (float): Maximum allowed cloud cover (0 to 1).
        
    Returns:
        tuple: List of items (image metadata) and the AOI geometry.
    """
    print("Loading Area of Interest (AOI)...")
    aoi = gpd.read_file(aoi_path)
    # Merge all geometries in the AOI into one for the search
    geometry = aoi.geometry.union_all().__geo_interface__
    
    # Cloud cover filter
    filters = {"eo:cloud_cover": {"lt": cloud_cover_limit}}
    
    print("Searching for images...")
    search = client.search(
        collections=[collection], intersects=geometry, datetime=date_range, query=filters
    )
    
    items = list(search.items())
    print(f"Found {len(items)} images matching the criteria.")
    return items, geometry

# -------------------------------
# Process images and calculate ndvi
# -------------------------------
def process_and_export_ndvi(items, geometry, output_folder):
    """
    Process each found image, calculate NDVI, and export as GeoTIFF.
    
    Args:
        items (list): List of items (images) to process.
        geometry (dict): AOI geometry.
        output_folder (str): Folder to save output files.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"\nStarting processing of {len(items)} images...")
    for i, item in enumerate(items):
        item_id = item.id
        filename = f"ndvi_{item_id}.tiff"
        output_path = os.path.join(output_folder, filename)
        
        print(f"Processing image {i+1}/{len(items)}: {item_id}")
        
        try:
            # Load a single item using odc-stac
            data_single = load([item], geopolygon=geometry, chunks={})
            
            # Calculate NDVI
            # Ensure bands 'nir' and 'red' exist in the dataset
            ndvi = (data_single.nir - data_single.red) / (data_single.nir + data_single.red)
            
            # Export NDVI as Cloud Optimized GeoTIFF (COG)
            odc.geo.xr.write_cog(ndvi, fname=output_path, overwrite=True)
            print(f"  -> File saved at: {output_path}")

        except AttributeError as e:
            print(f"  -> Error: Cannot calculate NDVI for {item_id}. Missing 'nir' or 'red' bands.")
            continue
        except Exception as e:
            print(f"  -> Unexpected error processing {item_id}: {e}")
            continue

# -------------------------------
# Main function
# -------------------------------
def main():
    """
    Main function orchestrating the workflow:
    1. Connect to STAC catalog.
    2. Search Sentinel-2 images for AOI and date range.
    3. Process images and export NDVI as GeoTIFFs.
    """
    # --- Configuration parameters ---
    base_path = Path(__file__).parent.parent.resolve() 

    # Path to the AOI GeoJSON file
    aoi_filepath = base_path / "data/parque_brena_recortado.geojson"
    output_folder = base_path / "ndvi"
    output_folder.mkdir(exist_ok=True) 
    
    # --- Workflow execution ---
    stac_client = connect_to_stac_catalog()

    initial_date = "2025-01-01"
    end_date = "2025-08-19"
    date_range = f"{initial_date}/{end_date}"
    
    items_found, aoi_geometry = search_sentinel_data(
        client=stac_client,
        aoi_path=aoi_filepath,
        collection="sentinel-2-l2a",
        date_range=date_range,
        cloud_cover_limit=0.2
    )
    
    if not items_found:
        print("No images found to process. Exiting script.")
        return
        
    process_and_export_ndvi(items_found, aoi_geometry, output_folder)
    
    print("\nProcess completed successfully.")

if __name__ == "__main__":
    main()
