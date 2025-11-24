import os
import geopandas as gpd
from pystac_client import Client
from odc.stac import load
import odc.geo
from . import config

def connect_to_stac(url=config.STAC_API_URL):
    print(f"Connecting to STAC catalog: {url}")
    return Client.open(url)

def search_images(client, aoi_path, collection, date_range, cloud_cover=config.CLOUD_COVER_LIMIT):
    print("Loading AOI and searching for images...")
    aoi = gpd.read_file(aoi_path)
    geometry = aoi.geometry.union_all().__geo_interface__
    
    filters = {"eo:cloud_cover": {"lt": cloud_cover}}
    
    search = client.search(
        collections=[collection], 
        intersects=geometry, 
        datetime=date_range, 
        query=filters
    )
    
    items = list(search.items())
    print(f"Found {len(items)} images.")
    return items, geometry

def download_and_calc_ndvi(items, geometry, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing {len(items)} images...")
    
    for i, item in enumerate(items):
        item_id = item.id
        output_path = output_dir / f"ndvi_{item_id}.tiff"
        
        if output_path.exists():
             print(f"[{i+1}/{len(items)}] Skipping {item_id} (already exists)")
             continue

        print(f"[{i+1}/{len(items)}] Processing {item_id}")
        
        try:
            data = load([item], geopolygon=geometry, chunks={})
            ndvi = (data.nir - data.red) / (data.nir + data.red)
            
            odc.geo.xr.write_cog(ndvi, fname=output_path, overwrite=True)

        except AttributeError:
            print(f"  Warning: Missing bands for {item_id}")
        except Exception as e:
            print(f"  Error processing {item_id}: {e}")

def run():
    client = connect_to_stac()
    
    items, geometry = search_images(
        client, 
        config.AOI_PATH, 
        config.COLLECTION, 
        config.DATE_RANGE
    )
    
    if not items:
        print("No images found.")
        return
        
    download_and_calc_ndvi(items, geometry, config.OUTPUT_DIR)
    print("Download phase complete.")

if __name__ == "__main__":
    run()
