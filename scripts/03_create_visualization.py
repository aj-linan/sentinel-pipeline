# ==============================================
# Serie temporal NDVI con suavizado y tendencia
# ==============================================

import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.mask import mask
import geopandas as gpd
from datetime import datetime
from scipy.stats import linregress

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
# Carpeta donde tienes los NDVI en GeoTIFF
path = "C:/Users/Ordenador Lenovo/Documents/geodata/proyecto_labrena/analisis_la_brena/"
ndvi_folder = os.path.join(path, "ndvi_10/tiff_clipped")

# Archivo GeoJSON o Shapefile con el AOI (Parque Natural de la Breña)
aoi_path = os.path.join(path, "data/parque_brena_combinado.geojson")

# -------------------------------
# 1. Leer AOI
# -------------------------------
aoi = gpd.read_file(aoi_path)
aoi = aoi.to_crs(epsg=32630)  # Ajusta si es necesario

# -------------------------------
# 2. Función para calcular NDVI medio
# -------------------------------
def calcular_ndvi_medio(raster_path, aoi_geom):
    """Recorta el raster al AOI y calcula la media de NDVI."""
    with rasterio.open(raster_path) as src:
        if aoi_geom.crs != src.crs:
            aoi_geom = aoi_geom.to_crs(src.crs)
        
        geoms = [aoi_geom.geometry.union_all()]  # Unir geometrías
        out_image, _ = mask(src, geoms, crop=True)
        ndvi = out_image[0]

        ndvi = ndvi[ndvi != src.nodata]
        if ndvi.size == 0:
            return np.nan
        
        return float(np.nanmean(ndvi))

# -------------------------------
# 3. Procesar archivos
# -------------------------------
resultados = []

for file in os.listdir(ndvi_folder):
    if file.lower().endswith(".tiff"):
        path = os.path.join(ndvi_folder, file)

        try:
            fecha_str = file.split("_")[4]  # Ajusta si cambia el formato
            fecha = datetime.strptime(fecha_str, "%Y%m%d").date()
        except:
            print(f"No se pudo extraer fecha de {file}")
            continue

        ndvi_medio = calcular_ndvi_medio(path, aoi)
        resultados.append({"fecha": fecha, "ndvi_medio": ndvi_medio})

df = pd.DataFrame(resultados).sort_values("fecha")

# -------------------------------
# 4. Suavizado con media móvil
# -------------------------------
ventana = 3  # Número de imágenes a promediar
df["ndvi_suavizado"] = df["ndvi_medio"].rolling(window=ventana, center=True).mean()

# -------------------------------
# 5. Cálculo de tendencia lineal
# -------------------------------
# Convertimos fechas a números (días desde la primera fecha)
# Convertir a datetime si no lo está
df["fecha"] = pd.to_datetime(df["fecha"])

# Convertimos fechas a números (días desde la primera fecha)
dias_desde_inicio = (df["fecha"] - df["fecha"].min()).dt.days
slope, intercept, r_value, p_value, std_err = linregress(dias_desde_inicio, df["ndvi_medio"])

tendencia = "creciente" if slope > 0 else "decreciente"
print(f"Tendencia NDVI: {tendencia}")
print(f"Pendiente: {slope:.6f} NDVI/día")
print(f"R²: {r_value**2:.3f}")

# -------------------------------
# 6. Graficar
# -------------------------------
plt.figure(figsize=(12,6))
plt.plot(df["fecha"], df["ndvi_medio"], marker="o", linestyle="-", color="green", alpha=0.5, label="NDVI original")
plt.plot(df["fecha"], df["ndvi_suavizado"], color="red", linewidth=2, label=f"NDVI suavizado ({ventana} imágenes)")

# Línea de tendencia
tend_line = intercept + slope * dias_desde_inicio
plt.plot(df["fecha"], tend_line, color="blue", linestyle="--", label="Tendencia lineal")

plt.title("Serie temporal NDVI - Parque Natural de la Breña", fontsize=14)
plt.xlabel("Fecha", fontsize=12)
plt.ylabel("NDVI medio", fontsize=12)
plt.legend()
plt.grid(True)
plt.savefig("serie_temporal_ndvi_suavizada.png") 
plt.show()


# -------------------------------
# 7. Guardar resultados
# -------------------------------
df.to_csv("serie_temporal_ndvi_suavizada.csv", index=False)
print("Serie temporal guardada como 'serie_temporal_ndvi_suavizada.csv'")
