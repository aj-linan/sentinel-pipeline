import importlib
from . import config

# Dynamic imports for modules starting with numbers
download = importlib.import_module(".01_download", package="src")
processing = importlib.import_module(".02_processing", package="src")

def main():
    print("\n=== Sentinel-2 NDVI Pipeline ===\n")
    
    # Phase 1: Download
    print("--- Phase 1: Download & Calculation ---")
    download.run()
    
    # Phase 2: Processing
    print("\n--- Phase 2: Analysis ---")
    processing.run()
    
    print("\n=== Pipeline Finished Successfully ===")

if __name__ == "__main__":
    main()
