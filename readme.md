# Proyecto NDVI - Parque Natural de la Breña y Marismas del Barbate (2015-2025)

Este proyecto tiene como objetivo obtener y analizar imágenes satelitales Sentinel-2 para calcular el NDVI (Índice de Vegetación de Diferencia Normalizada) en el Parque Natural de la Breña y Marismas del Barbate durante el período 2015-2025.

## Estructura del proyecto

- `data/raw/` - Datos originales, incluidas las imágenes Sentinel-2 descargadas y el shapefile/GeoJSON del área de estudio.  
- `data/processed/` - Datos procesados, como imágenes NDVI calculadas y recortadas.  
- `data/final/` - Productos finales comprimidos y listos para análisis.  
- `notebooks/` - Notebooks para análisis exploratorio y visualización.  
- `scripts/` - Scripts en Python para la descarga, procesamiento y cálculo de NDVI.  
- `results/` - Resultados visuales como gráficos y mapas generados.  
- `logs/` - Logs de ejecución (opcional).  
- `parque_brena.geojson` - Definición del área de estudio en formato GeoJSON.

## Instalación y dependencias

Se recomienda usar un entorno virtual. Instalar dependencias con:

```bash
pip install -r requirements.txt
