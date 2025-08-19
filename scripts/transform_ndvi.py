# 1. Librerías necesarias
import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping

# === CONFIGURACIÓN ===
# Ruta a tu AOI
path = "C:/Users/Ordenador Lenovo/Documents/geodata/proyecto_labrena/analisis_la_brena/"
aoi_path = os.path.join(path, "data/parque_brena_recortado.geojson")

# Carpeta con las imágenes originales
input_folder = os.path.join(path, "ndvi_10")

# Carpeta donde se guardarán las imágenes recortadas
output_folder = os.path.join(path, "ndvi_10/tiff_clipped")
os.makedirs(output_folder, exist_ok=True)

# 2. Cargar AOI
aoi = gpd.read_file(aoi_path)
aoi = aoi.to_crs("EPSG:4326")  # asegurar que está en WGS84
geojson_aoi = [mapping(aoi.union_all())]  # convertir a formato máscara

print(f"AOI cargado con {len(aoi)} geometrías")

# 3. Recortar imágenes
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tif") or filename.lower().endswith(".tiff"):
        input_path = os.path.join(input_folder, filename)
        
        with rasterio.open(input_path) as src:
            # Reproyectar AOI si es necesario
            if aoi.crs != src.crs:
                aoi = aoi.to_crs(src.crs)
                geojson_aoi = [mapping(aoi.union_all())]  # actualizar geometría
            
            # Recortar
            out_image, out_transform = mask(src, geojson_aoi, crop=True)
            out_meta = src.meta.copy()
            
            # Actualizar metadatos
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            # Guardar resultado
            output_path = os.path.join(output_folder, f"clipped_{filename}")
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
        
        print(f"Imagen recortada guardada: {output_path}")

print("Proceso completado.")
