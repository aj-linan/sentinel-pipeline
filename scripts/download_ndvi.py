# Get Sentinel Data within seconds in Python
# https://medium.com/rotten-grapes/download-sentinel-data-within-seconds-in-python-8cc9a8c3e23c
# Author: Krishna G. Lodha

import geopandas as gpd
from pystac_client import Client
from odc.stac import load
import odc.geo
import os

def connect_to_stac_catalog(url="https://earth-search.aws.element84.com/v1"):
    """
    Establece la conexión a un catálogo STAC público.
    
    Args:
        url (str): La URL del catálogo STAC.
        
    Returns:
        pystac_client.Client: Un objeto cliente de STAC.
    """
    print(f"Conectando al catálogo STAC en: {url}")
    return Client.open(url)

def search_sentinel_data(client, aoi_path, collection, date_range, cloud_cover_limit=0.2):
    """
    Busca imágenes de Sentinel-2 que cumplan con los criterios especificados.
    
    Args:
        client (pystac_client.Client): El cliente de STAC.
        aoi_path (str): Ruta al archivo GeoJSON del área de interés (AOI).
        collection (str): ID de la colección, ej: 'sentinel-2-l2a'.
        date_range (str): Rango de fechas, ej: '2023-01-10/2023-05-20'.
        cloud_cover_limit (float): Límite máximo de cobertura de nubes (0 a 1).
        
    Returns:
        list: Una lista de ítems (metadatos de las imágenes) encontrados.
    """
    print("Cargando el área de interés...")
    aoi = gpd.read_file(aoi_path)
    geometry = aoi.geometry.union_all().__geo_interface__
    
    filters = {"eo:cloud_cover": {"lt": cloud_cover_limit}}
    
    print("Buscando imágenes...")
    search = client.search(
        collections=[collection], intersects=geometry, datetime=date_range, query=filters
    )
    
    items = list(search.items())
    print(f"Se encontraron {len(items)} imágenes que cumplen los criterios.")
    return items, geometry

def process_and_export_ndvi(items, geometry, output_folder):
    """
    Procesa cada imagen encontrada, calcula el NDVI y exporta un archivo TIFF.
    
    Args:
        items (list): Lista de ítems (imágenes) a procesar.
        geometry (dict): Geometría del área de interés.
        output_folder (str): Carpeta donde se guardarán los archivos.
    """
    # Crear la carpeta de salida si no existe
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"\nIniciando el procesamiento de {len(items)} imágenes...")
    for i, item in enumerate(items):
        item_id = item.id
        filename = f"ndvi_{item_id}.tiff"
        output_path = os.path.join(output_folder, filename)
        
        print(f"Procesando imagen {i+1}/{len(items)}: {item_id}")
        
        try:
            # Cargar un solo ítem usando odc-stac
            data_single = load([item], geopolygon=geometry, chunks={})
            
            # Calcular NDVI
            # Es vital asegurar que las bandas 'nir' y 'red' existen
            ndvi = (data_single.nir - data_single.red) / (data_single.nir + data_single.red)
            
            # Exportar el resultado
            odc.geo.xr.write_cog(ndvi, fname=output_path, overwrite=True)
            print(f"  -> Archivo guardado en: {output_path}")

        except AttributeError as e:
            print(f"  -> Error: No se pudo calcular NDVI para {item_id}. Faltan bandas 'nir' o 'red'.")
            continue
        except Exception as e:
            print(f"  -> Ocurrió un error inesperado al procesar {item_id}: {e}")
            continue

def main():
    """
    Función principal que orquesta todo el flujo de trabajo.
    """
    # --- Parámetros de configuración ---
    base_path = "C:/Users/Ordenador Lenovo/Documents/geodata/proyecto_labrena/analisis_la_brena"
    aoi_filepath = os.path.join(base_path, "data/parque_brena_combinado.geojson")
    output_directory = os.path.join(base_path, "ndvi_10")
    
    # --- Ejecución del flujo de trabajo ---
    stac_client = connect_to_stac_catalog()

    fecha_inicial = "2010-01-01"
    fecha_final = "2025-08-10"
    date_range = f"{fecha_inicial}/{fecha_final}"
    
    items_found, aoi_geometry = search_sentinel_data(
        client=stac_client,
        aoi_path=aoi_filepath,
        collection="sentinel-2-l2a",
        date_range=date_range,
        cloud_cover_limit=0.2
    )
    
    if not items_found:
        print("No se encontraron imágenes para procesar. Finalizando el script.")
        return
        
    process_and_export_ndvi(items_found, aoi_geometry, output_directory)
    
    print("\nEl proceso completo ha finalizado con éxito.")

if __name__ == "__main__":
    main()