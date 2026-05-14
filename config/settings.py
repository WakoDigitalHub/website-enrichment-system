import os

# Base project directory (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input and output folders
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure folders exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_input_file():
    """Return the first Excel file found in the input folder."""
    for fname in os.listdir(INPUT_DIR):
        if fname.lower().endswith((".xlsx", ".xls")):
            return os.path.join(INPUT_DIR, fname)
    raise FileNotFoundError("No Excel file found in input folder.")

def get_output_file(input_file):
    """Return the output path with 'Enriched_' prefix in outputs folder."""
    input_name = os.path.basename(input_file)
    output_name = f"Enriched_{input_name}"
    return os.path.join(OUTPUT_DIR, output_name)

# Scraper settings (timeouts, retries, backoff)
SCRAPER_SETTINGS = {
    "aiohttp_timeout": 30,   # seconds
    "aiohttp_retries": 2,    # number of retries
    "aiohttp_backoff": 1.5,  # exponential backoff factor
    "playwright_timeout": 45000,  # milliseconds
    "limit_depth": 5     #limit depth"
}

# Configuration dictionary
CONFIG = {
    "input_file": get_input_file(),
    "output_file": None,
    "log_file": "log.txt"
}

CONFIG["output_file"] = get_output_file(CONFIG["input_file"])
