from pathlib import Path

# Base paths
BASE_PATH = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_PATH / "input"
OUTPUT_DIR = BASE_PATH / "ndvi"
RESULTS_DIR = BASE_PATH / "results"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# STAC Configuration
STAC_API_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"
CLOUD_COVER_LIMIT = 0.2

# AOI Configuration
AOI_FILENAME = "aoi.geojson"
AOI_PATH = DATA_DIR / AOI_FILENAME

# Date Range
INITIAL_DATE = "2025-01-01"
END_DATE = "2025-08-19"
DATE_RANGE = f"{INITIAL_DATE}/{END_DATE}"

# Processing Configuration
TARGET_CRS = "EPSG:32630"  # UTM Zone 30N (suitable for Spain/Cadiz area)
MOVING_AVERAGE_WINDOW = 3
